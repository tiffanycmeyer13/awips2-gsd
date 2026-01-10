#!/awips2/python/bin/python

##############################################################
#
# Script: purgeAllSeaLevelObs.py
#
# Date: 12/12/2024
#
# Author: Darrel K (NOAA/GSL)
#
# Description: This script will delete all sea level observations
# from the sealevel_observations and sea_level_obs tables.
#
##############################################################

from sys import argv
from os import system
import subprocess as sub


# Query the ebxml.registryobject table
syscmd = "psql -a -c \"select phy_event_custom_id,id from awips.sealevel_observations\" metadata;"
p = sub.Popen(syscmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE)
resultOutput, resultError = p.communicate()

# Parse out the lines from the query result
linesList = resultOutput.split(b"\n")
physicalEventNameList = []
physicalEventIdList = []
for l in linesList:
    l = l.decode()
    if "phy_event_custom_id" in l: continue
    spL = l.split("|")
    if len(spL) < 2: continue
    physicalEventNameList.append(spL[0].strip())
    physicalEventIdList.append(spL[1].strip())

physicalEventNameList = sorted(list(set(physicalEventNameList)))

# If no rows found, throw message and quit
if not physicalEventNameList:
    print("No sea level observations to delete\nExiting...")
    exit()

# Ask user if they wish to continue
print("======================================================")
yN = input("Sea Level Observations for the following physical events will be removed:\n\n{}\n\nDo you wish to continue? (y/n)".format("\n".join(physicalEventNameList)))
if yN not in ["y", "Y"]:
    print(f"{argv[0]} cancelled...")
    exit()

for obsId in physicalEventIdList:
    syscmd = f"psql -a -c \"delete from awips.sea_level_obs where sealevel_observations_id={obsId} \" metadata;"
    print(syscmd)
    system(syscmd)

    syscmd = f"psql -a -c \"delete from awips.sealevel_observations where id={obsId} \" metadata;"
    print(syscmd)
    system(syscmd)
