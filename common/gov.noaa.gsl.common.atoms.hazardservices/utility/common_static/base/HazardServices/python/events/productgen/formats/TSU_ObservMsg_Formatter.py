# *** Override behavior of TSU_ObservatoryMessage_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Formatter for Tsunami Observatory Message products
    @since: February 2023
    @author GSL Hazard Services Team
'''

import re
import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsMessageMethods
import HazardProductParts
import NWS_Base_Formatter
from com.raytheon.uf.common.hazards.productgen import ProductUtils


class Format(NWS_Base_Formatter.Format):

    def initialize(self, productDict):
        '''
        @summary: Create instance variables visible to all methods
        in this class
        @param productDict: The product-level dictionary
        @return: New instance variables (i.e., self.agu)
        '''
        super(Format, self).initialize(productDict)

        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = ""
        self.sectionDict = self.agu.getSectionDict(productDict)

    def execute(self, productDict):
        '''
        @summary: Creates the message text for this formatter
        based on the contents of the product dictionary created
        by the product generator
        @param productDict: The product-level dictionary
        @return: A list of strings, each containing a block of
        text for a single message
        '''
        self.initialize(productDict)
        legacyText = self.createTextProduct()
        legacyText = ProductUtils.wrapLegacy(legacyText)
        self.validateText(legacyText)
        return [legacyText]

    def recordGeneratedText(self, productDict, textProductList):
        '''
        @summary: Write the text product(s) from this formatter to a physical file
        @param productDict: The product-level dictionary
        @param textProductList: A list of text product(s) created by the formatter
        @return: None
        '''
        if self.issueFlag:
            AtomsDisseminationUtilities.AtomsDisseminationUtilities().writeAtomsFile(productDict, textProductList, self.__module__)

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary
        '''
        productParts = self.hazardProductParts.productParts_TSU_ObservMsg(self.productDict)

        return productParts

    def getProductValidationChecks(self):
        '''
        @summary: A optional list of product validators that will be called to
        verify the message contents are accurate
        @return: A list of validation python files, each one will need to be
        imported at the top of this file
        '''
        return []

    ######################################################
    #  Product Part Methods
    ######################################################
    def wmoHeader(self, productDict):
        '''
        @summary: Create the wmoHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        header = self.processPartValue(productDict.get("productBeginDict"), "wmoHeader",
                                       self.wmoHeader_text, productDict, True)
        return header

    def productHeader(self, productDict):
        '''
        @summary: Create the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "productHeader",
                                     self.productHeader_text, productDict, True)
        return text

    def physicalEventParametersBullet(self, productDict):
        '''
        @summary: Create the physicalEventParametersBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "physicalEventParametersBullet",
                                     self.physicalEventParametersBullet_text, productDict)
        return text

    def additionalInfoStatement(self, productDict):
        '''
        @summary: Create the additionalInfoStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "additionalInfoStatement",
                                     self.additionalInfoStatement_text, productDict)
        return text

    ###### Helper functions
    def wmoHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the wmoHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        officeId = self.amm.getOfficeIdBySiteId(self.siteID)
        ddhhmmTime = self.tpc.getFormattedTime(self.issueTime, "%d%H%M",
                                               stripLeading=False, changeNoonMidnight=False)
        wmoHeader = f"ADMN75 {officeId} {ddhhmmTime}\n"
        return wmoHeader

    def productHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        originTime = eventDict.get(f"originTime{self.fieldNameSuffix}")
        originTimeString = self.tpc.formatDatetime(originTime, "%b %d").upper()
        peTypeString = self.getPhysicalEventTypeString(eventDict.get("physicalEventType"))
        text = ("OBSERVATORY MESSAGE\n"
                f"{peTypeString} OF {originTimeString}\n")
        return text

    def physicalEventParametersBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the physicalEventParametersBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.physicalEventParametersBullet_text(productDict, self.fieldNameSuffix)

    def additionalInfoStatement_text(self, productDict):
        '''
        @summary: Supports the creation of the additionalInfoStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ("ADDITIONAL INFORMATION\n"
                "----------------------\n")
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        phraseList = []
        peType = eventDict.get("physicalEventType")
        if self.agu.isPhysicalEventTypeSeismic(peType):
            phraseList += [
                "The magnitude may change as more data becomes available.",
                "The magnitude are based on preliminary information.",
                ("Further information will be issued by the United States "
                 "Geological Survey (earthquake.usgs.gov) or the appropriate "
                 "regional seismic network.")
                ]
        else:
            phraseList += [
                f"A {peType.lower()} event occurred."
                ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n"
        text += "\n"
        return text

    def getPhysicalEventTypeString(self, peType):
        '''
        @summary: Get a string descriptor based on the physical event type
        @param peType: The physical event type (i.e., Seismic)
        @return: String
        '''
        peTypeString = ""
        if peType == "Seismic":
            peTypeString = "QUAKE"
        elif peType == "Volcanic":
            peTypeString = "VOLCANO"
        elif peType == "Landslide":
            peTypeString = "LANDSLIDE"
        elif peType == "Unknown":
            peTypeString = "UNKNOWN EVENT"
        return peTypeString
