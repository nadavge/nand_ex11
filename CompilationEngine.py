import sys
from collections import namedtuple
global labelCnt
global staticSymbols
global staticSymbolCnt

INDENT = 2
labelCnt = 1

ClassSymbol = namedtuple('ClassSymbol', ['type', 'num'])
staticSymbols = dict()
staticSymbolCnt = 0

MethodSymbol = namedtuple('MethodSymbol', ['type', 'kind', 'num'])

binaryOpActions = {'+': 'add', '-': 'sub', '*': 'call Math.multiply', ...
                   '/': 'call Math.divide', '&': 'and', '|': 'or',
                   '<': 'lt', '>': 'gt', '=': 'eq'}

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

        classFieldSymbols = self.compile_class_vars(class_name)
        self.compile_class_subroutines(class_name, classFieldSymbols)

        # }
        token = self.terminal_tag()
        self.close_tag('class')

    def compile_class_vars(self, class_name):
        '''Compile the class variable declarations'''
        global staticSymbols
        global staticSymbolCnt

        fieldSymbols = dict()
        fieldSymbolCnt = 1
        
        token = self.tokenizer.current_token()
        while token is not None and token.type == 'keyword' and\
                token.value in ['static', 'field']:

            #self.open_tag('classVarDec')
            # Advance here, to avoid eating the token in the condition above
            # and losing the token when needed afterwards

            if(token.value == 'static'):
                isStatic = True
            
            self.tokenizer.advance()
            # var scope (static/field)
            self.terminal_tag(token, False)

            # var type
            token = self.terminal_tag(False, False)
            varType = toke.value

            still_vars = True
            while still_vars:
                # var name
                token = self.terminal_tag(False, False)
                varName = token.value

                if(isStatic):
                    staticSymbols[varName] = ClassSymbol(varType, staticSymbolCnt)
                    staticSymbolCnt += 1
                else:
                    fieldSymbols[varName] = ClassSymbol(varType, staticSymbolCnt)
                    fieldSymbolCnt += 1

                token = self.tokenizer.advance()
                still_vars = token == ('symbol', ',')

                # We print the token outside unless variables still exist
                if still_vars:
                    self.terminal_tag(token, False)

            # Don't use advance since the ',' check already advances it
            # semi-colon
            self.terminal_tag(token, False)

            token = self.tokenizer.current_token()

            #self.close_tag('classVarDec')

        return fieldSymbols

    def compile_class_subroutines(self, class_name, classFieldSymbols):
        '''Compile the class subroutines'''
        
        token = self.tokenizer.current_token()
        while token is not None and token.type == 'keyword'\
                and token.value in ['constructor', 'function', 'method']:
            self.open_tag('subroutineDec')
            
            self.tokenizer.advance() # Advance for same reason as in varDec
            # method/constructor/function
            self.terminal_tag(token)

            # type
            token = self.terminal_tag()

            # name
            token = self.terminal_tag()

            # open parameterList
            token = self.terminal_tag()

            self.compile_parameter_list()

            # close parameterList
            token = self.terminal_tag()

            subroutineSymbolDict = dict()
            self.compile_subroutine_body(subroutineSymbolDict, classFieldSymbols)

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

    def compile_subroutine_body(self, subroutineSymbolDict, classFieldSymbols):
        '''Compile a parameter list for a subroutine'''
        #self.open_tag('subroutineBody')

        # {
        token = self.terminal_tag()

        self.compile_subroutine_vars(subroutineSymbolDict)

        self.compile_statements(classFieldSymbols)

        # }
        token = self.terminal_tag()

        #self.close_tag('subroutineBody')

    def compile_subroutine_vars(self, subroutineSymbolDict):
        '''Compile the variable declerations of a subroutine'''
        token = self.tokenizer.current_token()

        varCnt = 1

        # Check that a variable declarations starts
        while token is not None and token == ('keyword', 'var'):
            #self.open_tag('varDec')

            token = self.terminal_tag(False, False)
            # TODO: bug, for some reason pops "False"

            # type
            token = self.terminal_tag(False, False)
            varType = token.value

            # name
            token = self.terminal_tag(False, False)
            varName = token.value
            varDict[varName] = MethodSymbol(varType, 'local', varCnt)
            varCnt += 1

            # repeat as long as there are parameters, o.w prints the semi-colon
            while self.terminal_tag().value == ',':
                # name
                token = self.terminal_tag(False, False)
                varName = token.value
                varDict[varName] = MethodSymbol(varType, 'var', varCnt)
                varCnt += 1

            token = self.tokenizer.current_token()

            #self.close_tag('varDec')

    def compile_statements(self, classFieldSymbols=None, methodSymbols=None):
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
                self.compile_statement_let(classFieldSymbols, methodSymbols)
            elif token == ('keyword', 'do'):
                self.compile_statement_do()
            elif token == ('keyword', 'return'):
                self.compile_statement_return()
            else:
                check_statements = False

        self.close_tag('statements')

    def compile_statement_if(self):
        '''Compile the if statment'''
        global labelCnt
        
        #self.open_tag('ifStatement')
        
        # if
        token = self.terminal_tag(False, False)
        # (
        token = self.terminal_tag(False, False)
        
        self.compile_expression()

        # )
        token = self.terminal_tag(False, False)

        # {
        token = self.terminal_tag(False, False)

        self.ostream.write("not\n")
        label1 = labelCnt
        self.ostream.write("if-goto L" + str(labelCnt) + "\n")
        labelCnt += 1

        # Compile inner statements
        self.compile_statements()

        label2 = labelCnt
        self.ostream.write("goto L" + str(label2) + "\n")
        labelCnt += 1
        self.ostream.write("label L" + str(label1))

        # }
        token = self.terminal_tag()

        token = self.tokenizer.current_token()
        if token == ('keyword', 'else'):
            # else
            self.tokenizer.advance()
            self.terminal_tag(token, False)
            # (
            token = self.terminal_tag(False, False)
            
            self.compile_expression()

            # )
            token = self.terminal_tag(False, False)

            # {
            token = self.terminal_tag(False, False)

            # Compile inner statements
            self.compile_statements()

            self.ostream.write("label L" + str(label2) + "\n")

            # }
            token = self.terminal_tag(False, False)

        #self.close_tag('ifStatement')

    def compile_statement_while(self):
        '''Compile the while statment'''
        global labelCnt
        
        #self.open_tag('whileStatement')

        # while
        token = self.terminal_tag(False, False)
        # (
        token = self.terminal_tag(False, False)

        label1 = labelCnt
        self.ostream.write("label L" + str(label1) + "\n")
        labelCnt += 1
        label2 = labelCnt
        labelCnt += 1
        
        self.compile_expression()

        self.ostream.write("not\n")
        self.ostream.write("if-goto L" + str(label2) + "\n")

        # )
        token = self.terminal_tag(False, False)

        # {
        token = self.terminal_tag(False, False)

        # Compile inner statements
        self.compile_statements()
        self.ostream.write("goto L" + str(label1) + "\n")
        self.ostream.write("label L" + str(label2) + "\n")

        # }
        token = self.terminal_tag(False, False)

        #self.close_tag('whileStatement')

    def compile_statement_let(self, classFieldSymbols, methodSymbols):
        '''Compile the let statment'''
        global staticSymbols
        
        #self.open_tag('letStatement')

        # let
        self.terminal_tag(False, False)

        # var name
        token = self.terminal_tag(False, False)
        varName = token.value

        #TODO: which case is this?
        token = self.tokenizer.current_token()
        if token.value == '[':
            self.terminal_tag() # [
            self.compile_expression()
            self.terminal_tag() # ]

        # =
        self.terminal_tag(False, False)

        self.compile_expression()

        if(varName in methodSymbols):
                [varType, varKind, varNum] = methodSymbols[varName]
        elif(varName in classFieldSymbols):
                [varType, varNum] = classFieldSymbols[varName]
                varKind = "bla" #TODO: what type?
        elif(varName in staticSymbols):
                [varType, varNum] = staticSymbols[varName]
                varKind = "static"
        self.ostream.write("push " + varKind + " " + str(varNum))

        # ;
        self.terminal_tag(False, False)

        #self.close_tag('letStatement')

    def compile_statement_do(self):
        '''Compile the do statment'''
        self.open_tag('doStatement')

        # do
        token = self.terminal_tag(False, False)

        # func name / class / var name
        token = self.terminal_tag(False, False)
        funcName = token.value

        # Check if a '.', o.w it's a '('
        token = self.terminal_tag(False, False)
        if token == ('symbol', '.'):
            # function name
            token = self.terminal_tag(False, False)
            funcName += "." + token.value

            # (
            token = self.terminal_tag(False, False)

        self.compile_expression_list()

        # )
        self.terminal_tag(False, False)
        # ;
        self.terminal_tag(False, False)

        #self.close_tag('doStatement')

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

        self.close_tag('returnStatement')

    def compile_expression_list(self):
        '''Compile a subroutine call expression_list'''
        #self.open_tag('expressionList')
        # Handle expression list, so long as there are expressions
        token = self.tokenizer.current_token()

        while token != ('symbol', ')'):
            if token == ('symbol', ','):
                self.terminal_tag(False, False)
            else:
                self.compile_expression()
            token = self.tokenizer.current_token()

        self.close_tag('expressionList')

    def compile_expression(self):
        '''Compile an expression'''
        #self.open_tag('expression')

        #TODO: push
        self.compile_term()
        
        token = self.tokenizer.current_token()
        while token.value in '+-*/&|<>=':
            binaryOp = token.value
            #self.terminal_tag(False, False)
            
            self.compile_term()
            self.ostream.write(binaryOpActions[binaryOp])

            token = self.terminal_tag(False, False)
            #token = self.tokenizer.current_token()

        #self.close_tag('expression')

    def compile_term(self):
        '''Compile a term as part of an expression'''
        #self.open_tag('term')

        token = self.terminal_tag(False, False)

        # In case of unary operator, compile the term after the operator
        if token.type == 'symbol' and token.value in ['-', '~']:
            self.compile_term()
            if(token.value == '-'):
                self.ostream.write('neg')
            elif(token.value == '~'):
                self.ostream.write('not')
        # In case of opening parenthesis for an expression
        elif token.value == '(':
            self.compile_expression()
            self.terminal_tag(False, False) # )
        # In case of a function call or variable name
        elif token.type == 'identifier':
            token = self.tokenizer.current_token()
            if token.value == '[': # Array
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

        #self.close_tag('term')

    def open_tag(self, name):
        '''Open a containing tag, and indent from now on'''
        self.ostream.write(' '*self.indent)
        self.ostream.write('<{}>\n'.format(name))
        self.indent += INDENT

    def close_tag(self, name):
        '''Close an open tag, and decrease the indentation level'''
        self.indent -= INDENT
        self.ostream.write(' '*self.indent)
        self.ostream.write('</{}>\n'.format(name))

    def terminal_tag(self, token=None, toPrint=True):
        '''Write a tag to the ostream, if a token is not provided
        use current token and advance the tokenizer. return the token'''
        if token is None:
            token = self.tokenizer.advance()
            print(token)

        if(toPrint):
            self.ostream.write(' '*self.indent)
            self.ostream.write(
                                        '<{0}> {1} </{0}>\n'.format(token.type, self.sanitize(token))
                                )

        return token

    @staticmethod
    def sanitize(token):
        '''Sanitize the given input to allow writing to XML, return
        the tokens santized value'''
        value = token.value

        if token.type == 'stringConstant':
            return value[1:-1]
        elif value == '<':
            return '&lt;'
        elif value == '>':
            return '&gt;'
        elif value == '"':
            return '&quot;'
        elif value == '&':
            return '&amp;'

        return value
