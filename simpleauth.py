import argparse
import tornado

from handlers import Create, Login, Auth

simpleauth = tornado.web.Application([
	(r"/login", Login),
	(r"/create", Create),
	(r"/auth", Auth),
])

if __name__ == '__main__':
	parser = argparse.ArgumentParser

	parser.add_argument(
		'-p', 
		'--port', 
		metavar='port', 
		type=int,
		default=7999,
		help='listen on the specified port'
	)

	args = parser.parse_args()

	simpleauth.listen(args.port)
	print('Listening on port {port}'.format(port=args.port))
	iol = tornado.ioloop.IOLoop.instance()
	iol.start()