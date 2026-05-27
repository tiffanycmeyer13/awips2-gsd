#!/awips2/python/bin/python

import os
import time
import glob

logsDir = "/awips2/edex/logs/*"

syscmd = f"grep TfsImageryDecoder {logsDir} | grep ERROR"
print(syscmd)
os.system(syscmd)
syscmd = f"grep TfsImageryEdexDao {logsDir} | grep ERROR"
print(syscmd)
os.system(syscmd)
