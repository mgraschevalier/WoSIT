import os
import json

from hashlib import sha1


class BuildHistory:
    __files = None
    __history_path = None



    def __init__(self, history_path=None):
        self.__files = {}

        if history_path is None:
            history_path = ".build_history"
        
        self.__history_path = history_path

        self.__loadHistory()


    
    def __loadHistory(self):
        if os.path.isfile(self.__history_path):
            self.__files = json.load(open(self.__history_path, "r"))



    def saveHistory(self, history_path=None):
        if history_path is None:
            history_path = self.__history_path
        json.dump(self.__files, open(history_path, "w"), indent=2)



    def computeTag(self, path):
        if not os.path.isfile(path):
            # if path in list(self.__files.keys()):
            #     del self.__files[path]
            return None
        
        tag = None
        with open(path, "rb") as f:
            data = f.read()
            tag = sha1(data).hexdigest()
        return tag

    

    def addFile(self, path):
        if type(path) is list:
            for p in path:
                self.addFile(p)
            return
        
        # if not os.path.isfile(path):
        #     return
            ##raise ValueError(f"File \"{path}\" does not exist.")
        
        if path in list(self.__files.keys()):
            return
        
        tag = None
        self.__files.update({path:tag})


    
    def updateFile(self, path):
        if type(path) is list:
            for p in path:
                self.updateFile(p)
            return

        if not path in list(self.__files.keys()):
            return
            ##raise ValueError(f"File \"{path}\" not found in build history.")

        tag = self.computeTag(path)
        self.__files[path] = tag



    def cleanHistory(self):
        to_remove = []
        for path, tag in self.__files.items():
            if not os.path.isfile(path):
                to_remove.append(path)

        for path in to_remove:
            del self.__files[path]



    def getChangedFiles(self):
        olst = []
        for path, tag in self.__files.items():
            new_tag = self.computeTag(path)
            if tag != new_tag and tag is not None and new_tag is not None:
                olst.append(path)
        return olst
    

    
    ## Returns True if specified file's content did not change.
    ## Returns False if file's content changed or file is not tracked.
    def isSame(self, path):
        if path in (self.__files.keys()):
            tag = self.__files[path]
            ntag = self.computeTag(path)
            if tag == ntag and tag is not None and ntag is not None:
                return True
        return False
