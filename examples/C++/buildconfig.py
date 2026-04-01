# /!\ This line is mandatory /!\
from wosit.builder import addRule

import os 


APP = "myappcompiledwithmywositandanamethatiscertailnytoolooooooooonnnnnng"


SRC_DIR = "./src/"
OBJ_DIR = "./obj/"

cppfiles = os.listdir(SRC_DIR)
cppfiles = [f for f in cppfiles if f.endswith(".cpp")]

CC = "g++"


ofiles = []
for cppf in cppfiles:
    opath = OBJ_DIR + cppf.replace(".cpp", ".o")
    ofiles.append(opath)

    os.makedirs(OBJ_DIR, exist_ok=True)

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