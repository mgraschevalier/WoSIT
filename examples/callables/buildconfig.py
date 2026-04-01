from wosit.Function import Function, Variable
from wosit.builder import addRule



class myclass:
    mymember = None

    def __init__(self, member):
        self.mymember = member
        
        
    def callme(self):
        print(self.mymember)

bobo = myclass("Also works with class methods!")



addRule(target="class",
        command=Function(bobo.callme)
)


def funcreturn(a, b):
    print(a)
    print(b)
    return "This is a returned value"


# Create a shared object retvar
retvar = Variable("IT HAS NOT BEEN MODIFIED")
addRule(target="returnvalue",
        source="class",
        command=Function(funcreturn, ("This function", Variable("returns something")), retvar)
)


addRule(target="all",
        source="returnvalue",
        command=Function(print, args=(retvar,)))
