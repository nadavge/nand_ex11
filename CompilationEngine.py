import sys

class CompilationEngine:
	'''A compilation engine for the Jack programming language'''

	def __init__(self, tokenizer, ostream):
		'''Initialize the compilation engine
		@tokenizer the tokenizer from the input code file
		@ostream the output stream to write the code to'''
		self.tokenizer = tokenizer
		self.ostream = ostream
		self.indent = 0

	def compile_class(self):
		'''Compile a class block'''
		self.open_tag('class')

		token = self.tokenizer.advance()
		if token is None or token != ('keyword', 'class'):
			print('Error compiling class, missing class token')
			sys.exit(1)

		self.terminal_tag(token)

		token = self.tokenizer.advance()
		if token is None or token.type != 'identifier':
			print('Error compiling class, missing or invalid class name')
			sys.exit(1)

		self.terminal_tag(token)
		class_name = token.value

		token = self.tokenizer.advance()
		if token is None or token != ('symbol','{'):
			print('Error compiling class, missing opening parenthesis')
			sys.exit(1)

		self.terminal_tag(token)

		self.compile_class_vars(class_name)
		self.compile_class_subroutines(class_name)

		token = self.tokenizer.advance()
		if token is None or token != ('symbol','}'):
			print('Error compiling class, missing closing parenthesis')
			sys.exit(1)

		self.terminal_tag(token)
		self.close_tag('class')

	def compile_class_vars(self, class_name):
		'''Compile the class variable declarations'''
		self.open_tag('classVarDec')
		# TODO
		self.close_tag('classVarDec')

	def compile_class_subroutines(self, class_name):
		'''Compile the class subroutines'''
		self.open_tag('subroutineDec')
		# TODO
		self.close_tag('subroutineDec')

	def open_tag(self, name):
		'''Open a containing tag, and indent from now on'''
		self.ostream.write(' '*self.indent)
		self.ostream.write('<{}>\n'.format(name))
		self.indent += 2

	def close_tag(self, name):
		'''Close an open tag, and decrease the indentation level'''
		self.indent -= 2
		self.ostream.write(' '*self.indent)
		self.ostream.write('</{}>\n'.format(name))

	def terminal_tag(self, token):
		'''Write a tag to the ostream'''
		self.ostream.write(' '*self.indent)
		self.ostream.write(
				'<{0}> {1} </{0}>\n'.format(token.type, self.sanitize(token.value))
			)

	@staticmethod
	def sanitize(value):
		'''Sanitize the given input to allow writing to XML'''
		if value == '<':
			return '&lt;'
		elif value == '>':
			return '&gt;'
		elif value == '"':
			return '&quot;'
		elif value == '&':
			return '&amp;'

		return value
