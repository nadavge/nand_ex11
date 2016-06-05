
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
		pass

	def write_tag(self, token):
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
