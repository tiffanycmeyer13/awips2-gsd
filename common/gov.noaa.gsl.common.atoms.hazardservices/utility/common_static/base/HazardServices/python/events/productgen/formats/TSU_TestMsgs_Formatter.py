# *** Override behavior of TSU_TestMsgs_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Formatter for Tsunami Test Messages
    @since: May 2024
    @author GSL Hazard Services Team
'''

import random
import AtomsDisseminationUtilities
import AtomsMessageMethods
import GeneralConstants
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

        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = ""
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
        productParts = self.hazardProductParts.productParts_TSU_TestMsgs(self.productDict)

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

    def summaryHeadline(self, productDict):
        '''
        @summary: Create the summaryHeadline product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "summaryHeadline",
                                     self.summaryHeadline_text, productDict)
        return text

    def tsuTestResponseBullet(self, productDict):
        '''
        @summary: Create the tsuTestResponseBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"), "tsuTestResponseBullet",
                                     self.tsuTestResponseBullet_text, productDict)
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
        if self.productRegion == "IntlPacCommTest":
            wmoId = "WEPA40"
            awipsId = "TSUPAC"
        elif self.productRegion == "IntlCarCommTest":
            wmoId = "WECA41"
            awipsId = "TSUCAX"
        elif self.productRegion == "PacificPublic":
            wmoId = "WEAK51"
            awipsId = "TSUAK1"
        elif self.productRegion in ["PacificSegmented", "Alaska"]:
            wmoId = "WEPA41"
            awipsId = "TSUWCA"
        elif self.productRegion == "AtlanticPublic":
            wmoId = "WEXX30"
            awipsId = "TSUATE"
        elif self.productRegion == "AtlanticSegmented":
            wmoId = "WEXX20"
            awipsId = "TSUAT1"
        wmoHeader = f"{wmoId} {officeId} {ddhhmmTime}\n{awipsId}\n"
        return wmoHeader

    def productHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        centerLocation = ""
        if self.siteID == "PTWC":
            startText = "TEST... TSUNAMI DUMMY - COMMUNICATIONS TEST ...TEST"
            centerLocation = self.amm.ptwcOfficeLocationEnglish()
            issueTime = self.getIssuanceTimeDate(["UTC"])
        elif self.siteID == "NTWC":
            startText = "TEST...Public Tsunami Message Number 1...TEST"
            centerLocation = self.amm.ntwcOfficeLocationEnglish()
            if self.productRegion in ["AtlanticPublic", "AtlanticSegmented"]:
                timeZone = "EST5EDT"
            elif self.productRegion in ["PacificPublic", "PacificSegmented"]:
                timeZone = "PST8PDT"
            elif self.productRegion == "Alaska":
                timeZone = "AKST9AKDT"
            issueTime = self.getIssuanceTimeDate([timeZone])
        if centerLocation:
            text = (f"{startText}\n"
                    f"{centerLocation}\n"
                    f"{issueTime}")
        return text

    def summaryHeadline_text(self, productDict):
        '''
        @summary: Supports the creation of the summaryHeadline product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        # Add ugcheader, vtecString, arealIst for segmented test messages
        text = ""
        if self.productRegion in ["AtlanticSegmented", "PacificSegmented", "Alaska"]:
            if self.productRegion == "AtlanticSegmented":
                text += ("GMZ130-132-135-150-155-230-231-232-235>237-250-255-330-335-\n"
                         "350-355-430-432-435-436-450-452-455-532-534-536-538-550-552-\n"
                         "555-557-630>636-650-655-730-750-752-755-765-830-836-850-853-\n"
                         "856-656-657-031-032-034-035-042>044-052>055-AMZ630-650-651-\n"
                         "550-552-555-450-452-454-330-350-352-354-250-252-254-256-131-\n"
                         "135>137-150>156-158-230-231-ANZ631>638-656-658-650-652-654-\n"
                         "430-431-450>455-331-332-335-338-340-345-350>355-230>237-250-\n"
                         "251-254-255-256-150>154-050>052-TXZ251-256-257-351-354-355-\n"
                         "451-454-455-234-242>247-342>347-442-443-447-214-236>238-313-\n"
                         "335>338-436>439-215-216-615-616-LAZ041-073-074-052>054-241-\n"
                         "252>254-066>070-076-078-MSZ086>088-ALZ261>266-FLZ201>206-008-\n"
                         "010-012-014-108-112>118-127-128-134-139-142-148-149-050-151-\n"
                         "155-160-162-165-069-075-076>078-174-074-154-168-172-173-347-\n"
                         "447-647-747-047-054-059-064-141-147-159-164-024-124-125-133-\n"
                         "138-GAZ153-154-165-166-117-119-139-141-SCZ048>052-054-056-\n"
                         "NCZ106-108-110-044>047-080-081-092>095-098-103-104-193>199-\n"
                         "203>205-015>017-030>032-102-VAZ084>096-098-523>525-099-100-\n"
                         "MDZ024-025-DEZ002>004-NJZ006-012>014-020>027-106-108-NYZ071>075-\n"
                         "078>081-176>179-CTZ009>012-RIZ002-004>008-MAZ007-014>016-019>024-\n"
                         "NHZ014-MEZ022>028-029-030-NBZ570-550-660-641-NSZ210-230-260-\n"
                         "250-110-120-130-170-160-150-140-270-280-320-410-450-440-430-\n"
                         "QCZ670-680-NLZ340-220-230-210-120-132-140-241-242-110-131-\n"
                         "540-530-570-520-510-560-610-720-710-730-740-750-760-770-")
            elif self.productRegion == "PacificSegmented":
                text += ("PZZ530-531-AKZ317>332-135-131-125-121-171-181-185-187-191-195-\n"
                         "BCZ130-230-250-260-280-160-142-141-150-121-122-220-210-922-\n"
                         "912-921-911-110-WAZ503-504-506-507-509>511-011-514>517-021-\n"
                         "558-559-ORZ001-002-021-022-CAZ006-043-087-101-103-104-109-\n"
                         "340>342-346-349-350-354-362-364-505-506-508-509-529-530-\n"
                         "549-550-552-")
            elif self.productRegion == "Alaska":
                text += "AKZ121-126-132-135-171-181-185-187-191-195-317>332-"
            text += (f"{self.getExpireTimeText()}-\n"
                     f"{self.getVetecStringText()}\n"
                     f"{self.getAreaList()}\n\n")

        if self.siteID == "PTWC":
            if self.productRegion == "IntlPacCommTest":
                text += ("THIS IS A TEST MESSAGE. THIS MESSAGE APPLIES TO AREAS WITHIN\n"
                        "AND BORDERING THE PACIFIC OCEAN AND ADJACENT SEAS...EXCEPT\n"
                        "ALASKA...BRITISH COLUMBIA...WASHINGTON...OREGON AND CALIFORNIA.\n\n")
            elif self.productRegion == "IntlCarCommTest":
                text += ("THIS IS A TEST MESSAGE. THIS MESSAGE APPLIES ONLY TO COUNTRIES\n"
                        "AND TERRITORIES WITHIN AND BORDERING THE CARIBBEAN SEA THAT\n"
                        "PARTICIPATE IN THE TSUNAMI AND OTHER COASTAL HAZARDS WARNING\n"
                        "SYSTEM FOR THE CARIBBEAN AND ADJACENT REGIONS - THE CARIBE-EWS.\n\n")
            text += "...TEST PTWC MONTHLY "
            text += "CARIBE-EWS " if self.productRegion == "IntlCarCommTest" else ""
            text += "COMMUNICATION TEST...\n\n"
        elif self.siteID == "NTWC":
            if self.productRegion in ["AtlanticPublic", "AtlanticSegmented",
                                      "PacificPublic", "PacificSegmented"]:
                text += f"{self.testMessageText()}"
            if self.productRegion in ["AtlanticPublic", "AtlanticSegmented"]:
                text += ("...ESTO ES UNA PRUEBA PARA DETERMINAR LOS TIEMPOS DE TRANSMISION\n"
                         "   ENVUELTOS EN LA DISEMINACION DE INFORMACION SOBRE TSUNAMIS...\n\n")
            if self.productRegion == "Alaska":
                text += ("...THIS IS A TEST OF TSUNAMI COMMUNICATIONS FOR THE STATE OF "
                         "   ALASKA...\n\n")
        return text

    def tsuTestResponseBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsuTestResponseBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        if self.siteID == "PTWC":
            text = self.ptwcTestText()
        elif self.siteID == "NTWC":
            text = self.ntwcResponsePartners()
            if self.productRegion != "Alaska":
                text += self.ntwcResponseContent()
                text += self.ntwcResponseChannels()
            if self.productRegion in ["PacificPublic", "AtlanticPublic"]:
                text += self.testMessageText()
        return text

    def ptwcTestText(self):
        '''
        @summary: Build a formatted text phrase listing all textual blocks of
        the PTWC test message
        @return: String
        '''
        text = ("PLEASE NOTE - THE WEBSITE FOR PTWC MESSAGES IS NOW AT\n"
                "                          TSUNAMI.GOV\n"
                "              THE FORMER WEBSITE HAS NOW BEEN RETIRED.\n"
                "              PLEASE UPDATE YOUR BOOKMARKS ACCORDINGLY.\n\n")
        phraseList = [
            ("THIS IS A TEST MESSAGE. THIS IS A SCHEDULED TEST OF THE "
             "COMMUNICATION METHODS USED TO DISSEMINATE TSUNAMI INFORMATION "
             "FROM THE PACIFIC TSUNAMI WARNING CENTER TO THE " + 
                ("PTWS TSUNAMI WARNING FOCAL POINTS." if self.productRegion == "IntlPacCommTest"
                else "CARIBE-EWS TSUNAMI WARNING FOCAL POINTS AND NATIONAL TSUNAMI WARNING CENTERS.")),
            ("THIS TEST IS CONDUCTED ON THE FIRST " + 
             ("TUESDAY" if self.productRegion == "IntlPacCommTest" else "THURSDAY") + 
             " OF EACH MONTH AT " + 
             ("2230" if self.productRegion == "IntlPacCommTest" else "1530") + 
             " UTC. THE MESSAGE IS SENT BY SEVERAL COMMUNICATIONS METHODS "
             "INCLUDING THE GLOBAL TELECOMMUNICATIONS SYSTEM OR GTS... THE "
             "AERONAUTICAL FIXED TELECOMMUNICATIONS NETWORK OR AFTN... BY "
             "EMAIL... AND BY TELEFAX."),
            ("THIS MESSAGE SHOULD ARRIVE BY ALL DESIGNATED METHODS WITHIN A FEW "
             "MINUTES OF ITS BEING DISSEMINATED. TSUNAMI WARNING FOCAL POINTS "
             "SHOULD CHECK THAT IT WAS RECEIVED BY ALL METHODS IN A TIMELY "
             "FASHION."),
            ("RESPONSE - IT IS ONLY NECESSARY TO RESPOND IF THE TEST WAS "
             "UNACCEPTABLY DELAYED OR NOT RECEIVED BY ONE OR MORE DESIGNATED "
             "COMMUNICATION METHODS. IN THAT CASE... PLEASE NOTIFY THE PACIFIC "
             "TSUNAMI WARNING CENTER BY EMAIL... INDICATING WHICH METHOD OR "
             "METHODS FAILED AND THE EMAIL OF A PERSON OR PERSONS TO CORRESPOND "
             "WITH REGARDING THE PROBLEM."),
            ("PACIFIC TSUNAMI WARNING CENTER EMAIL - COMMS@PTWC.NOAA.GOV"),
            (("THE IOC... THE U.S. CARIBBEAN TSUNAMI WARNING PROGRAM... AND " if self.productRegion == "IntlCarCommTest" else "") + 
             "THE PACIFIC TSUNAMI WARNING CENTER WILL WORK TO RESOLVE ANY "
             "COMMUNICATIONS PROBLEMS THAT ARE IDENTIFIED."),
            ("THIS IS A TEST MESSAGE. THANK YOU FOR YOUR PARTICIPATION IN THIS TEST.")
            ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase, "", "")
            text += f"{wrappedPhrase}\n\n"
        return text

    def ntwcResponsePartners(self):
        '''
        @summary: Build a formatted text phrase listing all required response partners
        for the NTWC test message
        @return: String
        '''
        text = ""
        partnerList = []
        if self.productRegion == "Alaska":
            partnerList = [
                    ("This test is being conducted to determine the effectiveness and "
                     "extent of dissemination of tsunami warning messages using the NOAA "
                     "Weather Radio broadcast and the Emergency Alert System in Alaska "
                     "only. Instructions for public and agency response are found on the "
                     "web at ready.alaska.gov."),
                     ("This is only a test.")
                     ]
        else:
            text = ("RESPONSES ARE REQUIRED FROM\n"
                    "---------------------------\n")
            if self.productRegion in ["AtlanticPublic", "AtlanticSegmented"]:
                partnerList = [
                    ("All Coastal Weather Forecast Offices in the Eastern and "
                     "Southern Regions - respond using tsunami message "
                     "acknowledgment (TMA) procedures. Emergency alert systems and "
                     "NOAA Weather Radio are NOT to be activated."),
                    ("State and Territorial Warning Points in ME, NH, MA, CT - "
                     "RI, NY, NJ, DE, MD, PA, VA, NC, SC, GA, FL, AL - "
                     "MS, LA, and TX."),
                    "Joint Typhoon Warning Center in Hawaii.",
                    ("Atlantic Storm Prediction Center NS, Government of Canada "
                     "Operations Center, and Saint-Pierre et Miquelon.")
                    ]
            elif self.productRegion in ["PacificPublic", "PacificSegmented"]:
                partnerList = [
                    "All Coastal Weather Forecast Offices in Alaska, Washington, Oregon and California",
                    "USAF 11th Rescue Coordination Center at Elmendorf AFB",
                    "California, Oregon, Washington and Alaska State Warning Points",
                    "Emergency Management British Columbia",
                    "The Pacific Storm Prediction Centre in British Columbia",
                    "Joint Typhoon Warning Center in Hawaii",
                    "U.S. Coast Guard 11th, 13th, 17th District Offices",
                    "U.S. Coast Guard Kodiak COMMSTA and CAMSPAC Point Reyes, CA",
                    "Canadian Coast Guard MCTS COMOX and/or Victoria",
                    "FAA Regional Operations Center in Seattle",
                    "All Pacific Coast TsunamiReady Community Warning Points."
                    ]
        for phrase in partnerList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        text += "\n"
        return text

    def ntwcResponseContent(self):
        '''
        @summary: Build a formatted text phrase listing the information to provide
        in a response
        @return: String
        '''
        text = ("RESPONSES SHOULD INCLUDE\n"
                "------------------------\n")
        responseList = [
            "Time-of-receipt",
            "Agency name",
            "Email address",
            "Phone number"
            ]
        for phrase in responseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n"
        text += "\n\n"
        return text

    def ntwcResponseChannels(self):
        '''
        @summary: Build a formatted text phrase listing the ways in which a response
        can be sent
        @return: String
        '''
        headerPhrase = ("Weather Service Offices should respond in accordance with local "
                        "directives. All others should reply by one of the available methods "
                        "below.")
        wrappedPhrase = self.amm.wrapText(headerPhrase, "", "")
        text = (f"{wrappedPhrase}\n\n\n"
                 "SEND RESPONSE BY\n"
                 "----------------\n")
        responseTypeList = [
            "Web - ntwc.arh.noaa.gov/commtest/index.html",
            "Email address - ntwc@noaa.gov",
            "AFTN address  - PAAQYQYX",
            "AWIPS         - TMA",
            "Fax           - 907-745-6071",
            ]
        for phrase in responseTypeList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n"
        text += "\n"
        return text

    def getExpireTimeText(self):
        '''
        @summary: Get the expire time string
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.tpc.getFormattedTime(self.getEndTime(), "%d%H%M",
                                         stripLeading=False, changeNoonMidnight=False)

    def getVetecStringText(self):
        '''
        @summary: Get the vtecrecord string
        @param productDict: The product-level dictionary
        @return: String
        '''
        startTime = self.tpc.getFormattedTime(self.issueTime, "%y%m%dT%H%MZ",
                                              stripLeading=False, changeNoonMidnight=False)
        endTime = self.tpc.getFormattedTime(self.getEndTime(), "%y%m%dT%H%MZ",
                                              stripLeading=False, changeNoonMidnight=False)
        etn = random.randint(1, 9999)
        vtecString = f"/T.NEW.PAAQ.TS.W.{etn:04d}.{startTime}-{endTime}/"
        return vtecString

    def getAreaList(self):
        '''
        @summary: Get area liststring
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        if self.productRegion == "PacificSegmented":
            text = ("Alaska, British Columbia, Washington, Oregon and California\n"
                    "coastal areas")
        elif self.productRegion == "AtlanticSegmented":
            text = ("The U.S. east coast, Gulf of America coasts, and Eastern \n"
                    "Canadian coastal areas")
        elif self.productRegion == "Alaska":
            text = ("SOUTHERN COASTAL AREAS OF ALASKA\n"
                    f"{self.getIssuanceTimeDate(['AKST9AKDT'])}"
                    )
        return text

    def getEndTime(self):
        '''
        @summary: Get the end time mills
        @return: Integer
        '''
        return int(self.issueTime) + (60 * GeneralConstants.MILLIS_PER_MINUTE)

    def testMessageText(self):
        '''
        @summary: Get the test message text
        @return: String
        '''
        return ("...THIS MESSAGE IS FOR TEST PURPOSES ONLY...\n\n"
                "...THIS IS A TEST TO DETERMINE TRANSMISSION TIMES INVOLVED IN THE\n"
                "   DISSEMINATION OF TSUNAMI INFORMATION...\n\n")
