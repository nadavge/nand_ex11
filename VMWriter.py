kind_to_segment = {'static': 'static',
                   'field': 'this',
                   'arg': 'argument',
                   'var': 'local'}

class VMWriter:
	'''A jack to VM writer, used by the compiler to output the code matching
	to the analyzed code'''

	def __init__(self, ostream):
		'''Initialize the VMWriter with a given output stream'''
		self.ostream = ostream
		self.label_count = 0

	def write_if(self, label):
		'''Write an if-goto used in while/if.
		used to jump to label if the condition *doesn't* hold'''
		self.ostream.write('not\n') # Negate to jump if the conditions doesn't hold
		self.ostream.write('if-goto {}\n'.format(label))

	def write_goto(self, label):
		'''Write a goto for the VM'''
		self.ostream.write('goto {}\n'.format(label))

	def write_label(self, label):
		'''Write a label in VM'''
		self.ostream.write('label {}\n'.format(label))

	def write_function(self, jack_subroutine):
		'''Write a function header for a Jack subroutine'''
		class_name = jack_subroutine.jack_class.name
		name = jack_subroutine.name
		local_vars = jack_subroutine.var_symbols
		subroutine_type = jack_subroutine.subroutine_type

		self.ostream.write('function {}.{} {}\n'.format(class_name, name, local_vars))

	def write_return(self):
		'''Write the return statement'''
		self.ostream.write('return\n')

	def write_call(self, class_name, func_name, arg_count):
		'''Write a call to a function with n-args'''
		self.ostream.write('call {0}.{1} {2}\n'.format(
				class_name, func_name, arg_count
			))

	def write_pop_symbol(self, jack_symbol):
		'''Pop the value in the top of the stack to the supplied symbol'''
		kind = jack_symbol.kind
		offset = jack_symbol.id # the offset in the segment

		segment = kind_to_segment[kind]
		self.write_pop(segment, offset)

	def write_push_symbol(self, jack_symbol):
		'''Push the value from the symbol to the stack'''
		kind = jack_symbol.kind
		offset = jack_symbol.id # the offset in the segment

		segment = kind_to_segment[kind]
		self.write_push(segment, offset)

	def write_pop(self, segment, offset):
		'''Pop the value in the top of the stack to segment:offset'''
		self.ostream.write('pop {0} {1}\n'.format(segment, offset))

	def write_push(self, segment, offset):
		'''Push the value to the stack from segment:offset'''
		self.ostream.write('push {0} {1}\n'.format(segment, offset))

	def write(self, action):
		'''Write something'''
		self.ostream.write('{}\n'.format(action))

	def write_int(self, n):
		'''Write an int'''
		self.write_push('constant', n)

	def write_string(self, s):
		'''Allocates a new string, and appends all the chars one-by-one'''
		s = s[1:-1]
		self.write_int(len(s))
		self.write_call('String', 'new', 1)
		for c in s:
			self.write_int(ord(c))
			self.write_call('String','appendChar', 2)
