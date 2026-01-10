# *** Override behavior of AtomsDisseminationUtilities.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Contains methods to support dissemination of
    products through an external medium

    @since: April 2025
    @author: GSL Hazard Services Team
'''

import os
import TimeUtil


class AtomsDisseminationUtilities(object):

    def getMessageShipmentScript(self):
        '''
        @summary: Path that will compress the formatter text file folder and ship it to the ls1
        system
        @return: String
        '''
        return os.path.join(os.sep, "data", "fxa", "ATOMS", "scripts", "compressAndSendFiles.py")

    def writeAtomsProductFiles(self):
        '''
        @summary: Configurable method to determine if a user wishes to write
        all product text output to a directory under the self.atomsDisseminationRootPath()
        @return: True if you wish to write files; False if you wish to not write files
        '''
        return True

    def atomsDisseminationRootPath(self):
        '''
        @summary: The root path to store the text products produced from
        within the AWIPS Tsunami Operations Messaging Service (ATOMS)
        @return: String
        '''
        return os.path.join(os.sep, "data", "fxa", "ATOMS", "dissemination")
        # return os.path.join(os.sep, "tmp", "ATOMS", "dissemination")

    def getAtomsDisseminationFilePath(self, productDict):
        '''
        @summary: Get the path(s) to write a single suite of products
        issued from the AWIPS Tsunami Operations Messaging Service (ATOMS)
        @param productDict: The product-level dictionary
        @return: String
        '''
        storagePath = self.atomsDisseminationRootPath()
        physicalEventName = productDict.get("customId")
        if physicalEventName:
            storagePath = os.path.join(storagePath, physicalEventName)
        issueTimeString = TimeUtil.epochTimeMillisToDatetime(productDict.get("issueTime")).strftime("%Y%m%d-%H%M%S")
        if issueTimeString:
            storagePath = os.path.join(storagePath, issueTimeString)
        productRegion = productDict.get("productRegion")
        if productRegion:
            storagePath = os.path.join(storagePath, productRegion)
        productCategory = productDict.get("productCategory")
        if productCategory:
            storagePath = os.path.join(storagePath, productCategory)
        return storagePath

    def buildDirectory(self, storagePath, defaultPermissions=0o755):
        '''
        @summary: Build a directory within the AWIPS system
        @param storagePath: The directory path where file(s) will be stored
        @param defaultPermissions: The default permissions to supply to the folder
        @return: Boolean as to whether the building was good or not
        '''
        success = True
        if not os.path.exists(storagePath):
            try:
                os.makedirs(storagePath, exist_ok=True)
                os.chmod(storagePath, defaultPermissions)
                success = True
                print(f"SUCCESS: Created the storage directory: {storagePath}")
            except:
                success = False
        return success

    def writeAtomsFile(self, productDict, textProductList, formatterName):
        '''
        @summary: Write the ATOMS file to the storage path
        @param productDict: The product-level dictionary
        @param textProductList: A list of text products to write
        @param formatterName: The name of the formatter
        @return: None
        '''
        if self.writeAtomsProductFiles():
            storagePath = self.getAtomsDisseminationFilePath(productDict)
            directoryBuilt = self.buildDirectory(storagePath)
            if directoryBuilt:
                productNumber = 1
                for textOutput in textProductList:
                    fileName = f"{formatterName}_{productNumber}.txt"
                    try:
                        outPath = os.path.join(storagePath, fileName)
                        w = open(outPath, "w")
                        w.write(textOutput)
                        w.close()
                        print(f"SUCCESS: Created the ATOMS product file: {outPath}")
                        productNumber += 1
                    except:
                        print(f"ERROR: Could not store the ATOMS file: {outPath}")
                        print(f"File Text: {textOutput}")
            else:
                print(f"ERROR: Could not create the ATOMS storage directory: {storagePath}")

    def getEventMapsJsonRootPath(self):
        '''
        @summary: The root path to store the maps including energy, polygon and travel time, and
        json file
        @return: String
        '''
        return "https://www.tsunami.gov/"

    def getEventMapsJsonUri(self, productDict):
        '''
        @summary: Get the path(s) to post json and maps related with this physical event
        @param productDict: The product-level dictionary
        @return: String
        '''
        rootPath = self.getEventMapsJsonRootPath()
        physicalEventName = productDict.get("customId")
        officeID = productDict.get("officeId")
        wmoID = productDict.get("wmoID")
        messageNumber = str(productDict.get("messageNumber"))
        issueTime = TimeUtil.epochTimeMillisToDatetime(productDict.get("issueTime"))
        issueTimeYear = str(issueTime.year)
        issueTimeMonth = str(issueTime.month)
        issueTimeDay = str(issueTime.day)
        mapJsonUri = os.path.join(rootPath, "events", officeID, issueTimeYear, issueTimeMonth, issueTimeDay,
                                      physicalEventName, messageNumber, wmoID)
        return mapJsonUri
