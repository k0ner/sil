from interpreter import Interpreter
from lexer import Lexer
from ast import *
from ply import yacc

class Parser(Interpreter, Lexer):
    
    precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'POW'),
    ('right', 'UMINUS'),
    )
    
    tokens = Lexer.tokens
    
    def p_statement(self,p):
        """statement : expression
                     | relexpr
                     | block
                     | import"""
        p[0] = p[1]
        
    def p_import(self, p):
        """import : IMPORT FILENAME"""
        print p[2]
        f = open(p[2], 'r')
        file = f.read()
        print file
        p[0] = Block(yacc.parse(file))
    
    def p_expression_binop(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression'''
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_statement_assign(self, p):
        """expression : NAME ASSIGN assignment"""
        p[0] = Assign(p[1], p[3])
        
    def p_assignment(self, p):
        """assignment : expression
                      | relexpr"""
        p[0] = p[1]

    def p_relexpr(self, p):
        """relexpr : expression EQ expression
                    | expression NE expression
                    | expression GT expression
                    | expression LT expression
                    | expression GE expression
                    | expression LE expression"""
        #=======================================================================
        #            | expression"""
        # if len(p) == 2:
        #    p[0] = Boolean(p[1])
        # else:
        #=======================================================================
        p[0] = RelExpr(p[2], p[1], p[3])

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]
        
    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = UnaryOp(p[1], p[2])
        
    def p_expression_integer(self, p):
        'expression : INTEGER'
        p[0] = Integer(p[1])
        
    def p_expression_float(self, p):
        'expression : FLOAT'
        p[0] = Float(p[1])
        
    def p_expression_string(self, p):
        'expression : STRING'
        p[0] = String(p[1])
        
    def p_expression_boolean(self, p):
        'expression : BOOLEAN'
        p[0] = Boolean(p[1])
        
    def p_statement_if(self, p):
        """expression : IF test THEN block
                      | IF test THEN block ELSE block"""
        if len(p) == 5:
            p[0] = IfThenElse(p[2], p[4], None)
        else:
            p[0] = IfThenElse(p[2], p[4], p[6])
        
    def p_statement_while(self, p):
        """expression : WHILE test DO block"""
        p[0] = While(p[2], p[4])
        
    def p_def(self, p):
        """expression : DEF NAME LPAREN args RPAREN COLON block"""
        p[0] = FuncDef(p[2], p[4], p[7])
    
    def p_print(self, p):
        """expression : PRINT args"""
        p[0] = Print(p[2])
    
    def p_args(self, p):
        """args : expression
                | expression COMA args"""
        if len(p) == 2:
            p[0] = Args(p[1])
        else:
            p[0] = Args(p[1], p[3])
            
    def p_fun_args(self, p):
        """fun_args : expression
                    | expression COMA fun_args"""
        if len(p) == 2:
            p[0] = Args(p[1])
        else:
            p[0] = Args(p[1], p[3])
        
    def p_block(self, p):
        """block : expression
                 | return
                 | expression SEMICOLON block"""
        if len(p) == 2:
            p[0] = Block(p[1])
        else:
            p[0] = Block(p[1], p[3])
    
    def p_test(self, p):
        """test : LPAREN relexpr RPAREN
                | relexpr"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]
        
    def p_return(self, p):
        """return : RETURN
                  | RETURN expression"""
        if len(p) == 2:
            p[0] = Return()
        else:
            p[0] = Return(p[2])
    
    def p_expression_name(self, p):
        'expression : NAME'
        p[0] = Select(p[1])


    def p_func_call(self, p):
        'expression : NAME LPAREN fun_args RPAREN'
        p[0] = FuncCall(p[1], p[3])

    def p_error(self, p):
        print "Syntax error at '%s'" % p.value

if __name__ == '__main__':
    calc = Parser()
    calc.run()