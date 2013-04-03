from conf import    \
	db_conn,        \
	hash_schemes,   \
	default_scheme, \
	default_hasher, \
	auth_token_duration

from passlib.utils import generate_password

from collections import namedtuple


def token_expire_time():
	if auth_token_duration is None:
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

def create_db():
	db_conn.execute("""
		CREATE TABLE Users
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
		CREATE TABLE Sessions
		(
			token       TEXT PRIMARY KEY,
			user_id		INT,
			expires		DATE,
			FOREIGN KEY(user_id) REFERENCES Users(id)
		);
	""")

	cursor = db_conn.execute("""
		INSERT INTO Users
			(username, email, hash_scheme, passhash)
		VALUES
			(?, ?, ?, ?)
		""", ('root', 'root@example.com', default_scheme, default_hasher(generate_password(20)))
	)
	db_conn.commit()
	
	print('Root Token:', create_token(cursor.lastrowid))

def get_user(token):
	User = namedtuple('User', ['user_id', 'username'])

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

	return User(*r)