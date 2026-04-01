from multiprocessing import Queue


class Variable:
    __value = None
    __queue = None

    def __init__(self, init_value=None):
        self.__queue = Queue(maxsize=1)
        if not init_value is None:
            self.__value = init_value
            self.__queue.put(init_value)


    def get(self):
        if not self.__queue.empty():
            self.__value = self.__queue.get()
        return self.__value
    

    def set(self, value):
        if not self.__queue.empty():
            self.__queue.get()
        self.__queue.put(value)



class Function:
    function = None
    args = None
    ret = None
    quiet = False

    def __init__(self, function, args=None, ret=None, quiet=False):
        self.function = function

        if args is not None:
            if type(args) is not tuple:
                raise ValueError("Arguments must be passed as a tuple.")
        self.args = args

        if not ret is None:
            if not type(ret) is Variable:
                raise ValueError("Return argument \"ret\" must be of type \"Variable\".")
            self.ret = ret

        self.quiet = quiet


    def getFunction(self):
        return self.function
    

    def getArgs(self):
        return self.args
    
    def setRet(self, retvalue):
        self.ret.set(retvalue)