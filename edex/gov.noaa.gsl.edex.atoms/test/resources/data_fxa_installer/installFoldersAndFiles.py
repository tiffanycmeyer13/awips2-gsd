#!/awips2/python/bin/python

import os

baseDir = os.path.join(os.sep, "data", "fxa", "ATOMS")

for subDir in ["compressed", "dissemination", "scripts"]:
    tmpPath = os.path.join(baseDir, subDir)
    if not os.path.exists(tmpPath):
        print(f"Creating {tmpPath}...")
        os.makedirs(tmpPath, exist_ok=True)
        os.chmod(tmpPath, 0o755)

scriptsPath = os.path.join(baseDir, "scripts")
os.system(f"cp -v compressAndSendFiles.py  {scriptsPath}")
