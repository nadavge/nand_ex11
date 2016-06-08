import sys
import os
import JackTokenizer
import CompilationEngine

def compile_file(file_path):
	'''Compile a file by its path, save the result to a file
	with the same name and a vm suffix'''
		
	with open(file_path, 'r') as ifile:
		file_name = os.path.basename(file_path)
		file_path_no_ext, _ = os.path.splitext(file_path)
		file_name_no_ext, _ = os.path.splitext(file_name)

		ofile_path = file_path_no_ext+'.vm'
		with open(ofile_path, 'w') as ofile:
			tokenizer = JackTokenizer.JackTokenizer(ifile.read())
			compiler = CompilationEngine.CompilationEngine(tokenizer, ofile)
			compiler.compile_class()

def compile_dir(dir_path):
	'''Compile all Jack files in a directory'''
	for file in os.listdir(dir_path):
		file_path = os.path.join(dir_path, file)
		_, file_ext = os.path.splitext(file_path)
		# Choose only jack files
		if os.path.isfile(file_path) and file_ext.lower()=='.jack':
			compile_file(file_path)

def main():
	"""The main program, loading the file/files and calling the translator"""
	if len(sys.argv) < 2:
		print('usage: JackCompiler (file|dir)'.format(sys.argv[0]))
		sys.exit(1)

	input_path = sys.argv[1]

	if os.path.isdir(input_path):
		compile_dir(input_path)
	elif os.path.isfile(input_path):
		compile_file(input_path)
	else:
		print("Invalid file/directory, compilation failed")
		sys.exit(1)


if __name__=="__main__":
	main()