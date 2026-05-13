
from multiprocessing.pool import ThreadPool


def _runprocess(func, args):
    retval = func(*args)
    return retval



class ProcessPool():

    def __init__(self, processes=1):
        if processes < 1:
            raise ValueError("Argument \"processes\" must be equal or higher than 1.")
        self.__nb_processes = processes



    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    #     for p, q in self.__procs:
    #         if hasattr(p, 'kill'):
    #             p.kill()  # Use kill if available (Python >= 3.7)
    #         else:
    #             p.terminate()  # Fallback to terminate for Python 3.6 compatibility


    def map(self, func, args_iter):

        args = [(func, (arg,)) for arg in args_iter]

        retvalues = None
        with ThreadPool(self.__nb_processes) as p:
            retvalues = p.starmap(func=_runprocess, iterable=args)

        return retvalues