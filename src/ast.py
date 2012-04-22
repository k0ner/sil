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
    def __init__(self, name, args, body, returns=None, coord=None):
        self.type = 'func_def'
        self.name = name
        self.args = args
        self.body = body
        self.returns = returns
        self.coord = coord
        
class FuncCall(Node):
    def __init__(self, name, args, coord=None):
        self.type = 'funccall'
        self.name = name
        self.args = args
        self.coord = coord
        
class FuncDefArgs(Node):
    def __init__(self, argsList, coord=None):
        self.type = 'funcdefargs'
        self.argsList = argsList
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

class Assign(Node):
    def __init__(self, name, value, coord=None):
        self.type = 'assignment'
        self.name = name
        self.value = value
        self.coord = coord

class BinaryOp(Node):
    def __init__(self, op, left, right, coord=None):
        self.type = 'binaryop'
        self.op = op
        self.left = left
        self.right = right
        self.coord = coord
        
class UnaryOp(Node):
    def __init__(self, op, expr, coord=None):
        self.type = 'unaryop'
        self.op = op
        self.expr = expr
        self.coord = coord
        
class RelExpr(Node):
    def __init__(self, op, left, right, coord=None):
        self.type = 'relexpr'
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
        self.type = 'ifelse'
        self.cond = cond
        self.ifTrue = ifTrue
        self.ifFalse = ifFalse
        self.coord = coord
        
class Select(Node):
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
        
class PointerAssignment(Node):
    def __init__(self, name, point_to, coord=None):
        self.type = 'pointer_assignment'
        self.name = name
        self.point_to = point_to
        self.coord = coord
        
class PointerSelection(Node):
    def __init__(self, name, coord=None):
        self.type = 'pointer_selection'
        self.name = name
        self.coord = coord