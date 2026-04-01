
from multiprocessing import Process, Semaphore, JoinableQueue


def _runprocess(semaphore, q, func, args):
    retval = func(*args)
    q.put(retval)
    q.task_done()
    semaphore.release()


class ProcessPool():
    __procs = None
    __semaphore = None


    def __init__(self, processes=1):
        if processes < 1:
            raise ValueError("Argument \"processes\" must be equal or higher than 1.")
        self.__semaphore = Semaphore(processes)



    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for p, q in self.__procs:
            p.kill()



    def map(self, func, args_iter):
        self.__procs = []

        ## Start every process
        for arg in args_iter:
            self.__semaphore.acquire()
            q = JoinableQueue()
            p = Process(target=_runprocess, args=(self.__semaphore, q, func, (arg,)))
            p.start()
            self.__procs.append((p,q))


        ## Wait for processes to finish and retrieve returned values.
        retvalues = []
        for p,q in self.__procs:
            p.join()
            q.join()
            if not q.empty():
                retvalues.append(q.get())
            else:
                retvalues.append(None)

        return retvalues