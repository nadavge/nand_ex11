from collections import namedtuple

JackSymbol = namedtuple('Symbol', ['kind', 'type', 'id'])

class JackClass:
	'''A Jack class representation for the Jack compiler'''

	def __init__(self, name):
		self.name = name
		self.symbols = dict()

		self.static_symbols = 0
		self.field_symbols = 0

	def add_field(self, name, var_type):
		'''Add a field symbol to the class'''
		self.symbols[name] = JackSymbol('field', var_type, self.field_symbols)
		self.field_symbols += 1

	def add_static(self, name, var_type):
		'''Add a static symbol to the class'''
		self.symbols[name] = JackSymbol('static', var_type, self.static_symbols)
		self.static_symbols += 1

	def get_symbol(self, name):
		'''Get a symbol from the class'''
		return self.symbols.get(name)

class JackSubroutine:
	'''A Jack subroutine representation for the Jack compiler'''

	def __init__(self, name, subroutine_type, return_type, jack_class):
		self.name = name
		self.jack_class = jack_class
		self.subroutine_type = subroutine_type
		self.return_type = return_type

		self.symbols = dict()
		self.arg_symbols = 0
		self.var_symbols = 0

		if subroutine_type == 'method':
			self.add_arg('this', self.jack_class.name)

	def add_arg(self, name, var_type):
		'''Add an arg symbol to the class'''
		self.symbols[name] = JackSymbol('arg', var_type, self.arg_symbols)
		self.arg_symbols += 1

	def add_var(self, name, var_type):
		'''Add a var symbol to the class'''
		self.symbols[name] = JackSymbol('var', var_type, self.var_symbols)
		self.var_symbols += 1

	def get_symbol(self, name):
		'''Get a symbol from within the scope of the subroutine'''
		symbol = self.symbols.get(name)
		if symbol is not None:
			return symbol

		return self.jack_class.get_symbol(name)
