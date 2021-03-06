import conf

from passlib.utils import generate_password
from collections import namedtuple

import string
import math


def estimate_entropy(password):
	alphabet_size = 0
	pwd_letters = set(password)

	for alph in estimate_entropy.alphabets:
		if alph & pwd_letters:
			alphabet_size += len(alph)
			pwd_letters -= alph

	alphabet_size += len(pwd_letters)

	if( alphabet_size == 0 ):
		return 0

	# from http://blog.shay.co/password-entropy/
	entropy = len(password) * math.log(alphabet_size, 2)

	return entropy

estimate_entropy.alphabets = [
	set(string.ascii_lowercase),
	set(string.ascii_uppercase),
	set(string.digits),
	set(string.punctuation),
]

def token_expire_time():
	if conf.AUTH_TOKEN_DURATION is None:
		return None
	else:
		#TODO
		return None

def create_token(user_id, expires=None):
	if expires is None:
		expires = token_expire_time()

	token = generate_password(conf.AUTH_TOKEN_LENGTH)

	conf.DB_CONN.execute("""
		INSERT INTO Sessions
			(token, user_id, expires)
		VALUES
			(?, ?, ?)
		""", (token, user_id, expires)
	)
	conf.DB_CONN.commit()

	return token

def create_db():
	conf.DB_CONN.execute("""
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

	conf.DB_CONN.execute("""
		CREATE TABLE Sessions
		(
			token       TEXT PRIMARY KEY,
			user_id		INT,
			expires		DATE,
			FOREIGN KEY(user_id) REFERENCES Users(id)
		);
	""")

	cursor = conf.DB_CONN.execute("""
		INSERT INTO Users
			(username, email, hash_scheme, passhash)
		VALUES
			(?, ?, ?, ?)
		""", ('root', 'root@example.com', conf.DEFAULT_SCHEME, 'NOPASS') 
		# Cannot login as root as it's passhash will never match a hash
	)
	conf.DB_CONN.commit()
	
	print('Root Token:', create_token(cursor.lastrowid))

def get_user(token):
	User = namedtuple('User', ['user_id', 'username'])

	cursor = conf.DB_CONN.execute("""
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