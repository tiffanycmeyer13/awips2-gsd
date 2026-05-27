#!/awips2/python/bin/python

import os
import time
import glob

logsDir = "/awips2/edex/logs/*"

syscmd = f"grep TfsPhysicalEventDecoder {logsDir} | grep ERROR"
print(syscmd)
os.system(syscmd)
syscmd = f"grep PhysicalEventEdexDao {logsDir} | grep ERROR"
print(syscmd)
os.system(syscmd)
