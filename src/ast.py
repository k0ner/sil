class Node : pass

class Return(Node):
    def __init__(self, value=None, coord=None):
        self.type = 'return'
        self.value = value
        self.coord = coord
        
class ReturnClosure(Node):
    def __init__(self, value, coord=None):
        self.type = 'return_closure'
        self.value = value

class Print(Node):
    def __init__(self, args, coord=None):
        self.type = 'print'
        self.args = args
        self.coord = coord

class FuncDef(Node):
    def __init__(self, name, args, body, coord=None):
        self.type = 'func_def'
        self.name = name
        self.args = args
        self.body = body
        self.coord = coord
        
class FuncCall(Node):
    def __init__(self, name, args, coord=None):
        self.type = 'func_call'
        self.name = name
        self.args = args
        self.coord = coord

class Block(Node):
    def __init__(self, stmts, coord=None):
        self.type = 'block'
        self.stmts = stmts
        self.coord = coord

class While(Node):
    def __init__(self, cond, body, coord=None):
        self.type = 'while'
        self.cond = cond
        self.body = body
        self.coord = coord
        
class DoWhile(Node):
    def __init__(self, cond, body, coord=None):
        self.type = 'do_while'
        self.cond = cond
        self.body = body
        self.coord = coord

class Assignment(Node):
    def __init__(self, name, value, coord=None):
        self.type = 'assignment'
        self.name = name
        self.value = value
        self.coord = coord

class BinaryOp(Node):
    def __init__(self, op, left, right, coord=None):
        self.type = 'binary_op'
        self.op = op
        self.left = left
        self.right = right
        self.coord = coord
        
class UnaryOp(Node):
    def __init__(self, op, expr, coord=None):
        self.type = 'unary_op'
        self.op = op
        self.expr = expr
        self.coord = coord
        
class Comparision(Node):
    def __init__(self, op, left, right, coord=None):
        self.type = 'comparision'
        self.op = op
        self.left = left
        self.right = right
        self.coord = coord
        
class Boolean(Node):
    def __init__(self, value, coord=None):
        self.type = 'bool'
        self.value = value
        self.coord = coord
        
class Integer(Node):
    def __init__(self, value, coord=None):
        self.type = 'int'
        self.value = value
        self.coord = coord
        
class String(Node):
    def __init__(self, value, coord=None):
        self.type = 'string'
        self.value = value
        self.coord = coord
    
class Float(Node):
    def __init__(self, value, coord=None):
        self.type = 'float'
        self.value = value
        self.coord = coord
        
class IfThenElse(Node):
    def __init__(self, cond, ifTrue, ifFalse, coord=None):
        self.type = 'if_then_else'
        self.cond = cond
        self.ifTrue = ifTrue
        self.ifFalse = ifFalse
        self.coord = coord
        
class Selection(Node):
    def __init__(self, name, coord=None):
        self.type = 'selection'
        self.name = name
        self.coord = coord
        
class GlobalSelection(Node):
    def __init__(self, name, coord=None):
        self.type = 'global_selection'
        self.name = name
        self.coord = coord
        
class GlobalAssignment(Node):
    def __init__(self, name, value, coord=None):
        self.type = 'global_assignment'
        self.name = name
        self.value = value
        self.coord = coord
        
class Switch(Node):
    def __init__(self, select, cases, coord=None):
        self.type = 'switch'
        self.select = select
        self.cases = cases
        
class Break(Node):
    def __init__(self, coord=None):
        self.type = 'break'
        
class PreOperation(Node):
    def __init__(self, op, select, coord=None):
        self.type = 'pre_op'
        self.op = op
        self.select = select
        
class PostOperation(Node):
    def __init__(self, op, select, coord=None):
        self.type = 'post_op'
        self.op = op
        self.select = select
        
class Array(Node):
    def __init__(self, value=None, coord=None):
        self.type = 'array'
        self.value = value
        self.coord = coord
        
class ArraySelection(Node):
    def __init__(self, name, value, coord=None):
        self.type = 'array_selection'
        self.name = name
        self.value = value
        self.coord = coord