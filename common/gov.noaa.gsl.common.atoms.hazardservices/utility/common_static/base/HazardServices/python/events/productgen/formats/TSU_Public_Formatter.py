# *** Override behavior of TSU_Public_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Formatter for TSU products
    @since: Feb 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsMessageMethods
import HazardProductParts
import NWS_Base_Formatter
import PhraseMethodsUtil
import TextProductCommon
import TimeUtil
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
        self.pmUtil = PhraseMethodsUtil.PhraseMethodsUtil()
        self.tpc = TextProductCommon.TextProductCommon()

        self.productRegion = productDict.get("productRegion")
        self.siteID = productDict.get("siteID")
        self.fieldNameSuffix = f"_{productDict.get('productLabel')}"

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
        productParts = self.hazardProductParts.productParts_TSU(self.productDict, self.productRegion, "Pub")

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
        return self.getFormattedText(header, endText="\n")

    def productHeader(self, productDict):
        '''
        @summary: Create the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "productHeader",
                                     self.productHeader_text, productDict, True)
        return text

    def updatesBullet(self, productDict):
        '''
        @summary: Create the updatesBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict, "updatesBullet",
                                     self.updatesBullet_text, productDict)
        return text

    def ugcHeader(self, productDict):
        '''
        @summary: Create the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "ugcHeader_pub",
                                     self.ugcHeader_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def vtecString(self, productDict):
        '''
        @summary: Create the vtecString product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "vtecString_pub",
                                     self.vtecString_text, productDict, True)
        return text

    def summaryHeadlines(self, productDict):
        '''
        @summary: Create the summaryHeadlines product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "summaryHeadlines_pub",
                                     self.summaryHeadlines_text, productDict)
        return text

    def areaList(self, productDict):
        '''
        @summary: Create the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "areaList_pub",
                                     self.areaList_text, productDict)
        return text

    def dangerEvaluation(self, productDict):
        '''
        @summary: Create the dangerEvaluation product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "dangerEvaluation",
                                     self.dangerEvaluation_text, productDict)
        return self.getFormattedText(text, endText="\n\n")

    def audienceBullet(self, productDict):
        '''
        @summary: Create the audienceBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "audienceBullet",
                                     self.audienceBullet_text, productDict)
        return text

    def evaluationBullet(self, productDict):
        '''
        @summary: Create the evaluationBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "evaluationBullet",
                                     self.evaluationBullet_text, productDict)
        return text

    def physicalEventParametersBullet(self, productDict):
        '''
        @summary: Create the physicalEventParametersBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "physicalEventParametersBullet",
                                     self.physicalEventParametersBullet_text, productDict)
        return text

    def tsunamiForecastsBullet(self, productDict):
        '''
        @summary: Create the tsunamiForecastsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"), "tsunamiForecastsBullet",
                                     self.tsunamiForecastsBullet_text, productDict)
        return text

    def tsunamiObservationsBullet(self, productDict):
        '''
        @summary: Create the tsunamiObservationsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"), "tsunamiObservationsBullet",
                                     self.tsunamiObservationsBullet_text, productDict)
        return self.getFormattedText(text, endText="\n\n")

    def recommendedActionsBullet(self, productDict):
        '''
        @summary: Create the recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"), "recommendedActionsBullet",
                                     self.recommendedActionsBullet_text, productDict)
        startText = self.actionsStartText(productDict)
        return self.getFormattedText(text, startText=startText)

    def tsunamiImpactsBullet(self, productDict):
        '''
        @summary: Create the tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"), "tsunamiImpactsBullet",
                                     self.tsunamiImpactsBullet_text, productDict)
        startText = self.impactStartText(productDict)
        return self.getFormattedText(text, startText=startText)

    def additionalInfoStatement(self, productDict):
        '''
        @summary: Create the additionalInfoStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"), "additionalInfoStatement",
                                     self.additionalInfoStatement_text, productDict)
        return text

    ###### Helper functions
    def wmoHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the wmoHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.wmoHeader_text(productDict, self.issueTime, self.productRegion, "Pub")

    def productHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        startText = self.amm.productHeaderStart_text(productDict, "TSU", isPublic=True)
        officeLoc = self.amm.getOfficeLocation(self.siteID, self.backupSiteID)
        bestTimezone = self.amm.getProductLevelTimezone(productDict)
        timeText = self.getIssuanceTimeDate([bestTimezone])
        return f"{startText}{officeLoc}\n{timeText}"

    def ugcHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        ugcHeader = ""
        for segmentDict in productDict.get("segments"):
            ugcHeader += self.slm.ugcHeader_text(segmentDict)
        return ugcHeader

    def vtecString_text(self, productDict):
        '''
        @summary: Supports the creation of the vtecString product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        vtecString = ""
        for segmentDict in productDict.get("segments"):
            vtecString += f"{self.slm.vtecString_text(segmentDict)}"
            vtecString = self.amm.replaceSiteIdWithOfficeId(vtecString, self.siteID)
        return vtecString

    def summaryHeadlines_text(self, productDict):
        '''
        @summary: Supports the creation of the summaryHeadlines product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        if self.siteID == "NTWC":
            headlineText = self.amm.getNTWC_SummaryHeadlines(productDict)
        else:
            headlineText = self.amm.getPTWC_SummaryHeadlines(productDict)
        return headlineText

    def areaList_text(self, productDict):
        '''
        @summary: Supports the creation of the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        if self.productRegion == "Pr":
            areaPhrase = ("Coastal areas of Puerto Rico - the U.S. Virgin Islands and "
                          "the British Virgin Islands")
            areaListText = f"{self.amm.wrapText(areaPhrase, '', '')}\n"
        else:
            areaListText = self.amm.getAreaListTextProduct(productDict)
        return areaListText

    def dangerEvaluation_text(self, productDict):
        '''
        @summary: Supports the creation of the dangerEvaluation product part
        NOTE: This is only available for NTWC in the AkBcWc & EcGc product regions
        @param productDict: The product-level dictionary
        @return: String
        '''
        dangerIdentifier = productDict.get(f"stillEvaluatingDanger{self.fieldNameSuffix}")
        dangerMsg = ""
        # For Volcano and landslide, add more information to this section
        activeSectionDict = self.agu.getActiveSectionDicts(productDict)[0]
        vtec = activeSectionDict.get("vtecRecord")
        hazardAction = vtec.get("act")
        eventDict = activeSectionDict.get("eventDicts")[0]
        peType = eventDict.get("physicalEventType")
        if not self.agu.isPhysicalEventTypeSeismic(peType):
            dangerMsg = self.getMorePhysicalEventInformation(eventDict, peType, hazardAction)

        if self.productRegion == "AkBcWc":
            dangerMsg += "For other US and Canadian Pacific coasts in North America, "
        elif self.productRegion == "EcGc":
            dangerMsg += ("For other US and Canadian Coasts in the Atlantic and Gulf "
                         "of America, ")
        if dangerMsg:
            if dangerIdentifier == "dangerStillBeingEvaluated":
                dangerMsg += ("the level of tsunami danger is being evaluated.  Further "
                              "information will be provided in supplementary messages.")
            else:
                dangerMsg += "there is no tsunami threat."
        return dangerMsg

    def updatesBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the updatesBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.getUpdatesBulletText(productDict, self.fieldNameSuffix)

    def audienceBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the audienceBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.getAudienceBullet_text(self.productRegion)

    def evaluationBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the evaluationBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        phraseList = []
        text = ("EVALUATION\n"
                "----------\n")
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        phraseList += [
            self.amm.getPhysicalEventDescriptionString(eventDict, self.fieldNameSuffix),
            self.amm.getEvalutionBulletLocation_text(self.productRegion),
            # TIB / TS.S earliest ETAs should use ReverseTTT whereas TS.WWYs should use the TTT fcst table
            # since those ETAs may be in the product. So pass False at the end of this method call below.
            self.amm.getEvaluationEarliestEstimatedArrivalTime_text(eventDict, self.fieldNameSuffix,
                                                                    self.productRegion, False)
            ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def recommendedActionsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.getRecommendedActionsText(productDict)

    def actionsStartText(self, productDict):
        '''
        @summary: Generate the starting text that will appear above the
        recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        headerText = "RECOMMENDED ACTIONS"
        if self.agu.areAllSegmentsEnding(productDict):
            headerText += " - UPDATED"
        dashText = self.tpc.getDashesUnderString(headerText, "\n")
        startText = f"{headerText}\n{dashText}"
        return startText

    def tsunamiForecastsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiForecastsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        tableText = self.amm.getTsunamiForecastRunsTableText(productDict,
                                                             self.officeTimeZone,
                                                             self.fieldNameSuffix)
        if tableText.strip():
            headerText = ("FORECASTS OF TSUNAMI ACTIVITY\n"
                          "-----------------------------\n")
            forecastPhrase = ("Tsunami activity is forecast to start at the following "
                              "locations at the specified times.")
            headerText += f"{self.amm.wrapText(forecastPhrase, '', '')}\n\n"
            text = f"{headerText}{tableText}"
        return text

    def tsunamiObservationsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiObservationsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        tableText = self.amm.getTsunamiObservationTableText(productDict,
                                                            self.officeTimeZone,
                                                            self.fieldNameSuffix)
        observationText = ("OBSERVATIONS OF TSUNAMI ACTIVITY\n"
                           "---------------------------------\n")
        if tableText.strip():
            observationText += tableText
        else:
            obsPhrase = "No tsunami observations are available to report."
            observationText += self.amm.wrapText(obsPhrase)
        return observationText

    def physicalEventParametersBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the physicalEventParametersBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.physicalEventParametersBullet_text(productDict, self.fieldNameSuffix)

    def tsunamiImpactsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.getImpactsBulletText(productDict, self.fieldNameSuffix)

    def impactStartText(self, productDict):
        '''
        @summary: Generate the starting text that will appear above the
        tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        headerText = "POTENTIAL IMPACTS"
        if self.agu.areAllSegmentsEnding(productDict):
            headerText += " - UPDATED"
        dashText = self.tpc.getDashesUnderString(headerText, "\n")
        startText = f"{headerText}\n{dashText}"
        return startText

    def additionalInfoStatement_text(self, productDict):
        '''
        @summary: Supports the creation of the additionalInfoStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ("ADDITIONAL INFORMATION AND NEXT UPDATE\n"
                "--------------------------------------\n")
        phraseList = []
        if self.agu.areAllSegmentsEnding(productDict):
            eventDict = self.agu.getAllEventDicts(productDict)[0]
            phraseList += [
                (f"This will be the final {self.amm.getWarningCenterByEventDict(eventDict)} message issued for this event."),
                ]
        else:
            phraseList += [
                self.amm.getNextMsgText(productDict, "", self.fieldNameSuffix),
                "Refer to the internet site tsunami.gov for more information.",
                ("Authoritative information about the earthquake can be obtained "
                 "from the corresponding regional seismic network or the U.S. "
                 "Geological Survey at earthquake.usgs.gov."),
                ]
        if self.productRegion == "AkBcWc":
            phraseList += [
                ("Pacific coastal residents outside California, Oregon, Washington "
                 "British Columbia and Alaska should refer to the Pacific Tsunami "
                 "Warning Center messages at tsunami.gov."),
                ]
        elif self.productRegion == "EcGc":
            phraseList += [
                ("Caribbean coastal regions including Puerto Rico, U.S. Virgin "
                 "Islands and British Virgin Islands should refer to the Pacific "
                 "Tsunami Warning Center messages at tsunami.gov."),
                    ]
        elif self.productRegion == "Pr":
            phraseList += self.amm.puertoRicoAdditionalInfo()
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def getMorePhysicalEventInformation(self, eventDict, physicalEventType, hazardAction):
        '''
        @summary: Generate extra physical event information
        @param eventDict: The event level dictionary
        @param physicalEventType: The physical event type such volcano, landslide
        @param hazardAction: The hazard event action such as NEW or CON
        @return: String
        '''
        text = ""
        actionText = ""
        peName = eventDict.get(f"peName{self.fieldNameSuffix}")
        suffix = "dangerous to coastlines in the warning area."
        if self.agu.isPhysicalEventTypeVolcanic(physicalEventType):
            if peName:
                volcanoText = f"{peName} Volcano"
            else:
                volcanoText = "a volcano"
            if hazardAction == "NEW":
                actionText = "the potential to trigger"
            elif hazardAction == "CON":
                actionText = "generated"
            if actionText:
                text = (f"An eruption on {volcanoText} has occurred which has "
                        f"{actionText} a tsunami {suffix}")
        elif self.agu.isPhysicalEventTypeLandslide(physicalEventType):
            if peName:
                landslideText = peName
            else:
                landslideText = "a landslide"
            if hazardAction == "NEW":
                actionText = f"have been observed in {landslideText} indicative of a possible landslide tsunami"
            elif hazardAction == "CON":
                actionText = f"continue in {landslideText} indicative of continuing tsunami activity"
            if actionText:
                text = f"Significant water level fluctuations {actionText} {suffix}"
        elif self.agu.isPhysicalEventTypeUnknown(physicalEventType):
            text = self.amm.getUnknownDescription().strip() + "."
        if text:
            text = f"{self.amm.wrapText(text, '', '')}\n\n"
        return text
