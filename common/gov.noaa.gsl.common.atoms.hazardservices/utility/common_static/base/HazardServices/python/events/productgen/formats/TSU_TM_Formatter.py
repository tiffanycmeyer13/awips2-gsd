# *** Override behavior of TSU_TM_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Formatter for Tsunami Threat Message products
    @since: August 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
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
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = ""
        self.productRegion = productDict.get("productRegion")
        self.sectionDict = self.agu.getSectionDict(productDict)
        self.officeTimeZone = self.alu.getProductRegionTimeZone(self.productRegion)
        eventDict = self.getAllEventDicts(self.sectionDict)[0]
        self.newForecastInfo = eventDict.get("newForecastInfo")
        self.finalMessage = eventDict.get("isFinalThreatMessage")
        self.initialMessage = eventDict.get("status").upper() == "PENDING"

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
        productParts = self.hazardProductParts.productParts_TSU_TM(self.productDict)

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

    def summaryHeadlines(self, productDict):
        '''
        @summary: Create the summaryHeadlines product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        segmentDict = productDict.get("segments")[0]
        text = self.processPartValue(segmentDict, "summaryHeadlines",
                                     self.summaryHeadlines_text, productDict)
        return text

    def audienceBullet(self, productDict):
        '''
        @summary: Create the audienceBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "audienceBullet",
                                     self.audienceBullet_text, productDict)
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

    def evaluationBullet(self, productDict):
        '''
        @summary: Create the evaluationBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "evaluationBullet",
                                     self.evaluationBullet_text, productDict)
        return text

    def recommendedActionsBullet(self, productDict):
        '''
        @summary: Create the recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "recommendedActionsBullet",
                                     self.recommendedActionsBullet_text, productDict)
        return text

    def tsunamiForecastsBullet(self, productDict):
        '''
        @summary: Create the tsunamiForecastsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "tsunamiForecastsBullet",
                                     self.tsunamiForecastsBullet_text, productDict)
        return text

    def tsunamiImpactsBullet(self, productDict):
        '''
        @summary: Create the tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "tsunamiImpactsBullet",
                                     self.tsunamiImpactsBullet_text, productDict)
        return text

    def tsunamiEstimatedArrivalTime(self, productDict):
        '''
        @summary: Create the tsunamiEstimatedArrivalTime product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "tsunamiEstimatedArrivalTime",
                                     self.tsunamiEstimatedArrivalTime_text, productDict)
        return text

    def tsunamiObservationsBullet(self, productDict):
        '''
        @summary: Create the tsunamiObservationsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(self.sectionDict, "tsunamiObservationsBullet",
                                     self.tsunamiObservationsBullet_text, productDict)
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
        return self.amm.wmoHeader_text(productDict, self.issueTime, self.productRegion, "Pub")

    def productHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        startText = self.amm.productHeaderStart_text(productDict, "TSU_TM")
        officeLoc = self.amm.getOfficeLocation(self.siteID, self.backupSiteID)
        bestTimezone = self.alu.getPrimaryTimezoneByProductRegionAbbreviation(self.productRegion)
        timeText = self.tpc.formatDatetime(self.issueTime, '%H%M %Z %a %b %e %Y', bestTimezone).strip() + "\n"
        return f"{startText}{officeLoc}\n{timeText}"

    def summaryHeadlines_text(self, productDict):
        '''
        @summary: Supports the creation of the summaryHeadlines product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        finalText = ""
        if self.finalMessage:
            finalText = " FINAL"
        headline = f"...PTWC{finalText} TSUNAMI THREAT MESSAGE...\n"
        return headline

    def audienceBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the audienceBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        audienceText = self.amm.getAudienceBullet_text(self.productRegion)
        if not self.initialMessage:
            changeType = None
            if self.finalMessage or self.newForecastInfo:
                changeType = "UPDATED"
            elif not self.newForecastInfo:
                changeType = "UNCHANGED"
            if changeType:
                audienceText += f"THE TSUNAMI FORECAST IS {changeType} IN THIS MESSAGE.\n\n"
        return audienceText

    def evaluationBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the evaluationBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ("EVALUATION\n"
                "----------\n")
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        phraseList = [self.amm.getPhysicalEventDescriptionString(eventDict, self.fieldNameSuffix)]
        if self.finalMessage:
            phraseList += [("Based on all available data... the tsunami threat from this "
                            "earthquake has now passed.")]
        else:
            phraseList += [("Based on all available data... hazardous tsunami waves are "
                            "forecast for some coasts.")]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def physicalEventParametersBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the physicalEventParametersBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.physicalEventParametersBullet_text(productDict, self.fieldNameSuffix)

    def tsunamiForecastsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiForecastsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        if not self.finalMessage:
            threatForecast = self.getTsunamiThreatForecast(productDict, self.officeTimeZone,
                                                           self.fieldNameSuffix)
        else:
            threatText = "There is no longer a tsunami threat from this earthquake."
            threatForecast = f"{self.amm.wrapText(threatText)}\n"

        if threatForecast:
            headerText = "TSUNAMI THREAT FORECAST"
            if self.newForecastInfo or self.finalMessage:
                headerText += "...UPDATED"
            headerDashes = self.tpc.getDashesUnderString(headerText)
            text += (f"{headerText}\n"
                     f"{headerDashes}\n"
                     f"{threatForecast}\n")
        return text

    def getTsunamiThreatForecast(self, productDict, tz, suffix, language=""):
        '''
        @summary: Build the threat forecast text block for each of the categories
        @param productDict: The product-level dictionary
        @param tz: The configured office-level time zone
        @param suffix: The field name suffix
        @param language: The optional language (default is English)
        @return: String
        '''
        threatText = ""

        # Get the event-level dictionary
        eventDict = self.agu.getAllEventDicts(productDict)[0]

        # Determine the analysis type performed on the stations
        stationAnalysisType = eventDict.get("stationAnalysisType")

        # Get either a list of country names or a dictionary or categories
        countryInformation = eventDict.get("threatCountryInformation")

        # Logic for a threat message with no amplitude information
        if countryInformation:
            countryInformation.sort()
            if stationAnalysisType and stationAnalysisType != "amplitudes":
                if "km" in stationAnalysisType:
                    distanceValue = stationAnalysisType.replace("km", "")
                    threatCriteriaText = f"{distanceValue} km of the epicenter along the coasts of"
                else:
                    threatCriteriaText = "the next three hours along some coasts of"
                countryText = self.tpc.joinStrings(countryInformation, separator="... ",
                                                   lastSeparator=" and ", prefix="  ", suffix="",
                                                   cap=False)
                threatHeader = ("Hazardous tsunami waves from this earthquake are possible "
                                f"within {threatCriteriaText}")
                threatText += (f"{self.amm.wrapText(threatHeader)}\n\n"
                               f"    {countryText}.\n\n")
            # Logic for a threat message with amplitude information
            else:
                countryInformationDict = countryInformation[0]
                threatImpactDict = {
                    "high": "reaching more than 3",
                    "medium": "reaching 1 to 3",
                    "low": "reaching 0.3 to 1",
                    }
                if self.productRegion == "Pac":
                    threatImpactDict["veryLow"] = "are forecast to be less than 0.3"
                for category in threatImpactDict:
                    countryList = countryInformationDict.get(category)
                    if countryList:
                        countryList.sort()
                        countryText = self.tpc.joinStrings(countryList, separator="... ",
                                                           lastSeparator=" and ", prefix="  ",
                                                           suffix="", cap=False)
                        threatHeader = (f"Tsunami waves {threatImpactDict[category]} meters "
                                        "above the tide level are possible along some coasts of")
                        threatText += (f"{self.amm.wrapText(threatHeader)}\n\n"
                                       f"    {countryText}.\n\n")
        return threatText

    def tsunamiObservationsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiObservationsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        tableText = self.amm.getTsunamiObservationTableText(productDict,
                                                            self.officeTimeZone,
                                                            self.fieldNameSuffix)
        if tableText:
            obsText = ("Observed max tsunami height is the highest recorded water level "
                       "above the tide level up to the time of this message.")
            headerText = ("TSUNAMI OBSERVATIONS\n"
                          "--------------------\n"
                          f"{self.amm.wrapText(obsText)}\n\n")
            text = f"{headerText}{tableText}"
        return text

    def tsunamiEstimatedArrivalTime_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiEstimatedArrivalTime product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        tableText = ""
        if not self.finalMessage:
            tableText = self.amm.getTsunamiForecastRunsTableText(productDict,
                                                                 self.officeTimeZone,
                                                                 self.fieldNameSuffix)
        if tableText.strip():
            toaText = ("Estimated times of arrival -eta- of the initial tsunami wave "
                       "for places with a potential tsunami threat. Actual arrival times "
                       "may differ and the initial wave may not be the largest. A tsunami "
                       "is a series of waves and the time between waves can be five minutes "
                       "to one hour.")
            headerText = ("ESTIMATED TIMES OF ARRIVAL\n"
                          "--------------------------\n"
                          f"{self.amm.wrapText(toaText)}\n\n"
                          "--------------------------------------------------------------\n\n")
            text = f"{headerText}{tableText}"
        return text

    def recommendedActionsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        actionText = ("RECOMMENDED ACTIONS\n"
                      "-------------------\n")
        if not self.finalMessage:
            phraseList = [
                ("Government agencies responsible for the threatened coastal areas "
                 "should take action to inform and instruct any coastal populations "
                 "at risk in accordance with their own evaluation, procedures and "
                 "the level of threat."),
                ("Persons located in threatened coastal areas should stay alert areas "
                 "for information and follow instructions from national and local authorities."),
                ]
        else:
            phraseList = [
                ("Remain observant and exercise normal caution near the sea. Otherwise... "
                 "no action is required."),
                ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            actionText += f"{wrappedPhrase}\n\n"
        return actionText

    def tsunamiImpactsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        impactsText = ("POTENTIAL IMPACTS\n"
                       "-----------------\n")
        if not self.finalMessage:
            phraseList = [
                ("A tsunami is a series of waves. The time between wave crests can vary "
                 "from 5 minutes to an hour. The hazard may persist for many hours or "
                 "longer after the initial wave."),
                ("impacts can vary significantly from one section of coast to the next "
                 "due to local bathymetry and the shape and elevation of the shoreline."),
                ("Impacts can also vary depending upon the state of the tide at the time "
                 "of the maximum tsunami waves."),
                ("persons caught in the water of a tsunami may drown... be crushed by "
                 "debris in the water... or be swept out to sea."),
                ]
        else:
            phraseList = [
                ("Minor sea level fluctuations may occur in coastal areas near the "
                 "earthquake over the next few hours."),
                ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            impactsText += f"{wrappedPhrase}\n\n"
        return impactsText

    def additionalInfoStatement_text(self, productDict):
        '''
        @summary: Supports the creation of the additionalInfoStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ("NEXT UPDATE AND ADDITIONAL INFORMATION\n"
                "--------------------------------------\n")
        phraseList = []
        if not self.finalMessage:
            phraseList += [
                ("This message will be updated in one hour or sooner if the "
                 "situation warrants."),
                ]
        else:
            eventDict = self.agu.getAllEventDicts(productDict)[0]
            phraseList += [
                (f"This will be the final {self.amm.getWarningCenterByEventDict(eventDict)} statement issued for this event unless new "
                 "information is received or the situation changes."),
                ]
        phraseList += [
            ("Authoritative information about the earthquake from the United States "
             "Geological Survey can be found at earthquake.usgs.gov."),
            ("Further information about this event may be found at tsunami.gov.")]
        phraseList += self.amm.nonUsProductRegionsAdditionalInfo(self.productRegion)
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

