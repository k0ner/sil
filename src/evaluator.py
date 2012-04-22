import copy
from ast import Node
from structures import *
import re

class Evaluator():

    def __init__(self):
        self.__variables = { }
        self.__globals = None
        self.__closures = Map()
        self.__functions = Map()
    
    #przerobic na postac nastepujaca:
    # function = getattr(self,"visit_"+nazwa)
    # return function(ast)
    def visit(self, ast):
        if ast.type == "selection":
            return self.visit_Select(ast)
        if ast.type == "assignment":
            return self.visit_Assign(ast)
        if ast.type == "ifelse":
            return self.visit_IfThenElse(ast)
        if ast.type == "relexpr":
            return self.visit_RelExpr(ast)
        if ast.type == "bool":
            return self.visit_Boolean(ast)
        if ast.type == "int":
            return self.visit_Integer(ast)
        if ast.type == "string":
            return ast.value
        if ast.type == "unaryop":
            return self.visit_UnaryOp(ast)
        if ast.type == "binaryop":
            return self.visit_BinaryOp(ast)
        if ast.type == "while":
            return self.visit_While(ast)
        if ast.type == "block":
            return self.visit_Block(ast)
        if ast.type == "funcdef":
            return self.visit_FuncDef(ast)
        if ast.type == "print":
            return self.visit_Print(ast.args)
        if ast.type == "funccall":
            return self.visit_FuncCall(ast)
        if ast.type == "return":
            return self.visit_Return(ast)
        func = getattr(self, "visit_" + ast.type)
        return func(ast)
        
    def visit_Return(self, node):
        return self.visit(node.value)
    
    def visit_Print(self, node):
        for item in node:
            if isinstance(item, Node):
                print self.visit(item),
            else:
                print item
        print
    
    def visit_FuncDef(self, node):
        self.__functions.add(node.name, node.args, node.body)
    
    def visit_return_closure(self, node):
        closure = node.value.stmts[0]
        current_variables = { }
        for k, v in self.__variables.items():
            if self.is_simple_type(v):
                current_variables.update({k : v})
        self.__closures.add(closure.name, closure.args, closure.body)
        print self.__closures.get(closure.name)
        return tuple([ self.__closures.get(closure.name), current_variables])

    def visit_pointer_assignment(self, node):
        self.__variables[node.name] = node.point_to
        print self.__variables

    #to musi zostac przerobione, bo i tak nie bedzie dzialalo!
    def visit_pointer_selection(self, node):
        print "tutaj"
        return self.__variables[node.name]

    def visit_FuncCall(self, node):
        
        #dostajemy wszystkie definicje funkcji zwiazanych z dana nazwa, pozniej musimy sprawdzic zmienne czy sa odpowiedniego typu
        defList = self.__functions.get(node.name)
        is_closure = False
        
        if defList == []:
            try:
                defList = self.__variables[node.name]
                is_closure = True
            except Exception:
                print "Function", node.name, "not found."
                return
        print "####otrzymane funckje", defList

        #kopiujemy srodowiska
        if not self.__globals:
            self.__globals = copy.deepcopy(self.__variables)
            
        if is_closure:
            """trzeba uwazac, bo tutaj wszystko dziala jako przekazywanie przez wartosc, a nie przez referencje,
            wiec jesli przekazemy do funkcji zmienna to bedzie przekazana jej aktualna wartosc!!
            przy wywolaniu typu: z = 1; add_z = returnClosure(z); print add_z(x);
            wyswietlona zostanie wartosc x+1
            jesli dalej damy z = 3 i znowu wywolamy print add_z(x) to dalej bedzie sie wyswietlalo
            x+1, a nie jak moznaby przypuszczac x+3, poniewaz w fcji returnClosure(z) zostala uzyta wartosc tej zmiennej, a nie referencja"""
            tmpVariables = copy.deepcopy(self.__variables)
            self.__variables.update(defList[1])
            defList = defList[0]
        else:
            tmpVariables = copy.deepcopy(self.__variables)
        tmpFunctions = copy.deepcopy(self.__functions)
        
        callArgs = [tuple([re.search('(?<=\')\w+', str(type(self.visit(arg)))).group(0), self.visit(arg)]) for arg in node.args]
        possibleToUse = []
        for definition in defList:
            #definition[1] to jest lokalizacja argumentow w krotce
            if len(definition[1]) == len(callArgs):
                bestFits = True
                i = 0;
                metric = 0.0;
                #lecimy po wszystkich argumentach i sprawdzamy czy da sie rzutowac, jesli nie to przerywamy petle
                while i < len(definition[1]):
                    if definition[1][i][0] == callArgs[i][0]:
                        print "zgadza sie"
                        metric += 1.
                    elif definition[1][i][0] == 'int' and callArgs[i][0] == 'float':
                        bestFits = False
                        metric += 0.9
                        print "rzutowanie float na int"
                    elif definition[1][i][0] == 'float' and callArgs[i][0] == 'int':
                        bestFits = False
                        metric += 0.45
                        print "rzutowanie int na float"
                    elif definition[1][i][0] == 'bool' and callArgs[i][0] == 'int':
                        bestFits = False
                        metric += 0.8
                        print "rzutowanie int na bool"
                    elif definition[1][i][0] == 'bool' and callArgs[i][0] == 'float':
                        bestFits = False
                        metric += 0.7
                        print "rzutowanie float na bool"
                    else:
                        bestFits = False
                        break
                    i = i+1
                    
                #jesli mamy best fita, to super
                if bestFits:
                    print "dobrze dopasowalo"
                    possibleToUse = definition
                    break
                #dodajemy do listy w postaci elementu slownika {wartosc_metryki : definicja}
                possibleToUse.append(tuple([metric, definition]))
        #musimy teraz posortowac od razu odwrotnie, zeby wziac pierwszy element (rownie dobrze mozemy wziac ostatni, ale tak jest bardziej intuicyjnie)
        
        if isinstance(possibleToUse, list):
            possibleToUse = sorted(possibleToUse, key=lambda item: item[0], reverse=True)
            definition = possibleToUse[0][1]
        else:
            definition = possibleToUse
        
        i = 0
        while i < len(definition[1]):
            self.__variables[definition[1][i][1]] = self.assign_with_cast(definition[1][i][0], callArgs[i][1])
            i += 1
            
        result = self.visit(definition[2])
        self.__functions = copy.deepcopy(tmpFunctions)
        if self.__globals:
            self.__variables = copy.deepcopy(self.__globals)
            self.__globals = None
        else:
            self.__variables = copy.deepcopy(tmpVariables)
        return result
    
    def visit_Block(self, node):
        for item in node.stmts:
            result = self.visit(item)
        return result
    
    def visit_While(self, node):
        while ( self.visit(node.cond) ):
            x = self.visit(node.body)
            if x:
                return x
        return
    
    def visit_Assign(self, node):
        result = self.visit(node.value)
        self.__variables[node.name] = result
        print self.__variables
        return result
    
    def visit_global_assignment(self, node):
        result = self.visit(node.value)
        try:
            #ponizsza instrukcja jest tylko po to zeby rzucilo wyjatek jesli nie ma takiej zmiennej globalnej
            self.__globals[node.name]
            self.__globals[node.name] = result
            self.__variables[node.name] = result
        except KeyError:
            #nie mozemy stworzyc nowej zmiennej
            print "Variable", node.name, "does not exist in global context. Cannot create global variable from a local context."
            result = None
        except Exception:
            print "global prefix used in incorrect context"
            result = None
        return result
    
    def visit_global_selection(self, node):
        try:
            result = self.__globals[node.name]
        except KeyError:
            print "Variable", node.name, "does not exist in global context."
            result = None
        return result
    
    def visit_Select(self, node):
        return self.__variables[node.name]
        #=======================================================================
        # result = self.__variables[node.name]
        # if self.toReturn:
        #    print "byla funckja :-)"
        #    self.__variables = copy.deepcopy(self.tmpNames)
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
        
    def is_simple_type(self, value):
        if isinstance(value, int) or isinstance(value, str) or isinstance(value, float) or isinstance(value, bool):
            return True
        return False
        
    def assign_with_cast(self, castTo, value):
        if castTo == 'int':
            return int(value)
        if castTo == 'float':
            return float(value)
        if castTo == 'bool':
            return bool(value)
        if castTo == 'string':
            return str(value)