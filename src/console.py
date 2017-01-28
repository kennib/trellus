import atexit
import curses
from library import *

class TrellusConsole():
	def __init__(self, server, symbol_table=None):
		self.server = server

		# Initialise symbol table
		self.symbol_table = symbol_table if symbol_table else {}

		# Add builtin symbols
		builtin_symbol_table = library(self)
		self.symbol_table.update(builtin_symbol_table)

		# Start off with a generic symbol
		self.symbol = SymbolList([TrellusSymbol('symbol')])

	def interact(self):
		# Create curses screen
		self.screen = curses.initscr()
		# Take keyboard input
		curses.noecho()
		curses.cbreak()
		self.screen.keypad(True)
		try:
			self.run()
		except Exception as error:
			self.close()
			raise error
		except KeyboardInterrupt as error:
			self.close()
			raise error
		# Clean up when done
		atexit.register(self.close)

	def run(self):
		while True:
			self.screen.clear()

			# Output current symbol
			self.screen.addstr(1, 2, str(self.symbol))

			# Evaluate the symbol
			choice = self.screen.getch()
			self.symbol = self.symbol.eval(self.symbol_table)
			self.screen.refresh()

	def get_symbol(self, *args):
		self.screen.clear()

		# Output current symbol
		self.screen.addstr(1, 2, str(self.symbol))

		# Output directive
		self.screen.addstr(3, 2, 'Choose a symbol')

		# Output options
		symbols = [TrellusSymbol(label) for label in self.symbol_table.keys()]
		for index, symbol in enumerate(symbols):
			self.screen.addstr(4+index, 2, str(index) + " - " + str(symbol))

		# Get input
		self.screen.refresh()
		choice = self.screen.getch()

		# Process input
		if choice in [ord(str(i)) for i in range(10)]:
			index = int(chr(choice))
			if index < len(symbols):
				return SymbolList([
					TrellusSymbol('apply'),
					symbols[index],
					SymbolList([TrellusSymbol('parameters'), symbols[index]]),
				])

		# If no choice, then return the original symbol
		return self.symbol

	def get_string(self, *args):
		self.screen.clear()

		# Output current symbol
		self.screen.addstr(1, 2, str(self.symbol))

		# Output directive
		self.screen.addstr(3, 2, 'Enter a string')

		# Get input
		self.screen.refresh()
		curses.echo()
		string = self.screen.getstr(4, 2).decode("utf-8")
		curses.noecho()

		return TrellusSymbol(repr(string))

	def close(self):
		# Return to normal terminal
		self.screen.keypad(False)
		curses.nocbreak()
		curses.echo()
		curses.endwin()
