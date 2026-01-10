#!/awips2/python/bin/python

##############################################################
#
# Script: purgeAllPhysicalEvents.py
#
# Date: 02/05/2023
#
# Author: Rob W
#
# Description: This script will delete all PhysicalEvents
# and related stuff from the atoms database tables,
# and message numbers, but will not purge the registry.
#
##############################################################

from sys import argv
from os import system
import subprocess as sub


# Unfort cascade doesn't work since edex doesn't seem
# to generate ON DELETE CASCADE on the foreign keys
# properly? And so we're just deleting all of them.

tablesToDelete = ["seismic_event_data", "addl_seismic_event_data", "landslide_event_data",
                  "phy_event", "physicaleventdata", "sea_level_obs", "sealevel_observations",
                  "tfs_imagery", "tsunami_station_fcst", "tsunami_fcst", "unknown_event_data",
                  "volcanic_event_data"]

for tableName in tablesToDelete:
    syscmd = f"psql -a -c \"delete from awips.{tableName} cascade \" metadata;"
    print(syscmd)
    system(syscmd)

syscmd = f"./purgeAllMessageNumbers.py;"
print(syscmd)
system(syscmd)


