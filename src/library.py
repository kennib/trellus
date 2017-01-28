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
	'apply': SymbolList([TrellusSymbol('symbol'), TrellusSymbol('symbol')])
}

def parameters(symbol):
	return parameter_table.get(str(symbol), SymbolList([]))
