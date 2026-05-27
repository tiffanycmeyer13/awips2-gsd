# *** Override behavior of TSU_Segmented_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Segmented Formatter for TSU products
    @since: July 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsMessageMethods
import HazardConstants
import HazardProductParts
import NWS_Base_Formatter
from com.raytheon.uf.common.hazards.productgen import ProductUtils


class Format(NWS_Base_Formatter.Format):

    def initialize(self, productDict):
        '''
        @summary: Create instance variables visible to all methods
        in this class
        @param productDict: The product-level dictionary
        @return: New instance variables (i.e., self.hazardProductParts)
        '''
        super(Format, self).initialize(productDict)

        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = f"_{productDict.get('productLabel')}"
        self.productRegion = productDict.get("productRegion")

    def execute(self, productDict):
        '''
        @summary: Creates the message text for this formatter
        based on the contents of the product dictionary created
        by the product generator
        @param productDict: The product-level dictionary
        @return: A list of strings, each containing a block of
        text for a single message
        '''
        productRegion = productDict.get("productRegion")
        if productRegion in self.getValidProductRegions():
            self.initialize(productDict)
            legacyText = self.createTextProduct()
            legacyText = ProductUtils.wrapLegacy(legacyText)
            self.validateText(legacyText)
            return [legacyText]
        else:
            return []

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
        productParts = self.hazardProductParts.productParts_TSU(self.productDict,
                                                                self.productRegion, "Std")

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
        header = self.processPartValue(productDict.get("productBeginDict"), "wmoHeader_Std",
                                       self.wmoHeader_text, productDict, True)
        return self.getFormattedText(header, endText="\n")

    def productHeader(self, productDict):
        '''
        @summary: Create the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "productHeader_Std",
                                     self.productHeader_text, productDict, True)
        return text

    def summaryHeadlines(self, segmentDict):
        '''
        @summary: Create the summaryHeadlines product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = self.processPartValue(segmentDict, "summaryHeadlines_Std",
                                     self.summaryHeadlines_text, segmentDict)
        return text

    def areaList(self, segmentDict):
        '''
        @summary: Create the areaList product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        areaListText = self.processPartValue(segmentDict.get("segmentBeginDict"), "areaList_Std",
                                             self.areaList_text, segmentDict)
        return self.getFormattedText(areaListText, endText="\n")

    def issuanceTimeDate(self, segmentDict):
        '''
        @summary: Create the areaList product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = self.processPartValue(segmentDict.get("segmentBeginDict"), "issuanceTimeDate",
                                     self.issuanceTimeDate_text, segmentDict, True)
        return text

    def vtecString(self, segmentDict):
        text = self.processPartValue(segmentDict.get("segmentBeginDict"), 'vtecString_Std',
                                     self.slm.vtecString_text, segmentDict, True)
        text = self.amm.replaceSiteIdWithOfficeId(text, self.siteID)
        return text

    def locationBullet(self, segmentDict):
        '''
        @summary: Create the locationBullet product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = self.processPartValue(segmentDict, "locationBullet",
                                     self.locationBullet_text, segmentDict)
        return text

    def whatBullet(self, segmentDict):
        '''
        @summary: Create the whatBullet product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = self.processPartValue(segmentDict, "whatBullet",
                                     self.whatBullet_text, segmentDict)
        return self.getFormattedText(text, endText="\n\n")

    def physicalEventDescription(self, segmentDict):
        '''
        @summary: Create the physicalEventDescription product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = self.processPartValue(segmentDict, "physicalEventDescription",
                                     self.physicalEventDescription_text, segmentDict)
        return text

    def tsunamiStartTime(self, segmentDict):
        '''
        @summary: Create the tsunamiStartTime product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = self.processPartValue(segmentDict, "tsunamiStartTime",
                                     self.tsunamiStartTime_text, segmentDict)
        return text

    def additionalInfo(self, segmentDict):
        '''
        @summary: Create the additionalInfo product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = self.processPartValue(segmentDict, "additionalInfo",
                                     self.additionalInfo_text, segmentDict)
        return text

    ###### Helper functions
    def wmoHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the wmoHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.wmoHeader_text(productDict, self.issueTime,
                                       self.productRegion, "Std")

    def productHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        startText = self.amm.productHeaderStart_text(productDict, "TSU")
        officeLoc = self.amm.getOfficeLocation(self.siteID, self.backupSiteID)
        bestTimezone = self.amm.getProductLevelTimezone(productDict)
        timeText = self.getIssuanceTimeDate([bestTimezone])
        return f"{startText}{officeLoc}\n{timeText}"

    def locationBullet_text(self, segmentDict):
        '''
        @summary: Supports the creation of the locationBullet product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        return ("If you are located in this coastal area, move off the\n"
                "beach and out of harbors and marinas.\n\n")

    def summaryHeadlines_text(self, segmentDict):
        '''
        @summary: Supports the creation of the summaryHeadlines product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        summaryHeadline = self.slm.summaryHeadlines_text(segmentDict, False, False)
        headlineText = ""
        if self.siteID == "PTWC":
            headlineText = self.amm.getSummaryHeadlinesWithLocationText(segmentDict,
                                                                        summaryHeadline,
                                                                        self.siteID)
        else:
            # Strip off right-most ellipses (...)
            headlineText = summaryHeadline.rstrip("...")
            # Add affected states if they are defined
            statesList = self.amm.getStatesInProductSegment(segmentDict)
            if statesList:
                if "IS NOW IN EFFECT" in headlineText:
                    prefixConnector = "WHICH INCLUDES "
                elif "IS MODIFIED TO INCLUDE" in headlineText:
                    prefixConnector = ""
                else:
                    prefixConnector = "FOR "
                statesText = self.tpc.joinStringsWithOxfordComma(statesList).upper()
                headlineText += f" {prefixConnector}THE COASTAL AREAS OF {statesText}"
            # Add from/to break point segments
            breakPointSegmentDicts = segmentDict.get("breakPointSegmentDicts")
            consecutiveNumGroups = self.agu.getConsecutiveSegmentGroups(breakPointSegmentDicts)
            fromToList = []
            for startNum, endNum in consecutiveNumGroups:
                fromText = toText = ""
                fromToDict = self.amm.getFromToBreakpointInfo(segmentDict, breakPointSegmentDicts,
                                                              startNum, endNum)
                if fromToDict["fromName"] != "None":
                    fromText = (f"FROM {fromToDict['fromName']}, "
                                f"{fromToDict['fromState']}")
                    if fromToDict["fromDescriptor"] != "None":
                        fromText += f", WHICH IS LOCATED {fromToDict['fromDescriptor']},"
                if fromToDict["toName"] != "None":
                    toText = f" TO {fromToDict['toName']}, {fromToDict['toState']}"
                    if fromToDict["toDescriptor"] != "None":
                        toText += f", WHICH IS LOCATED {fromToDict['toDescriptor']}"
                if fromText and toText:
                    fromToList.append(f"{fromText}{toText}")
            if fromToList:
                fromToText = self.tpc.joinStringsWithOxfordComma(fromToList)
                headlineText += f" {fromToText}"
            headlineText += "..."
        headlineText += "\n\n"
        return headlineText.upper()

    def areaList_text(self, segmentDict):
        '''
        @summary: Supports the creation of the areaList product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        areaText = self.amm.getAreaListTextSegment(segmentDict, self.productRegion)
        areaText = areaText.replace("coastal areas from", "Coastal areas between and including")
        areaText = self.amm.capitalizeFirstLetter(areaText)
        return areaText

    def issuanceTimeDate_text(self, segmentDict):
        '''
        @summary: Supports the creation of the issuanceTimeDate product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        bestTimezone = segmentDict.get("timeZones")[0]
        return self.getIssuanceTimeDate([bestTimezone])

    def whatBullet_text(self, segmentDict):
        '''
        @summary: Supports the creation of the whatBullet product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        return self.amm.getAreaStatusDefinition(segmentDict)

    def physicalEventDescription_text(self, segmentDict):
        '''
        @summary: Supports the creation of the physicalEventDescription product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        eventDict = self.agu.getAllEventDicts(self.productDict)[0]
        descriptionString = self.amm.getPhysicalEventDescriptionString(eventDict,
                                                                       self.fieldNameSuffix)
        earthquakeText = f"{descriptionString}\n\n"
        return earthquakeText

    def tsunamiStartTime_text(self, segmentDict):
        '''
        @summary: Supports the creation of the tsunamiStartTime product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = ""
        tableText = self.amm.getTsunamiForecastRunsTableText(segmentDict,
                                                             self.officeTimeZone,
                                                             self.fieldNameSuffix)
        if tableText.strip():
            headerText = ("FORECASTS OF TSUNAMI ACTIVITY\n"
                          "-----------------------------\n")
            forecastPhrase = "Estimated tsunami start times for selected sites are:"
            headerText += f"{self.amm.wrapText(forecastPhrase)}\n\n"
            text = f"{headerText}{tableText}"
        return text

    def additionalInfo_text(self, segmentDict):
        '''
        @summary: Supports the creation of the additionalInfo product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        text = ""
        phraseList = []
        if self.agu.isSegmentCancelExpire(segmentDict):
            eventDict = self.agu.getAllEventDicts(self.productDict)[0]
            phraseList += [
                "No tsunami danger presently exists for this area.",
                (f"This will be the final {self.amm.getWarningCenterByEventDict(eventDict)} message for this region. Refer "
                 "to the internet site tsunami.gov for more information."),
                ]
        else:
            sectionDict = self.agu.getActiveSectionDicts(segmentDict)[0]
            hazType = sectionDict.get("vtecRecord").get("hdln").lower()
            phraseList += [
                (f"The {hazType} will remain in effect until further notice. "
                 "Refer to the internet site tsunami.gov for more information.")
                ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase, "", "")
            text += f"{wrappedPhrase}\n\n"
        return text

    def getValidProductRegions(self):
        '''
        @summary: Get the valid product regions where the segmented format will appear
        @return: List of strings
        '''
        return AtomsMessageMethods.AtomsMessageMethods().productRegionsWithSegmented()
