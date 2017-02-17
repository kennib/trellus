from types import FunctionType as function
from copy import deepcopy

from ast import *

def library(console=None):
	symbol_table = {
		'eval': SymbolList([TrellusSymbol('eval'), TrellusSymbol('symbol'), TrellusSymbol('symbol')]),
		'evals': SymbolList([TrellusSymbol('evals'), TrellusSymbol('symbol')]),
		'subtypes': SymbolList([TrellusSymbol('subtypes'), TrellusSymbol('symbol')]),
		'usable': SymbolList([TrellusSymbol('usable'), TrellusSymbol('symbol'), TrellusSymbol('symbol')]),
		'uses': SymbolList([TrellusSymbol('uses'), TrellusSymbol('symbol')]),
		'publish': SymbolList([TrellusSymbol('publish'), TrellusSymbol('symbol')]),
		'fetch': SymbolList([TrellusSymbol('fetch'), TrellusSymbol('symbol')]),
		'subtype': SymbolList([TrellusSymbol('subtype'), TrellusSymbol('symbol'), TrellusSymbol('symbol')]),
	}

	if console:
		symbol_table[symbol_table['evals']] = lambda symbol: evals(console.symbol_table, symbol)
		symbol_table[symbol_table['subtypes']] = lambda symbol: subtypes(console.symbol_table, symbol)
		symbol_table[symbol_table['uses']] = lambda symbol: uses(console.symbol_table, symbol)
		symbol_table[TrellusSymbol('symbol')] = lambda symbol: console.get_symbol(symbol)
		symbol_table[TrellusSymbol('symbol-list')] = lambda symbol: console.get_symbol(symbol)
		symbol_table[TrellusSymbol('boolean')] = lambda symbol: console.get_symbol(symbol)
		symbol_table[TrellusSymbol('string')] = lambda symbol: console.get_string(symbol)

	if console.server:
		symbol_table[symbol_table['publish']] = lambda symbol: console.server.publish(symbol)
		symbol_table[symbol_table['fetch']] = lambda symbol: console.server.fetch(symbol)
	
	if console is None:
		symbol_table[symbol_table['evals']] = lambda symbol: (symbol_table, symbol)
		symbol_table[symbol_table['subtypes']] = lambda symbol: subtypes(symbol_table, symbol)
		symbol_table[symbol_table['uses']] = lambda symbol: containers(symbol_table, symbol)

	symbol_table[symbol_table['eval']] = lambda definition, *symbols: eval(definition, *symbols)
	symbol_table[symbol_table['subtype']] = lambda symbol, type_symbol: subtype(symbol, type_symbol)
	symbol_table[symbol_table['usable']] = usable

	return symbol_table

def eval(definition, *symbols):
	if type(definition) == function:
		return definition(*symbols)
	else:
		return definition

def evals(symbol_table, symbol):
	symbols = [
		(deepcopy(type_symbol), deepcopy(definition))
		for type_symbol, definition in symbol_table.items()
		if subtype(symbol, type_symbol) == TrellusSymbol('true')
	]
	return SymbolList([TrellusSymbol('list')]+symbols)

def subtypes(symbol_table, symbol):
	sub_symbols = [
		deepcopy(sub_symbol)
		for sub_symbol in symbol_table.keys()
		if (type(sub_symbol) == TrellusSymbol or type(sub_symbol) == SymbolList)
		and subtype(sub_symbol, symbol) == TrellusSymbol('true')
	]
	try:
		sub_symbols += deepcopy(subtype_table[symbol.symbol].symbols)
	except:
		pass
	return SymbolList([TrellusSymbol('list')]+sub_symbols)

subtype_table = {
	'boolean': SymbolList([TrellusSymbol('true'), TrellusSymbol('false')])
}

def subtype(symbol, type_symbol):
	# The 'symbol' symbol has all symbols as a subtype
	if type_symbol == TrellusSymbol('symbol'):
		return TrellusSymbol('true')
	# The 'symbol-list' symbol has all symbol lists as a subtype
	if type_symbol == TrellusSymbol('symbol-list') and type(symbol) == SymbolList:
		return TrellusSymbol('true')
	# Symbols are a subtype of themselves
	if symbol == type_symbol:
		return TrellusSymbol('true')
	# If the symbol is in the subtypes table
	elif symbol in subtype_table.get(str(type_symbol), SymbolList([])).symbols:
		return TrellusSymbol('true')
	# If the symbols are both lists of symbols
	elif type(symbol) == SymbolList and type(type_symbol) == SymbolList:
		if len(symbol.symbols) == len(type_symbol.symbols):
			# See if each subsymbol of the symbol is a subtype of each subsymbol of the type
			if all(subtype(sub_symbol, type_sub_symbol) == TrellusSymbol('true') for sub_symbol, type_sub_symbol in zip(symbol.symbols, type_symbol.symbols)):
				return TrellusSymbol('true')
			else:
				return TrellusSymbol('false')
		else:
			return TrellusSymbol('false')
	# If the symbol is a singular symbol
	elif type(symbol) == TrellusSymbol:
		# The symbol is a literal
		try:
			literal = __builtins__.eval(symbol.symbol)
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

def usable(symbol, function_symbol):
	if type(function_symbol) is TrellusSymbol:
		if subtype(symbol, function_symbol) == TrellusSymbol('true'):
			return TrellusSymbol('true')
		else:
			return TrellusSymbol('false')
	elif type(function_symbol) is SymbolList:
		if any(subtype(symbol, sub_symbol) == TrellusSymbol('true') for sub_symbol in function_symbol.symbols):
			return TrellusSymbol('true')
		else:
			return TrellusSymbol('false')
	else:
		return TrellusSymbol('false')

def uses(symbol_table, symbol):
	# Get definitions and substitute in the given symbol
	uses = [
		SymbolList(deepcopy([symbol if subtype(symbol, definition_symbol) == TrellusSymbol('true') else definition_symbol for definition_symbol in definition.symbols]))
		for type_symbol, definition in symbol_table.items()
		if usable(symbol, definition) == TrellusSymbol('true')
	]

	return SymbolList([TrellusSymbol('list')]+uses)
