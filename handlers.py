import tornado.web

import conf

from utils import \
	get_user,     \
	create_token

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

		cursor = conf.DB_CONN.execute("""
			INSERT INTO Users
				(username, email, hash_scheme, passhash)
			VALUES
				(?, ?, ?, ?)
			""", (username, email, conf.DEFAULT_SCHEME, conf.DEFAULT_HASHER(password))
		)
		conf.DB_CONN.commit()

		# TODO potential race condition if tornado is multithreaded
		token = create_token(cursor.lastrowid)
		self.write(token)

class Login(tornado.web.RequestHandler):
	SUPPORTED_METHODS = ('POST')

	def post(self):
		username = self.get_argument("username", default=None, strip=False)
		password = self.get_argument("password", default=None, strip=False)

		cursor = conf.DB_CONN.execute("""
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
			# To simplify code path
			user_id, hash_scheme, passhash = (0, conf.DEFAULT_SCHEME, '')
		else:
			user_id, hash_scheme, passhash = r

		if conf.HASH_SCHEMES[hash_scheme].verify(password, passhash):
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
