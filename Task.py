import os

from Token import *


from ThreadPool import *



class Task:
    __target = None
    __sources = None
    __command = None

    __parsed = False
    __parsed_signature = False

    __parsed_stage= False


    def __init__(self, target, sources=None, command=None):
        if not type(target) in [Token, Task]:
            raise ValueError("Must be of type \"Task or Token\".")

        if not all(type(s) in [Token, Task] for s in sources):
            raise ValueError("Must be of type \"Task or Token\".")


        self.__target = target
        self.__sources = sources

        self.__command = command



    def getSignature(self):
        return self.__target.getSignature()


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




    # TODO: NEED TO CHECK FOR CHANGES ETC TO UPDATE STAGES
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



    # Call the update() method of all sources, then
    # updates itself and return 'True' or return 'False' if no
    # changes applied.
    def update(self, pool=None):
        # No need to search deeper for updates if task already parsed,
        # as all dependencies have already been parsed too.
        if self.__parsed is True:
            return True
        
        # Call update process on all sources
        update_results = []
        for s in self.__sources:
            res = s.update(pool=pool)
            update_results.append(res)

        if not pool is None:
            if len(self.__sources) > 0 and any(r is True for r in update_results):
                pool.waitAll()

        # Set flag to signal this task and all its sources have already
        # been parsed for changes and executed as needed.
        self.__parsed = True


        # If some source updated or target changed, execute
        if self.__target.hasChanged() or (len(self.__sources) > 0 and any(r is True for r in update_results)):
            if pool is None:
                self.__execute(self.__command)
            else:
                pool.add(self.__execute, (self.__command, pool))
            
            return True
        return False



    def execute(self):
        return self.__executeShell(self.__command)



    def __execute(self, command, pool=None):
        res = self.__executeShell(command)
        if res != 0:
            return res
        self.__target.updateSignature()

        if not pool is None:
            pool.release()

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
