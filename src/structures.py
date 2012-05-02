class Map:
    def __init__(self):
        self.container = set()
        
    def add(self, name, args, body):
        result = self.contains(name, args, body)
        if result[0]:
            self.container.remove(result[1])
        self.container.add(tuple([name, args, body]))
        
    def contains(self, name, args, body):
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
                return (True, item)
                break
        return (False, None)
    
    def get(self, name):
        result = [ ]
        for item in self.container:
            if name == item[0]:
                result.append(item)
        return result
