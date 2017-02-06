from ast import *

def library(console=None):
	symbol_table = {}

	if console:
		symbol_table['eval'] = lambda symbol: symbol.eval(console.symbol_table)
		symbol_table['symbol'] = console.get_symbol
		symbol_table['string'] = console.get_string

	if console.server:
		symbol_table['publish'] = console.server.publish
		symbol_table['fetch'] = console.server.fetch
	
	symbol_table['apply'] = apply
	symbol_table['parameters'] = parameters
	symbol_table['subtype'] = subtype

	return symbol_table

def apply(symbol, params):
	if hasattr(params, 'symbols'):
		return SymbolList([symbol]+params.symbols)
	else:
		return SymbolList([symbol, params])

parameter_table = {
	'eval': SymbolList([TrellusSymbol('symbol')]),
	'symbol': SymbolList(),
	'string': SymbolList(),
	'publish': SymbolList([TrellusSymbol('symbol')]),
	'fetch': SymbolList([TrellusSymbol('symbol')]),
	'subtype': SymbolList([TrellusSymbol('symbol'), TrellusSymbol('symbol')]),
	'apply': SymbolList([TrellusSymbol('symbol'), TrellusSymbol('symbol')])
}

def parameters(symbol):
	return parameter_table.get(str(symbol), SymbolList([]))

subtype_table = {
	'boolean': SymbolList([TrellusSymbol('true'), TrellusSymbol('false')])
}

def subtype(symbol, type_symbol):
	# The 'symbol' symbol has all symbols as a subtype
	if type_symbol == TrellusSymbol('symbol'):
		return TrellusSymbol('true')
	# If the symbol is in the subtypes table
	elif symbol in subtype_table.get(str(type_symbol), SymbolList([])).symbols:
		return TrellusSymbol('true')
	# If the symbols are both lists of symbols
	elif type(symbol) == SymbolList and type(type_subsymbol) == SymbolList:
		if len(symbol.symbols) == len(type_symbol.symbols):
			# See if each subsymbol of the symbol is a subtype of each subsymbol of the type
			if all(subtype(sub_symbol, type_subsymbol) == TrellusSymbol('true') for sub_symbol, type_sub_symbol in zip(symbol.symbols, type_symbol.symbols)):
				return TrellusSymbol('true')
			else:
				return TrellusSymbol('false')
		else:
			return TrellusSymbol('false')
	# If the symbol is a singular symbol
	elif type(symbol) == TrellusSymbol:
		# The symbol is a literal
		try:
			literal = eval(symbol.symbol)
		# The symbol is not a literal
		except:
			return TrellusSymbol('false')

		# Literal cases
		if type(literal) == str:
			return subtype(TrellusSymbol('string'), type_symbol)
		else:
			return TrellusSymbol('false')
	# Can't possibly match
	else:
		return TrellusSymbol('false')
