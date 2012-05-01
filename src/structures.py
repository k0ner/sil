class Map:
    def __init__(self):
        self.container = set()
        
    def add(self, name, args, body):
        exists = False
        for item in self.container:
            #tutaj trzeba poprawic, bo nie wykryje roznicy pomiedzy bool x i bool y
            if name == item[0]:
                i = 0
                if len(args) == len(item[1]):
                    while i < len(args):
                        if args[i][0] == item[1][i][0]:
                            i += 1
                        else:
                            break
                    if i == len(args):
                        exists = True
            if exists:
                self.remove()
        self.container.add(tuple([name, args, body]))
        
    def contains(self, name, args, body):
        for item in self.container:
            #tutaj trzeba poprawic, bo nie wykryje roznicy pomiedzy bool x i bool y
            if name == item[0] and args == item[1]:
                return True
        return False
    
    def get(self, name):
        result = [ ]
        for item in self.container:
            if name == item[0]:
                result.append(item)
        return result
