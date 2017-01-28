from server import *
from storage import *
from console import *

if __name__ == '__main__':
	import argparse
	from code import interact

	# Parse command line arguments
	parser = argparse.ArgumentParser(description='Set up a trellus server')
	parser.add_argument('--host', metavar='host', type=str,
				   help='The host address e.g. "localhost" or "127.0.0.1"')
	parser.add_argument('--port', metavar='port', type=int,
				   help='The port the server will be connected to')
	parser.add_argument('--seeds', type=str, nargs='*',
				   help='The host:port of servers used to connect to the larger trellus network')
	parser.add_argument('--storage', type=str,
				   help='The file in which trellus data will be stored')

	args = parser.parse_args()

	server_args = {}
	if args.host:
		server_args['host'] = args.host
	if args.port:
		server_args['port'] = args.port
	if args.seeds:
		server_args['seeds'] = [(host, int(port)) for host, port in [seed.split(':') for seed in args.seeds]]
	if args.storage:
		server_args['storage_filename'] = args.storage

	# Create a trellus server
	server = TrellusServer(**server_args)
	# Interact with trellus
	console = TrellusConsole(server, symbol_table=dict(server.storage))
	console.interact()
