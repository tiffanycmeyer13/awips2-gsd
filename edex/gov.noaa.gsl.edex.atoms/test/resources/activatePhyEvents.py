#!/awips2/python/bin/python

##############################################################
#
# Script: activatePhyEvents.py
#
# Author: Rob Weingruber
#
# Description: This script will set active=false or true 
# for one or all physical events in the DB
#
# Use like so:
#    activatePhyEvents.py False phyEventId
#    activatePhyEvents.py True
#  where phyEventId is optional. If omitted, all events affected.
#
##############################################################

from sys import argv
from os import system
import subprocess as sub

######################################
# The pattern to search for
######################################

if len(argv) <= 1:
    print("Usage: activatePhyEvents.py FalseOrTrue phyEventId")
    print("where phyEventId is optional and can be a pattern.")
    print("Example: activatePhyEvents.py False Alaska.Cat5")
    print("Example: activatePhyEvents.py True %DBRegion_%")
    exit()

isActive = argv[1]

customId = None
if len(argv) > 2:
  customId = argv[2]

######################################
#
#
######################################

if customId:
  syscmd = f"psql -a -c \"update awips.phy_event set isactive = '{isActive}' where customid like '{customId}'\" metadata;"
else:
  syscmd = f"psql -a -c \"update awips.phy_event set isactive = '{isActive}'\" metadata;"

print(syscmd)
system(syscmd)
