from interpreter import Interpreter
from lexer import Lexer
from ast import *
from ply import yacc
from evaluator import Evaluator

class Parser(Interpreter, Lexer):

    precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'POW'),
    ('right', 'UMINUS'),
    )

    tokens = Lexer.tokens

    def p_interpreter_type(self, p):
        '''interpreter : type'''
        print p[1].type + ":", Evaluator.visit(p[1])
        
    def p_interpreter_other(self, p):
        '''interpreter : comparision
                       | select
                       | array_selection
                       | func_call_stmt
                       | expression'''
        print Evaluator.visit(p[1])

    def p_interpreter_statemenet(self, p):
        '''interpreter : statement'''
        p[0] = p[1]

    def p_statement(self,p):
        '''statement : expression
                     | comparision
                     | import
                     | func_call_stmt
                     | stmts'''
        if isinstance(p[1], list):
            p[0] = Block(p[1])
        else:
            p[0] = Block([p[1]])

    def p_import(self, p):
        '''import : IMPORT FILENAME'''
        print p[2]
        try:
            f = open(p[2], 'r')
            file = f.read()
            p[0] = Block([yacc.parse(file)])
        except Exception:
            print 'No such file', p[2]

    def p_returning_value(self, p):
        '''returning_value : expression
                           | func_call_stmt'''
        p[0] = p[1]

    def p_expression_binop(self, p):
        '''expression : returning_value PLUS returning_value
                      | returning_value MINUS returning_value
                      | returning_value TIMES returning_value
                      | returning_value DIVIDE returning_value
                      | returning_value POW returning_value'''
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_operation_with_assignment(self, p):
        '''assign_stmt : NAME PLUS_ASSIGN returning_value
                       | NAME MINUS_ASSIGN returning_value
                       | NAME TIMES_ASSIGN returning_value
                       | NAME DIVIDE_ASSIGN returning_value
                       | NAME POW_ASSIGN returning_value'''
        if p[2] == '+=':
            p[0] = Assignment(p[1], BinaryOp('+', Selection(p[1]), p[3]))
        if p[2] == '-=':
            p[0] = Assignment(p[1], BinaryOp('-', Selection(p[1]), p[3]))
        if p[2] == '*=':
            p[0] = Assignment(p[1], BinaryOp('*', Selection(p[1]), p[3]))
        if p[2] == '/=':
            p[0] = Assignment(p[1], BinaryOp('/', Selection(p[1]), p[3]))
        if p[2] == '**=':
            p[0] = Assignment(p[1], BinaryOp('**', Selection(p[1]), p[3]))

    def p_assign_stmt(self, p):
        '''assign_stmt : NAME ASSIGN assignment'''
        p[0] = Assignment(p[1], p[3])

    def p_global_assign_stmt(self, p):
        '''assign_stmt : GLOBAL_NAME ASSIGN assignment'''
        p[0] = GlobalAssignment(p[1], p[3])

    def p_assignment(self, p):
        '''assignment : expression
                      | comparision
                      | func_call_stmt'''
        p[0] = p[1]

    def p_relexpr(self, p):
        '''comparision : returning_value EQ returning_value
                       | returning_value NE returning_value
                       | returning_value GT returning_value
                       | returning_value LT returning_value
                       | returning_value GE returning_value
                       | returning_value LE returning_value'''
        p[0] = Comparision(p[2], p[1], p[3])

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_type(self, p):
        '''expression : type
                      | select
                      | preop
                      | postop
                      | array_selection'''
        p[0] = p[1]

    def p_array_selection(self, p):
        '''array_selection : select array_get
                           | func_call_stmt array_get'''
        p[0] = ArraySelection(p[1], p[2])

    def p_array_get_expr(self, p):
        'array_get : LBRACKET expression RBRACKET'
        p[0] = [p[2]]

    def p_array_get_expr_col_expr(self, p):
        'array_get : LBRACKET expression COLON expression RBRACKET'
        p[0] = [p[2], p[4]]

    def p_array_get_col(self, p):
        'array_get : LBRACKET COLON RBRACKET'
        p[0] = [None, None]

    def p_array_col_expr(self, p):
        'array_get : LBRACKET COLON expression RBRACKET'
        p[0] = [None, p[3]]

    def p_array_expr_col(self, p):
        'array_get : LBRACKET expression COLON RBRACKET'
        p[0] = [p[2], None]

    def p_pre_operation(self, p):
        '''preop : DOUBLEPLUS select
                 | DOUBLEMINUS select'''
        p[0] = PreOperation(p[1], p[2])
        
    def p_post_operation(self, p):
        '''postop : select DOUBLEPLUS
                  | select DOUBLEMINUS'''
        p[0] = PostOperation(p[2], p[1])

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = UnaryOp(p[1], p[2])

    def p_type_integer(self, p):
        'type : INTEGER_TYPE'
        p[0] = Integer(p[1])

    def p_type_float(self, p):
        'type : FLOAT_TYPE'
        p[0] = Float(p[1])

    def p_type_string(self, p):
        'type : STRING_TYPE'
        p[0] = String(p[1])

    def p_type_boolean(self, p):
        'type : BOOLEAN_TYPE'
        p[0] = Boolean(p[1])
        
    def p_type_array(self, p):
        '''type : LBRACKET RBRACKET
                | LBRACKET array_elements RBRACKET'''
        if len(p) == 3:
            p[0] = Array()
        else:
            p[0] = Array(p[2])
        
    def p_array_elements(self, p):
        '''array_elements : expression
                          | expression COMMA array_elements'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_select_name(self, p):
        'select : NAME'
        p[0] = Selection(p[1])

    def p_global_selection(self, p):
        '''select : GLOBAL_NAME'''
        p[0] = GlobalSelection(p[1])

    def p_if_stmt(self, p):
        '''if_stmt : IF test THEN suite
                   | IF test THEN suite ELSE suite'''
        if len(p) == 5:
            p[0] = IfThenElse(p[2], p[4], None)
        else:
            p[0] = IfThenElse(p[2], p[4], p[6])

    def p_suite(self, p):
        '''suite : simple_stmt
                 | BEGIN stmts END'''
        if len(p) == 2:
            p[0] = Block(p[1])
        else:
            p[0] = Block(p[2])

    #should refers all statements but used in a single line
    def p_simple_stmt(self, p):
        #currently only for test issues
        '''simple_stmt : stmt'''
        p[0] = [p[1]]

    def p_stmts(self, p):
        '''stmts : stmt
                 | stmt SEMICOLON stmts'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_stmt(self, p):
        #for test too
        '''stmt : compound_stmt
                | assign_stmt
                | print_stmt
                | return_stmt
                | break_stmt
                | continue_stmt
                | expression'''
        p[0] = p[1]

    def p_compound_stmt(self, p):
        '''compound_stmt : if_stmt
                         | while_stmt
                         | func_def_stmt
                         | do_while_stmt
                         | switch_stmt'''
