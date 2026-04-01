import os

from wosit.Token import Token
from wosit.Function import Variable, Function



PRINT_COLOR_CODE = "51"


class Task:
    __target = None
    __sources = None
    __command = None

    __parsed_stage = False
    __need_update = False

    __level = None


    def __init__(self, target, sources=None, command=None):
        if not type(target) in [Token, Task]:
            raise ValueError("Target must be of type \"Task or Token\".")

        if not all(type(s) in [Token, Task] for s in sources):
            raise ValueError("Sources must be of type \"Task or Token\".")


        self.__target = target
        self.__sources = sources

        self.__command = command
    

    # Returns the mtime of the target
    def getmtime(self):
        return self.__target.getmtime()


    def getName(self):
        return self.__target.get()


    def getCommand(self):
        return self.__command


    def __addStage(self, stages, level, obj):
        if level in list(stages.keys()):
            stages[level].append(obj)
        else:
            stages.update({level:[obj]})

        return stages



    def getLevel(self):
        if not self.__level is None:
            return self.__level
        
        if len(self.__sources) == 0:
            self.__level = 0
            return 0
        
        max_level = 0
        is_any_task = False
        for s in self.__sources:
            if type(s) is Task:
                is_any_task = True
                slv = s.getLevel()
                max_level = max(max_level, slv)
        
        if not is_any_task:
            self.__level = 0
            return 0
        else:
            self.__level = max_level + 1
            return max_level + 1
    


    def buildNextStage(self, stages):
        # Do not add itself again if already parsed.
        if self.__parsed_stage is True:
            return self.__need_update

        
        need_update = False

        self_time = self.getmtime()
        if self_time is None:
            need_update = True
        
        

        src_update = False
        for s in self.__sources:
            if type(s) is Task:
                # Recursively add sources to stages
                src_update |= s.buildNextStage(stages)
            elif type(s) is Token:
                source_time = s.getmtime()

                if not self_time is None:
                    if source_time is None:
                        src_update = True
                    else:
                        src_update |= (s.getmtime() > self.getmtime()) # If source newer than target
                        
        
        self.__parsed_stage = True

        need_update |= src_update

        if len(self.__sources) == 0:
            need_update = True

        self.__need_update = need_update

        if need_update:
            t_level = self.getLevel()

            self.__addStage(stages, t_level, self)
            return True
        
        return False



    def buildStages(self):
        stages = {}
        self.buildNextStage(stages)
        return stages



    def execute(self):
        if not self.__command is None:
            res = 1
            if type(self.__command) is str:
                res = self.__executeShell(self.__command)
            elif type(self.__command) is Function:
                res = self.__executeCallable(self.__command)

            if res != 0:
                return res
        
        return 0



    def __printCommand(self, text):
        print(f"\033[38;5;{PRINT_COLOR_CODE}m{text}\033[0m")


    def __executeShell(self, command):
        cmdlines = command.split("\n")
        cmdlines = [ln.lstrip().rstrip() for ln in cmdlines]

        # TODO: Add support for '\' splitting the shell commands
        for c in cmdlines:
            if c == "":
                continue
            if c[0] != "@":
                self.__printCommand(f"""{c}""")
            else:
                c = c[1:]
            res = os.system(c) # TODO: Open one shell and execute all lines of a rule into the same one.
            if res:
                return res
        return 0


    def __argsToStr(self, args):
        olst = []
        for a in args:
            if type(a) is str:
                olst.append(f"\"{a}\"")
            else:
                olst.append(str(a))
        return olst


    def __executeCallable(self, command):
        func = command.function
        args = command.args
        if args is None:
            if not command.quiet:
                self.__printCommand(f"{func.__name__}()")
            retval = func()
        else:
            args = [a.get() if type(a) is Variable else a for a in args]

            strargs = self.__argsToStr(args)
            if not command.quiet:
                self.__printCommand(f"""{func.__name__}({", ".join(strargs)})""")
            retval = func(*args)

        if command.ret is not None:
            if type(command.ret) is Variable:
                command.setRet(retval)
        return 0