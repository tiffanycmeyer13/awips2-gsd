# *** Override behavior of Tsunami_Dissemination_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Organizes the previous formatted messages into a package
    to send outside the AWIPS firewall to the LS workstation
    @since: January 2025
    @author GSL Hazard Services Team
'''

import glob, os
import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import NWS_Base_Formatter


class Format(NWS_Base_Formatter.Format):

    def initialize(self, productDict):
        '''
        @summary: Create instance variables visible to all methods
        in this class
        @param productDict: The product-level dictionary
        @return: New instance variables (i.e., self.agu)
        '''
        super(Format, self).initialize(productDict)

        self.adu = AtomsDisseminationUtilities.AtomsDisseminationUtilities()
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary
        '''
        return []

    def getProductValidationChecks(self):
        '''
        @summary: A optional list of product validators that will be called to
        verify the message contents are accurate
        @return: A list of validation python files, each one will need to be
        imported at the top of this file
        '''
        return []

    def execute(self, productDict):
        '''
        @summary: Creates the message text for this formatter
        based on the contents of the product dictionary created
        by the product generator
        @param productDict: The product-level dictionary
        @return: A list of strings, each containing a block of
        text for a single message
        '''
        # Initialize the product dictionary
        self.initialize(productDict)
        if self.issueFlag and self.sendFiles() and self.productID not in ["ADA", "ADM", "TSU_TST"]:
            # Get the path where all previous formatters wrote files to
            storageFolder = self.adu.getAtomsDisseminationFilePath(productDict)
            # Determine if the compression script exists
            compressionScriptPath = self.adu.getMessageShipmentScript()
            if os.path.exists(compressionScriptPath):
                writtenFiles = glob.glob(os.path.join(storageFolder, "*"))
                print(f"======================================")
                print(f" The storage folder is: {storageFolder}")
                print(f" Number of files being sent to ls1: {len(writtenFiles)}")
                print(f" Files to be shipped: {writtenFiles}")
                # Compress the formatted file and ship them to ls1
                os.system(f"python {compressionScriptPath} -f {storageFolder} -p &")
        # This formatter returns no files
        return []

    def sendFiles(self):
        '''
        @summary: Flag to determine whether this formatter will run the script defined in the
        getScriptPath() method and send files from the lx workstation to the ls workstation
        @return: Boolean
        '''
        return True