#                         | for_stmt
        p[0] = p[1]

    def p_switch_stmt(self, p):
        '''switch_stmt : SWITCH select BEGIN case_stmts END'''
        p[0] = Switch(p[2], p[4])
        
    def p_case_stmts(self, p):
        '''case_stmts : DEFAULT COLON stmts
                      | CASE expression COLON stmts
                      | CASE expression COLON stmts case_stmts'''
        if len(p) == 4:
            p[0] = [tuple([p[1], Block(p[3])])]
        elif len(p) == 5:
            p[0] = [tuple([p[2], Block(p[4])])]
        else:
            p[0] = [tuple([p[2], Block(p[4])])] + p[5]

    def p_do_while_stmt(self, p):
        '''do_while_stmt : DO suite WHILE test'''
        p[0] = DoWhile(p[4], p[2])
            
    def p_while_stmt(self, p):
        '''while_stmt : WHILE test suite'''
        p[0] = While(p[2], p[3])
        
    def p_print_stmt(self, p):
        '''print_stmt : PRINT func_call_args'''
        p[0] = Print(p[2])
        
    def p_func_def_stmt(self, p):
        '''func_def_stmt : DEF NAME LPAREN RPAREN suite
                         | DEF NAME LPAREN func_def_args RPAREN suite'''
        if len(p) == 6:
            p[0] = FuncDef(p[2], tuple([]), p[5])
        else:
            p[0] = FuncDef(p[2], p[4], p[6])

    def p_func_def_args(self, p):
        '''func_def_args : type_name NAME
                         | type_name NAME COMMA func_def_args'''
        if len(p) == 3:
            #musimy uzyc tuples, bo listy i dicty sa unhashable, a 
            #potrzebujemy ponizsza strukture wsadzic do seta. 
            p[0] = tuple([tuple([p[1],p[2]])])
        else:
            p[0] = tuple([tuple([p[1],p[2]])]) + p[4]

    def p_type_name(self, p):
        '''type_name : INTEGER_NAME
                     | STRING_NAME
                     | FLOAT_NAME
                     | BOOLEAN_NAME'''
        p[0] = p[1]

    def p_test(self, p):
        '''test : LPAREN comparision RPAREN
                | comparision'''
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_break_stmt(self, p):
        'break_stmt : BREAK'
        p[0] = Break()

    def p_continue_stmt(self, p):
        'continue_stmt : CONTINUE'
        p[0] = Continue()

    def p_return_none(self, p):
        '''return_stmt : RETURN'''
        p[0] = Return()

    def p_return_stmt(self, p):
        '''return_stmt : RETURN expression
                       | RETURN comparision
                       | RETURN func_call_stmt'''
        p[0] = Return(p[2])

    def p_return_closure(self, p):
        '''return_stmt : RETURN func_def_stmt'''
        p[0] = ReturnClosure(p[2])

    def p_func_call(self, p):
        '''func_call_stmt : NAME LPAREN RPAREN
                          | NAME LPAREN func_call_args RPAREN'''
        if len(p) == 4:
            p[0] = FuncCall(p[1], [])
        else:
            p[0] = FuncCall(p[1], p[3])

    def p_func_call_args(self, p):
        '''func_call_args : arg
                          | arg COMMA func_call_args'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_func_call_args_arg(self, p):
        '''arg : expression
               | func_call_stmt'''
        p[0] = p[1]

    def p_error(self, p):
        print 'Syntax error at'

if __name__ == '__main__':
    calc = Parser()
    calc.run()