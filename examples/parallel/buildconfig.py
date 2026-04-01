from wosit.builder import *


from random import randint

srcs = []
for i in range(40):
    t = f"t{i}"
    srcs.append(t)
    wtime = randint(1, 3)

    addRule(
            target=t,
            command=f"""
            sleep 1
            """
    )


addRule(
    target="all",
    source=srcs,
    command="""
    echo Finished everything else!!!!
    """
)