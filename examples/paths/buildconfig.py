from wosit.builder import addRule


addRule(
    path = "d1",
    target = "t1.txt",
    source = "s1.txt",
    command = f"""
        cat s1.txt
        echo This is target 1. > t1.txt
    """
)


addRule(
    target = "t2.txt",
    source = "d1/t1.txt",
    command = f"""
        cat d1/t1.txt
        echo This is target 2. > t2.txt
    """
)




addRule(
    target = "all",
    source = "t2.txt"
)


addRule(
    target = "clean",
    command = f"""
        rm -rf t2.txt
        rm -rf d1/t1.txt
    """
)