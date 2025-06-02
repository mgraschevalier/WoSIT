
import sys


class ArgParser:
    __targets = None
    __args = None
    
    def __init__(self):
        self.__targets = []
        self.__args = {}

        args = sys.argv[1:]
        nbargs = len(args)
        
        
        for a in args:
            if a.startswith("-"):
                continue
            if "=" in a:
                aparts = a.split("=")
                if aparts[0] in list(self.__args.keys()):
                    raise ValueError(f"Argument \"{aparts[0]}\" already defined.")
                self.__args.update({aparts[0]:aparts[1]})
            else:
                if a in self.__targets:
                    raise ValueError(f"Target \"{a}\" already in list.")
                self.__targets.append(a)
    


    def getTargets(self):
        return self.__targets.copy()
    

    
    def getArgs(self):
        return self.__args.copy()
    


    def getArg(self, argname):
        if argname in (self.__args.keys()):
            return self.__args[argname]
        return None
