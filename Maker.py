import os
import copy

import glob

import multiprocessing


from BuildHistory import *


def taskExecutor(task):
    command = task["command"]
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



def isInList(obj, lst):
    is_in = False
    for el in lst:
        if type(el) is list:
            if isInList(obj, el):
                return True
        else:
            if obj == el:
                return True
    return False





class Maker:
    tasks = None
    stages = None
    pattern_rules = None

    __build_history = None


    def __init__(self):
        self.tasks = []
        self.stages = []
        self.pattern_rules = []

        self.__build_history = BuildHistory()



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
    


    def patternMatche(lst, pattern_s, pattern_o):
        for el in lst:
            pass



    def addRule(self, target, source=None, command=None):

        if not type(target) is list:
            target = [target]
        
        if not type(source) is list:
            source = [source]


        if command is None:
            command = ""

        
        source = self.__expandPaths(source)
        target = self.__expandPaths(target)


        for t in target:
            ## Pattern rule
            if "%" in t:
                self.pattern_rules.append({"target":t, "source":source, "command":command})


            ## Normal rule
            else:
                if "%" in command or any("%" in s for s in source):
                    raise ValueError("Can't use \% placeholder in non-pattern rules.")
                
                if t in self.__getTaskTargetNameList():
                    raise ValueError(f"Target \"{t}\" already defined.")

                self.tasks.append({"target":t, "source":source, "command":command, "build":True})



    def __getTaskFromTarget(self, target, task_list=None):
        if task_list is None:
            task_list = self.tasks

        for t in task_list:
            if t["target"] is None:
                continue
            if t["target"] == target:
                return t
        return None



    def getDepsGraph(self, task):
        return self.__getDepsGraph(task)



    def __getDepsGraph(self, task, graph=None):
        if graph is None:
            graph = []

        targets_list = self.__getTaskTargetNameList()

        deptasks = []
        for src in task["source"]:
            if src is None:
                return graph

            # If file exist and target does not exist we reached the
            # lowest source file in graph so stop searching for children.
            if os.path.isfile(src) and not src in targets_list:
                return graph

            next_task = self.__getTaskFromTarget(src, self.tasks)
            deptasks.append(next_task)

            if next_task is None:
                raise ValueError(f"No rule to make source \"{src}\".")
            
            self.__getDepsGraph(next_task, graph)

        graph.append(deptasks)

        return graph



    def getDepsList(self, task):
        graph = self.__getDepsGraph(task)
        olist = []
        for stage in graph:
            for t in stage:
                olist.append(t)
        return olist
    


    def __hasAnyDeps(self, task, rlist):
        for src in task["source"]:
            for r in rlist:
                if src == r["target"]:
                    return True
        return False



    def buildStages(self, task_list=None):
        return self.__buildStages(task_list)

    def __buildStages(self, task_list=None):
        if task_list is None:
            task_list = self.tasks

        tasks = copy.deepcopy(task_list)

        stages = [[]]
        stages[0] = tasks

        modif = True
        while modif:
            modif = False

            nbstages = len(stages)
            for i in range(nbstages):
                s = stages[i]
                to_next_stage = []
                for t in s:
                    if self.__hasAnyDeps(t,s):
                        to_next_stage.append(t)
                        ##print(f"""Move {r["target"]} to stage {i+1}""")
                        modif = True
                
                if modif is True:
                    ## Remove tasks from current stage
                    stages[i] = [t for t in stages[i] if t not in to_next_stage]

                    ## Add tasks to next stage
                    if i+1 < len(stages):
                        stages[i+1] += to_next_stage
                    else:
                        stages.append(to_next_stage)

        return stages


    
    def __getTaskTargetNameList(self, task_list=None):
        if task_list is None:
            task_list = self.tasks

        lst = []
        for t in self.tasks:
            lst.append(t["target"])
        return lst
    



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



    ## Search for a matching pattern
    def __searchTargetPattern(self, src):
        for p in self.pattern_rules:
            
            patmatch = self.__matchPattern(p["target"], src)
            
            if not patmatch is None:
                target = p["target"].replace("%", patmatch)
                source = [s.replace("%", patmatch) for s in p["source"]]
                command = p["command"].replace("%", patmatch)

                return {"target":target, "source":source, "command":command, "build":True}
            
        return None



    ## Will try to resolve undefined sources by matching patterns to create tasks.
    def __resolvePatterns(self, task_list=None):
        if task_list is None:
            task_list = self.tasks

        tnamelist = self.__getTaskTargetNameList(task_list)

        modifs = True
        missing_target = False
        while modifs:
            modifs = False
            missing_pat = False
            to_add = []

            for t in task_list:
                for s in t["source"]:
                    ## Check if source task exist
                    if s not in tnamelist:
                        ## Try to match source to defined patterns.
                        pat = self.__searchTargetPattern(s)
                        if pat is None:
                            missing_target = True
                        else:
                            tnamelist.append(pat["target"])
                            to_add.append(pat)
                            modifs = True
            
            task_list += to_add

        if missing_pat is True:
            raise ValueError(f"""Could not find matching pattern to build some targets.""")
    
        return task_list
        

    def __resolveTasks(self, task_list=None):
        if task_list is None:
            task_list = self.tasks

        for t in task_list:
            target = t["target"]
            source = t["source"]
            command = t["command"]

            c = command.replace("$@", target)
            if not None in source and len(source) > 0:
                c = c.replace("$^", " ".join(source))
                c = c.replace("$<", source[0])
            
            t["command"] = c
        
        return task_list



    def graphToList(self, graph):
        olst = []
        for stage in graph:
            for el in stage:
                olst.append(el)
        return olst
    


    def __updateBuildStatus(self, task_list):
        for t in task_list:
            if all(self.__build_history.isSame(s) for s in t["source"]):
                t["build"] = False
            else:
                t["build"] = True
            

            tisfile = os.path.isfile(t["target"])
            if tisfile and (not self.__build_history.isSame(t["target"])) or t["build"] is True:
                t["build"] = True

            elif not tisfile:
                t["build"] = True
                

        return task_list



    def __graphRemoveNoBuild(self, graph):
        graph = copy.deepcopy(graph)
        ograph = []
        for stage in graph:
            ograph.append([t for t in stage if t["build"] is True])
        return ograph
    


    def __addToBuildHistory(self, task):
        if type(task) is not list:
            task = [task]

        path_lst = []
        for t in task:
            path_lst.append(t["target"])
            for s in t["source"]:
                path_lst.append(s)
        
        path_lst = list(set(path_lst))
        for path in path_lst:
            self.__build_history.addFile(path)




    def executeTasks(self, target=None, max_process=None):
        if type(target) is list:
            if len(target) == 0:
                self.executeTasks(target=None, max_process=max_process)
            else:
                for tname in target:
                    self.executeTasks(tname, max_process)
            return 0

        if target is None:
            self.executeTasks(target="all", max_process=max_process)
            return 0

        ttarg = self.__expandPaths(target)[0]
        t = self.__getTaskFromTarget(ttarg)
        if t is None:
            raise ValueError(f"No target named \"{ttarg}\" found.")
        g = self.getDepsGraph(t)
        tasks = self.graphToList(g)
        tasks.append(t)


        tasks = self.__resolvePatterns(tasks)
        tasks = self.__resolveTasks(tasks)

        self.__addToBuildHistory(tasks)
        tasks = self.__updateBuildStatus(tasks)

        stages = self.__buildStages(tasks)
        stages = self.__graphRemoveNoBuild(stages)
            
        
        targets_list = self.__getTaskTargetNameList()
        for s in stages:
            with multiprocessing.Pool(max_process) as pool:
                ret = pool.map(taskExecutor, s)
            
            # Update build history
            for i in range(len(ret)):
                if ret[i] == 0:
                    self.__build_history.updateFile(s[i]["target"])
                    #print(s[i]["target"])
                    
                    # Update source files that are not targets as well
                    for src in s[i]["source"]:
                        if os.path.isfile(src) and not src in targets_list:
                            self.__build_history.updateFile(src)
            
            self.__build_history.saveHistory()

            if any(r != 0 for r in ret):
                raise ValueError("\nAt least one task returned an exception.")
        
        ##print("Done!")



    def listTargetNames(self):
        olst = [t["target"] for t in self.tasks]
        olst += [p["target"] for p in self.pattern_rules]
        return olst
    

    def printTargetNames(self):
        lst = self.listTargetNames()
        for t in lst:
            print(t)
