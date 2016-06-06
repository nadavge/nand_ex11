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
		
		token = self.tokenizer.current_token()
		while token is not None and token.type == 'keyword' and\
				token.value in ['static', 'field']:
			# Advance here, to avoid eating the token in the condition above
			# and losing the token when needed afterwards
			self.tokenizer.advance()
			self.terminal_tag(token)

			token = self.tokenizer.advance()
			if token is None or token.type not in ['keyword', 'identifier']:
				print('Error compiling varDec, invalid type')
				sys.exit(1)
			self.terminal_tag(token)
			# TODO handle arrays?

			still_vars = True
			while still_vars:
				token = self.tokenizer.advance()
				if token is None or token.type != 'identifier':
					print('Error compiling varDec, invalid varname identifier')
					sys.exit(1)
				self.terminal_tag(token)

				token = self.tokenizer.advance()
				still_vars = token == ('symbol', ',')

				# We print the token outside unless variables still exist
				if still_vars:
					self.terminal_tag(token)

			# Don't use advance since the ',' check already advances it
			if token is None or token != ('symbol',';'):
				print('Error compiling varDec, missing semi-colon')
				sys.exit(1)
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
			self.terminal_tag(token)

			# function type
			# TODO handle array function types?
			token = self.tokenizer.advance()
			if token is None or token.type not in ['keyword', 'identifier']:
				print('Error compiling subroutine, invalid type')
				sys.exit(1)
			self.terminal_tag(token)

			# name
			token = self.tokenizer.advance()
			if token is None or token.type != 'identifier':
				print('Error compiling subroutine, invalid name')
				sys.exit(1)
			self.terminal_tag(token)

			# open parameterList
			token = self.tokenizer.advance()
			if token is None or token != ('symbol','('):
				print('Error compiling subroutine, missing parameterList')
				sys.exit(1)
			self.terminal_tag(token)

			# TODO handle parameter list

			# close parameterList
			token = self.tokenizer.advance()
			if token is None or token != ('symbol',')'):
				print('Error compiling subroutine, missing parameterList')
				sys.exit(1)
			self.terminal_tag(token)

			# TODO handle subroutine body

			token = self.tokenizer.current_token()



		self.close_tag('subroutineDec')

	def compile_parameter_list(self):
		'''Compile a parameter list for a subroutine'''
		self.open_tag('parameterList')

		token = self.tokenizer.current_token()
		while token:
			token = self.tokenizer.advance()
			if token is None or token.type != 'identifier':
				print('Error compiling varDec, invalid varname identifier')
				sys.exit(1)
			self.terminal_tag(token)



			# We print the token outside unless variables still exist
			if still_vars:
				self.terminal_tag(token)

		self.close_tag('parameterList')

	def compile_parameter_list(self):
		'''Compile a parameter list for a subroutine'''
		# TODO
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
