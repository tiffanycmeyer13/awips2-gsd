# *** Override behavior of TsunamiMessageRetransmitTool.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Supports the retransmission of recently
    created tsunami products
    
    @since: February 2025
    @author: GSL Hazard Services Team
'''

import datetime, glob, os
import logging, UFStatusHandler
import AtomsDisseminationUtilities
import AtomsLocationUtilities
import EventSetFactory
import TsunamiRecommenderCommon


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()

        self.logger = logging.getLogger("TsunamiMessageRetransmitTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsl.common.atoms.hazardservices", "TsunamiMessageRetransmitTool",
            level=logging.INFO))
        self.logger.setLevel(logging.INFO)

        self.adu = AtomsDisseminationUtilities.AtomsDisseminationUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()

    def defineScriptMetadata(self):
        """
        @return: JSON string containing information about this
                 tool
        """
        return {
            "toolName": "TsunamiMessageRetransmitTool",
            "author": "GSL",
            "version": "1.0",
            "description": ("Re-sends the last set of products for a selected physical "
                            "event across the firewall.")
            }

    def defineDialog(self, eventSet):
        '''
        @summary: Define the contents of the window that pops up when the tool is launched
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return
        @param kwargs: Additional key word arguments to this method.
        @return: MegaWidget dialog definition to solicit user input before running tool
        '''

        # Determine that a physical event that was selected from the PEM
        selectedEventList = list(self.pem.getSelectedPhysicalEvents())
        errorMsg = self.agu.validateSelectedPhysicalEvent(selectedEventList)
        if errorMsg:
            return {"resultsMessage": errorMsg}

        # Get physical event ID
        physicalEvent = selectedEventList[0]
        physicalEventID = physicalEvent.getCustomId()

        # Get path to transmitted files
        transmissionFolder = os.path.join(self.adu.atomsDisseminationRootPath(), physicalEventID)
        if not os.path.exists(transmissionFolder):
            errorMsg = f"No files stored in {transmissionFolder} to transmit. Exiting tool."
            return {"resultsMessage": errorMsg}

        # Get date stamped folders for this physical event
        dateFolders = sorted(glob.glob(os.path.join(transmissionFolder, "*")))
        if not dateFolders:
            errorMsg = f"No folders found underneath {transmissionFolder}. Exiting tool."
            return {"resultsMessage": errorMsg}

        # Get the most recent folder
        mostRecentDateFolder = dateFolders[-1]

        # Build window and associated megawidgets
        dialogDict = {
            "title": "Tsunami Message Retransmit Tool",
            "fields": [
                self.getInfoLabel(physicalEventID, mostRecentDateFolder),
                self.transmitFolderHiddenField(mostRecentDateFolder),
                self.retransmitCheckList(mostRecentDateFolder),
                ],
            "valueDict": {},
            }

        # Return the dialogDict
        return dialogDict

    def getInfoLabel(self, physicalEventID, transmitFolder):
        '''
        @summary: Build a Label megawidget with some info
        @param physicalEventID: The physical event identifier (e.g., HumboldtDec2024)
        @param transmitFolder: The root path to the latest batch of files created
        for a physical event
        e.g., /data/fxa/ATOMS/dissemination/HumboldtDec2024/20250130-220626
        @return: Dictionary of megawidget properties
        '''
        stringTime = os.path.basename(transmitFolder)
        issueTimeDT = datetime.datetime.strptime(stringTime, "%Y%m%d-%H%M%S")
        lastIssueTime = issueTimeDT.strftime("%m/%d/%Y at %H:%M:%S UTC")
        return {
            "fieldType": "Label",
            "fieldName": "informationLabel",
            "label": (f"Physical Event ID: {physicalEventID}\n"
                      f"Last Issuance Time: {lastIssueTime}"),
            "labelBold": True,
            }

    def transmitFolderHiddenField(self, transmitFolder):
        '''
        @summary: Build a HiddenField megawidget that will contain the
        root path to the latest batch of files created for a physical event
        e.g., /data/fxa/ATOMS/dissemination/HumboldtDec2024/20250130-220626
        @param transmitFolder: The folder to store in the HiddenField
        @return: Dictionary of megawidget properties
        '''
        return {
            "fieldType": "HiddenField",
            "fieldName": "transmitRootFolder",
            "values": transmitFolder,
            }

    def retransmitCheckList(self, transmitFolder):
        '''
        @summary: Create a CheckList that allows the user to choose specific
        product regions (e.g., Hawaii) and product types (e.g., TSU) to retransmit
        @param transmitFolder: The root path to the latest batch of files created
        for a physical event
        e.g., /data/fxa/ATOMS/dissemination/HumboldtDec2024/20250130-220626
        @return: Dictionary of megawidget properties
        '''
        # Determine the product regions underneath these folders
        productRegions = sorted(glob.glob(os.path.join(transmitFolder, "*")))
        # Build labels
        choiceList = []
        for regionPath in productRegions:
            regionAbbrev = os.path.basename(regionPath)
            regionName = self.alu.getProductRegionNameFromAbbreviation(regionAbbrev)
            productTypes = sorted(glob.glob(os.path.join(regionPath, "*")))
            for productType in productTypes:
                label = (f"{os.path.basename(productType)}"
                         f"{self.labelSeparator()}{regionName}")
                choiceList.append(label)
        # Create megawidget
        return {
            "fieldType": "CheckList",
            "fieldName": "regionsToTransmit",
            "label": "Select product(s) and region(s) to retransmit:",
            "choices": choiceList,
            "values": choiceList,
            "labelBold": True,
            }

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        @summary: Executes tool actions after the 'Run' button is
        pressed
        @param eventSet: A set of events which include session
        attributes
        @param dialogInputMap: A map of information retrieved from
        a user's interaction with a dialog
        @param visualFeatures: Input gathering visual features; not
        used by this tool.
        @return: An empty eventSet with the resultsMessage
        '''
        # EventSet to store messages
        messageEventSet = EventSetFactory.createEventSet()
        # Get the root path
        transmitRootFolder = dialogInputMap["transmitRootFolder"]
        # Get the script transmission path
        compressionScriptPath = self.adu.getMessageShipmentScript()
        messageList = []
        for regionString in dialogInputMap["regionsToTransmit"]:
            # Split the label to get the product type (e.g., TSU) and name (e.g., Hawaii)
            productType, regionName = regionString.split(self.labelSeparator())
            # Get the region abbreviation from the name (e.g., Hawaii --> Hi)
            regionAbbrev = self.alu.getProductRegionAbbreviationFromName(regionName)
            # Build the full path to the folder containing the messages
            storageFolder = os.path.join(transmitRootFolder, regionAbbrev, productType)
            numWrittenFiles = len(glob.glob(os.path.join(storageFolder, "*")))
            # Compress the formatted file and ship them to ls1
            os.system(f"python {compressionScriptPath} -f {storageFolder} -p &")
            msg = (f"Retransmitted {numWrittenFiles} {productType} messages "
                   f"from {storageFolder} for the {regionName} product region!")
            messageList.append(msg)
        # Write messages back to the user
        if messageList:
            message = "\n\n".join(messageList)
        else:
            message = "No files retransmitted"
        messageEventSet.addAttribute("resultsMessage", message)
        return messageEventSet

    def labelSeparator(self):
        '''
        @summary: The label separator between the product type (e.g., TSU) and the
        product region name (e.g., American Samoa)
        @return: String
        '''
        return " | "


def __str__(self):
    return "Tsunami Message Retransmit Tool"
