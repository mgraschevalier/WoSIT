import os
import glob




def getBasename(path):
    if type(path) is list:
        return [getBasename(p) for p in path]
    
    return os.path.basename(path)



## Returns a list of filenames without their path.
## Accepts wildcard syntax.
def listFiles(path):
    flist = glob.glob(path)

    return getBasename(flist)