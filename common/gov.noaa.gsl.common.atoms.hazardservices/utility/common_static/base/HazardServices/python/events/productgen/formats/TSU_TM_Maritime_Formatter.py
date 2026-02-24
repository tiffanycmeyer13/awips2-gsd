# *** Override behavior of TSU_TM_Maritime_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All

'''
    Description: Issued alongside TS.ThreatMessage hazard events
    when the coast of a county, territory, or geographically-named
    place immediately adjacent to a navigation area (NAVAREA) has
    a forecast of tsunami amplitudes of 0.3 m or greater.
    @since: June 2025
    @author GSL Hazard Services Team
    @todo:
    - Need to be able to handle when no amplitude forecast exists
'''

import AtomsDisseminationUtilities
import AtomsFcstObsUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMessageMethods
import GenericRegistryObjectDataAccess as GRODA
import GeometryFactory
import HazardProductParts
import NWS_Base_Formatter
from com.raytheon.uf.common.hazards.productgen import ProductUtils


class Format(NWS_Base_Formatter.Format):

    def runThisFormatter(self):
        '''
        @summary: A user-defined flag to determine whether to run
        this formatter by default
        @return: Boolean
        '''
        return True

    def initialize(self, productDict):
        '''
        @summary: Create instance variables visible to all methods
        in this class
        @param productDict: The product-level dictionary
        @return: New instance variables (i.e., self.hazardProductParts)
        '''
        super(Format, self).initialize(productDict)
        self.afou = AtomsFcstObsUtilities.AtomsFcstObsUtilities()
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = ""
        self.productRegion = productDict.get("productRegion")
        self.eventDict = self.getAllEventDicts(productDict)[0]
        self.finalThreatMessage = self.eventDict.get("isFinalThreatMessage")
        self.affectedNAVAREAs = self.checkIfNavigationalAreasAffected()
        self.isPractice = self.eventDict.get("practice")
        self.registryObjectType = "ATOMS_MaritimeMessageNumber"
        self.uniqueObjectId = (f"{self.eventDict.get('customId')}_"
                               f"{self.eventDict.get('productRegion')}")

    def amplitudeMinimum(self):
        '''
        @summary: The minimum amplitude needed at a station to check
        what naviational area (NAVAREA) the station is within
        @return: Float
        '''
        return 0.3

    def getAllCountries(self):
        '''
        @summary: Retrieve all countries from the affected navigational area
        (NAVAREA) dictionary
        @return: List of strings
        '''
        countryList = []
        for navarea in self.affectedNAVAREAs:
            countryList += self.affectedNAVAREAs[navarea]["location"]
        return sorted(countryList)

    def checkIfNavigationalAreasAffected(self):
        '''
        @summary: Check if any navigational areas (NAVAREAs) have a wave
        amplitude that exceeds the minimum height criteria (e.g., 0.3 m)
        @return: NoneType
        '''
        # Get all user-selected stations that have an amplitude >= 0.3 m
        forecastRunTable = self.eventDict.get(f"forecastRunTable{self.fieldNameSuffix}")
        validStations = self.afou.getStationsExceedingSomeAmplitudeFromForecastRunTable(forecastRunTable,
                                                                                        self.amplitudeMinimum())
        # No stations found, do not create message
        if not validStations:
            return False

        # Walk through station and determine if the station is in any of the NAVAREAs
        validAreas = {}
        navareaShapeDict = self.alu.navigationalAreaDictionary(True)
        for stationInfo in validStations:
            lat, lon = self.afou.convertLatLonStringToFloats(stationInfo[4])
            pt = GeometryFactory.createPoint([lon, lat])
            for navarea in navareaShapeDict:
                if pt.within(navareaShapeDict[navarea]):
                    stateOrCountry = stationInfo[3]
                    if navarea not in validAreas:
                        validAreas[navarea] = {"location": [stateOrCountry]}
                    elif stateOrCountry not in validAreas[navarea]["location"]:
                        validAreas[navarea]["location"].append(stateOrCountry)
                    break
        return validAreas

    def execute(self, productDict):
        '''
        @summary: Creates the message text for this formatter
        based on the contents of the product dictionary created
        by the product generator
        @param productDict: The product-level dictionary
        @return: A list of strings, each containing a block of
        text for a single message
        '''
        # Check if formatter should be run
        if not self.runThisFormatter():
            return []

        # Initialize the product dictionary
        self.initialize(productDict)

        # If affected NAVAREAs found then create message
        messages = []
        if self.affectedNAVAREAs:
            legacyText = self.createTextProduct()
            legacyText = ProductUtils.wrapLegacy(legacyText)
            self.validateText(legacyText)
            if self.issueFlag:
                self.writeMaritimeRegistryObject(productDict)
            messages.append(legacyText)
        return messages

    def getMaritimeMessageNumber(self):
        '''
        @summary: Get the maritime message number from the registry
        @param objectType: The object type (e.g., ATOMSMaritimeMessageNumber)
        @param uniqueID: The unique ID assigned to the object (e.g., Cat5a_abcd_Pr)
        @return: Integer
        '''
        queryParameters = [
            ("objectType", self.registryObjectType),
            ("uniqueID", self.uniqueObjectId),
            ]
        objectDicts = GRODA.queryObjects(queryParameters, self.isPractice)
        if objectDicts:
            return int(objectDicts[0]["messageNumber"])
        else:
            return 1

    def writeMaritimeRegistryObject(self, productDict):
        '''
        @summary: Write contents of the event-level dictionary to
        the registry
        @param productDict: The product-level dictionary
        @return: NoneType
        '''
        currentMessageNumber = self.getMaritimeMessageNumber()
        objectDict = {
            "objectType": self.registryObjectType,
            "uniqueID": self.uniqueObjectId,
            "messageNumber": currentMessageNumber + 1
            }
        GRODA.storeObject(objectDict, self.isPractice)

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
        productParts = self.hazardProductParts.productParts_TSU_Maritime(self.productDict)
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

    def productHeader(self, productDict):
        '''
        @summary: Create the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "productHeader",
                                     self.productHeader_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def navareaRecipients(self, productDict):
        '''
        @summary: Create the navareaRecipients product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "navareaRecipients",
                                     self.navareaRecipients_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def tsunamiThreat(self, productDict):
        '''
        @summary: Create the tsunamiThreat product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "tsunamiThreat",
                                     self.tsunamiThreat_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def tsunamiInfo(self, productDict):
        '''
        @summary: Create the tsunamiInfo product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "tsunamiInfo",
                                     self.tsunamiInfo_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def tsunamiForecast(self, productDict):
        '''
        @summary: Create the tsunamiForecast product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "tsunamiForecast",
                                     self.tsunamiForecast_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def recommendedActions(self, productDict):
        '''
        @summary: Create the recommendedActions product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "recommendedActions",
                                     self.recommendedActions_text, productDict, True)
        return self.getFormattedText(text)

    ######################################################
    #  Product Part Helper Methods
    ######################################################

    def productHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        messageNumber = f"{self.getMaritimeMessageNumber()}".zfill(2)
        startText = f"MARITIME TSUNAMI THREAT MESSAGE NUMBER {messageNumber}"
        officeLoc = self.amm.getOfficeLocation(self.siteID, self.backupSiteID)
        bestTimezone = self.alu.getPrimaryTimezoneByProductRegionAbbreviation(self.productRegion)
        timeText = self.tpc.formatDatetime(self.issueTime, '%H%M %Z %a %b %e %Y', bestTimezone).strip()
        return f"{startText}\n{officeLoc}\n{timeText}"

    def navareaRecipients_text(self, productDict):
        '''
        @summary: Supports the creation of the navareaRecipients product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        navAreaList = [f"NAVAREA {navarea}" for navarea in self.affectedNAVAREAs]
        navAreaString = self.tpc.joinStringsWithOxfordComma(navAreaList)
        text = f"THIS MESSAGE IS FOR {navAreaString}."
        return self.amm.wrapText(text, "", "")

    def tsunamiThreat_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiThreat product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        if self.finalThreatMessage:
            text = "THE TSUNAMI THREAT HAS NOW LARGELY PASSED."
        else:
            text = "A TSUNAMI THREAT IS OCCURRING."
        return self.amm.wrapText(text, "", "")

    def tsunamiInfo_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiInfo product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        eventDescription = self.amm.getPhysicalEventDescriptionString(self.eventDict,
                                                                      self.fieldNameSuffix)
        text = f"A TSUNAMI WAS GENERATED BY {eventDescription.upper()}"
        return self.amm.wrapText(text, "", "")

    def tsunamiForecast_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiForecast product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        if not self.finalThreatMessage:
            countryText = self.tpc.joinStringsWithOxfordComma(self.getAllCountries())
            text = f"HAZARDOUS TSUNAMI WAVES ARE FORECAST FOR SOME COASTS OF {countryText.upper()}."
        return self.amm.wrapText(text, "", "")

    def recommendedActions_text(self, productDict):
        '''
        @summary: Supports the creation of the recommendedActions product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        if self.finalThreatMessage:
            phraseList = [
                ("HOWEVER, SHIPS APPROACHING THE COAST SHOULD STILL CONSULT LOCAL "
                 "AUTHORITIES REGARDING LOCAL CONDITIONS AND ADVICES.")
                ]
        else:
            phraseList = [
                ("TSUNAMI WAVES ARE NOT A HAZARD TO SHIPS IN DEEP WATER BUT CAN "
                 "CAUSE STRONG CURRENTS AND RAPID SEA LEVEL CHANGES IN SHALLOW "
                 "WATER AS WELL AS INUNDATION OF THE COAST."),
                ("SHIPS APPROACHING THE COAST SHOULD CONSULT LOCAL AUTHORITIES "
                 "REGARDING LOCAL CONDITIONS AND ADVICES.")
                ]

        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase, "", "")
            text += f"{wrappedPhrase}\n\n"
        return text
