from multiprocessing import Process, BoundedSemaphore



class ThreadPool:
    __semaphore = None
    __max_process = None

    __procs = None

    def __init__(self, max_process=1):
        self.__semaphore = BoundedSemaphore(max_process)
        self.__max_process = max_process

        self.__procs = []



    def getSemaphore(self):
        return self.__semaphore


    
    def add(self, func, args=None):
        self.__semaphore.acquire()

        p = Process(target=func, args=args)
        p.start()
        
        self.__procs.append(p)
        return p


    
    def waitAll(self):
        for p in self.__procs:
            p.join()
        self.__procs = []


    def release(self):
        self.__semaphore.release()
