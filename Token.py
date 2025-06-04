import os

from hashlib import sha1



class Token:
    __object = None
    __type = None

    __is_valid = False

    __signature = None

    def __init__(self, object, signatures=None):
        self.__object = object

        if type(object) is str:
            if os.path.isfile(object):
                self.__type = "file"
        else:
            self.__type = None

        if not signatures is None:
            if self.__object in list(signatures.keys()):
                self.__signature = signatures[self.__object]



    def get(self):
        return self.__object
    
    def set(self, object):
        self.__object = object



    def __computeSignature(self, path):
        if not os.path.isfile(path):
            return None
        
        signature = None
        with open(path, "rb") as f:
            data = f.read()
            signature = sha1(data).hexdigest()
        return signature
    


    def hasChanged(self):
        newsig = self.__computeSignature(self.__object)
        if newsig is None or self.__signature is None:
            return True
        
        elif newsig != self.__signature:
            return True
        
        else:
            return False



    def getSignature(self):
        if self.__signature is None:
            self.updateSignature()
        return self.__signature



    def updateSignature(self):
        self.__signature = self.__computeSignature(self.__object)



    def getAllSignatures(self, signatures=None):
        if self.__signature is None:
            self.__signature = self.getSignature()

        return {self.__object:self.__signature}
    
    

    def update(self, pool=None):
        if self.hasChanged():
            return True
        return False