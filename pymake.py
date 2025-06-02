
from Maker import *
from ArgParser import *

import argparse


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument("-l", "--list", action="store_true", help="List targets.")

    # parsed_args = parser.parse_args()


    __args = ArgParser()
    build = Maker()

    def addRule(target, source=None, command=None):
        build.addRule(target=target, source=source, command=command)

    import buildconfig

    # if parsed_args.list is True:
    #     print("Available targets:")
    #     tnames = build.listTargetNames()
    #     print("\n".join(tnames))
    # else:
    build.executeTasks(__args.getTargets(), max_process=2)
