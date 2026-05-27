#!/awips2/python/bin/python

######################################################################################################################
# Name        : compressAndSendFiles.py 
# Version     : 1.0
# Date        : 1/29/25
# Author      : Darrel Kingfield/David Tomalak/Rob Weingruber (GSL)
# Description : Wrapper to send ATOMS generated zip file to ldad@ls1:/data/ldad/ATOMS/incoming and then run the script
#               /data/ldad/ATOMS/bin/sendATOMSEmail.
######################################################################################################################

import argparse, os, sys, time

# Build argparse elements 
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", dest="folderPath", help="The folder containing file(s) to send", required=True)
parser.add_argument("-i", "--imagery", dest="imageryFlag", help="Use this flag if you are ingesting imagery", default=False, const=True, nargs="?", type=bool)
parser.add_argument("-p", "--products", dest="productFlag", help="Use this flag if you are ingesting formatted product text", default=False, const=True, nargs="?", type=bool)
args = parser.parse_args()

# Parse what the user provided
folderPath = args.folderPath
imageryFlag = args.imageryFlag
productFlag = args.productFlag

# Check that the user explicitly specified whether this was imagery or product information
if not imageryFlag and not productFlag:
    print(f"You must specify whether this folder contains imagery (-i) or products (-p). Exiting...")
    exit()

# Paths to the compressed and outgoing directories
compressedDir = os.path.join(os.sep, "data", "fxa", "ATOMS", "compressed")
outgoingDirectory = os.path.join(os.sep, "data", "ldad", "ATOMS", "incoming")

# If input path exists then send it
if os.path.exists(folderPath):
   # Split the input path into is components
   # For products
   # ['', 'data', 'fxa', 'ATOMS', 'dissemination', 'HumboldtDec2024', '20250129_210856', 'AkBcWc', "TSU"] 
   # For imagery
   # ['', 'data', 'fxa', 'ATOMS', 'dissemination', 'HumboldtDec2024', 'imagery']
   pathComps = folderPath.split(os.sep)
   if imageryFlag:
       lastIndex = -2
   else:
       lastIndex = -4
   # Create path to the zip file
   compressedFile = "{}.zip".format("_".join(pathComps[lastIndex:]))
   zipPath = os.path.join(compressedDir, compressedFile)
   # Compress the file
   os.system(f"zip -r -j {zipPath} {folderPath}/*")
   # Sleep
   time.sleep(1)
   # Send the file
   os.system(f"/usr/bin/scp {zipPath} ldad@ls1:{outgoingDirectory}")
   # Run scripts from the ls1 system
   os.system(f"ssh -t ldad@ls1 'sh /data/ldad/ATOMS/bin/sendEmail.sh {compressedFile}'")

