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
		help='listen on the specified port'
	)

	parser.add_argument(
		'-d', 
		'--database', 
		metavar='db',
		type=str,
		default='users.sqlite',
		help='listen on the specified port'
	)

	args = parser.parse_args()

	conf.DB_NAME = args.db
	conf.init()

	if args.create:
		print('Creating new db "{db}"'.format(db=args.db))
		utils.create_db()
	else:
		simpleauth.listen(args.port)
		print('Listening on port {port}'.format(port=args.port))
		iol = tornado.ioloop.IOLoop.instance()
		iol.start()