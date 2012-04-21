from interpreter import Interpreter

class Lexer(Interpreter):
    
    reserved = {
                'if' : 'IF',
                'then' : 'THEN',
                'else' : 'ELSE',
                'while' : 'WHILE',
                'do' : 'DO',
                'def' : 'DEF',
                'print' : 'PRINT',
                'return' : 'RETURN',
                'import' : 'IMPORT',
                'begin' : 'BEGIN',
                'end' : 'END',
                'int' : 'INTEGER_NAME',
                'str' : 'STRING_NAME',
                'bool' : 'BOOLEAN_NAME',
                'float' : 'FLOAT_NAME'}
    
    relops = [ 'EQ', 'NE', 'GT', 'LT', 'GE', 'LE' ]
    
    tokens = [
        'NAME', 'INTEGER_TYPE', 'FLOAT_TYPE', 'STRING_TYPE', 'BOOLEAN_TYPE',
        'PLUS', 'MINUS', 'POW', 'TIMES', 'DIVIDE', 'ASSIGN',
        'LPAREN', 'RPAREN', 'NEWLINE', 'COLON', 'SEMICOLON', 'COMA', 'FILENAME'
        ] + list(reserved.values()) + relops
    
    t_EQ = r'=='
    t_NE = r'!='
    t_GT = r'>'
    t_LT = r'<'
    t_GE = r'>='
    t_LE = r'<='
    
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_POW = r'\*\*'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_ASSIGN = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COLON = r':'
    t_SEMICOLON = r';'
    t_COMA = r','
    
    t_ignore = " \t\n"
    
    def t_FILENAME(self, t):
        r'<(\w+)(\.\w+)?>'
        t.value = str(t.value)[1:-1]
        return t
    
    def t_BOOLEAN_TYPE(self, t):
        r'(True)|(False)'
        t.value = bool(t.value)
        return t
    
    def t_STRING_TYPE(self, t):
        r'(\'.+\')|(\".+\")'
        t.value = str(t.value)[1:-1]
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'NAME')    # Check for reserved words
        return t
    
    def t_FLOAT_TYPE(self, t):
        r"""(\d+\.\d*|\.\d+)([eE][-+]?\d+)?"""
        try:
            t.value = float(t.value)
        except ValueError:
            print 'Line %d: Float %s error!' % (t.lineno, t.value) # TODO
            t.value = 0.0
        return t

    def t_INTEGER_TYPE(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print "Integer value too large", t.value
            t.value = 0
        #print "parsed number %s" % repr(t.value)
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
    
    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)
