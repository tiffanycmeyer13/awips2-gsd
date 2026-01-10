#!/awips2/python/bin/python

##############################################################
#
# Script: purgePhysicalEvent.py
#
# Date: 02/05/2023
#
# Author: Suneng Zhuo (CU/CIRES & NOAA/ESRL/GSL)
#
# Description: This script will the physical event from the DB
# and the associated message number from the registry.
#
# Use for purging physical events, like so:
#    purgePhysicalEvent.py DK_RW_20220907
#    ie: purgePhysicalEvent.py CustomID
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
  yN = input("Use this searchPattern \"{}\" and remove the physical event (and all associated with it)? (y/n)".format(customId))
  if yN != "y" and yN != "Y":
    print(f"{argv[0]} cancelled...")
    exit()

######################################
#
#
######################################

# Unfort cascade doesn't work since edex doesn't seem
# to generate ON DELETE CASCADE on the foreign keys
# properly?
syscmd = f"psql -a -c \"delete from awips.phy_event cascade where customid='{customId}'\" metadata;"
print(syscmd)
system(syscmd)

syscmd = f"./purgeMessageNumber.py {customId};"
print(syscmd)
system(syscmd)

