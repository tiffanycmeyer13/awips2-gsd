#!/awips2/python/bin/python

##############################################################
#
# Script: purgeSeaLevelObsForSingleEvent.py
#
# Date: 12/12/2024
#
# Author: Darrel K (NOAA/GSL)
#
# Description: This script will delete all sea level observations
# from the sealevel_observations and sea_level_obs tables for a
# single user-provided physical event name. If no physical
# event name is provided, a list of possible options will be
# provided to you.
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
physicalEventIdDict = {}
for l in linesList:
    l = l.decode()
    if "phy_event_custom_id" in l: continue
    spL = l.split("|")
    if len(spL) < 2: continue
    physicalEventName = spL[0].strip()
    physicalEventNameList.append(physicalEventName)
    if physicalEventName not in physicalEventIdDict:
        physicalEventIdDict[physicalEventName] = []
    physicalEventIdDict[physicalEventName].append(spL[1].strip())

physicalEventNameList = sorted(list(set(physicalEventNameList)))

# If no rows found, throw message and quit
if not physicalEventNameList:
    print("No sea level observations to delete\nExiting...")
    exit()

# If no or incorrect physical event name provided, nudge user to retry
if len(argv) < 2 or argv[1] not in physicalEventNameList:
    print("\n=================================================")
    print("Please provide a correct physical event name to this script. Your options are: \n")
    print("\n".join(physicalEventNameList) + "\n")
    print(f"EXAMPLE: {argv[0]} {physicalEventNameList[0]}")
    print("=================================================\n")
    exit()

# Get user-provided physical event name
physicalEventName = argv[1]

# Ask user if they wish to continue
print("======================================================")
yN = input("Sea Level Observations for the following physical event will be removed:\n\n{}\n\nDo you wish to continue? (y/n)".format(physicalEventName))
if yN not in ["y", "Y"]:
    print(f"{argv[0]} cancelled...")
    exit()

# Get all ids associated with this physical event and purge only them
physicalEventSlobsIds = physicalEventIdDict[physicalEventName]

for obsId in physicalEventSlobsIds:
    syscmd = f"psql -a -c \"delete from awips.sea_level_obs where sealevel_observations_id={obsId} \" metadata;"
    print(syscmd)
    system(syscmd)

    syscmd = f"psql -a -c \"delete from awips.sealevel_observations where id={obsId} \" metadata;"
    print(syscmd)
    system(syscmd)
