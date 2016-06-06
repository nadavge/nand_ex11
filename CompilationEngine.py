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

		# class keyword
		token = self.tokenizer.advance()
		self.terminal_tag(token)

		# class name
		token = self.tokenizer.advance()
		self.terminal_tag(token)
		class_name = token.value

		# {
		token = self.tokenizer.advance()
		self.terminal_tag(token)

		self.compile_class_vars(class_name)
		self.compile_class_subroutines(class_name)

		# }
		token = self.tokenizer.advance()

		self.terminal_tag(token)
		self.close_tag('class')

	def compile_class_vars(self, class_name):
		'''Compile the class variable declarations'''
		self.open_tag('classVarDec')
		
		token = self.tokenizer.current_token()
		while token is not None and token.type == 'keyword' and\
				token.value in ['static', 'field']:
			# Advance here, to avoid eating the token in the condition above
			# and losing the token when needed afterwards
			self.tokenizer.advance()
			# var scope (static/field)
			self.terminal_tag(token)

			# var type
			token = self.tokenizer.advance()
			self.terminal_tag(token)
			# TODO handle arrays?

			still_vars = True
			while still_vars:
				# var name
				token = self.tokenizer.advance()
				self.terminal_tag(token)

				token = self.tokenizer.advance()
				still_vars = token == ('symbol', ',')

				# We print the token outside unless variables still exist
				if still_vars:
					self.terminal_tag(token)

			# Don't use advance since the ',' check already advances it
			# semi-colon
			self.terminal_tag(token)

			token = self.tokenizer.current_token()

		self.close_tag('classVarDec')

	def compile_class_subroutines(self, class_name):
		'''Compile the class subroutines'''
		self.open_tag('subroutineDec')
		
		token = self.tokenizer.current_token()
		while token is not None and token.type == 'keyword'\
				and token.value in ['constructor', 'function', 'method']:
			self.tokenizer.advance() # Advance for same reason as in varDec
			# method/constructor/function
			self.terminal_tag(token)

			# type
			# TODO handle array function types?
			token = self.tokenizer.advance()
			self.terminal_tag(token)

			# name
			token = self.tokenizer.advance()
			self.terminal_tag(token)

			# open parameterList
			token = self.tokenizer.advance()
			self.terminal_tag(token)

			self.compile_parameter_list()

			# close parameterList
			token = self.tokenizer.advance()
			self.terminal_tag(token)

			self.compile_subroutine_body()

			token = self.tokenizer.current_token()

		self.close_tag('subroutineDec')

	def compile_parameter_list(self):
		'''Compile a parameter list for a subroutine'''
		self.open_tag('parameterList')

		token = self.tokenizer.current_token()

		# Check if the next token is a valid variable type
		still_vars = token is not None and token.type in ['keyword', 'identifier']
		while still_vars:
			self.tokenizer.advance() # Don't advance to avoid eating
			# var type
			self.terminal_tag(token)

			# var name
			token = self.tokenizer.advance()
			self.terminal_tag(token)

			token = self.tokenizer.current_token()
			
			# If there are still vars
			if token == ('symbol', ','):
				self.terminal_tag(token)
				self.tokenizer.advance()
				token = self.tokenizer.current_token()
				still_vars = token is not None and token.type in ['keyword', 'identifier']
			else:
				still_vars = False

		self.close_tag('parameterList')

	def compile_subroutine_body(self):
		'''Compile a parameter list for a subroutine'''
		self.open_tag('subroutineBody')

		# {
		token = self.tokenizer.advance()
		self.terminal_tag(token)

		self.compile_subroutine_vars()

		# TODO handle statements

		# }
		token = self.tokenizer.advance()
		self.terminal_tag(token)

		self.close_tag('subroutineBody')

	def compile_subroutine_vars(self):
		'''Compile the variable declerations of a subroutine'''
		self.open_tag('varDec')

		token = self.tokenizer.current_token()

		# Check that a variable declarations starts
		while token is not None and token == ('keyword', 'var'):
			self.tokenizer.advance()
			self.terminal_tag(token)

			# type
			token = self.tokenizer.advance()
			self.terminal_tag(token)
			# TODO handle arrays

			# name
			token = self.tokenizer.advance()
			self.terminal_tag(token)

			# semi-colon
			token = self.tokenizer.advance()
			self.terminal_tag(token)

			token = self.tokenizer.current_token()

		self.close_tag('varDec')

	def compile_subroutine_statments(self):
		'''Compile subroutine statements'''
		pass

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
		# TODO match token type to expected string
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
