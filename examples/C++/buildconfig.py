# /!\ This line is mandatory /!\
from pymake import *

from pathutils import *



APP = "myappcompiledwithmypymakeandanamethatiscertailnytoolooooooooonnnnnng"


SRC_DIR = "./src/"
OBJ_DIR = "./obj/"

cppfiles = listFiles(SRC_DIR + "/*.cpp")

CC = "g++"


ofiles = []
for cppf in cppfiles:
    opath = OBJ_DIR + cppf.replace(".cpp", ".o")
    ofiles.append(opath)

    addRule(
        target = opath,
        source = SRC_DIR+cppf,
        command = f"""
        {CC} -c {SRC_DIR}/{cppf} -o {opath}
        """
    )


addRule(
    target="all",
    source=APP
)


addRule(
    target=APP,
    source=ofiles,
    command=f"""
    {CC} {" ".join(ofiles)} -o {APP}
    """
)


addRule(
    target="run",
    source=APP,
    command=f"""
    ./{APP}
    """
)




addRule(
    target="clean",
    command=f"""
    rm -rf {OBJ_DIR}/*
    rm -rf {APP}
    """
)