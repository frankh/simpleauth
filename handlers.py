import tornado.web

from conf import    \
	db_conn,        \
	hash_schemes,   \
	default_scheme, \
	default_hasher

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

		cursor = db_conn.execute("""
			INSERT INTO Users
				(username, email, hash_scheme, passhash)
			VALUES
				(?, ?, ?, ?)
			""", (username, email, default_scheme, default_hasher(password))
		)
		db_conn.commit()

		# TODO potential race condition if tornado is multithreaded
		token = create_token(cursor.lastrowid)
		self.write(token)

class Login(tornado.web.RequestHandler):
	SUPPORTED_METHODS = ('POST')
	DEFAULT_HASH = default_hasher('')

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
			# To simplify code path
			user_id, hash_scheme, passhash = (0, default_scheme, self.DEFAULT_HASH)
		else:
			user_id, hash_scheme, passhash = r

		if hash_schemes[hash_scheme].verify(password, passhash):
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
