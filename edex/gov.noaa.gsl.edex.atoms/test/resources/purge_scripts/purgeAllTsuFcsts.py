#!/awips2/python/bin/python

##############################################################
#
# Script: purgeAllTsuFcsts.py
#
# Date: 12/12/2024
#
# Author: Rob W / Darrel K (NOAA/GSL & CU/CIRES)
#
# Description: This script will delete all Tsunami Forecasts
# from the tsunami_fcst and tsunami_station_fcst tables.
#
##############################################################

from sys import argv
from os import system
import subprocess as sub


# Query the awips.tsunami_fcst table to get all physical event names and ids that have forecasts
syscmd = "psql -a -c \"select phy_event_custom_id,id from awips.tsunami_fcst\" metadata;"
p = sub.Popen(syscmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE)
resultOutput, resultError = p.communicate()

# Parse out the lines from the query result to extract out the physical event names and forecast ids
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
    print("No tsunami forecasts to delete\nExiting...")
    exit()

# Ask user if they wish to continue
print("======================================================")
yN = input("Forecasts for the following physical events will be removed:\n\n{}\n\nDo you wish to continue? (y/n)".format("\n".join(physicalEventNameList)))
if yN not in ["y", "Y"]:
    print(f"{argv[0]} cancelled...")
    exit()

# Purge
for forecastId in physicalEventIdList:
    syscmd = f"psql -a -c \"delete from awips.tsunami_station_fcst where tsunami_fcst_id={forecastId} \" metadata;"
    print(syscmd)
    system(syscmd)

    syscmd = f"psql -a -c \"delete from awips.tsunami_fcst where id={forecastId} \" metadata;"
    print(syscmd)
    system(syscmd)
