import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.websocket
 
from passlib.hash import sha256_crypt
from passlib.utils import generate_password

import sqlite3

import settings

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
