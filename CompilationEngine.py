import VMWriter
import CompilationTypes
from collections import namedtuple

INDENT = 2
binary_op_actions = {'+': 'add',
                     '-': 'sub',
                     '*': 'call Math.multiply 2',
                     '/': 'call Math.divide 2',
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
        self.vm_writer = VMWriter.VMWriter(ostream)

    @staticmethod
    def get_label():
        '''Return a label for use'''
        global label_count

        label = 'L{}'.format(label_count)
        label_count += 1

        return label

    def compile_class(self):
        '''Compile a class block'''
        self.tokenizer.advance() # class

        # class name
        class_name = self.tokenizer.advance().value
        jack_class = CompilationTypes.JackClass(class_name)

        self.tokenizer.advance() # {

        self.compile_class_vars(jack_class)
        self.compile_class_subroutines(jack_class)

        self.tokenizer.advance() # }

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
            var_type = self.tokenizer.advance().value

            still_vars = True
            while still_vars:
                # var name
                var_name = self.tokenizer.advance().value

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
            subroutine_type = self.tokenizer.advance().value
            # return type
            return_type = self.tokenizer.advance().value
            # name
            name = self.tokenizer.advance().value

            jack_subroutine = CompilationTypes.JackSubroutine(
                    name, subroutine_type, return_type, jack_class
                )

            self.tokenizer.advance() # ( - open parameterList

            self.compile_parameter_list(jack_subroutine)

            self.tokenizer.advance() # ) - close parameterList

            self.compile_subroutine_body(jack_subroutine)

            # load the next token to check 
            token = self.tokenizer.current_token()

    def compile_parameter_list(self, jack_subroutine):
        '''Compile a parameter list for a subroutine'''

        token = self.tokenizer.current_token()
        # Check if the next token is a valid variable type
        still_vars = token is not None and token.type in ['keyword', 'identifier']
        while still_vars:
            # param type
            token = self.tokenizer.advance() # Don't advance to avoid eating
            param_type = token.value
            # param name
            param_name = self.tokenizer.advance().value

            jack_subroutine.add_arg(param_name, param_type)

            token = self.tokenizer.current_token()
            # If there are still vars
            if token == ('symbol', ','):
                self.tokenizer.advance() # Throw the ',' away
                token = self.tokenizer.current_token()
                still_vars = token is not None and token.type in ['keyword', 'identifier']
            else:
                still_vars = False


    def compile_subroutine_body(self, jack_subroutine):
        '''Compile the subroutine body'''

        self.tokenizer.advance() # {

        self.compile_subroutine_vars(jack_subroutine)

        self.vm_writer.write_function(jack_subroutine)

        if jack_subroutine.subroutine_type == 'constructor':
            field_count = jack_subroutine.jack_class.field_symbols
            self.vm_writer.write_push('constant', field_count)
            self.vm_writer.write_call('Memory', 'alloc', 1)
            # Set 'this' in the function to allow it to return it
            self.vm_writer.write_pop('pointer', 0)
        elif jack_subroutine.subroutine_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)

        self.compile_statements(jack_subroutine)

        self.tokenizer.advance() # }

    def compile_subroutine_vars(self, jack_subroutine):
        '''Compile the variable declerations of a subroutine'''

        token = self.tokenizer.current_token()
        # Check that a variable declarations starts
        while token is not None and token == ('keyword', 'var'):
            self.tokenizer.advance()
            # var_type
            var_type = self.tokenizer.advance().value
            # var_name
            var_name = self.tokenizer.advance().value

            jack_subroutine.add_var(var_name, var_type)

            # repeat as long as there are parameters, o.w eats the semi-colon
            while self.tokenizer.advance().value == ',':
                # var_name
                var_name = self.tokenizer.advance().value
                jack_subroutine.add_var(var_name, var_type)

            token = self.tokenizer.current_token()

    def compile_statements(self, jack_subroutine):
        '''Compile subroutine statements'''

        check_statements = True
        while check_statements:
            token = self.tokenizer.current_token()

            if token == ('keyword', 'if'):
                self.compile_statement_if(jack_subroutine)
            elif token == ('keyword', 'while'):
                self.compile_statement_while(jack_subroutine)
            elif token == ('keyword', 'let'):
                self.compile_statement_let(jack_subroutine)
            elif token == ('keyword', 'do'):
                self.compile_statement_do(jack_subroutine)
            elif token == ('keyword', 'return'):
                self.compile_statement_return(jack_subroutine)
            else:
                check_statements = False

    def compile_statement_if(self, jack_subroutine):
        '''Compile the if statement'''
        self.tokenizer.advance() # if
        self.tokenizer.advance() # (
        
        self.compile_expression(jack_subroutine)

        self.tokenizer.advance() # )
        self.tokenizer.advance() # {

        false_label = CompilationEngine.get_label()
        end_label = CompilationEngine.get_label()

        self.vm_writer.write_if(false_label)

        # Compile inner statements
        self.compile_statements(jack_subroutine)

        self.vm_writer.write_goto(end_label)
        self.vm_writer.write_label(false_label)

        self.tokenizer.advance() # }

        token = self.tokenizer.current_token()
        if token == ('keyword', 'else'):
            self.tokenizer.advance() # else
            self.tokenizer.advance() # {

            # Compile inner statements
            self.compile_statements(jack_subroutine)

            self.tokenizer.advance() # }

        self.vm_writer.write_label(end_label)

    def compile_statement_while(self, jack_subroutine):
        '''Compile the while statment'''
        self.tokenizer.advance() # while
        self.tokenizer.advance() # (

        while_label = CompilationEngine.get_label()
        false_label = CompilationEngine.get_label()

        self.vm_writer.write_label(while_label)        
        self.compile_expression(jack_subroutine)

        self.tokenizer.advance() # )
        self.tokenizer.advance() # {

        self.vm_writer.write_if(false_label)

        # Compile inner statements
        self.compile_statements(jack_subroutine)
        
        self.vm_writer.write_goto(while_label)
        self.vm_writer.write_label(false_label)
        
        self.tokenizer.advance() # }

    def compile_statement_let(self, jack_subroutine):
        '''Compile the let statment'''

        self.tokenizer.advance() # let
        var_name = self.tokenizer.advance().value # var name
        jack_symbol = jack_subroutine.get_symbol(var_name)

        is_array = self.tokenizer.current_token().value == '['
        if is_array:
            self.tokenizer.advance() # [
            self.compile_expression(jack_subroutine) # Index
            self.tokenizer.advance() # ]
            self.tokenizer.advance() # =
            # Add the base and index
            self.vm_writer.write_push_symbol(jack_symbol)
            self.vm_writer.write('add')
            # Base 'that' at base+index, stored in stack
            # to avoid the expression assigned changing pointer:1, we don't
            # pop it yet
            self.compile_expression(jack_subroutine) # Expression to assign
            self.vm_writer.write_pop('temp', 0) # Store assigned value in temp
            self.vm_writer.write_pop('pointer', 1) # Restore destination
            self.vm_writer.write_push('temp', 0) # Restore assigned value
            self.vm_writer.write_pop('that', 0) # Store in target
        else:
            self.tokenizer.advance() # =
            self.compile_expression(jack_subroutine) # Expression to assign
            self.vm_writer.write_pop_symbol(jack_symbol)

        self.tokenizer.advance() # ;

    def compile_statement_do(self, jack_subroutine):
        '''Compile the do statment'''
        self.tokenizer.advance() # do

        self.compile_term(jack_subroutine) # Do options are a subset of terms
        self.vm_writer.write_pop('temp', 0) # Pop to avoid filling the stack with garbage

        self.tokenizer.advance() # ;

    def compile_statement_return(self, jack_subroutine):
        '''Compile the return statment'''
        self.tokenizer.advance() # return

        # Check if an expression is given
        token = self.tokenizer.current_token()
        if token != ('symbol', ';'):
            self.compile_expression(jack_subroutine)
        else:
            self.vm_writer.write_int(0)

        self.vm_writer.write_return()
        self.tokenizer.advance() # ;

    def compile_expression_list(self, jack_subroutine):
        '''Compile a subroutine call expression_list'''
        # Handle expression list, so long as there are expressions
        count = 0 # Count expressions
        token = self.tokenizer.current_token()
        while token != ('symbol', ')'):

            if token == ('symbol', ','):
                self.tokenizer.advance()

            count += 1
            self.compile_expression(jack_subroutine)
            token = self.tokenizer.current_token()

        return count

    def compile_expression(self, jack_subroutine):
        '''Compile an expression'''
        self.compile_term(jack_subroutine)
        
        token = self.tokenizer.current_token()
        while token.value in '+-*/&|<>=':
            binary_op = self.tokenizer.advance().value
            
            self.compile_term(jack_subroutine)
            self.vm_writer.write(binary_op_actions[binary_op])

            token = self.tokenizer.current_token()

    def compile_term(self, jack_subroutine):
        '''Compile a term as part of an expression'''

        token = self.tokenizer.advance()
        # In case of unary operator, compile the term after the operator
        if token.value in ['-', '~']:
            self.compile_term(jack_subroutine)
            if token.value == '-':
                self.vm_writer.write('neg')
            elif token.value == '~':
                self.vm_writer.write('not')
        # In case of opening parenthesis for an expression
        elif token.value == '(':
            self.compile_expression(jack_subroutine)
            self.tokenizer.advance() # )
        elif token.type == 'integerConstant':
            self.vm_writer.write_int(token.value)
        elif token.type == 'stringConstant':
            self.vm_writer.write_string(token.value)
        elif token.type == 'keyword':
            if token.value == 'this':
                self.vm_writer.write_push('pointer', 0)
            else:
                self.vm_writer.write_int(0) # null / false
                if token.value == 'true':
                    self.vm_writer.write('not')

        # In case of a function call or variable name
        elif token.type == 'identifier':
            # Save token value as symbol and function in case of both
            token_value = token.value
            token_var = jack_subroutine.get_symbol(token_value)

            token = self.tokenizer.current_token()
            if token.value == '[': # Array
                self.tokenizer.advance() # [
                self.compile_expression(jack_subroutine)
                self.vm_writer.write_push_symbol(token_var)
                self.vm_writer.write('add')
                # rebase 'that' to point to var+index
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)
                self.tokenizer.advance() # ]
            else:
                # Default class for function calls is this class
                func_name = token_value
                func_class = jack_subroutine.jack_class.name
                # Used to mark whether to use the default call, a method one
                default_call = True
                arg_count = 0

                if token.value == '.':
                    default_call = False
                    self.tokenizer.advance() # .
                    # try to load the object of the method
                    func_obj = jack_subroutine.get_symbol(token_value)
                    func_name = self.tokenizer.advance().value # function name
                    # If this is an object, call as method
                    if func_obj:
                        func_class = token_var.type # Use the class of the object
                        arg_count = 1 # Add 'this' to args
                        self.vm_writer.write_push_symbol(token_var) # push "this"
                    else:
                        func_class = token_value
                    token = self.tokenizer.current_token()

                # If in-fact a function call
                if token.value == '(':
                    if default_call:
                        # Default call is a method one, push this
                        arg_count = 1
                        self.vm_writer.write_push('pointer', 0)

                    self.tokenizer.advance() # (
                    arg_count += self.compile_expression_list(jack_subroutine)
                    self.vm_writer.write_call(func_class, func_name, arg_count)
                    self.tokenizer.advance() # )
                # If a variable instead
                elif token_var:
                    self.vm_writer.write_push_symbol(token_var)
