# *** Override behavior of TIB_Public_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Formatter for Tsunami Information Statement products
    @since: April 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMapUtilities
import AtomsMessageMethods
import FramedTextCheck
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
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.amu = AtomsMapUtilities.AtomsMapUtilities()
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = ""
        self.productRegion = productDict.get("productRegion")
        self.officeTimeZone = self.alu.getProductRegionTimeZone(self.productRegion)
        self.eventDict = self.agu.getAllEventDicts(productDict)[0]

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
            AtomsDisseminationUtilities.AtomsDisseminationUtilities().writeAtomsFile(
                                            productDict, textProductList, self.__module__)

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary
        '''
        self.tisType = self.getTisType(self.productDict)
        productParts = self.hazardProductParts.productParts_TIB(self.productDict)

        return productParts

    def getProductValidationChecks(self):
        '''
        @summary: A optional list of product validators that will be called to
        verify the message contents are accurate
        @return: A list of validation python files, each one will need to be
        imported at the top of this file
        '''
        if self.issueFlag:
            return [FramedTextCheck]
        else:
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

    def ugcHeader(self, productDict):
        '''
        @summary: Create the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "ugcHeader",
                                     self.ugcHeader_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def areaList(self, productDict):
        '''
        @summary: Create the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        areaListText = self.processPartValue(productDict.get("productBeginDict"), "areaList",
                                             self.areaList_text, productDict)
        return self.getFormattedText(areaListText, endText="\n")

    def summaryHeadlines(self, segmentDict):
        '''
        @summary: Create the summaryHeadlines product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        headlines = self.processPartValue(segmentDict.get("segmentBeginDict"), "summaryHeadlines",
                                          self.summaryHeadlines_text, segmentDict)
        # Made the headlines statement uppercase when manual edits are made
        headlines = headlines.upper()
        return headlines

    def audienceBullet(self, sectionDict):
        '''
        @summary: Create the audienceBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "audienceBullet",
                                     self.audienceBullet_text, sectionDict)
        return text

    def updatesBullet(self, sectionDict):
        '''
        @summary: Create the updatesBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        updatesText = self.processPartValue(sectionDict, "updatesBullet",
                                     self.updatesBullet_text, sectionDict)
        startText = ("UPDATES\n"
                     "-------\n"
                     )
        return self.getFormattedText(updatesText, startText, endText="\n\n")

    def evaluationBullet(self, sectionDict):
        '''
        @summary: Create the evaluationBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "evaluationBullet",
                                     self.evaluationBullet_text, sectionDict)
        return text

    def recommendedActionsBullet(self, sectionDict):
        '''
        @summary: Create the recommendedActionsBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "recommendedActionsBullet",
                                     self.recommendedActionsBullet_text, sectionDict)
        return text

    def tsunamiImpactsBullet(self, sectionDict):
        '''
        @summary: Create the tsunamiImpactsBullet product part
        @param productDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "tsunamiImpactsBullet",
                                     self.tsunamiImpactsBullet_text, sectionDict)
        return text

    def physicalEventParametersBullet(self, sectionDict):
        '''
        @summary: Create the physicalEventParametersBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "physicalEventParametersBullet",
                                     self.physicalEventParametersBullet_text, sectionDict)
        return text

    def tsunamiActivityObservations(self, sectionDict):
        '''
        @summary: Create the tsunamiActivityObservations product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "tsunamiActivityObservations",
                                     self.tsunamiActivityObservations_text, sectionDict)
        return text

    def additionalInfoStatement(self, sectionDict):
        '''
        @summary: Create the additionalInfoStatement product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "additionalInfoStatement",
                                     self.additionalInfoStatement_text, sectionDict)
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
        startText = self.amm.productHeaderStart_text(productDict, "TIB")
        officeLoc = self.amm.getOfficeLocation(self.siteID, self.backupSiteID)
        bestTimezone = self.alu.getPrimaryTimezoneByProductRegionAbbreviation(self.productRegion)
        if self.productRegion in self.amm.nonUsProductRegions():
            timeText = self.tpc.formatDatetime(self.issueTime, '%H%M %Z %a %b %e %Y', bestTimezone).strip() + "\n"
        else:
            timeText = self.getIssuanceTimeDate([bestTimezone])
        return f"{startText}{officeLoc}\n{timeText}"

    def ugcHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        ugcStr = self.amm.getTisUgcsBasedOnProductRegion(self.productRegion)
        ddhhmmTime = self.tpc.getFormattedTime(self.issueTime, '%d%H%M', stripLeading=0)
        text = f"{ugcStr}-{ddhhmmTime}-"
        return text

    def areaList_text(self, productDict):
        '''
        @summary: Supports the creation of the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        segmentDict = productDict.get("segments")[0]
        areaList = self.amm.getAreaListTextSegment(segmentDict, self.productRegion)
        return areaList

    def summaryHeadlines_text(self, segmentDict):
        '''
        @summary: Supports the creation of the summaryHeadlines product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        productRegionText = ""
        if self.siteID == "PTWC" and self.tisType == "tisHigh":
            text = "...POSSIBLE TSUNAMI THREAT FROM A DISTANT EARTHQUAKE"
        else:
            text = "...THIS IS A TSUNAMI INFORMATION STATEMENT"
            highMagnitude = self.amm.isTisSignificantMagnitude(self.eventDict)
            if self.siteID == "NTWC" and self.amu.isQuakeInArcticOceanProcRegion(self.eventDict, self.fieldNameSuffix):
                productRegionText = self.amm.getArcticOceanProcRegionText()
            elif self.tisType == "tisHigh" or highMagnitude:
                productRegionText = self.alu.getProductRegionNameFromAbbreviation(self.productRegion)
            if productRegionText:
                text += f" for {productRegionText}"
        text += "...\n"
        return text

    def updatesBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the updatesBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ""
        if self.tisType == "tisFinal":
            text = " * Final TIS"
        return text

    def audienceBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the audienceBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        return self.amm.getAudienceBullet_text(self.productRegion)

    def evaluationBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the evaluationBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ("EVALUATION\n"
                "----------\n")
        if self.amu.isQuakeInArcticOceanProcRegion(self.eventDict, self.fieldNameSuffix):
            regionText = self.amm.getArcticOceanProcRegionText()
        else:
            regionText = self.alu.getProductRegionNameFromAbbreviation(self.productRegion)
        warningCenter = self.amm.getWarningCenterByEventDict(self.eventDict)
        peType = self.eventDict.get("physicalEventType")
        phraseList = []
        prefix = ""
        isSupplementalMsg = self.amm.isTisSupplementalMessage(sectionDict)
        # Though the below logic seems complex, I think it actually reproduces
        # what NTWC's EarlyBird software does - see
        # https://docs.google.com/document/d/10ChdoGKF3SD_zYRn-EeVCez0l6T-Iv_axGlpQJjCPbg/edit?tab=t.0
        if self.tisType == "tisFinal" or (isSupplementalMsg and self.tisType != "tisHigh"):
            phraseList += [f"There is no tsunami danger for {regionText}."]
            if self.amm.isTisSignificantMagnitude(self.eventDict):
                phraseList += [
                    ("Some of the areas listed above may experience non-damaging sea level changes.")
                    ]
        else:
            if self.agu.isPhysicalEventTypeSeismic(peType):
                prefix = "An earthquake"
                # TIS potential danger
                if self.tisType == "tisHigh":
                    prefix = "A very large earthquake"
                    if self.amu.isQuakeInArcticOceanProcRegion(self.eventDict, self.fieldNameSuffix):
                        phraseList += [
                            "A widespread, damaging tsunami is NOT expected.",
                            ("In coastal areas of strong shaking, local tsunamis may be "
                             "generated."),
                            ("Due to very limited sea level data from the source region, it "
                             "is not possible for this Center to rapidly confirm or evaluate "
                             "the strength of a tsunami if one has been generated.")
                            ]
                    else:
                        phraseList += [
                            ("Earthquakes of this size are known to generate tsunamis "
                             "potentially dangerous to coasts outside the source region."),
                            (f"The {warningCenter} is analyzing the event to determine "
                             "the level of danger."),
                            "More information will be issued as it becomes available.",
                            ("This earthquake has the potential to generate a destructive "
                             "tsunami in the source region.")
                            ]
                # TIS low
                elif not self.amm.isTisSignificantMagnitude(self.eventDict):
                    phraseList += [
                        "There is NO tsunami danger from this earthquake."
                        ]
                    prefix = ""
                # TIS Significant
                else:
                    phraseList += [f"There is no tsunami danger for {regionText}."]
                    # if in the indian ocean
                    if self.amu.isQuakeInIndianOceanProcRegion(self.eventDict, self.fieldNameSuffix):
                        phraseList += [("This evaluation is based on the earthquake location which "
                                        "is outside the Pacific.")
                                        ]
                    # If in the mid-Atlantic Ridge
                    elif self.amu.isQuakeInMidAtlanticRidgeRegion(self.eventDict, self.fieldNameSuffix):
                        phraseList += [("Based on the earthquake location near the Mid-Atlantic Ridge, "
                                        "a damaging tsunami is not expected.")
                                        ]
                    # Deep evaluation
                    elif self.amm.isQuakeDeep(self.eventDict, self.fieldNameSuffix):
                        phraseList += [
                            "Based on the depth of the earthquake, a tsunami is not expected.",
                            ]
                    # Inland evaluation
                    elif self.amm.isPhysicalEventOnshore(self.eventDict, self.fieldNameSuffix):
                        phraseList += [
                            ("Based on the onshore location of the earthquake, "
                             "a tsunami is not expected.")
                            ]
                    elif self.siteID == "NTWC":
                        # Shallow evaluation
                        phraseList += [
                        ("Based on earthquake information and historic tsunami records, "
                         "the earthquake is not expected to generate a tsunami.")
                        ]
            elif self.agu.isPhysicalEventTypeVolcanic(peType):
                prefix = "A volcano eruption"
            elif self.agu.isPhysicalEventTypeLandslide(peType):
                prefix = "A landslide"
            if prefix:
                phraseList += [f"{prefix} has occurred with parameters listed below."]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def recommendedActionsBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the recommendedActionsBullet product part
        @param productDict: The section-level dictionary
        @return: String
        '''
        if self.tisType in ["tisLow", "tisFinal"] and self.productRegion not in ["As", "Gu", "Pr"]:
            return ""
        else:
            text = ("RECOMMENDED ACTIONS\n"
                    "-------------------\n")
            phraseList = []
            if self.tisType == "tisHigh":
                regionText = self.alu.getProductRegionNameFromAbbreviation(self.productRegion)
                phraseList += [
                    ("Stay alert for further information. There is the possibility "
                     "that a tsunami watch...advisory...or warning could be issued "
                     f"later for {regionText}."),
                    ]
            elif self.productRegion in ["As", "Gu", "Pr"]:
                phraseList += ["No action is required."]
            for phrase in phraseList:
                wrappedPhrase = self.amm.wrapText(phrase)
                text += f"{wrappedPhrase}\n\n"
            return text

    def tsunamiImpactsBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the tsunamiImpactsBullet product part
        @param productDict: The section-level dictionary
        @return: String
        '''
        if self.tisType in ["tisLow", "tisFinal"] and self.productRegion not in ["As", "Gu", "Pr"]:
            return ""
        else:
            text = ("POTENTIAL IMPACTS\n"
                    "-----------------\n")
            phraseList = []
            if self.tisType == "tisHigh":
                phraseList += [
                    "Potential tsunami impacts are still being evaluated.",
                    ]
                if self.productRegion in ["As", "Gu", "Pr", "Hi"]:
                    # TIB / TS.S earliest ETAs should use ReverseTTT whereas TS.WWYs should use the TTT fcst table
                    # since those ETAs may be in the product. So pass True at the end of this method call below.
                    phraseList += [self.amm.getEvaluationEarliestEstimatedArrivalTime_text(self.eventDict,
                                                                                           self.fieldNameSuffix,
                                                                                           self.productRegion,
                                                                                           True)]
            elif self.productRegion in ["As", "Gu", "Pr"]:
                phraseList += ["No tsunami impacts are expected."]
            for phrase in phraseList:
                wrappedPhrase = self.amm.wrapText(phrase)
                text += f"{wrappedPhrase}\n\n"
            return text

    def physicalEventParametersBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the physicalEventParametersBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        return self.amm.physicalEventParametersBullet_text(sectionDict, self.fieldNameSuffix)

    def tsunamiActivityObservations_text(self, sectionDict):
        '''
        @summary: Supports the creation of the tsunamiActivityObservations product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ""
        tableText = self.amm.getTsunamiObservationTableText(sectionDict,
                                                            self.officeTimeZone,
                                                            self.fieldNameSuffix)
        if tableText.strip():
            text = ("OBSERVATIONS OF TSUNAMI ACTIVITY - UPDATED\n"
                    "------------------------------------------\n")
            phrase = ("Observed max tsunami height is the highest recorded water level "
                     "above the tide level up to the time of this message.")
            text += f"{self.amm.wrapText(phrase)}\n\n"
            text += tableText
        return text

    def additionalInfoStatement_text(self, sectionDict):
        '''
        @summary: Supports the creation of the additionalInfoStatement product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ("ADDITIONAL INFORMATION AND NEXT UPDATE\n"
                "--------------------------------------\n")
        phraseList = []
        onlyOrFinal = "only"
        warningCenter = self.amm.getWarningCenterByEventDict(self.eventDict)
        coastalDescription = self.getCostalDescription()
        highMagnitude = self.amm.isTisSignificantMagnitude(self.eventDict)
        isSupplementalMsg = self.amm.isTisSupplementalMessage(sectionDict)
        peType = self.eventDict.get("physicalEventType")
        if self.tisType == "tisFinal" or isSupplementalMsg:
            onlyOrFinal = "final"
        phraseList += [(f"This will be the {onlyOrFinal} {warningCenter} statement issued "
                        "for this event unless additional information becomes available.")]
        if self.tisType == "tisHigh" or self.tisType == "tisFinal" or highMagnitude:
            phraseList += ["Refer to the internet site tsunami.gov for more information."]
            if self.siteID == "NTWC":
                phraseList += [(f"{coastalDescription} should refer to the Pacific "
                                "Tsunami Warning Center messages at tsunami.gov."), ]
            if self.tisType == "tisHigh" and not isSupplementalMsg:
                phraseList += [("Messages will be issued hourly to keep you informed of the "
                                "progress of this event."), ]
        if self.productRegion in self.amm.nonUsProductRegions():
            phraseList += self.amm.nonUsProductRegionsAdditionalInfo(self.productRegion)
        elif self.productRegion == "Pr":
            phraseList += self.amm.puertoRicoAdditionalInfo()
        if self.agu.isPhysicalEventTypeSeismic(peType):
            phraseList += [("Authoritative information about the earthquake can be obtained "
                            "from the corresponding regional seismic network or the U.S. "
                            "Geological Survey at earthquake.usgs.gov."), ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def getTisType(self, productDict):
        '''
        @summary: Get the Tsunami Information Statement type from the first
        event-level dictionary
        @param productDict: The product-level dictionary
        @return: String
        '''
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        tisType = eventDict.get("tisType")
        return tisType

    def getCostalDescription(self):
        '''
        @summary: Get the coastal description
        @return: String
        '''
        text = ""
        if self.productRegion == "AkBcWc":
            text = ("Pacific coastal regions outside California, Oregon, Washington, "
                    "British Columbia, and Alaska")
        elif self.productRegion == "EcGc":
            text = "Caribbean coastal regions"
        return text
