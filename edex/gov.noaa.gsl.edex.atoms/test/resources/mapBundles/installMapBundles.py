#!/awips2/python/bin/python

import argparse
import os
import glob
import sys

caveStaticRoot = "/awips2/edex/data/utility/cave_static/site"

# Build parser and get user-specified input(s)
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--delete", dest = "deleteFiles", help="Delete files before copying in new ones", default=False, const=True, nargs="?", type=bool)
args = parser.parse_args()
deleteFlag = args.deleteFiles

for twc in ["NTWC", "PTWC"]:
    # Copy in the updated mapStyle
    mapStyleDir = os.path.join(caveStaticRoot, twc, "mapStyles")
    if not os.path.exists(mapStyleDir):
        os.system(f"mkdir -p {mapStyleDir}")
    elif deleteFlag:
        os.system(f"rm -rvf {mapStyleDir}/mapstylepreferences.xml")
    os.system(f"cp -vp mapStyles/mapstylepreferences.xml {mapStyleDir}")

    # Copy in the updated bundle files
    bundleDir = os.path.join(caveStaticRoot, twc, "bundles", "maps")
    if not os.path.exists(bundleDir):
        os.system(f"mkdir -p {bundleDir}")
    elif deleteFlag:
        os.system(f"rm -rvf {bundleDir}/*")
    os.system(f"cp -Rvp bundles/maps/* {bundleDir}")
