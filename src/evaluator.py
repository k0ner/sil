import copy
from ast import Node

class Evaluator():

    def __init__(self):
        self.names = { }
        self.toReturn = False
    
    def visit(self, ast):
        if ast.type == "string":
            return ast.value
        if ast.type == "selection":
            print ast.type
            return self.visit_Select(ast)
        if ast.type == "assignment":
            print ast.type
            return self.visit_Assign(ast)
        if ast.type == "ifelse":
            print ast.type
            return self.visit_IfThenElse(ast)
        if ast.type == "relexpr":
            print ast.type
            return self.visit_RelExpr(ast)
        if ast.type == "boolean":
            print ast.type
            return self.visit_Boolean(ast)
        if ast.type == "integer":
            print ast.type
            return self.visit_Integer(ast)
        if ast.type == "unaryop":
            print ast.type
            return self.visit_UnaryOp(ast)
        if ast.type == "binaryop":
            print ast.type
            return self.visit_BinaryOp(ast)
        if ast.type == "while":
            print ast.type
            return self.visit_While(ast)
        if ast.type == "block":
            print ast.type
            return self.visit_Block(ast)
        if ast.type == "funcdef":
            print ast.type
            return self.visit_FuncDef(ast)
        if ast.type == "print":
            print ast.type
            return self.visit_Print(ast.args)
        if ast.type == "funccall":
            print ast.type
            return self.visit_FuncCall(ast)
        if ast.type == "return":
            print ast.type
            return self.visit_Return(ast)
        
    def visit_Return(self, node):
        return self.visit(node.value)
    
    def visit_Print(self, node):
        if isinstance(node, Node):
            print self.visit(node.arg),
        else:
            print node
        if node.nextArgs:
            self.visit_Print(node.nextArgs)
        else:
            print
    
    def visit_FuncDef(self, node):
        self.names[node.name] = node
    
    def visit_FuncCall(self, node):
        tmpNames = copy.deepcopy(self.names)
        definition = self.names[node.name]
        defArgs = definition.args
        callArgs = node.args
        if defArgs.arg:
            self.names[defArgs.arg] = self.visit(callArgs.arg)
            print self.names
        while defArgs.nextArgs:
            defArgs = defArgs.nextArgs
            callArgs = callArgs.nextArgs
            self.names[defArgs.arg] = self.visit(callArgs.arg)
        result = self.visit(definition.body)
        self.names = copy.deepcopy(tmpNames)
        return result
    
    def visit_Block(self, node):
        if node.nextBlock:
            self.visit(node.expr)
            return self.visit(node.nextBlock)
        else :
            return self.visit(node.expr)
    
    def visit_While(self, node):
        while ( self.visit(node.cond) ):
            x = self.visit(node.body)
            if x:
                return x
        return
    
    def visit_Assign(self, node):
        self.names[node.name] = self.visit(node.value)
        print self.names
        return
    
    def visit_Select(self, node):
        return self.names[node.name]
        #=======================================================================
        # result = self.names[node.name]
        # if self.toReturn:
        #    print "byla funckja :-)"
        #    self.names = copy.deepcopy(self.tmpNames)
        #    self.tmpNames = None
        # return result
        #=======================================================================
        
    
    def visit_RelExpr(self, node):
        if node.op == '==':
            return self.visit(node.left) == self.visit(node.right)
        elif node.op == '!=':
            return self.visit(node.left) != self.visit(node.right)
        elif node.op == '>':
            return self.visit(node.left) > self.visit(node.right)
        elif node.op == '<':
            return self.visit(node.left) < self.visit(node.right)
        elif node.op == '>=':
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op == '<=':
            return self.visit(node.left) <= self.visit(node.right)
        
    def visit_BinaryOp(self, node):
        if node.op == '+':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == '-':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == '*':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == '/':
            return self.visit(node.left) / self.visit(node.right)
        
    def visit_UnaryOp(self, node):
        if node.op == '-':
            return -(self.visit(node.expr))

    def visit_Integer(self, node):
        return node.value
    
    def visit_Boolean(self, node):
        return bool(node.value)
    
    def visit_IfThenElse(self, node):
        if self.visit(node.cond):
            return self.visit(node.ifTrue)
        elif node.ifFalse:
            return self.visit(node.ifFalse)
    
    def printAst(self, ast):
        print ast.expr