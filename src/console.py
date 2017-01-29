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
		self.init_windows()
		while True:
			# Update display
			self.display_symbol()

			# Clear choices display
			self.choices_window.clear()
			self.choices_window.refresh()

			# Evaluate the symbol
			choice = self.screen.getch()
			self.symbol = self.symbol.eval(self.symbol_table)

	def init_windows(self):
		# Create two windows, one for displaying values and one for displaying choices
		window_height = 8
		self.display_window = curses.newwin(window_height, curses.COLS - 1, 0, 0)
		self.choices_window = curses.newwin(curses.LINES - 1 - window_height, curses.COLS - 1, window_height, 0)
		self.screen.refresh()

	def display_symbol(self):
		# Clear window
		self.display_window.clear()

		# Window dressing
		self.display_window.border(0)
		self.display_window.addstr(0, 2, ' Current Symbol ')

		# Output current symbol
		self.display_window.addstr(2, 3, str(self.symbol))

		# Draw window
		self.display_window.refresh()

	def get_symbol(self, *args):
		# Update symbol display
		self.display_symbol()

		# Clear choices display
		self.choices_window.clear()

		# Output directive
		self.choices_window.addstr(1, 2, 'Choose a symbol')

		# Output options
		symbols = [TrellusSymbol(label) for label in self.symbol_table.keys()]
		for index, symbol in enumerate(symbols):
			self.choices_window.addstr(2+index, 2, str(index) + " - " + str(symbol))

		# Get input
		self.choices_window.refresh()
		choice = self.choices_window.getch()

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
		# Update symbol display
		self.display_symbol()

		# Clear choices display
		self.choices_window.clear()

		# Output directive
		self.choices_window.addstr(1, 2, 'Enter a string')

		# Get input
		self.choices_window.refresh()
		curses.echo()
		string = self.choices_window.getstr(2, 2).decode("utf-8")
		curses.noecho()

		return TrellusSymbol(repr(string))

	def close(self):
		# Return to normal terminal
		self.screen.keypad(False)
		curses.nocbreak()
		curses.echo()
		curses.endwin()
