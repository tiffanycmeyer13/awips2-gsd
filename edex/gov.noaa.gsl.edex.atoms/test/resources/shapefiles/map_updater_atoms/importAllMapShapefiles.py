#!/awips2/python/bin/python

####################################################################
#
# Script: importAllMapShapefiles.py
#
# Author: Darrel Kingfield (NOAA/GSL)
#
# Description: Scans the folders in the current working directory
# and imports the shapefile(s) contained within each folder into
# a new mapdata.{TABLE_NAME} database table where {TABLE_NAME} is
# the name of the folder. Multiple shapefiles will be appended
# into the same table.
#
####################################################################



import argparse
import datetime
import glob
import os
import sys
import time
import subprocess as sub

# Establish the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--restore", dest = "restoreFlag", help="Restore the cwa and zone tables", default=False, const=True, nargs="?", type=bool)

# Parse the arguments
args = parser.parse_args()

# Determine whether the cwa and zone tables are to be restored
restoreFlag = args.restoreFlag

if restoreFlag:
    tableSkipList = ["cwa", "zone"]
else:
    tableSkipList = ["NWS_Baseline_cwa", "NWS_Baseline_zone"]

if datetime.datetime.now() >= datetime.datetime(2026, 3, 3):
    shapeSkipList = ["z_18mr25.shp", "w_18mr25.shp"]
else:
    shapeSkipList = ["z_03mr26.shp", "w_03mr26.shp"]


# Verify the import script exists
curDir = os.getcwd()
importScript = os.path.join(curDir, "importSingleShapefile.py")
if not os.path.exists(importScript):
    print(f"ERROR: Could not find {importScript}")
    print("Make sure you are running this on a system with access to this script")
    exit()

# Determine if postgres is running
syscmd = '''ps -ef | grep "postgres: " | grep -v grep'''
p = sub.Popen(syscmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE)
out = p.communicate()[0].decode("utf-8")

# Start postgres if not running
killPostgres = False
if not out:
    killPostgres = True
    os.system("sudo systemctl start postgresql@awips")
    # Sleep so postgres can start fully
    time.sleep(3)

# Run script for each shapefile
shapefileDirs = sorted(glob.glob("*"))
for tableName in shapefileDirs:
    if not os.path.isdir(tableName) or tableName in tableSkipList:
        continue
    os.chdir(tableName)
    shapefilePaths = sorted(glob.glob("*.shp"))
    firstRun = True
    for shapefilePath in shapefilePaths:
        if os.path.basename(shapefilePath) in shapeSkipList:
            continue
        syscmd = f"python {importScript} -s $PWD/{shapefilePath} -t {tableName}"
        if not firstRun:
            syscmd += " -a"
        else:
            firstRun = False
        print(syscmd)
        os.system(syscmd)
    os.chdir(curDir)

# Kill postgres if this script started it up
if killPostgres:
    os.system("sudo systemctl stop postgresql@awips")
