from multiprocessing import Pool


class FuncTask:
    args = None
    func = None

    def __init__(self, func, args=None):
        self.func = func
        self.args = args


    def __call__(self):
        return self.func(*self.args)


def taskExecutor(functask):
    print(callable(functask))
    return functask()



def f1(a, b):
    return a+b


def f2(a, b):
    return a*b




if __name__ == "__main__":
    print(taskExecutor(FuncTask(f1, (1,2))))