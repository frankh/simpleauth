import argparse
import tornado

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

	socket_app.listen(arg.port)
	print('Listening on port {port}'.format(port=args.port))
	iol = tornado.ioloop.IOLoop.instance()
	iol.start()