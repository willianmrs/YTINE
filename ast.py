class AST():
    def __init__(self, name, children, leaf=None ):
        self.name = name
        self.children = children
        self.leaf = leaf

    def __str__(self, level=0):
        ret = "|"*level+repr(self.name)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret