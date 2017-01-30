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
		self.selection = self.symbol

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
			self.display()

			# Clear choices display
			self.choices_window.clear()
			self.choices_window.refresh()

			# Evaluate the symbol
			choice = self.screen.getkey()
			if choice == '\n':
				self.symbol = self.symbol.eval(self.symbol_table)
				self.selection = self.symbol

	def init_windows(self):
		# Create two windows, one for displaying values and one for displaying choices
		self.window_height = 8
		self.display_window = curses.newwin(self.window_height, curses.COLS - 1, 0, 0)
		self.choices_window = curses.newwin(curses.LINES - 1 - self.window_height, curses.COLS - 1, self.window_height, 0)
		self.screen.refresh()

	def display(self, controls=True):
		# Clear window
		self.display_window.clear()

		# Window dressing
		self.display_window.border(0)
		self.display_window.addstr(0, 2, ' Current Symbol ')

		# Display window controls
		if controls:
			self.display_window.addstr(self.window_height - 1, 2, ' Enter - Evaluate ')

		# Display the symbol
		self.display_symbol(self.symbol, row=2, column=3, window=self.display_window, selection=self.selection)

		# Draw window
		self.display_window.refresh()

	def display_symbol(self, symbol, row=None, column=None, window=None, selection=None, selected=False):
		row = row if row is not None else 0
		column = column if column is not None else 0
		window = window if window is not None else self.screen

		# Check if symbol should be displayed as selected
		selected = symbol == selection or selected

		# Calculate color of text
		color = curses.A_STANDOUT if selected else 0

		# Output symbol
		if type(symbol) is SymbolList:
			# Output symbol list
			self.display_window.addstr(2, column, '(', color)
			for symbol in symbol.symbols:
				row, column = self.display_symbol(symbol, row, column+1, window, selection, selected)
			self.display_window.addstr(2, column, ')', color)
			return row, column+1
		elif type(symbol) is TrellusSymbol:
			# Output singular symbol
			self.display_window.addstr(2, column, symbol.symbol, color)
			return row, column + len(symbol.symbol)

	def get_symbol(self, *args):
		# Update symbol display
		self.display(controls=False)

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
		self.display(controls=False)

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
