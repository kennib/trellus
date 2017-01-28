import hashlib
import atexit
import dill
from kad import DHT

from storage import *
from ast import *

class TrellusServer():
	def __init__(self, host='localhost', port=6161, seeds=[], storage_filename=None):
		"""Initialise TrellusServer and start the DHT server"""
		self.host = host
		self.port = port

		self.seeds = seeds

		self.dht = DHT(self.host, self.port, seeds=self.seeds)

		# Get local stored variables
		if storage_filename:
			self.storage = TrellusLocalStorage(storage_filename)
		else:
			self.storage = {}

		# Write to storage when the server is closed
		if hasattr(self.storage, 'close'):
			atexit.register(self.storage.close)

	def publish(self, object, name=None):
		"""Publish an object to trellus, get the hash of the object back"""
		# Serialize the object for hashing and storing
		object_serialized = dill.dumps(object)
		object_string = object_serialized.decode('latin-1')
		hash = hashlib.sha224(object_serialized).hexdigest()

		# Store the object locally
		if self.storage:
			self.storage[hash] = object
			if name:
				self.storage[name] = object

		# Store the object - with a name if we have one
		self.dht[hash] = object_string
		if name:
			self.dht[name] = object_string

		return TrellusSymbol(hash)
	
	def fetch(self, symbol):
		"""Retrieve the symbol from trellus"""
		name = symbol.symbol
		if self.storage and name in self.storage:
			# Fetch the object from storage
			object = self.storage[name]
		else:
			# Fetch the object from trellus
			object_string = self.dht[name]
			object_serialized = object_string.encode('latin-1')
			hash = hashlib.sha224(object_serialized).hexdigest()
			object = dill.loads(object_serialized)
			# Put in local storage
			self.storage[hash] = object
			self.storage[name] = object

		return object
