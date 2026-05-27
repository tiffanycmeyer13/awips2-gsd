# *** Override behavior of ADA_TextFormatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Text formatter for Tsunami Conference Call products
    @since: February 2023
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsMessageMethods
import HazardProductParts
import NWS_Base_Formatter
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

        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = ""

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
        productParts = self.hazardProductParts.productParts_ADA(self.productDict)

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

    def headlineStatement(self, productDict):
        '''
        @summary: Create the headlineStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        statement = self.processPartValue(productDict.get("productBeginDict"),
                                          "headlineStatement", self.headlineStatement_text,
                                          productDict)
        statement = statement.strip().strip(".").upper()
        return self.getFormattedText(statement, startText="...", endText="...\n")

    def whatBullet(self, productDict):
        '''
        @summary: Create the whatBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"),
                                     "whatBullet", self.whatBullet_text, productDict)
        return text

    ######################################################
    #  Helper Methods
    ######################################################

    def wmoHeader_text(self, productDict):
        '''
        @summary: Helper method to assemble the wmoHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        officeId = self.amm.getOfficeIdBySiteId(self.siteID)
        ddhhmmTime = self.tpc.getFormattedTime(self.issueTime, "%d%H%M",
                                               stripLeading=False)
        wmoHeader = f"ADA {officeId} {ddhhmmTime}"
        return wmoHeader

    def headlineStatement_text(self, productDict):
        '''
        @summary: Helper method to assemble the headlineStatement product part
        @see: The headlineStatement() method contains additional header and footer
        formatting for this product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return "TSUNAMI TELECONFERENCE IS SCHEDULED"

    def whatBullet_text(self, productDict):
        '''
        @summary: Helper method to assemble the whatBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        callLocation = productDict.get("callLocation")
        if callLocation == "Pacific":
            regionParticipantsText = self.pacificRegionText()
            timeZones = self.pacificRegionTimeZones()
        else:
            # Defaults to Atlantic
            regionParticipantsText = self.atlanticRegionText()
            timeZones = self.atlanticRegionTimeZones()
        # Get formatted string of time zones
        callTime = productDict.get("callTime")
        timeZoneText = self.getTimeZoneText(callTime, timeZones)

        return ("A TELECONFERENCE CONCERNING THE ONGOING TSUNAMI IS SCHEDULED FOR\n"
            "---------------------------------------------------------------------\n"
            f"{regionParticipantsText}\n"
            "THE TELECONFERENCE WILL BE LED BY THE NATIONAL TSUNAMI\n"
            "WARNING CENTER.\n\n"
            "THE TELECONFERENCE WILL BE HELD AT\n"
            "----------------------------------\n"
            f"{timeZoneText}\n"
            f"{self.getPhoneNumberAndPassword()}")

    def atlanticRegionText(self):
        '''
        @summary: The participants in an Atlantic tsunami conference call
        @return: String
        '''
        text = ""
        phraseList = [
            "ATLANTIC AND GULF OF AMERICA COASTAL WEATHER FORECAST OFFICES",
            "ATLANTIC AND GULF OF AMERICA COASTAL STATE WARNING POINTS",
            "ATLANTIC AND GULF OF AMERICA FEMA REGIONAL OFFICES",
            "ATLANTIC AND GULF OF AMERICA US COAST GUARD DISTRICT OFFICES",
            "PUERTO RICO AND VIRGIN ISLAND EMERGENCY MANAGEMENT AGENCIES",
            "PUERTO RICO SEISMIC NETWORK",
            ]
        for phrase in phraseList:
            wrappedText = self.amm.wrapText(phrase)
            text += f"{wrappedText}\n"
        return text

    def pacificRegionText(self):
        '''
        @summary: The participants in a Pacific tsunami conference call
        @return: String
        '''
        text = ""
        phraseList = [
            "PACIFIC COASTAL WEATHER FORECAST OFFICES",
            "WEST COAST STATE WARNING POINTS",
            "U.S. COAST GUARD DISTRICT OFFICES",
            "THE BRITISH COLUMBIA PROVINCIAL EMERGENCY PROGRAM",
            ]
        for phrase in phraseList:
            wrappedText = self.amm.wrapText(phrase)
            text += f"{wrappedText}\n"
        return text

    def getTimeZoneText(self, callTime, timezoneList):
        '''
        @summary: Create the time zone block of text for this message
        @param callTime: Time of the conference call in epoch milliseconds
        @param timezoneList: Basin-specific time zones specified by either the
        atlanticRegionTimeZones() or pacificRegionTimeZones() method
        @return: String
        Example:
             * 1545 AKDT Jun 16 2024
             * 1645 PDT Jun 16 2024
             * 2345 UTC Jun 16 2024
        '''
        callTimeDT = TimeUtil.epochTimeMillisToDatetime(callTime)
        timeFormat = "%H%M %Z %b %e %Y"
        timeText = ""
        for singleTZ in timezoneList:
            tzTimeDT = TimeUtil.changeTimezoneOfDatetimeObject(callTimeDT, singleTZ)
            timezoneString = tzTimeDT.strftime(timeFormat)
            timeText += f"{self.amm.wrapText(timezoneString)}\n"
        return timeText

    def atlanticRegionTimeZones(self):
        '''
        @summary: The time zones to be listed in an Atlantic tsunami conference call
        @return: List of strings
        @see: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list
        of names
        '''
        return ["CST6CDT", "EST5EDT", "AST4ADT", "UTC"]

    def pacificRegionTimeZones(self):
        '''
        @summary: The time zones to be listed in a Pacific tsunami conference call
        @return: List of strings
        @see: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list
        of names
        '''
        return ["AKST9AKDT", "PST8PDT", "UTC"]

    def getPhoneNumberAndPassword(self):
        '''
        @summary: The phone number and password phrase
        @return: String
        '''
        return "CALL 1-877-708-6816 PASSCODE 2763065#"
