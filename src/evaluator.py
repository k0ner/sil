import copy
from ast import Node, GlobalSelection, Selection
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
        if not ast:
            return
        if not isinstance(ast, Node):
            return ast
        func = getattr(self, "visit_" + ast.type)
        return func(ast)
        
    def visit_pre_op(self, node):
        if isinstance(node.select, GlobalSelection):
            result = self.__globals[node.select.name]
            if node.op == '++': 
                result = result + 1
                self.__globals[node.select.name] = result
            elif node.op == '--':
                result = result - 1
                self.__globals[node.select.name] = result
        elif isinstance(node.select, Selection):
            result = self.__variables[node.select.name]
            if node.op == '++':
                result = result + 1 
                self.__variables[node.select.name] = result
            if node.op == '--':
                result = result - 1
                self.__variables[node.select.name] = result
        return result
    
    def visit_post_op(self, node):
        if isinstance(node.select, GlobalSelection):
            result = self.__globals[node.select.name]
            if node.op == '++':
                self.__globals[node.select.name] = result + 1
            elif node.op == '--':
                self.__globals[node.select.name] = result - 1
        elif isinstance(node.select, Selection):
            result = self.__variables[node.select.name]
            if node.op == '++':
                self.__variables[node.select.name] = result + 1
            if node.op == '--':
                self.__variables[node.select.name] = result - 1
        return result
    
    def visit_return(self, node):
        return self.visit(node.value)
    
    def visit_print(self, node):
        for item in node.args:
            if isinstance(item, Node):
                print self.visit(item),
            else:
                print item
        print
        
    def visit_break(self, node):
        return node.type
    
    def visit_func_def(self, node):
        self.__functions.add(node.name, node.args, node.body)
    
    def visit_return_closure(self, node):
        closure = node.value.stmts[0]
        current_variables = { }
        for k, v in self.__variables.items():
            if self.is_simple_type(v):
                current_variables.update({k : v})
        self.__closures.add(closure.name, closure.args, closure.body)
        return tuple([ self.__closures.get(closure.name), current_variables])

    def visit_func_call(self, node):
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
                        metric += 1.
                    elif definition[1][i][0] == 'int' and callArgs[i][0] == 'float':
                        bestFits = False
                        metric += 0.9
                    elif definition[1][i][0] == 'float' and callArgs[i][0] == 'int':
                        bestFits = False
                        metric += 0.45
                    elif definition[1][i][0] == 'bool' and callArgs[i][0] == 'int':
                        bestFits = False
                        metric += 0.8
                    elif definition[1][i][0] == 'bool' and callArgs[i][0] == 'float':
                        bestFits = False
                        metric += 0.7
                    else:
                        bestFits = False
                        break
                    i = i+1
                    
                #jesli mamy best fita, to super
                if bestFits:
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
    
    def visit_block(self, node):
        for item in node.stmts:
            result = self.visit(item)
            if result == 'break':
                break
        return result
    
    def visit_do_while(self, node):
        while True:
            result = self.visit(node.body)
            if result == 'break':
                break
            if not self.visit(node.cond):
                break
        return result
    
    def visit_while(self, node):
        while ( self.visit(node.cond) ):
            result = self.visit(node.body)
            if result == 'break':
                break
        return result
    
    def visit_assignment(self, node):
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
    
    def visit_selection(self, node):
        return self.__variables[node.name]
        #=======================================================================
        # result = self.__variables[node.name]
        # if self.toReturn:
        #    print "byla funckja :-)"
        #    self.__variables = copy.deepcopy(self.tmpNames)
        #    self.tmpNames = None
        # return result
        #=======================================================================
    
    def visit_comparision(self, node):
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
        
    def visit_binary_op(self, node):
        if node.op == '+':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == '-':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == '*':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == '/':
            return self.visit(node.left) / self.visit(node.right)
        elif node.op == '**':
            return self.visit(node.left) ** self.visit(node.right)
        
    def visit_unary_op(self, node):
        if node.op == '-':
            return -(self.visit(node.expr))

    def visit_string(self, node):
        return node.value

    def visit_float(self, node):
        return node.value

    def visit_int(self, node):
        return node.value
    
    def visit_bool(self, node):
        return node.value
    
    def visit_if_then_else(self, node):
        if self.visit(node.cond):
            return self.visit(node.ifTrue)
        elif node.ifFalse:
            return self.visit(node.ifFalse)
        
    def visit_switch(self, node):
        value = self.visit(node.select)
        execute = False
        for case in node.cases:
            case_val = self.visit(case[0])
            if case_val == value or execute or case_val == 'default':
                execute = True
                result = self.visit(case[1])
                if result == 'break':
                    break
    
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