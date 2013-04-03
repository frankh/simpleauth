import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.websocket
 
from passlib.hash import sha256_crypt
from passlib.utils import generate_password

import sqlite3

import settings

schemes = {
	'sha256_crypt': sha256_crypt
}

db_conn = sqlite3.connect(settings.DB_NAME)

def init_db():	

	db_conn.execute("""
		CREATE TABLE IF NOT EXISTS Users
		(
			id          INTEGER PRIMARY KEY,
			username    TEXT NOT NULL UNIQUE, 
			email       TEXT NOT NULL UNIQUE, 
			hash_scheme TEXT NOT NULL, 
			passhash    TEXT NOT NULL,
			create_date DATE DEFAULT CURRENT_TIMESTAMP,
			last_login  DATE
		);
	""")

	db_conn.execute("""
		CREATE TABLE IF NOT EXISTS Sessions
		(
			token       TEXT PRIMARY KEY,
			user_id		INT,
			expires		DATE,
			FOREIGN KEY(user_id) REFERENCES Users(id)
		);
	""")

	db_conn.commit()


	root_user = db_conn.execute("""
		SELECT id FROM Users WHERE username=?
	""", ('root',)).fetchone()

	if not root_user:
		crypt = schemes[settings.HASH_SCHEME]

		cursor = db_conn.execute("""
			INSERT INTO Users
				(username, email, hash_scheme, passhash)
			VALUES
				(?, ?, ?, ?)
			""", ('root', 'root@example.com', settings.HASH_SCHEME, crypt.encrypt(generate_password(20)))
		)
		db_conn.commit()

		print('Root Token:', create_token(cursor.lastrowid))

def token_expire_time():
	if settings.TOKEN_DURATION is None:
		return None
	else:
		#TODO
		return None

def create_token(user_id, expires=None):
	if expires is None:
		expires = token_expire_time()

	token = generate_password(20)

	db_conn.execute("""
		INSERT INTO Sessions
			(token, user_id, expires)
		VALUES
			(?, ?, ?)
		""", (token, user_id, expires)
	)
	db_conn.commit()

	return token

def get_user(token):
	cursor = db_conn.execute("""
		SELECT
			user_id,
			username
		FROM
			Sessions s
		JOIN 
			Users u ON s.user_id = u.id 
		WHERE
			s.token = ?
	""", (token,))

	r = cursor.fetchone()

	if not r:
		return None

	return r

init_db()

class Create(tornado.web.RequestHandler):
	SUPPORTED_METHODS = ('POST')

	def post(self):
		super_token = self.get_argument("super_token", default=None, strip=False)
		username    = self.get_argument("username"   , default=None, strip=False)
		email       = self.get_argument("email"      , default=None, strip=False)
		password    = self.get_argument("password"   , default=None, strip=False)

		# Only allow root to create users.
		if not (get_user(super_token) and get_user(super_token)[1] == 'root'):
			self.set_status(401)
			return

		crypt = schemes[settings.HASH_SCHEME]

		cursor = db_conn.execute("""
			INSERT INTO Users
				(username, email, hash_scheme, passhash)
			VALUES
				(?, ?, ?, ?)
			""", (username, email, settings.HASH_SCHEME, crypt.encrypt(password))
		)
		db_conn.commit()

		# TODO potential race condition if tornado is multithreaded
		token = create_token(cursor.lastrowid)
		self.write(token)

class Login(tornado.web.RequestHandler):
	SUPPORTED_METHODS = ('POST')
	DEFAULT_HASH = schemes[settings.HASH_SCHEME].encrypt('')

	def post(self):
		username = self.get_argument("username", default=None, strip=False)
		password = self.get_argument("password", default=None, strip=False)

		cursor = db_conn.execute("""
			SELECT 
				id,
				hash_scheme, 
				passhash 
			FROM 
				Users 
			WHERE 
				username=?
		""", (username,))

		r = cursor.fetchone()
		if not r:
			# To prevent timing attacks on whether user exists.
			user_id, hash_scheme, passhash = (0, settings.HASH_SCHEME, self.DEFAULT_HASH)
		else:
			user_id, hash_scheme, passhash = r

		if schemes[hash_scheme].verify(password, passhash):
			token = create_token(user_id)
			self.write(token)
		else:
			self.set_status(401)

class Auth(tornado.web.RequestHandler):
	def post(self):
		token = self.get_argument("token", default=None, strip=False)

		if not get_user(token):
			self.set_status(401)
		else:
			self.write(get_user(token)[1])

socket_app = tornado.web.Application([
	(r"/login", Login),
	(r"/create", Create),
	(r"/auth", Auth),
])

if __name__ == '__main__':
	socket_app.listen(7999)
	print('Listening on port 7999')
	iol = tornado.ioloop.IOLoop.instance()
	tornado.ioloop.PeriodicCallback(lambda: None,500,iol).start()
	iol.start()
