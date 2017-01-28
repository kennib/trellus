import string
from ast import *

WHITESPACE = string.whitespace

def parse(code, index=0):
	index = parse_whitespace(code, index)
	index, symbol = parse_list(code, index)
	index = parse_whitespace(code, index)
	
	if index < len(code):
		return SymbolList([TrellusSymbol('extra-input'), TrellusSymbol(str(index))])
	else:
		return symbol

def parse_whitespace(code, index=0):
	while index < len(code) and code[index] in WHITESPACE:
		index += 1
	return index

def parse_list(code, index=0):
	symbols = []
	if code[index] == '(':
		start_index = index
		index += 1
		index = parse_whitespace(code, index)
		while index < len(code) and code[index] != ')':
			if code[index] == '(':
				index, symbol = parse_list(code, index)
			else:
				index, symbol = parse_symbol(code, index)
			index = parse_whitespace(code, index)
			symbols.append(symbol)

		if code[index] == ')':
			return index+1, SymbolList(symbols)
		else:
			return index, SymbolList([TrellusSymbol('missing-closing-parenthesis'), TrellusSymbol(str(start_index))])
	else:
		return index, SymbolList([TrellusSymbol('expected-a-list'), TrellusSymbol(str(index))])

def parse_symbol(code, index=0):
	index = parse_whitespace(code, index)
	start_index = index
	while index < len(code) and code[index] not in WHITESPACE+'()':
		index += 1
	return index, TrellusSymbol(code[start_index:index])

if __name__ == '__main__':
	from operator import add, sub, mul
	code = """
(print
	(add
		(int '24')
		(sub 37 (10))
	)
	()
	(dog
		(add
			(mul cat 3)
			(sub 9 1)
		)
	)
)
	"""

	symbol = parse(code)
	print(symbol)
	result = symbol.eval({'add': add, 'sub': sub, 'mul': mul, 'int': int, 'print': print})
	print(result)
