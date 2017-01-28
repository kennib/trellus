import re
from code import InteractiveConsole

class TrellusConsole(InteractiveConsole):
	def __init__(self, server, locals=None, filename="<console>"):
		"""Add trellus to the Python interactive console"""
		self.server = server

		# Add trellus to __builtins__
		builtins = __builtins__.__dict__ if hasattr(__builtins__, '__dict__') else __builtins__
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
