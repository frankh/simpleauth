import sqlite3
import passlib.hash

DB_NAME = 'users.sqlite'
DB_CONN = None

HASH_SCHEMES = {
	'sha256_crypt': passlib.hash.sha256_crypt
}

DEFAULT_SCHEME = 'sha256_crypt'
DEFAULT_HASHER = HASH_SCHEMES[DEFAULT_SCHEME].encrypt

AUTH_TOKEN_DURATION = None
AUTH_TOKEN_LENGTH = 100

def init():
	global DB_CONN
	DB_CONN = sqlite3.connect(DB_NAME)
	#TODO
