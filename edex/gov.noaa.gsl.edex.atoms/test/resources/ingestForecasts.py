#!/awips2/python/bin/python

import os
import time
import glob

manualEndpoint = "/awips2/edex/data/manual"

paths = [r'./otherTfsTestData/tfsFcst*.xml', r'./threatDBTestData/tfsFcst*.xml']

for path in paths:
    ingestFiles = glob.glob(path)
    for f in ingestFiles:
        syscmd = f"cp {f} {manualEndpoint}"
        print(syscmd)
        os.system(syscmd)
        time.sleep(0.25)
