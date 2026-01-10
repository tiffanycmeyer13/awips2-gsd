#!/awips2/python/bin/python

##############################################################
#
# Script: purgeMessageNumber.py
#
# Date: 02/05/2023
#
# Author: Suneng Zhuo (CU/CIRES & NOAA/ESRL/GSL)
#
# Description: This script will remove all registry objects
# from the ebxml tables that have an Id matching the given
# searchPattern (customId of the physical event). In other
# words, all registry message numbers associated with the
# supplied physical event custom id will be removed, for
# all product regions.
#
# Use for purging message numbers, like so:
#    purgeMessageNumber.py DK_RW_20220907
#    ie: purgeMessageNumber.py CustomID
#
# This will remove DK_RW_20220907_AkBcWc, DK_RW_20220907_EcGc,
# etc
#
#
##############################################################

from sys import argv
from os import system
import subprocess as sub

######################################
# The pattern to search for
######################################

if len(argv) > 1:
  customId = argv[1]
  # Ask user if they wish to continue
  yN = input(f"Use this searchPattern \"ATOMS_Message_{customId}\" and remove from slot and registryobject? (y/n)")
  if yN != "y" and yN != "Y":
    print(f"{argv[0]} cancelled...")
    exit()
else:
    print("Please provide a physical event ID (e.g., HumboldtDec2024)")
    print("Exiting...")
    exit()

######################################
# Search for all registry objects that
# match the searchPattern above
######################################

# Check if any records exist with the pattern ATOMS_Message_%
syscmd = f"psql -a -c \"select lid from ebxml.registryobject where lid like 'ATOMS_Message_{customId}%'\" metadata;"
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
