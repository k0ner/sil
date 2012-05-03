import copy
from ast import Node, GlobalSelection, Selection
from structures import *
import re

class Evaluator():

    variables = { }
    global_variables = None
    closures = Map()
    functions = Map()
    fake = False

    #przerobic na postac nastepujaca:
    # function = getattr(self,"visit_"+nazwa)
    # return function(ast)
    @staticmethod
    def visit(ast):
        if not ast:
            return
        if not isinstance(ast, Node):
            return ast
        func = getattr(Evaluator(), "visit_" + ast.type)
        return func(ast)

    def visit_pre_op(self, node):
        if isinstance(node.select, GlobalSelection):
            result = Evaluator.global_variables[node.select.name]
            if node.op == '++': 
                result = result + 1
                Evaluator.global_variables[node.select.name] = result
            elif node.op == '--':
                result = result - 1
                Evaluator.global_variables[node.select.name] = result
        elif isinstance(node.select, Selection):
            result = Evaluator.variables[node.select.name]
            if node.op == '++':
                result = result + 1 
                Evaluator.variables[node.select.name] = result
            if node.op == '--':
                result = result - 1
                Evaluator.variables[node.select.name] = result
        return result

    def visit_post_op(self, node):
        if isinstance(node.select, GlobalSelection):
            result = Evaluator.global_variables[node.select.name]
            if node.op == '++':
                Evaluator.global_variables[node.select.name] = result + 1
            elif node.op == '--':
                Evaluator.global_variables[node.select.name] = result - 1
        elif isinstance(node.select, Selection):
            result = Evaluator.variables[node.select.name]
            if node.op == '++':
                Evaluator.variables[node.select.name] = result + 1
            if node.op == '--':
                Evaluator.variables[node.select.name] = result - 1
        return result

    def visit_return(self, node):
        return self.visit(node.value)

    def visit_print(self, node):
        for item in node.args:
            if isinstance(item, Node):
                result = self.visit(item)
                if not Evaluator.fake:
                    print result,
            else:
                if not Evaluator.fake:
                    print item
        if not Evaluator.fake:
            print

    def visit_break(self, node):
        return node.type

    def visit_func_def(self, node):
        
        Evaluator.fake = True
        tmpVar = copy.deepcopy(Evaluator.variables)
        tmpGlobalVar = copy.deepcopy(Evaluator.global_variables)
        tmpClosures = copy.deepcopy(Evaluator.closures)
        tmpFunctions = copy.deepcopy(Evaluator.functions)
        
        if not Evaluator.global_variables:
            Evaluator.global_variables = copy.deepcopy(Evaluator.variables)
        
        Evaluator.functions.add(node.name, node.args, node.body)
        for arg in node.args:
            Evaluator.variables[arg[1]] = Evaluator.assign_with_cast(arg[0], 0)
        Evaluator.visit(node.body)
        
        Evaluator.functions = copy.deepcopy(tmpFunctions)
        Evaluator.closures = copy.deepcopy(tmpClosures)
        Evaluator.global_variables = copy.deepcopy(tmpGlobalVar)
        Evaluator.variables = copy.deepcopy(tmpVar)
        Evaluator.fake = False
        
        if Evaluator.functions.contains(node.name, node.args, node.body)[0]:
            while True:
                s = raw_input("Function " + node.name + " with applied arguments already exists. Override? [y/N]: ")
                if s == "y":
                    Evaluator.functions.add(node.name, node.args, node.body)
                    break
                if s == "N" or s == "n" or s == "":
                    break
        else:
            Evaluator.functions.add(node.name, node.args, node.body)

    def visit_return_closure(self, node):
        closure = node.value
        current_variables = { }
        for k, v in Evaluator.variables.items():
            if Evaluator.is_simple_type(v):
                current_variables.update({k : v})
        
        Evaluator.fake = True
        tmpVar = copy.deepcopy(Evaluator.variables)
        tmpGlobalVar = copy.deepcopy(Evaluator.global_variables)
        tmpClosures = copy.deepcopy(Evaluator.closures)
        tmpFunctions = copy.deepcopy(Evaluator.functions)
        
        Evaluator.closures.add(closure.name, closure.args, closure.body)
        for arg in closure.args:
            Evaluator.variables[arg[1]] = Evaluator.assign_with_cast(arg[0], 0)
        Evaluator.visit(closure.body)
        
        Evaluator.functions = copy.deepcopy(tmpFunctions)
        Evaluator.closures = copy.deepcopy(tmpClosures)
        Evaluator.global_variables = copy.deepcopy(tmpGlobalVar)
        Evaluator.variables = copy.deepcopy(tmpVar)
        Evaluator.fake = False
        
        Evaluator.closures.add(closure.name, closure.args, closure.body)

        return tuple([ Evaluator.closures.get(closure.name), current_variables])

    def visit_func_call(self, node):
        #dostajemy wszystkie definicje funkcji zwiazanych z dana nazwa, pozniej musimy sprawdzic zmienne czy sa odpowiedniego typu
        defList = Evaluator.functions.get(node.name)
        Evaluator.is_closure = False
        
        if defList == []:
            try:
                defList = Evaluator.variables[node.name]
                Evaluator.is_closure = True
            except Exception:
                print "Function", node.name, "not found."
                return

        #kopiujemy srodowiska
        if not Evaluator.global_variables:
            Evaluator.global_variables = copy.deepcopy(Evaluator.variables)
            
        if Evaluator.is_closure:
            """trzeba uwazac, bo tutaj wszystko dziala jako przekazywanie przez wartosc, a nie przez referencje,
            wiec jesli przekazemy do funkcji zmienna to bedzie przekazana jej aktualna wartosc!!
            przy wywolaniu typu: z = 1; add_z = returnClosure(z); print add_z(x);
            wyswietlona zostanie wartosc x+1
            jesli dalej damy z = 3 i znowu wywolamy print add_z(x) to dalej bedzie sie wyswietlalo
            x+1, a nie jak moznaby przypuszczac x+3, poniewaz w fcji returnClosure(z) zostala uzyta wartosc tej zmiennej, a nie referencja"""
            tmpVariables = copy.deepcopy(Evaluator.variables)
            Evaluator.variables.update(defList[1])
            defList = defList[0]
        else:
            tmpVariables = copy.deepcopy(Evaluator.variables)
        tmpFunctions = copy.deepcopy(Evaluator.functions)
        
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
                        metric += 0.7
                    elif definition[1][i][0] == 'float' and callArgs[i][0] == 'int':
                        bestFits = False
                        metric += 0.9
                    elif definition[1][i][0] == 'bool' and callArgs[i][0] == 'int':
                        bestFits = False
                        metric += 0.8
                    elif definition[1][i][0] == 'bool' and callArgs[i][0] == 'float':
                        bestFits = False
                        metric += 0.45
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
            Evaluator.variables[definition[1][i][1]] = Evaluator.assign_with_cast(definition[1][i][0], callArgs[i][1])
            i += 1
            
        if not Evaluator.fake:
            result = self.visit(definition[2])
        else:
            result = 0
        Evaluator.functions = copy.deepcopy(tmpFunctions)
        if Evaluator.global_variables:
            Evaluator.variables = copy.deepcopy(Evaluator.global_variables)
            Evaluator.global_variables = None
        else:
            Evaluator.variables = copy.deepcopy(tmpVariables)
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
        result = None
        while ( self.visit(node.cond) ):
            result = self.visit(node.body)
            if result == 'break':
                break
        return result

    def visit_assignment(self, node):
        result = self.visit(node.value)
        Evaluator.variables[node.name] = result
        print Evaluator.variables
        return result

    def visit_global_assignment(self, node):
        result = self.visit(node.value)
        try:
            #ponizsza instrukcja jest tylko po to zeby rzucilo wyjatek jesli nie ma takiej zmiennej globalnej
            Evaluator.global_variables[node.name]
            Evaluator.global_variables[node.name] = result
            Evaluator.variables[node.name] = result
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
            result = Evaluator.global_variables[node.name]
        except KeyError:
            print "Variable", node.name, "does not exist in global context."
            result = None
        return result

    def visit_selection(self, node):
        return Evaluator.variables[node.name]

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

    def visit_array(self, node):
        result = []
        if node.value:
            for element in node.value:
                result += [Evaluator.visit(element)]
        return result
    
    def visit_array_selection(self, node):
        result = Evaluator.visit(node.name)
        
        if len(node.value) == 1:
            return result[Evaluator.visit(node.value[0])]
        elif not node.value[0]:
            if not node.value[1]:
                return result
            else:
                return result[:Evaluator.visit(node.value[1])]
        elif not node.value[1]:
            return result[Evaluator.visit(node.value[0]):]
        else:
            return result[Evaluator.visit(node.value[0]):Evaluator.visit(node.value[1])]

    def visit_global_array_selection(self, node):
        try:
            result = Evaluator.visit(node.name)
            if ':' in node.value:
                if len(node.value) == 1:
                    result = result[node.name]
                elif node.value[0] == ':':
                    result = result[:int(node.value[1:])]
                else:
                    result = result[int(node.value[:-1]):]
            else:
                result = result[int(node.value)]
        except KeyError:
            print "Variable", node.name, "does not exist in global context."
            result = None
        return result

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

    @staticmethod
    def is_simple_type(value):
        if isinstance(value, int) or isinstance(value, str) or isinstance(value, float) or isinstance(value, bool):
            return True
        return False
        
    @staticmethod
    def assign_with_cast(castTo, value):
        if castTo == 'int':
            return int(value)
        if castTo == 'float':
            return float(value)
        if castTo == 'bool':
            return bool(value)
        if castTo == 'string':
            return str(value)