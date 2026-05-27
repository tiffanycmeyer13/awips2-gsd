#!/awips2/python/bin/python

import os
import time
import glob

logsDir = "/awips2/edex/logs/*"

syscmd = f"grep TsunamiForecastDecoder {logsDir} | grep ERROR"
print(syscmd)
os.system(syscmd)
syscmd = f"grep TsunamiForecastEdexDao {logsDir} | grep ERROR"
print(syscmd)
os.system(syscmd)
