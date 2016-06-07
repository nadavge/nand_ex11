all:
	chmod +x JackAnalyzer

tar: JackAnalyzer JackAnalyzer.py JackTokenizer.py CompilationEngine.py README Makefile
	tar cf project10.tar $^