import VMWriter
import CompilationTypes
from collections import namedtuple

INDENT = 2

binary_op_actions = {'+': 'add',
                     '-': 'sub',
                     '*': 'call Math.multiply',
                     '/': 'call Math.divide',
                     '&': 'and',
                     '|': 'or',
                     '<': 'lt',
                     '>': 'gt',
                     '=': 'eq'}

label_count = 0

class CompilationEngine:
    '''A compilation engine for the Jack programming language'''

    def __init__(self, tokenizer, ostream):
        '''Initialize the compilation engine
        @tokenizer the tokenizer from the input code file
        @ostream the output stream to write the code to'''
        self.tokenizer = tokenizer
        self.ostream = ostream # TODO remove ostream
        self.vm_writer = VMWriter.VMWriter(ostream)

    def compile_class(self):
        '''Compile a class block'''
        # class keyword
        self.tokenizer.advance()

        # class name
        token = self.tokenizer.advance()
        class_name = token.value
        jack_class = CompilationTypes.JackClass(class_name)

        # {
        self.tokenizer.advance()

        self.compile_class_vars(jack_class)
        self.compile_class_subroutines(jack_class)

        # }
        self.tokenizer.advance()

    def compile_class_vars(self, jack_class):
        '''Compile the class variable declarations'''
        
        token = self.tokenizer.current_token()
        while token is not None and token.type == 'keyword' and\
                token.value in ['static', 'field']:
            # Advance here, to avoid eating the token in the condition above
            # and losing the token when needed afterwards
            self.tokenizer.advance()
            
            is_static = token.value == 'static'

            # var type
            token = self.tokenizer.advance()
            var_type = token.value

            still_vars = True
            while still_vars:
                # var name
                token = self.tokenizer.advance()
                var_name = token.value

                if is_static:
                    jack_class.add_static(var_name, var_type)
                else:
                    jack_class.add_field(var_name, var_type)

                token = self.tokenizer.advance()
                still_vars = token == ('symbol', ',')

            # load next token, to check if another var declaration
            token = self.tokenizer.current_token()

    def compile_class_subroutines(self, jack_class):
        '''Compile the class subroutines'''
        
        token = self.tokenizer.current_token()
        while token is not None and token.type == 'keyword'\
                and token.value in ['constructor', 'function', 'method']:
            
            # Advance for same reason as in varDec
            token = self.tokenizer.advance()
            subroutine_type = token.value
            # return type
            token = self.tokenizer.advance()
            return_type = token.value
            # name
            token = self.tokenizer.advance()
            name = token.value

            jack_subroutine = CompilationTypes.JackSubroutine(
                    name, subroutine_type, return_type, jack_class
                )

            # ( - open parameterList
            self.tokenizer.advance()

            self.compile_parameter_list(jack_subroutine)

            # ) - close parameterList
            self.tokenizer.advance()

            self.compile_subroutine_body(jack_subroutine)

            # load the next token to check 
            token = self.tokenizer.current_token()

    def compile_parameter_list(self, jack_subroutine):
        '''Compile a parameter list for a subroutine'''

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


    def compile_subroutine_body(self, jack_subroutine):
        '''Compile a parameter list for a subroutine'''
        #self.open_tag('subroutineBody')

        # {
        token = self.terminal_tag()

        self.compile_subroutine_vars(subroutine_symbol_dict)

        self.compile_statements(class_field_symbols)

        # }
        token = self.terminal_tag()

        #self.close_tag('subroutineBody')

    def compile_subroutine_vars(self, subroutine_symbol_dict):
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

    def compile_statements(self, class_field_symbols=None, MethodSymbol=None):
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
                self.compile_statement_let(class_field_symbols, MethodSymbol)
            elif token == ('keyword', 'do'):
                self.compile_statement_do()
            elif token == ('keyword', 'return'):
                self.compile_statement_return()
            else:
                check_statements = False

        self.close_tag('statements')

    def compile_statement_if(self):
        '''Compile the if statment'''
        global label_count
        
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
        label1 = label_count
        self.ostream.write("if-goto L" + str(label_count) + "\n")
        label_count += 1

        # Compile inner statements
        self.compile_statements()

        label2 = label_count
        self.ostream.write("goto L" + str(label2) + "\n")
        label_count += 1
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
        global label_count
        
        #self.open_tag('whileStatement')

        # while
        token = self.terminal_tag(False, False)
        # (
        token = self.terminal_tag(False, False)

        label1 = label_count
        self.ostream.write("label L" + str(label1) + "\n")
        label_count += 1
        label2 = label_count
        label_count += 1
        
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

    def compile_statement_let(self, class_field_symbols, MethodSymbol):
        '''Compile the let statment'''
        global static_symbols
        
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

        if varName in MethodSymbol:
                [varType, varKind, varNum] = MethodSymbol[varName]
        elif varName in class_field_symbols:
                [varType, varNum] = class_field_symbols[varName]
                varKind = "bla" #TODO: what type?
        elif varName in static_symbols:
                [varType, varNum] = static_symbols[varName]
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
            binary_op = token.value
            #self.terminal_tag(False, False)
            
            self.compile_term()
            self.ostream.write(binary_op_actions[binary_op])

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
            if token.value == '-':
                self.ostream.write('neg')
            elif token.value == '~':
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

    def terminal_tag(self, token=None, to_print=True):
        '''Write a tag to the ostream, if a token is not provided
        use current token and advance the tokenizer. return the token'''
        if token is None:
            token = self.tokenizer.advance()
            print(token)

        if to_print:
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
