import os

from pymake.Function import *


class Token:
    __object = None
    __type = None


    def __init__(self, object):
        self.__object = object

        if type(object) is str:
            if os.path.isfile(object):
                self.__type = "file"
        else:
            self.__type = None



    def get(self):
        return self.__object
    
    def set(self, object):
        self.__object = object

    

    def __getmtime(self, obj):
        if type(obj) is Variable:
            return None
        if not os.path.isfile(obj):
            return None
        
        return os.path.getmtime(obj)
        

    def getmtime(self):
        return self.__getmtime(self.__object)