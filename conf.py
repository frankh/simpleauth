import sqlite3
import passlib.hash

def init():
	global db_name, db_conn, hash_schemes, default_scheme, default_hasher, auth_token_duration

	db_name = 'users.sqlite'
	db_conn = sqlite3.connect(db_name)

	hash_schemes = {
		'sha256_crypt': passlib.hash.sha256_crypt
	}

	default_scheme = 'sha256_crypt'
	default_hasher = hash_schemes[default_scheme].encrypt

	auth_token_duration = None