class Map:
    def __init__(self):
        self.container = set()
        
    def add(self, name, args, body):
        for item in self.container:
            if name == item[0] and args == item[1]:
                self.container.remove(item)
                break
        self.container.add(tuple([name, args, body]))
        
    def get(self, name):
        result = [ ]
        for item in self.container:
            if name == item[0]:
                result.append(item)
        return result
