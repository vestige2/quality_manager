import objgraph
import pygraphviz as pygraphviz


class _One:
    __slots__ = ['k1', 'k2']
    def __init__(self):
        self.k1 = 222
        self.k2 = 111
        print(_One.__dict__)

class _Two:
    def __init__(self):
        self.k3 = 5555
        self.k4 = 1111
        print(_Two.__dict__)


a = _One()
# print(a.__dict__)
b = _Two()

objgraph.show_refs(b)

pygraphviz.agraph