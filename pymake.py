
from Maker import *
from Function import *
from ArgParser import *

import argparse
import os

import importlib.util
import sys



def importModule(path):
    name = os.path.basename(path).split(".py")[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)



def main():
    #print(f"Name is: {__name__}")
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-l", "--list", action="store_true", help="List targets.")

    # parsed_args = parser.parse_args()


    __args = ArgParser()
    global build
    build = Maker()

    global addRule
    def addRule(target, source=None, command=None):
        build.addRule(target=target, source=source, command=command)

    importModule(os.path.join(os.getcwd(), "buildconfig.py"))

    # if parsed_args.list is True:
    #     print("Available targets:")
    #     tnames = build.listTargetNames()
    #     print("\n".join(tnames))
    # else:
    build.execute(__args.getTargets(), max_process=4)


if __name__ == "__main__":
    main()
