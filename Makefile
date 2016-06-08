all:
	chmod +x JackCompiler

tar: JackCompiler JackCompiler.py JackTokenizer.py CompilationEngine.py CompilationTypes.py VMWriter.py README Makefile
	tar cf project11.tar $^