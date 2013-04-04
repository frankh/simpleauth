import argparse
import tornado

from handlers import Create, Login, Auth

import conf
import utils

simpleauth = tornado.web.Application([
	(r"/login", Login),
	(r"/create", Create),
	(r"/auth", Auth),
])

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument(
		'-p', 
		'--port', 
		metavar='port', 
		type=int,
		default=7999,
		help='listen on the specified port'
	)

	parser.add_argument(
		'-c', 
		'--create', 
		metavar='create',
		action='store_const',
		const=True, 
		default=False,
		help='create a new database'
	)

	parser.add_argument(
		'-d', 
		'--database', 
		metavar='db_path',
		type=str,
		default='users.sqlite',
		help='the sqlite db file to use'
	)

	args = parser.parse_args()

	conf.DB_NAME = args.database
	conf.init()

	if args.create:
		print('Creating new db "{db}"'.format(db=args.database))
		utils.create_db()
	else:
		simpleauth.listen(args.port)
		print('Listening on port {port}'.format(port=args.port))
		print('Using user db "{db}"'.format(db=args.database))
		iol = tornado.ioloop.IOLoop.instance()
		iol.start()
