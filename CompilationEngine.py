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
		token = self.terminal_tag()

		# class name
		token = self.terminal_tag()
		class_name = token.value

		# {
		token = self.terminal_tag()

		self.compile_class_vars(class_name)
		self.compile_class_subroutines(class_name)

		# }
		token = self.terminal_tag()
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
			token = self.terminal_tag()
			# TODO handle arrays?

			still_vars = True
			while still_vars:
				# var name
				token = self.terminal_tag()

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
			token = self.terminal_tag()

			# name
			token = self.terminal_tag()

			# open parameterList
			token = self.terminal_tag()

			self.compile_parameter_list()

			# close parameterList
			token = self.terminal_tag()

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
			token = self.terminal_tag()

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
		token = self.terminal_tag()

		self.compile_subroutine_vars()

		self.compile_statements()

		# }
		token = self.terminal_tag()

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
			token = self.terminal_tag()
			# TODO handle arrays

			# name
			token = self.terminal_tag()

			# semi-colon
			token = self.terminal_tag()

			token = self.tokenizer.current_token()

		self.close_tag('varDec')

	def compile_statements(self):
		'''Compile subroutine statements'''
		self.open_tag('statements')

		check_statements = True
		while check_statements:
			token = self.tokenizer.current_token()

			if token == ('keyword', 'if'):
				self.compile_statement_if()
			elif token == ('keyword', 'while'):
				self.compile_statement_while()
			elif token == ('keyword', 'let'):
				self.compile_statement_let()
			elif token == ('keyword', 'do'):
				self.compile_statement_do()
			elif token == ('keyword', 'return'):
				self.compile_statement_return()
			else:
				check_statements = False

		self.close_tag('statements')

	def compile_statement_if(self):
		'''Compile the if statment'''
		self.open_tag('ifStatement')

		# if
		token = self.terminal_tag()
		# (
		token = self.terminal_tag()
		
		self.compile_expression()

		# )
		token = self.terminal_tag()

		# {
		token = self.terminal_tag()

		# Compile inner statements
		self.compile_statements()

		# }
		token = self.terminal_tag()

		token = self.tokenizer.current_token()
		if token == ('keyword', 'else'):
			# else
			self.tokenizer.advance()
			self.terminal_tag(token)
			# (
			token = self.terminal_tag()
			
			self.compile_expression()

			# )
			token = self.terminal_tag()

			# {
			token = self.terminal_tag()

			# Compile inner statements
			self.compile_statements()

			# }
			token = self.terminal_tag()

		self.close_tag('ifStatement')

	def compile_statement_while(self):
		'''Compile the while statment'''
		self.open_tag('whileStatement')

		# while
		token = self.terminal_tag()
		# (
		token = self.terminal_tag()
		
		self.compile_expression()

		# )
		token = self.terminal_tag()

		# {
		token = self.terminal_tag()

		# Compile inner statements
		self.compile_statements()

		# }
		token = self.terminal_tag()

		self.close_tag('whileStatement')

	def compile_statement_let(self):
		'''Compile the let statment'''
		self.open_tag('letStatement')

		# let
		token = self.terminal_tag()

		# var name
		token = self.terminal_tag()

		# TODO handle arrays

		# =
		token = self.terminal_tag()

		self.compile_expression()

		# ;
		token = self.terminal_tag()

		self.close_tag('letStatement')

	def compile_statement_do(self):
		'''Compile the do statment'''
		self.open_tag('doStatement')

		# do
		token = self.terminal_tag()

		# func name / class / var name
		self.terminal_tag()

		# Check if a '.', o.w it's a '('
		token = self.terminal_tag()
		if token == ('symbol', '.'):
			# function name
			self.terminal_tag()

			# (
			token = self.terminal_tag()

		self.compile_expression_list()

		# )
		self.terminal_tag()		
		# ;
		self.terminal_tag()

		self.close_tag('doStatement')

	def compile_statement_return(self):
		'''Compile the return statment'''
		self.open_tag('returnStatement')

		# return
		token = self.terminal_tag()

		# Check if an expression is given
		token = self.tokenizer.current_token()
		if token != ('symbol', ';'):
			self.compile_expression()

		# ;
		token = self.terminal_tag()

		self.open_tag('returnStatement')

	def compile_expression_list(self):
		'''Compile a subroutine call expression_list'''
		
		# Handle expression list, so long as there are expressions
		token = self.tokenizer.current_token()

		while token != ('symbol', ')'):
			if token == ('symbol', ','):
				self.terminal_tag()
			else:
				self.compile_expression()
			token = self.tokenizer.current_token()

	def compile_expression(self):
		'''Compile an expression'''
		self.open_tag('expression')

		self.compile_term()
		# TODO continue

		self.close_tag('expression')

	def compile_term(self):
		'''Compile a term as part of an expression'''
		token = self.terminal_tag()

		# In case of unary operator, compile the term after the operator
		if token.type == 'symbol' and token.value in ['-', '~']:
			self.compile_term()
		# In case of opening parenthesis for an expression
		elif token.value == '(':
			self.compile_expression()
			self.terminal_tag() # )
		# In case of a function call or variable name
		elif token.type == 'identifier':
			token = self.tokenizer.current_token()
			if token == '[': # Array
				self.terminal_tag() # [
				self.compile_expression()
				self.terminal_tag() # ]
			else:
				if token.value == '.':
					self.terminal_tag() # .
					self.terminal_tag() # function name
					token = self.tokenizer.current_token()

				if token.value == '(':
					self.terminal_tag() # (
					self.compile_expression_list()
					self.terminal_tag() # )

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

	def terminal_tag(self, token=None):
		'''Write a tag to the ostream, if a token is not provided
		use current token and advance the tokenizer. return the token'''
		# TODO match token type to expected string
		if token is None:
			token = self.tokenizer.advance()

		self.ostream.write(' '*self.indent)
		self.ostream.write(
				'<{0}> {1} </{0}>\n'.format(token.type, self.sanitize(token.value))
			)

		return token

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
