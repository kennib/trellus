class SymbolList():
	def __init__(self, symbols=None):
		self.symbols = symbols if symbols else []

	def eval(self, symbol_table, args=None):
		args = args if args else []
		if len(self.symbols) > 0:
			symbols = [
				symbol.eval(symbol_table) if type(symbol) is SymbolList
				else symbol
				for symbol in self.symbols[1:]
			]
			first_symbol = self.symbols[0]
			return first_symbol.eval(symbol_table, symbols)
		else:
			return self

	def __repr__(self):
		return '(' + ' '.join(str(symbol) for symbol in self.symbols) + ')'

	def __str__(self):
		return '(' + ' '.join(str(symbol) for symbol in self.symbols) + ')'

class TrellusSymbol():
	def __init__(self, symbol):
		self.symbol = symbol
	
	def eval(self, symbol_table, args=None):
		args = args if args else []
		# Try applying the symbol as a function
		try:
			object = symbol_table[self.symbol]
			return object(*args)
		except TypeError:
			pass
		except KeyError:
			pass

		# Try evaluating the symbol
		try:
			return TrellusSymbol(repr(eval(self.symbol)))
		except:
			return self

	def __repr__(self):
		return repr(self.symbol)

	def __str__(self):
		return str(self.symbol)
