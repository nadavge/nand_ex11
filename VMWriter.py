class VMWriter:
	'''A jack to VM writer, used by the compiler to output the code matching
	to the analyzed code'''

	def __init__(self, ostream):
		'''Initialize the VMWriter with a given output stream'''
		self.ostream = ostream
		self.label_count = 0
