import re
import hashlib
import dill
from kad import DHT
from code import InteractiveConsole

class TrellusServer():
	def __init__(self, host='localhost', port=6161, seeds=[]):
		"""Initialise TrellusServer and start the DHT server"""
		self.host = host
		self.port = port

		self.seeds = seeds

		self.dht = DHT(self.host, self.port, seeds=self.seeds)

	def publish(self, object, name):
		"""Publish an object to trellus, get the hash of the object back"""
		# Serialize the object for hashing and storing
		object_serialized = dill.dumps(object)
		object_string = object_serialized.decode('latin-1')
		hash = hashlib.sha224(object_serialized).hexdigest()

		# Store the object - with a name if we have one
		self.dht[hash] = object_string
		if name:
			self.dht[name] = object_string

		return hash
	
	def fetch(self, name):
		"""Retrieve the name from trellus"""
		object_serialized = self.dht[name].encode('latin-1')
		object = dill.loads(object_serialized)

		return object

class TrellusConsole(InteractiveConsole):
	def __init__(self, server, locals=None, filename="<console>"):
		"""Add trellus to the Python interactive console"""
		self.server = server

		# Add trellus to __builtins__
		builtins = __builtins__.__dict__
		builtins['publish'] = self.server.publish
		builtins['fetch'] = self.server.fetch

		# Add __builtins__ to local variables
		if locals is None:
			locals = {}
		locals.setdefault('__builtins__', builtins)

		super().__init__(locals=locals, filename=filename)

	def interact(self, *args, **kwargs):
		"""Add eadline history functionality to the console"""
		try:
			import readline
		except ImportError:
			pass

		super().interact(*args, **kwargs)

	def runcode(self, code):
		"""Intercept NameErrors, and try and find objects with that name from the trellus server"""

		retry = False
		try:
			exec(code, self.locals)
		except NameError as e:
			show_error = False

			# Get the missing name
			name = re.match("name '(\w+)' is not defined", str(e)).group(1)
			try:
				# Get the object for the missing name
				object = self.server.fetch(name)
				# Try again with the new object
				self.locals[name] = object
				retry = True
			except KeyError:
				show_error = True

			if show_error:
				# Give up and show the NameError
				self.showtraceback()
		except SystemExit:
			raise
		except:
			self.showtraceback()

		if retry:
			# Retry the code
			self.runcode(code)

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

	args = parser.parse_args()

	server_args = {}
	if args.host:
		server_args['host'] = args.host
	if args.port:
		server_args['port'] = args.port
	if args.seeds:
		server_args['seeds'] = [(host, int(port)) for host, port in [seed.split(':') for seed in args.seeds]]

	# Create a trellus server
	server = TrellusServer(**server_args)
	# Interact with trellus
	console = TrellusConsole(server)
	console.interact()
