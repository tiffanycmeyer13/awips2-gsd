#!/awips2/python/bin/python

##############################################################
#
# Script: purgeAllMessageNumbers.py
#
# Date: 12/17/2024
#
# Author: Suneng Zhuo/Darrel Kingfield (CU/CIRES & NOAA/ESRL/GSL)
#
# Description: This script will remove all message number
# registry objects from the ebxml tables that have an Id
# matching those in in List below.
#
##############################################################

import os
from sys import argv
from glob import glob
import subprocess as sub
import xml.etree.ElementTree as ET

# Check if any records exist with the pattern ATOMS_Message_%
syscmd = f"psql -a -c \"select lid from ebxml.registryobject where lid like 'ATOMS_Message_%'\" metadata;"
p = sub.Popen(syscmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE)
out,err = p.communicate()
out = out.decode()
rowString = out.split("----\n")[-1].split("\n")[0]
# If no records found, skip to next event
if "0 rows" in rowString:
    print("No message number objects to delete...exiting.")
    exit()

# Get all of the records for this event (e.g., ['Humboldt.2024Dec_AkBcWc'])
resultsList = out.split("\n")[3:-3]
nameList = [xx.strip() for xx in resultsList]

# Get values to purge from the slot table
for lid in nameList:
    syscmd = f"psql -a -c \"select value_id from ebxml.slot where parent_id='{lid}'\" metadata;"
    p = sub.Popen(syscmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE)
    out,err = p.communicate()
    out = out.decode()
    out = out.split("\n")[3:-3]
    valueIdList = [xx.strip() for xx in out]

    # Delete lid from slot table
    syscmd = f"psql -U awips -a -c \"delete from ebxml.slot where parent_id = '{lid}'\" metadata;"
    print(syscmd)
    os.system(syscmd)

    # Delete all rows from the id column in the value table
    for valueId in valueIdList:
        syscmd = f"psql -U awips -a -c \"delete from ebxml.value where id = '{valueId}'\" metadata;"
        print(syscmd)
        os.system(syscmd)

    # Delete lid from registryobject table
    syscmd = f"psql -U awips -a -c \"delete from ebxml.registryobject where lid = '{lid}'\" metadata;"
    print(syscmd)
    os.system(syscmd)
