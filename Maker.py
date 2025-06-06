import os
import glob
import json


from Token import *
from Task import *
from Function import *

from ProcessPool import *

class Maker:
    __patterns = None
    __rules = None

    __signatures = None


    def __init__(self):
        self.__rules = []
        self.__patterns = []


    def __expandPaths(self, paths):
        if type(paths) is not list:
            paths = [paths]

        ## Expand user and environment variables when possible
        paths = [os.path.expanduser(os.path.expandvars(p)) for p in paths if p is not None]

        ## Treat wildcards
        tp = []
        for p in paths:
            gp = glob.glob(p)
            if len(gp) == 0:
                tp.append(p)
            else:
                tp += gp
        paths = tp

        return paths



    def addRule(self, target, source=None, command=None):
        if not type(target) is list:
            target = [target]
        
        if not type(source) is list:
            source = [source]


        if command is None:
            command = ""

        
        source = self.__expandPaths(source)
        target = self.__expandPaths(target)


        target = [t for t in target]
        source = [s for s in source]


        for t in target:
            if "%" in t:
                patterns_list = self.__getTargetsList(self.__patterns)
                if t in patterns_list:
                    raise ValueError(f"Pattern \"{t}\" is already defined.")
                self.__patterns.append({"pattern":t, "sources":source, "command":command})

            else:
                if type(command) is str:
                    if "%" in command:
                        raise ValueError("Can't use % placeholder in non-pattern rules.")
        
                if any("%" in s for s in source):
                        raise ValueError("Can't use % placeholder in non-pattern rules.")
                
                targets_list = self.__getTargetsList(self.__rules)
                if t in targets_list:
                    raise ValueError(f"Rule \"{t}\" is already defined.")
                

                if type(command) is Function:
                    # Add variables to source
                    if not command.args is None:
                        source += [a for a in command.args if type(a) is Variable]

                rule = self.__resolveSymbols({"target":t, "sources":source, "command":command})
                self.__rules.append(rule)





    def __getTargetsList(self, rlist=None):
        if rlist is None:
            rlist = self.__rules

        lst = [r["target"] for r in rlist]
        return lst
    


    def getTargetsList(self):
        return self.__getTargetsList()
    


    def __resolveSymbols(self, rule):
        target = rule["target"]
        sources = rule["sources"]
        command = rule["command"]

        if not type(command) is str:
            return rule

        c = command.replace("$@", target)
        if not None in sources and len(sources) > 0:
            c = c.replace("$^", " ".join(sources))
            c = c.replace("$<", sources[0])
        
        rule["command"] = c
        return rule



    ## Walk through the given pattern and string to check if they match.
    ## If match there is, the placeholder substring is returned.
    ## Otherwise None is returned.
    def __matchPattern(self, pattern, str):
        id_p = 0
        id_s = 0

        found_placeholders = []

        hit_placeholder = False
        placeholder = ""
        while id_p < len(pattern) and id_s < len(str):
            cp = pattern[id_p]
            cs = str[id_s]

            if cp == "%":
                hit_placeholder = True
                placeholder += cs
                id_p += 1
                id_s += 1
                
            elif cp != cs and hit_placeholder is False:
                return None

            elif hit_placeholder is True:
                if cp == cs:
                    hit_placeholder = False
                    found_placeholders.append(placeholder)
                    placeholder = ""
                    id_p += 1                
                else:
                    placeholder += cs
                id_s += 1

            else:
                id_p += 1
                id_s += 1
        
            ## Avoid going over pattern length when '%' char is at end of pattern.
            if id_p >= len(pattern):
                id_p = len(pattern) - 1
        

        ## If reached end of string and still searching for placeholder
        if hit_placeholder is True:
            found_placeholders.append(placeholder)

        ## All placeholders found are not the same.
        if len(set(found_placeholders)) != 1:
            return None        

        ## If there is a match, 
        if len(found_placeholders) > 0:
            return found_placeholders[0]
        else:
            return None
        


    # Returns a matching pattern to the given name, None if not match could be found.
    def __searchPattern(self, name):
        for p in self.__patterns:
            patmatch = self.__matchPattern(p["pattern"], name)
            
            if not patmatch is None:
                otarget = p["pattern"].replace("%", patmatch)
                osources = [s.replace("%", patmatch) for s in p["sources"]]
                if type(p["command"]) is str:
                    ocommand = p["command"].replace("%", patmatch)
                else:
                    ocommand = p["command"]
                return {"target":otarget, "sources":osources, "command":ocommand}
            
        return None
    


    # Returns the rule with the same name or None if it could
    # not be found and could not be constructed from a pattern.
    def __getRule(self, name): # TODO: Need to compare paths and not strings!!!!! (ex: ./obj/test.o should be equal to obj/test.o)
        for r in self.__rules:
            if name == r["target"]:
                return r

        match = self.__searchPattern(name)
        if match is None:
            return None
        
        rule = self.__resolveSymbols(match)
        return rule




    def __buildTaskGraph(self, name):
        rule = self.__getRule(name)
        if rule is None:
            if not type(name) is Variable:
                if not os.path.isfile(name):
                    raise ValueError(f"Could not find rule or dependency \"{name}\".")
            return Token(name, signatures=self.__signatures)
        
        srclist = []
        for srcname in rule["sources"]:
            src = self.__buildTaskGraph(srcname)
            srclist.append(src)
        
        return Task(target=Token(rule["target"], signatures=self.__signatures), sources=srclist, command=rule["command"])

            

    def __saveSignatures(self, signatures):
        json.dump(signatures, open(".build_history", "w"), indent=2)


    def __loadSignatures(self):
        if os.path.isfile(".build_history"):
            try:
                return json.load(open(".build_history", "r"))
            except:
                pass
        return {}
    


    # Dummy function to call in a multiprocessing Pool
    def _taskExecute(self, task):
        return task.execute()



    def execute(self, name=None, max_process=1):
        if type(name) is list:
            if len(name) > 0:
                for n in name:
                    self.execute(n, max_process)
                return
            else:
                self.execute(None, max_process)
                return

        if name is None:
            name = "all"

        self.__signatures = self.__loadSignatures()

        # Chain rules in a dependcy graph
        taskgraph = self.__buildTaskGraph(name)
        # Retrieve execution stages based on dependency and need for update
        stages = taskgraph.buildStages()

        stage_levels = list(stages.keys())
        if len(stage_levels) == 0:
            return
        max_level = max(stage_levels)

        # Execute every stage element
        with ProcessPool(max_process) as p:
            res = None
            for i in range(max_level+1):
                stage = stages[i]
                res = p.map(self._taskExecute, stage)

                if any(r != 0 for r in res):
                    raise RuntimeError("The execution of a task failed.")


        # Update signatures
        new_signatures = taskgraph.getAllSignatures()
        new_signatures.update(self.__signatures)
        self.__saveSignatures(new_signatures)
