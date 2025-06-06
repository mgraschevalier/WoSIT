import os

from Token import *
from Function import *


class Task:
    __target = None
    __sources = None
    __command = None

    __parsed_signature = False

    __parsed_stage= False


    def __init__(self, target, sources=None, command=None):
        if not type(target) in [Token, Task]:
            raise ValueError("Target must be of type \"Task or Token\".")

        if not all(type(s) in [Token, Task] for s in sources):
            raise ValueError("Sources must be of type \"Task or Token\".")


        self.__target = target
        self.__sources = sources

        self.__command = command



    def getSignature(self):
        return self.__target.getSignature()


    # Recursively parse the graph to get all signatures
    def getAllSignatures(self, signatures=None):
        if signatures is None:
            signatures = {}

        if self.__parsed_signature is True:
            return signatures

        # Add all dependencies
        for s in self.__sources:
            sig = s.getAllSignatures(signatures)
            signatures.update(sig)

        # Add itself
        signatures.update({self.__target.get():self.getSignature()})
        
        self.__parsed_signature = True

        return signatures



    def __hasChanged(self):
        return self.__target.hasChanged()



    def __addStage(self, stages, level, obj):
        if level in list(stages.keys()):
            stages[level].append(obj)
        else:
            stages.update({level:[obj]})

        return stages



    def buildNextStage(self, stages):
        # Do not add itself again if already parsed.
        if self.__parsed_stage is True:
            return stages

        need_update = self.__hasChanged()

        src_update = False
        for s in self.__sources:
            if type(s) is Task:
                # Recursively add sources to stages
                src_update |= s.buildNextStage(stages)
            elif type(s) is Token:
                src_update |= s.hasChanged()
                        
        
        self.__parsed_stage = True

        need_update |= src_update

        if len(self.__sources) == 0:
            need_update = True

        if need_update:
            levels = list(stages.keys())
            if len(levels) == 0:
                t_level = 0
            elif src_update is False:
                t_level = max(levels)
            else:
                t_level = max(levels)+1

            self.__addStage(stages, t_level, self)
            return True
        
        return False



    def buildStages(self):
        stages = {}
        self.buildNextStage(stages)
        return stages



    # Returns True if Task is a leaf. Meaning it does not depend
    # on another Task. It can still depend on various sources (ex: files) 
    def isLeaf(self):
        if all(type(s) is Token for s in self.__sources):
            return True
        return False



    def execute(self):
        if not self.__command is None:
            res = 1
            if type(self.__command) is str:
                res = self.__executeShell(self.__command)
            elif type(self.__command) is Function:
                res = self.__executeCallable(self.__command)

            if res != 0:
                return res
        
        self.__target.updateSignature()
        return 0



    def __executeShell(self, command):
        cmdlines = command.split("\n")
        cmdlines = [ln.lstrip().rstrip() for ln in cmdlines]

        for c in cmdlines:
            if c == "":
                continue
            if c[0] != "@":
                print(f"""{c}""")
            else:
                c = c[1:]
            res = os.system(c)
            if res:
                return res
        return 0



    def __executeCallable(self, command):
        func = command.function
        args = command.args
        if args is None:
            retval = func()
        else:
            args = [a.get() if type(a) is Variable else a for a in args]
            retval = func(*args)

        if command.ret is not None:
            if type(command.ret) is Variable:
                command.setRet(retval)
        return 0