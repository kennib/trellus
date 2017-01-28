import dill

class TrellusLocalStorage(dict):
	def __init__(self, filename):
		self.filename = filename

		try:
			# Load data from file
			with open(self.filename, 'rb') as file:
				dict = dill.load(file)
				self.update(dict)
		except FileNotFoundError:
			pass

	def close(self):
		# Save the data
		with open(self.filename, 'wb') as file:
			dill.dump(dict(self), file)
			file.close()
