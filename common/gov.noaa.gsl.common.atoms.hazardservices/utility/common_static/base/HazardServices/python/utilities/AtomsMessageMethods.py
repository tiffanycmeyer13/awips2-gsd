# *** Override behavior of AtomsMessageMethods.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Contains methods that supports the tsunami message creation

    @since: June 2024
    @author: GSL Hazard Services Team
'''
import collections
import datetime
import textwrap
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsTableSeaLevelObservations
import Bridge
import CallsToActionAndImpacts
import GeneralConstants
import HazardConstants
import TextProductCommon
import TimeUtil
from gov.noaa.gsl.viz.atoms import ReverseTTTClientUtils
from gov.noaa.gsl.common.dataplugin.atoms import ReverseTTTRegion


class AtomsMessageMethods(object):

    def __init__(self):
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.bridge = Bridge.Bridge()
        self.ctaImpact = CallsToActionAndImpacts.CallsToActionAndImpacts()
        self.tpc = TextProductCommon.TextProductCommon()

    def productRegionsWithSpanish(self):
        '''
        @summary: A list of product regions that require a Spanish language
        message to be created
        @return: A list
        '''
        return ["AkBcWc", "EcGc", "Pr"]

    def productRegionsWithSegmented(self):
        '''
        @summary: A list of product regions that require a segmented message with
        Valid Time Event Code (VTEC) information
        @return: A list
        '''
        return ["AkBcWc", "EcGc", "Pr"]

    def nonUsProductRegions(self):
        '''
        @summary: A list of product regions that is non U.S. product region
        @return: A list
        '''
        return ["Pac", "Car"]

    '''
    NTWC Configurable location phrases
    '''

    def ntwcOfficeId(self):
        '''
        @summary: The office ID for NTWC
        @return: String
        '''
        return "PAAQ"

    def ntwcOfficeLocationEnglish(self):
        '''
        @summary: The location of NTWC in English
        @return: String
        '''
        return "NWS National Tsunami Warning Center Palmer AK"

    def ntwcOfficeLocationSpanish(self):
        '''
        @summary: The location of NTWC in Spanish
        @return: String
        '''
        return "NWS Centro Nacional de Alerta de Tsunami Palmer AK"

    def wmoAndAwipsInfoDict_NTWC(self):
        '''
        @summary: A dictionary containing the AWIPS ID, WMO ID, and product description for
        the NTWC messages. The keys in the dictionary consist of the following:
            - {Procedural_Region_Abbreviation}.{PIL}.{Formatter_Type}
        @return: Dictionary
        '''
        return {
            "AkBcWc.TSU.Pub": {
                "awipsID": "TSUAK1",
                "wmoID": "WEAK51",
                "productDescr": "Tsunami Warnings, Watches, and Advisories for AK, BC, and U.S. West Coast",
                },
            "AkBcWc.TSU.Std": {
                "awipsID": "TSUWCA",
                "wmoID": "WEPA41",
                "productDescr": "Segmented Tsunami Warnings, Watches, and Advisories for AK, BC, and U.S. West Coast",
                },
            "AkBcWc.TSU.Spanish": {
                "awipsID": "TSUSPN",
                "wmoID": "WEAK61",
                "productDescr": "Spanish Tsunami Warnings, Watches, and Advisories for AK, BC, and U.S. West Coast",
                },
            "AkBcWc.TIB.Pub": {
                "awipsID": "TIBAK1",
                "wmoID": "WEAK53",
                "productDescr": "Tsunami Information Statements for AK, BC, and U.S. West Coast",
                },
            "AkBcWc.TIB.Spanish": {
                "awipsID": "TIBSPN",
                "wmoID": "WEAK63",
                "productDescr": "Spanish Tsunami Information Statements for AK, BC, and U.S. West Coast",
                },
            "EcGc.TSU.Pub": {
                "awipsID": "TSUATE",
                "wmoID": "WEXX30",
                "productDescr": "Tsunami Warnings, Watches, and Advisories for U.S. East Coast, Gulf of America and Canada",
                },
            "EcGc.TSU.Std": {
                "awipsID": "TSUAT1",
                "wmoID": "WEXX20",
                "productDescr": "Segmented Tsunami Warnings, Watches, and Advisories for U.S. East Coast, Gulf of America and Canada",
                },
            "EcGc.TSU.Spanish": {
                "awipsID": "TSUSPA",
                "wmoID": "WEXX40",
                "productDescr": "Spanish Tsunami Warnings, Watches, and Advisories for U.S. East Coast, Gulf of America and Canada",
                },
            "EcGc.TIB.Pub": {
                "awipsID": "TIBATE",
                "wmoID": "WEXX32",
                "productDescr": "Tsunami Information Statements for U.S. East Coast, Gulf of America and Canada",
                },
            "EcGc.TIB.Spanish": {
                "awipsID": "TIBSPA",
                "wmoID": "WEXX42",
                "productDescr": "Spanish Tsunami Information Statements for U.S. East Coast, Gulf of America and Canada",
                },
            }

    '''
    PTWC Configurable location phrases
    '''

    def ptwcOfficeId(self):
        '''
        @summary: The office ID for PTWC
        @return: String
        '''
        return "PHEB"

    def ptwcOfficeLocationEnglish(self):
        '''
        @summary: The location of PTWC in English
        @return: String
        '''
        return "NWS Pacific Tsunami Warning Center Honolulu HI"

    def ptwcOfficeLocationSpanish(self):
        '''
        @summary: The location of PTWC in Spanish
        @return: String
        '''
        return "NWS Centro de Alerta de Tsunamis del Pacífico de Honolulu HI"

    def wmoAndAwipsInfoDict_PTWC(self):
        '''
        @summary: A dictionary containing the AWIPS ID, WMO ID, and product description for
        the PTWC messages. The keys in the dictionary consist of the following:
            - {Procedural_Region_Abbreviation}.{PIL}.{Formatter_Type}
        @return: Dictionary
        '''
        return {
            "Hi.TSU.Pub": {
                "awipsID": "TSUHWX",
                "wmoID": "WEHW40",
                "productDescr": "Tsunami Warnings, Watches, and Advisories for Hawaii",
                },
            "Hi.TIB.Pub": {
                "awipsID": "TIBHWX",
                "wmoID": "WEHW42",
                "productDescr": "Tsunami Information Statements for Hawaii",
                },
            "As.TSU.Pub": {
                "awipsID": "TSUPPG",
                "wmoID": "WEZS40",
                "productDescr": "Tsunami Warnings, Watches, and Advisories for American Samoa",
                },
            "As.TIB.Pub": {
                "awipsID": "TIBPPG",
                "wmoID": "WEZS42",
                "productDescr": "Tsunami Information Statements for American Samoa",
                },
            "Gu.TSU.Pub": {
                "awipsID": "TSUGUM",
                "wmoID": "WEGM40",
                "productDescr": "Tsunami Warnings, Watches, and Advisories for Guam/CNMI",
                },
            "Gu.TIB.Pub": {
                "awipsID": "TIBGUM",
                "wmoID": "WEGM42",
                "productDescr": "Tsunami Information Statements for Guam/CNMI",
                },
            "Pr.TSU.Pub": {
                "awipsID": "TSUCAR",
                "wmoID": "WECA40",
                "productDescr": "Tsunami Warnings, Watches, and Advisories for Puerto Rico/Virgin Islands",
                },
            "Pr.TSU.Std": {
                "awipsID": "TSUCA1",
                "wmoID": "WECA60",
                "productDescr": "Segmented Tsunami Warnings, Watches, and Advisories for Puerto Rico/Virgin Islands",
                },
            "Pr.TSU.Spanish": {
                "awipsID": "TSUSP1",
                "wmoID": "WECA50",
                "productDescr": "Spanish Tsunami Warnings, Watches, and Advisories for Puerto Rico/Virgin Islands",
                },
            "Pr.TIB.Pub": {
                "awipsID": "TIBCAR",
                "wmoID": "WECA42",
                "productDescr": "Tsunami Information Statements for Puerto Rico/Virgin Islands",
                },
            "Pr.TIB.Spanish": {
                "awipsID": "TIBSP1",
                "wmoID": "WECA52",
                "productDescr": "Spanish Tsunami Information Statements for Puerto Rico/Virgin Islands",
                },
            "Pac.TSU.Pub": {
                "awipsID": "TSUPAC",
                "wmoID": "WEPA40",
                "productDescr": ("Tsunami Warning, Watch, and/or Advisory Bulletin issued by Pacific Tsunami "
                                 "Warning Center (PTWC) to its U.S. and international AOR for confirmed or "
                                 "potentially destructive teletsunamis generated anywhere in the Pacific Basin."),
                },
            "Pac.TIB.Pub": {
                "awipsID": "TIBPAC",
                "wmoID": "WEPA42",
                "productDescr": "Tsunami Information Statements for the Pacific Basin",
                },
            "Car.TSU.Pub": {
                "awipsID": "TSUCAX",
                "wmoID": "WECA41",
                "productDescr": ("Tsunami Warning, Watch, and/or Advisory Bulletin issued by Pacific Tsunami Warning "
                                 "Center (PTWC) to its U.S. and international AOR for confirmed or potentially destructive "
                                 "teletsunamis generated anywhere in the Atlantic Basin."),
                },
            "Car.TIB.Pub": {
                "awipsID": "TIBCAX",
                "wmoID": "WECA43",
                "productDescr": "Tsunami Information Statements for the Atlantic Basin",
                },
            }

    '''
    Shared configurable phrases
    '''

    def ctaCategoryDictionary(self):
        return {
            "TS.W": ["ctaTsunamiWarningAreaGuidance"],
            "TS.A": ["ctaTsunamiWatchAreaGuidance"],
            "TS.B": ["ctaTsunamiMoveAwayFromWater", "ctaTsunamiFollowInstructions",
                     "ctaTsunamiMoveInlandIfEarthquake", "ctaTsunamiBoatOperators",
                     "ctaTsunamiDoNotGoToShore", "ctaTsunamiDoNotReturnToCoast"],
            }

    def impactCategoryDictionary(self):
        return {
            "TS.W": ["impactDamagingWavePowerfulCurrentsPossible", "impactRepeatedCoastalFloodingPossible",
                     "impactWavesCanDrownAndDestroy", "impactDebrisCauseInjuriesAndDamage",
                     "impactCurrentsWavesDestructive"],
            "TS.Y": ["impactStrongWaveCurrentPossible", "impactDrownInjurePeopleInWater",
                     "impactCurrentsBeachesHarborsDangerous"],
            "TS.Z": ["impactHoursToDaysAfterFirstWave", "impactFirstWaveNotLargest",
                     "impactWaveLast5to45Minutes", "impactCoastsAllDirectionsThreatened",
                     "impactStrongShakingEarthquakeOccurredTsunamiImminent",
                     "impactSignsOfATsunami", "impactTsunamiMayAppearAs"],
            }

    '''
    Methods to create/update phrases in the Tsunami Formatters
    '''

    def getOfficeLocationBySiteID(self, siteID, language=""):
        '''
        @summary: Given a site ID (e.g., NTWC) and a language, get the office location
        @param siteID: The site id (e.g., NTWC)
        @param language: The language of the product, choices are "Spanish" or it defaults
        to English
        @return: String
        '''
        if self.isSpanish(language):
            if siteID == "NTWC":
                return self.ntwcOfficeLocationSpanish()
            else:
                return self.ptwcOfficeLocationSpanish()
        else:
            if siteID == "NTWC":
                return self.ntwcOfficeLocationEnglish()
            else:
                return self.ptwcOfficeLocationEnglish()

    def getOfficeLocation(self, siteID, backupSiteID, language=""):
        '''
        @summary: Get the office location depending on the site and language
        @param siteID: The site id (e.g., NTWC)
        @param backupSiteID: The site id being backed up (e.g., PTWC); for non-backup
        operations, both siteID and backupSiteID will be the same
        @param language: The language of the product, choices are "Spanish" or it defaults
        to English
        @return: String
        '''
        officeLocationText = self.getOfficeLocationBySiteID(siteID, language)
        if siteID != backupSiteID:
            issuedByText = self.getEnglishSpanishDict(language)["issuedByText"]
            issuePrefix = self.capitalizeFirstLetter(issuedByText)
            backupOffice = self.getOfficeLocationBySiteID(backupSiteID, language)
            officeLocationText += f"\n{issuePrefix} {backupOffice}"
        return officeLocationText

    def replaceSiteIdWithOfficeId(self, inputText, siteID):
        '''
        @summary: Replace site ID (NTWC or PTWC) with office ID (PAAQ or PHEB)
        @param inputText: The input text string to search
        @param siteID: The site ID (i.e., NTWC or PTWC)
        @return: String
        '''
        if siteID == "NTWC":
            inputText = inputText.replace("NTWC", self.ntwcOfficeId())
        elif siteID == "PTWC":
            inputText = inputText.replace("PTWC", self.ptwcOfficeId())
        return inputText

    def wmoHeader_text(self, productDict, issueTime, region, formatterType):
        '''
        @summary: Helper method to build the wmoHeader product part
        @param productDict: The product-level dictionary
        @param issueTime: The hazard event issue time as a datetime object
        @param region: The product region abbreviation (i.e., 'Hi')
        @param formatterType: The type of the formatter (i.e., Pub or Spanish)
        @return: String and an updated productDict in memory
        '''
        # Get the AWIPS site from the product dictionary
        siteID = productDict.get("siteID")
        # Build the information dictionary
        infoDict = self.getAwipsInfoDict(region, productDict.get("productID"), formatterType, siteID)
        wmoID = infoDict.get("wmoID")
        officeId = infoDict.get("officeID")
        ddhhmmTime = self.tpc.getFormattedTime(issueTime, "%d%H%M", stripLeading=False)
        awipsID = infoDict.get("awipsID")
        # Only assign wmoID of a bulleted format to productDict which will
        # be displayed in "Product ID" section of TSU CAP message.
        if formatterType == "Pub":
            productDict["wmoID"] = wmoID
            productDict["productDescr"] = infoDict.get("productDescr")
            productDict["awipsId"] = awipsID
            productDict["officeId"] = officeId
        return f"{wmoID} {officeId} {ddhhmmTime}\n{awipsID}"

    def productHeaderStart_text(self, productDict, productID, language="", isPublic=False):
        '''
        @summary: Helper method to build the productHeader product part
        @param productDict: The product-level dictionary
        @param productID: The product identifier (i.e., TSU)
        @param language: The text language
        @return: String
        '''
        text = ""
        if productID in ["TSU", "TSU_TM"]:
            if productID == "TSU":
                text += "BULLETIN\n"
            if self.isSpanish(language):
                text += "Mensaje de Tsunami numero"
            else:
                if isPublic and productDict.get("siteID") == "NTWC":
                    text += "Public "
                text += "Tsunami Message Number"
        elif productID == "TIB":
            if self.isSpanish(language):
                text += "Boletin Informativo de Tsunami Numero"
            else:
                text += "Tsunami Information Statement Number"
        msgNum = self.agu.getTsunamiMessageNumber(productDict)
        text += f" {msgNum}\n"
        return text

    def getProductLevelTimezone(self, productDict):
        '''
        @summary: Loop over the segments in the product dictionary and get
        the timezone used the most frequently. If there is a tie, use the first
        one as it is associated with the highest priority segment
        @param productDict: The product-level dictionary
        @return: String
        @note: NWS 10-1701 directive states:
        In certain national products that span multiple time zones issued by NCs,
        the time may be shown in UTC, rather than local time.
        '''
        # Get all timezones found at the segment-level
        timezoneList = []
        for segmentDict in productDict.get("segments"):
            timezoneList += segmentDict.get("timeZones")
        timezoneList = list(set(timezoneList))
        # Use found time zone or UTC if multiple timezones found
        if len(timezoneList) == 1:
            return timezoneList[0]
        else:
            return "UTC"

    def getSummaryHeadlinesWithLocationText(self, segmentDict, headlineText, siteID):
        '''
        @summary: Add the location text to the summary headline
        @param segmentDict: The segment-level dictionary
        @param headlineText: Original headline text
        @param siteID: The current site ID (e.g., NTWC)
        @return: Return the summary headline with location text
        '''
        headline = headlineText
        locationText = ""
        eventDict = self.agu.getAllEventDicts(segmentDict)[0]
        productRegion = eventDict.get("productRegion")
        if siteID == "PTWC":
            locationList = segmentDict.get("subRegionLocations")
            locationText = self.getPTWC_HeadlineLocations(productRegion, locationList)
        else:
            locationText = f"the {self.getAreaListTextSegment(segmentDict, productRegion)}"
        if locationText:
            if "INCLUDE" in headlineText:
                forPrefix = ""
            else:
                forPrefix = "FOR "
            headline = headline.rstrip("...")
            headline += f" {forPrefix}{locationText.upper()}..."
        headline += "\n\n"
        return headline

    def getUpdatesBulletText(self, productDict, suffix, language=""):
        '''
        @summary: Helper method to create the updatesBullet product part
        @param productDict: The product-level dictionary
        @param suffix: The field name suffix
        @param language: The language (default is English)
        @return: String
        '''
        phraseDict = self.getEnglishSpanishDict(language)
        headerText = phraseDict["updatesText"].upper()
        dashText = self.tpc.getDashesUnderString(headerText, "\n")
        updateHeader = f"{headerText}\n{dashText}"
        updates = ""
        # Get updates text from both user input and predefined sections
        userInputUpdates = productDict.get(f"userInputUpdates{suffix}")
        predefinedUpdatesIDs = productDict.get(f"predefinedUpdates{suffix}_identifiers")
        if predefinedUpdatesIDs is None:
            return updates
        if userInputUpdates:
            updates += f" * {userInputUpdates}\n"

        stringListKey = f"predefinedUpdates{suffix}"
        if self.isSpanish(language):
            stringListKey = f"predefinedUpdates{suffix}_spanish"
        predefinedUpdates = productDict.get(stringListKey)
        for update in predefinedUpdates:
                updates += f" * {update}\n"
        # If there are no updates, display this default message
        if not updates:
            updateText = self.capitalizeFirstLetter(phraseDict["noUpdatesText"])
            updates = f"{updateText}\n"
        updates = f"{updateHeader}{updates}\n"

        return updates

    def physicalEventParametersBullet_text(self, inputDict, suffix, language=""):
        '''
        @summary: Helper method to create the physicalEventParametersBullet product part
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param suffix: The field name suffix
        @param language: The language (default is English)
        @return: String
        '''
        text = ""
        if inputDict.get("productID"):
            customId = inputDict.get("customId")
            peType = inputDict.get("physicalEventType")
            eventDicts = self.agu.getAllEventDicts(inputDict)
            for eventDict in eventDicts:
                if (eventDict.get("customId") == customId and
                    eventDict.get("physicalEventType") == peType):
                    break
        else:
            eventDict = self.agu.getAllEventDicts(inputDict)[0]
            customId = eventDict.get("customId")
            peType = eventDict.get("physicalEventType")
        originTimeText = self.formatOriginTime(eventDict, suffix, language)
        lonlatText = self.createLatLongText(eventDict, suffix, language)
        locationTableText = self.createLocationTextForTable(eventDict, suffix, language)
        if self.agu.isPhysicalEventTypeSeismic(eventDict.get("physicalEventType")):
            magnitude = eventDict.get(f"magnitude{suffix}")
            magnitudeText = f"{magnitude}"
            # Get the number of stations to average the magnitude for observatory message
            if eventDict.get("hazardType") == "TS.ObservatoryMessage":
                numStation = eventDict.get("numStationAverage")
                if numStation > 0:
                    magnitudeText += f" - {numStation} station average"
            depthText = self.getDepthText(eventDict, suffix, language)
            if self.isSpanish(language):
                headerText = "PARAMETROS PRELIMINARES DEL TERREMOTO"
                dashText = self.tpc.getDashesUnderString(headerText, "\n")
                text = (f"{headerText}\n{dashText}"
                        "Los siguientes parámetros se basan en una evaluación\n"
                        "preliminar rápida del terremoto y pueden ocurrir cambios.\n\n"
                        f" * Magnitud           {magnitudeText}\n"
                        f" * Tiempo de Origen   {originTimeText}\n"
                        f" * Coordenadas        {lonlatText}\n"
                        f" * Profundidad        {depthText}\n"
                        f" * Localizacion       {locationTableText}")
            else:
                headerText = "PRELIMINARY EARTHQUAKE PARAMETERS"
                dashText = self.tpc.getDashesUnderString(headerText, "\n")
                text = (f"{headerText}\n{dashText}"
                        "The following parameters are based on a rapid preliminary\n"
                        "assessment of the earthquake and changes may occur.\n\n"
                        f" * Magnitude        {magnitudeText}\n"
                        f" * Origin Time      {originTimeText}\n"
                        f" * Coordinates      {lonlatText}\n"
                        f" * Depth            {depthText}\n"
                        f" * Location         {locationTableText}")
        else:
            physicalEventFeatureName = eventDict.get(f"peName{suffix}")
            if self.isSpanish(language):
                headerText = f"Parametros preliminares para {peType} {customId}"
                dashText = self.tpc.getDashesUnderString(headerText, "\n")
                text = (f"{headerText}\n{dashText}"
                        f" * Tiempo de Origen   {originTimeText}\n"
                        f" * Coordenadas        {lonlatText}\n"
                        f" * Nombre             {physicalEventFeatureName}\n"
                        f" * Localizacion       {locationTableText}")
            else:
                headerText = f"Preliminary Parameters for {peType} {customId}"
                dashText = self.tpc.getDashesUnderString(headerText, "\n")
                text = (f"{headerText}\n{dashText}"
                        f" * Origin Time      {originTimeText}\n"
                        f" * Coordinates      {lonlatText}\n"
                        f" * Name             {physicalEventFeatureName}\n"
                        f" * Location         {locationTableText}")
        return text

    def getDepthText(self, eventDict, suffix, language=""):
        '''
        @summary: Create depth text description
         @param eventDict: The event-level dictionary
        @param suffix: The field name suffix provided to some megawidgets
        @param language: The language ("English" or "Spanish")
        @return: String
        '''
        milesText = self.getEnglishSpanishDict(language)["milesText"]
        originDepthInMi = eventDict.get(f"originDepth{suffix}")
        depthInMi = round(originDepthInMi)
        productRegionAbbrev = eventDict.get("productRegion")
        if productRegionAbbrev in self.nonUsProductRegions() or productRegionAbbrev == "Pr":
            depthInKm = round(originDepthInMi * GeneralConstants.KILOMETERS_PER_MILE)
            if productRegionAbbrev == "Pr":
                depthText = f"{depthInMi} {milesText} / {depthInKm} km"
            else:
                depthText = f"{depthInKm} km / {depthInMi} {milesText}"
        else:
            depthText = f"{depthInMi} {milesText}"
        return depthText

    def formatOriginTime(self, eventDict, suffix, language):
        '''
        @summary: Create an origin time text block containing multiple time zones
        @param eventDict: The event-level dictionary
        @param suffix: The field name suffix provided to some megawidgets
        @param language: The language ()
        @return: String
        '''
        originTimeMillis = eventDict.get(f"originTime{suffix}")
        originTimeDT = TimeUtil.epochTimeMillisToDatetime(originTimeMillis)
        productRegionAbbrev = eventDict.get("productRegion")
        timezoneList = self.alu.getTimezonesByProductRegionAbbreviation(productRegionAbbrev)
        siteID = eventDict.get("siteID")
        formatTZ = "%Z"
        if siteID == "NTWC" or productRegionAbbrev in self.nonUsProductRegions():
            formatHHMM = "%H%M"
            formatDate = "%b %d %Y"
        elif siteID == "PTWC":
            formatHHMM = "%-I%M %p"
            formatDate = "%b %-d %Y"
        originTimeList = []
        for singleTZ in timezoneList:
            originTimeText = ""
            if "AK" in singleTZ:
                numSpaces = 19
            else:
                numSpaces = 20
            if self.isSpanish(language):
                numSpaces += 2
            subBulletText = " " * numSpaces
            if originTimeList:
                originTimeText += subBulletText
            dt = TimeUtil.changeTimezoneOfDatetimeObject(originTimeDT, singleTZ)
            HHMM = dt.strftime(formatHHMM)
            tzString = dt.strftime(formatTZ)
            if siteID == "NTWC":
                tzString = tzString.rjust(4)
            dateString = dt.strftime(formatDate)
            originTimeText += f"{HHMM} {tzString} {dateString}"
            originTimeList.append(originTimeText)
        originTimeText = "\n".join(originTimeList)
        return originTimeText

    def createLatLongText(self, inputDict, suffix, language=""):
        '''
        @summary: Create a text string with the lat/lon information
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param suffix: The field name suffix
        @param language: The language (default is English)
        @return: String
        '''
        phraseDict = self.getEnglishSpanishDict(language)
        latitude = inputDict.get(f"originLatitude{suffix}")
        longitude = inputDict.get(f"originLongitude{suffix}")
        latLabel = phraseDict["northText"] if latitude >= 0.0 else phraseDict["southText"]
        longLabel = phraseDict["eastText"] if longitude >= 0.0 else phraseDict["westText"]
        latLonText = f"{abs(latitude):.1f} {latLabel} {abs(longitude):.1f} {longLabel}"
        return latLonText.title()

    def createLocationTextForTable(self, inputDict, suffix, language=""):
        '''
        @summary: Create a text string with the location information
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param suffix: The field name suffix
        @param language: The language (default is English)
        @return: String
        '''
        locationDescriptionDict = {
            "primary": None,
            "secondary": None,
            }
        for key in [f"locationDescription{suffix}", "locationDescription"]:
            locationDescriptionList = inputDict.get(key)
            if locationDescriptionList:
                locationDescriptionDict = locationDescriptionList[0]
                break
        if not locationDescriptionDict.get("primary"):
            locationDescriptionDict["primary"] = "|* ENTER EVENT LOCATION *|"
        primaryText = locationDescriptionDict["primary"]
        if self.isSpanish(language):
            primaryText = self.convertLocationTextToSpanish(primaryText)
        primaryText = self.capitalizeFirstLetter(primaryText)
        secondaryText = locationDescriptionDict["secondary"]
        tableText = f"{primaryText}\n"
        if secondaryText:
            if self.isSpanish(language):
                numSpaces = 22
                secondaryText = self.convertLocationTextToSpanish(secondaryText)
            else:
                numSpaces = 20
            subBulletText = " " * numSpaces
            secondaryText = self.capitalizeFirstLetter(secondaryText)
            tableText += f"{subBulletText}{secondaryText}\n"
        tableText += "\n"
        return tableText

    def convertLocationTextToSpanish(self, textString):
        '''
        @summary: Given a text string, convert key words in the string to Spanish
        @param textString: The string to translate
        @return: String
        '''
        englishDict = self.getEnglishSpanishDict("English")
        spanishDict = self.getEnglishSpanishDict("Spanish")
        for textKey in ["northeastText", "southeastText", "southwestText", "northwestText",
                        "northText", "eastText", "southText", "westText", "milesText", "ofText"]:
            englishText = englishDict[textKey]
            spanishText = spanishDict[textKey]
            textString = textString.replace(f" {englishText} ", f" {spanishText} ")
            textString = textString.replace(f" {englishText.title()} ", f" {spanishText.title()} ")
        return textString

    def getPhysicalEventDescriptionString(self, eventDict, suffix, language=""):
        '''
        @summary: Get a textual description of the physical event
        @param eventDict: The event-level dictionary
        @param suffix: The field name suffix
        @param language: The language of the text (e.g., nothing or "Spanish")
        @return: String
        '''
        productRegionAbbrev = eventDict.get("productRegion")
        physicalEventType = eventDict.get("physicalEventType")
        eventLocation = self.getPrimaryPhysicalEventLocation(eventDict, suffix, language)
        firstTimezone = self.alu.getTimezonesByProductRegionAbbreviation(productRegionAbbrev)[0]
        originTimeMillis = eventDict.get(f"originTime{suffix}")
        originTimeDT = TimeUtil.epochTimeMillisToDatetime(originTimeMillis)
        originTimeDT = TimeUtil.changeTimezoneOfDatetimeObject(originTimeDT, firstTimezone)
        if firstTimezone == "UTC":
            HHMM = originTimeDT.strftime("%H%M %Z")  # (e.g., 2202 UTC)
        else:
            HHMM = originTimeDT.strftime("%-I%M %p %Z")  # (e.g., 1002 PM AST)
        dateString = originTimeDT.strftime("%A %B %-d %Y")
        descriptionString = ""

        if self.agu.isPhysicalEventTypeSeismic(physicalEventType):
            magnitude = eventDict.get(f"magnitude{suffix}")
            descriptionHeader = self.getSeismicDescription(magnitude)
            descriptionString = f"{descriptionHeader}{eventLocation} at {HHMM} on {dateString}"
        else:
            descriptionHeader = " "
            physicalEventFeatureName = eventDict.get(f"peName{suffix}")
            if self.agu.isPhysicalEventTypeVolcanic(physicalEventType):
                descriptionHeader = self.getVolcanicDescription(physicalEventFeatureName)
            elif self.agu.isPhysicalEventTypeLandslide(physicalEventType):
                descriptionHeader = self.getLandslideDescription(physicalEventFeatureName)
            elif self.agu.isPhysicalEventTypeUnknown(physicalEventType):
                descriptionHeader = self.getUnknownDescription()
            descriptionString = (f"At {HHMM} on {dateString}{descriptionHeader}{eventLocation}")
        # Clean up extra space if there is no location and add '.' at the end
        descriptionString = self.capitalizeFirstLetter(descriptionString)
        descriptionString = f"{descriptionString.rstrip()}."
        return descriptionString

    def getPrimaryPhysicalEventLocation(self, eventDict, suffix, language="", expandDirection=True):
        '''
        @summary: Create a text string with the location information
        @param eventDict: The event-level dictionary
        @param suffix: The field name suffix
        @param language: The language (default empty for English but could be "Spanish" for Spanish)
        @param expandDirection: Boolean to determine whether to expand the cardinal direction
        abbreviation to its full name (e.g., SE --> southeast)
        @return: String
        '''
        locationDescriptionDict = {}
        for key in [f"locationDescription{suffix}", "locationDescription"]:
            locationDescriptionList = eventDict.get(key)
            if locationDescriptionList:
                locationDescriptionDict = locationDescriptionList[0]
                break
        primaryText = locationDescriptionDict.get("primary")
        if not primaryText:
            primaryText = "|* ENTER EVENT LOCATION *|"
        if expandDirection:
            for abbrev, direction in self.alu.cardinalDirectionDictionary().items():
                primaryText = primaryText.replace(f" {abbrev} ", f" {direction} ")
        if self.isSpanish(language):
            primaryText = self.convertLocationTextToSpanish(primaryText)
        return primaryText

    def getSeismicDescription(self, magnitude):
        '''
        @summary: Get the physical event description phrase for seismic physical events
        @param magnitude: The earthquake magnitude (e.g., 7.6)
        @return: String
        '''
        return f"an earthquake with preliminary magnitude of {magnitude} occurred "

    def getVolcanicDescription(self, physicalEventFeatureName):
        '''
        @summary: Get the physical event description phrase for volcanic physical events
        @param physicalEventFeatureName: The name of the physical event feature (i.e., Augustine)
        @return: String
        '''
        if physicalEventFeatureName:
            header = f"the {physicalEventFeatureName}"
        else:
            header = "a"
        return f" {header} volcano erupted "

    def getLandslideDescription(self, physicalEventFeatureName):
        '''
        @summary: Get the physical event description phrase for landslide physical events
        @param physicalEventFeatureName: The name of the physical event feature (i.e., Barry Arm)
        @return: String
        '''
        if physicalEventFeatureName:
            header = f"the {physicalEventFeatureName}"
        else:
            header = "a"
        return f" {header} landslide occurred "

    def getUnknownDescription(self):
        '''
        @summary: Get the physical event description phrase for unknown physical events
        @return: String
        '''
        return (" tsunami waves have been observed. The source of the "
                "tsunami waves is currently unknown and there is large "
                "uncertainty in estimating the impacts ")

    def getSegmentCategory(self, inputDict):
        '''
        @summary: Retrieve the category of tsunami information that is contained
        within this segment by querying the first VTEC record in the section-level
        dictionary
        @param inputDict: The product or segment dictionary
        @return: A string
        '''
        sigToCategoryDict = {
            "S": "Information",
            "W": "Warning",
            "Y": "Advisory",
            "A": "Watch"
            }
        allSectionDicts = self.agu.getAllSectionDicts(inputDict)
        if len(allSectionDicts) > 1:
            activeSectionDicts = self.agu.getActiveSectionDicts(inputDict)
            if activeSectionDicts:
                sectionDict = activeSectionDicts[0]
            else:
                sectionDict = allSectionDicts[0]
        else:
            sectionDict = self.agu.getSectionDict(inputDict)
        vtecRecord = sectionDict.get("vtecRecord")
        action = self.tpc.getVtecAction(vtecRecord)
        segmentCategory = ""
        if action == "CAN":
            segmentCategory = "Cancellation"
        else:
            segmentCategory = sigToCategoryDict.get(vtecRecord.get("sig") , "")
        return segmentCategory

    def getAreaStatusDefinition(self, inputDict):
        '''
        @summary: Return the definition of each area status level: Cancellation,
        Warning, Advisory, Watch and Information
        @param inputDict: The product or segment dictionary
        @return: A string
        '''
        definition = ""
        areaStatusLevel = self.getSegmentCategory(inputDict)
        if areaStatusLevel == "Warning":
            definition = ("Tsunami warnings mean that a tsunami with significant "
                          "inundation is possible or is already occurring. Tsunamis are "
                          "a series of waves dangerous many hours after initial arrival "
                          "time. The first wave may not be the largest.")
        elif areaStatusLevel == "Advisory":
            definition = ("Tsunami advisories mean that a tsunami capable of producing "
                          "strong currents or waves dangerous to persons in or very near "
                          "the water is expected or is already occurring. Areas in the "
                          "advisory should not expect widespread inundation. Tsunamis "
                          "are a series of waves dangerous many hours after initial "
                          "arrival time. The first wave may not be the largest.")
        elif areaStatusLevel == "Watch":
            definition = ("Tsunami watches are an advance notice to areas that could be "
                          "impacted by a tsunami at a later time. Watch areas may be upgraded "
                          "to warning or advisory status, or cancelled, based on new "
                          "information.")
        elif areaStatusLevel == "Cancellation":
            definition = ("Tsunami cancellations indicate the end of the damaging tsunami threat. "
                          "A cancellation is issued after an evaluation of sea level data confirms "
                          "that a destructive tsunami will not impact the alerted region, or "
                          "after tsunami levels have subsided to non-damaging levels.")
        elif areaStatusLevel == "Information":
            definition = ("An information statement indicates that an earthquake has occurred, "
                          "but does not pose a tsunami threat, or that a tsunami warning, "
                          "advisory, or watch has been issued for another section of the ocean. ")
        return definition

    def getOfficeIdBySiteId(self, siteID):
        '''
        @summary: Get the tsunami center office ID from the site ID
        @param siteID: The site ID (i.e., NTWC or PTWC)
        @return: String:
        '''
        officeID = ""
        if siteID == "NTWC":
            officeID = self.ntwcOfficeId()
        elif siteID == "PTWC":
            officeID = self.ptwcOfficeId()
        return officeID

    def getWarningCenterByEventDict(self, eventDict):
        '''
        @summary: Get the tsunami center name from the site ID in eventDict
        @param eventDict: Event level dictionary
        @return: String:
        '''
        siteId = eventDict.get("siteID")
        warningCenter = ""
        if siteId == "NTWC":
            warningCenter = "U.S. National Tsunami Warning Center"
        elif siteId == "PTWC":
            warningCenter = "Pacific Tsunami Warning Center"
        return warningCenter

    def getTsunamiObservationTableText(self, inputDict, tz, suffix, language=""):
        '''
        @summary: Build the table text with the tsunami station observations
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param tz: The office time zone
        @param suffix: The field name suffix
        @param language: The language (default is English)
        @return: String
        '''
        eventDicts = self.agu.getAllEventDicts(inputDict)
        tableText = ""
        stations = eventDicts[0].get(f"seaLevelObs{suffix}")
        if stations:
            seaLevelObsTable = AtomsTableSeaLevelObservations.Table(eventDicts=eventDicts,
                                                                    timeZone=tz,
                                                                    suffix=suffix,
                                                                    language=language)
            tableText = seaLevelObsTable.makeTable()
        return tableText

    def getTsunamiForecastRunsTableText(self, inputDict, tz, suffix, language=""):
        '''
        @summary: Build the table text with the tsunami forecast stations
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param tz: The office time zone
        @param suffix: The field name suffix
        @param language: The language (default is English)
        @return: String
        '''
        fcstRunTable = self.agu.getTsunamiForecastRunsTable(inputDict, tz, suffix, language)
        tableText = ""
        if fcstRunTable:
            tableText = fcstRunTable.makeTable()
        return tableText

    def getRecommendedActionsText(self, productDict, language=""):
        '''
        @summary: Helper method to create the recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        actionText = ""
        if self.agu.areAllSegmentsEnding(productDict):
            if self.isSpanish(language):
                actionText = (" * No regresen a zonas desalojadas hasta que las autoridades\n"
                              "locales de manejo de emergencia indiquen que es seguro\n"
                              "hacerlo.")
            else:
                actionText = (" * Do not re-occupy hazard zones until local emergency\n"
                              "   officials indicate it is safe to do so.")
            actionText += "\n\n"
        else:
            has_w = productDict.get("hasActiveWarnings")
            has_y = productDict.get("hasActiveAdvisories")
            hazCtaIds = collections.defaultdict(list)
            ctaCategoryDictionary = self.ctaCategoryDictionary()
            for segmentDict in productDict.get("segments"):
                activeSections = self.agu.getActiveSectionDicts(segmentDict)
                for sectionDict in activeSections:
                    for eventDict in sectionDict.get("eventDicts"):
                        eventCtaIds = eventDict.get("cta_identifier", [])
                        for id in eventCtaIds:
                            for type in ctaCategoryDictionary.keys():
                                if id in ctaCategoryDictionary.get(type) and id not in hazCtaIds[type]:
                                    hazCtaIds[type].append(id)
            if hazCtaIds:
                startingText = self.getActionStartText(productDict)
                if self.isSpanish(language):
                    startingText = self.getActionStartText(productDict, "Spanish")
                actionText += startingText
                hazCtaIds = sorted(hazCtaIds.items(), key=lambda t: t[0], reverse=True)
            for hazName, ctaIds in hazCtaIds:
                ctas = []
                ctaText = ""
                if hazName == "TS.W":
                    if self.isSpanish(language):
                        actionText += "Si usted esta en un area de aviso:"
                    else:
                        actionText += "If you are in a tsunami warning area:"
                    actionText += "\n\n"
                elif hazName == "TS.B":
                    if has_y:
                        if has_w:
                            if self.isSpanish(language):
                                actionText += "Si usted esta en un area de aviso o advertencia:"
                            else:
                                actionText += "If you are in a tsunami warning or advisory area:"
                        else:
                            if self.isSpanish(language):
                                actionText += "Si usted esta en un area de advertencia:"
                            else:
                                actionText += "If you are in a tsunami advisory area:"
                        actionText += "\n\n"
                elif hazName == "TS.A":
                    if self.isSpanish(language):
                        actionText += "Si usted esta en un area de vigilancia:"
                    else:
                        actionText += "If you are in a tsunami watch area:"
                    actionText += "\n\n"
                stringKey = "productString"
                if self.isSpanish(language):
                    stringKey = "spanishProductString"
                for cta in ctaIds:
                    ctaFuntion = getattr(self.ctaImpact, cta)
                    ctaText = self.wrapText(ctaFuntion().get(stringKey))
                    ctas.append(ctaText)
                if ctas:
                    ctasText = "\n\n".join(ctas)
                actionText += f"{ctasText}\n\n"

        return actionText

    def getActionStartText(self, productDict, language=""):
        '''
        @summary: The text appearing at the top of the recommendedActionsBullet
        product part
        @param productDict: The product-level dictionary
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        actionText = ""
        has_w = productDict.get("hasActiveWarnings")
        has_y = productDict.get("hasActiveAdvisories")
        if productDict.get("siteID") == "PTWC":
            startingText = "Actions to protect human life... safety and property will\n"
        else:
            startingText = "Actions to protect human life and property will\n"
        if self.isSpanish(language):
            startingText = "Las acciones para proteger la vida y propiedad pueden\n"
        if has_w:
            actionText += startingText
            if has_y:
                if self.isSpanish(language):
                    actionText += ("variar dentro de las areas de aviso y las areas de\n"
                                   "advertencia de tsunami.")
                else:
                    actionText += ("vary within tsunami warning areas and within tsunami\n"
                                   "advisory areas.")
            else:
                if self.isSpanish(language):
                    actionText += "variar dentro de las areas de aviso de tsunami."
                else:
                    actionText += "vary within tsunami warning areas."
            actionText += "\n\n"
        elif has_y:
            actionText += startingText
            if self.isSpanish(language):
                actionText += "variar dentro de las areas de advertencia."
            else:
                actionText += "vary within tsunami advisory areas."
            actionText += "\n\n"
        return actionText

    def getImpactsBulletText(self, productDict, fieldNameSuffix, language=""):
        '''
        @summary: Helper method to create the tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        impactsText = ""
        if self.agu.areAllSegmentsEnding(productDict):
            impactsText = self.getCancelImpacts(productDict, fieldNameSuffix, language)
        else:
            hazImpactIds = collections.defaultdict(list)
            impactCategoryDictionary = self.impactCategoryDictionary()
            has_w = productDict.get("hasActiveWarnings")
            has_y = productDict.get("hasActiveAdvisories")
            for segmentDict in productDict.get("segments"):
                activeSections = self.agu.getActiveSectionDicts(segmentDict)
                for sectionDict in activeSections:
                    for eventDict in sectionDict.get("eventDicts"):
                        impactIds = eventDict.get("impacts_identifier", [])
                        for id in impactIds:
                            for type in impactCategoryDictionary.keys():
                                if id in impactCategoryDictionary.get(type) and id not in hazImpactIds[type]:
                                    hazImpactIds[type].append(id)
            if hazImpactIds:
                startingText = self.getImpactsStartText(productDict)
                if self.isSpanish(language):
                    startingText = self.getImpactsStartText(productDict, "Spanish")
                impactsText += startingText
                hazImpactIds = sorted(hazImpactIds.items(), key=lambda t: t[0])
            for hazName, impactIds in hazImpactIds:
                impacts = []
                impactText = ""
                if hazName == "TS.W":
                    if self.isSpanish(language):
                        impactsText += "Si usted esta en un area de aviso:"
                    else:
                        impactsText += "If you are in a tsunami warning area:"
                    impactsText += "\n\n"
                elif hazName == "TS.Z":
                    if has_y and has_w:
                        if self.isSpanish(language):
                            impactsText += "Si usted esta en un area de aviso o advertencia:"
                        else:
                            impactsText += "If you are in a tsunami warning or advisory area:"
                        impactsText += "\n\n"
                elif hazName == "TS.Y":
                    if self.isSpanish(language):
                        impactsText += "Si usted esta en un area de advertencia:"
                    else:
                        impactsText += "If you are in a tsunami advisory area:"
                    impactsText += "\n\n"
                stringKey = "productString"
                if self.isSpanish(language):
                    stringKey = "spanishProductString"
                for impact in impactIds:
                    impactFuntion = getattr(self.ctaImpact, impact)
                    impactText = self.wrapText(impactFuntion().get(stringKey))
                    impacts.append(impactText)
                if impacts:
                    impactText = "\n\n".join(impacts)
                impactsText += f"{impactText}\n\n"

        return impactsText

    def getImpactsStartText(self, productDict, language=""):
        '''
        @summary: The text appearing at the top of the tsunamiImpactsBullet
        product part
        @param productDict: The product-level dictionary
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        impactText = ""
        has_w = productDict.get("hasActiveWarnings")
        has_y = productDict.get("hasActiveAdvisories")
        startText = "Impacts will vary at different locations "
        if self.isSpanish(language):
            startText = "Los impactos pueden variar en diferentes lugares dentro de\n"
        if has_w:
            impactText += startText
            if has_y:
                if self.isSpanish(language):
                    impactText += "las areas de aviso y las areas de advertencia."
                else:
                    impactText += "in the warning and\nin the advisory areas."
            else:
                if self.isSpanish(language):
                    impactText += "las areas de aviso."
                else:
                    impactText += "in the warning areas."
            impactText += "\n\n"
        elif has_y:
            impactText += startText
            if self.isSpanish(language):
                impactText += "area de advertencia."
            else:
                impactText += "in the advisory areas."
            impactText += "\n\n"
        return impactText

    def getCancelImpacts(self, productDict, fieldNameSuffix, language):
        '''
        @summary: Get cancel impact string for product
        @param productDict: The product-level dictionary
        @param fieldNameSuffix: The suffix of field name
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        impactsText = ""
        cancelChoice = productDict.get(f"tsunamiCancel_{fieldNameSuffix}")
        siteId = productDict.get("siteID")
        phraseList = []
        if siteId == "NTWC":
            productRegion = productDict.get("productRegion")
            if productRegion == "AkBcWc":
                location = "the U.S. West Coast, British Columbia and Alaska."
                if self.isSpanish(language):
                    location = "la costa oeste de los Estados Unidos, Columbia Britanica y Alaska."
            elif productRegion == "EcGc":
                location = "the U.S. East Coast, Gulf of America and Canada."
                if self.isSpanish(language):
                    location = "la costa este de los Estados Unidos, Golfo de América y Canadá."

            if cancelChoice == "noTsunami":
                phraseList = ["No destructive tsunami has been recorded.",
                              f"No tsunami danger exists for {location}",
                              ]
                if self.isSpanish(language):
                    phraseList = ["Ningun tsunami destructivo ha sido registrado.",
                                  f"No existe peligro de tsunami para {location}",
                                  ]
            elif cancelChoice == "noDamagingTsunamiInOAR":
                phraseList = [("A tsunami was generated by this event, but no longer "
                               "poses a threat."),
                               "Some areas may continue to see small sea level changes.",
                               ("The determination to re-occupy hazard zones must be made "
                                "by local officials."),
                               ]
                if self.isSpanish(language):
                    phraseList = [("Este evento generó un tsunami, pero ya no "
                                   "representa una amenaza."),
                                   ("Es posible que algunas áreas sigan viendo pequeños cambios "
                                    "en el nivel del mar."),
                                   ("Se debe tomar la determinación de volver a ocupar las zonas "
                                    "de peligro.por funcionarios locales."),
                                   ]
            elif cancelChoice == "damagingTsunamiInOAR":
                phraseList = [f"Tsunami activity has subsided along {location}",
                               ("Ongoing activity may persist in some areas causing strong "
                                "currents dangerous to swimmers and boats."),
                               ("The determination to re-occupy hazard zones must be made "
                                "by local officials."),
                               ]
                if self.isSpanish(language):
                    phraseList = [f"La actividad de tsunamis ha disminuido a lo largo {location}",
                                  ("La actividad en curso puede persistir en algunas áreas causando "
                                   "fuertes Corrientes peligrosas para nadadores y embarcaciones."),
                                  ("Se debe tomar la determinación de volver a ocupar las zonas de "
                                   "peligro por funcionarios locales."),
                                   ]
        elif siteId == "PTWC":
            regionText = self.alu.getProductRegionNameFromAbbreviation(productDict.get("productRegion"))
            if cancelChoice == "noTsunamiAtSource":
                phraseList = ["A tsunami was not generated at the source."]
            elif cancelChoice == "tsunamiGeneratedNoThreat":
                phraseList = [("a tsunami was generated at the source, but was small, therefore, "
                              f"the tsunami will not be a threat to {regionText}."),
                              ]
            elif cancelChoice == "forecastIndicatedNoThreat":
                phraseList = ["The model forecast indicated no threat."]
            elif cancelChoice == "tsunamiNotGeneratedOrBelow":
                phraseList = [("Tsunami was not generated or was generated but below "
                               "advisory/warning levels."),
                               ]
            elif cancelChoice == "destructiveTsunamiGeneratedFallBelow":
                phraseList = [("Destructive tsunami was generated (exceeding advisory/warning "
                               "levels), but now falls below advisory/warning levels.")
                               ]
        for phrase in phraseList:
            wrappedPhrase = self.wrapText(phrase)
            impactsText += f"{wrappedPhrase}\n\n"
        return impactsText

    def getAreaListTextProduct(self, productDict, language=""):
        '''
        @summary: Defines the areaList product part text for the AkBcWc
        product region
        @param productDict: The product-level dictionary
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        phraseDict = self.getEnglishSpanishDict(language)
        productRegion = productDict.get("productRegion")
        atomsProductInfoDict = self.bridge.getAtomsProductLocationInfo()
        areaText = ""
        # Order segments with active information first, cancellation information second
        rawSegmentDicts = productDict.get("segments")
        segmentDicts = []
        inactiveSegments = []
        for segmentDict in rawSegmentDicts:
            if self.agu.isSegmentCancelExpire(segmentDict):
                inactiveSegments.append(segmentDict)
            else:
                segmentDicts.append(segmentDict)
        partialCancel = False
        fullCancel = False
        if inactiveSegments:
            if segmentDicts:
                partialCancel = True
            else:
                fullCancel = True
        segmentDicts += inactiveSegments
        for segmentDict in segmentDicts:
            hazardAreaDict = {}
            # Get the vtec action to help determine NEW, CAN, EXA, CON language
            allSectionDicts = self.agu.getAllSectionDicts(segmentDict)
            if len(allSectionDicts) > 1:
                activeSectionDicts = self.agu.getActiveSectionDicts(segmentDict)
                if activeSectionDicts:
                    sectionDict = activeSectionDicts[0]
                else:
                    sectionDict = allSectionDicts[0]
            else:
                sectionDict = self.agu.getSectionDict(segmentDict)
            vtecRecord = sectionDict.get("vtecRecord")
            vtecAction = self.tpc.getVtecAction(vtecRecord)
            # Determine if all VTEC lines have an action of CAN or EXP
            segmentEnding = self.agu.isSegmentCancelExpire(segmentDict)
            # If partially ending (e.g., CAN/NEW), get first event with an active VTEC
            if segmentEnding:
                eventDict = self.agu.getAllEventDicts(segmentDict)[0]
            else:
                eventDict = self.agu.getActiveSectionDicts(segmentDict)[0].get("eventDicts")[0]
            # Get the hazard locations associated with this event
            hazardLocations = eventDict.get("hazardLocations", []) + eventDict.get("inclusionReferences", [])
            # Get the hazard name (e.g., Tsunami Warning)
            hazName = eventDict.get("headline").title()
            # Get hazard info line (e.g., Tsunami Warning in effect for:)
            hazNamePrefix = self.getHazardNamePrefixText(hazName, vtecAction, language)
            # Get coastal info line (e.g., * Coastal areas of)
            coastAreaPrefix = self.getCoastAreaPrefixText(segmentEnding, language)
            # Walk through the break point segments in this product segment and retrieve information
            breakPointSegmentDicts = segmentDict.get("breakPointSegmentDicts")
            # First, we need to determine if there are any special procedure areas and
            # if the segment ONLY contains special procedure areas
            onlySpecialAreas = True
            specialAreaNames = []
            inclusionSpecialAreas = []
            for segInfoDict in breakPointSegmentDicts:
                bpsName = segInfoDict.get("name")
                isSpecial = self.agu.isBreakPointSegmentSpecial(segInfoDict)
                if isSpecial:
                    specialAreaNames.append(bpsName)
                elif onlySpecialAreas:
                    onlySpecialAreas = False
                locInfoDict = atomsProductInfoDict.get(bpsName, {})
                inclusionSpecialAreas += locInfoDict.get("inclusionSpecialProcedures", [])
            # Next, we need to determine if any of these special procedure areas are included
            # an in existing break point segment, if so, remove it.
            if specialAreaNames and not onlySpecialAreas:
                for i in range(len(specialAreaNames) - 1, -1, -1):
                    if specialAreaNames[i] in inclusionSpecialAreas:
                        specialAreaNames.remove(specialAreaNames[i])
            if productRegion == "AkBcWc":
                subRegionInfoDict = {}
                for segInfoDict in breakPointSegmentDicts:
                    bpName = segInfoDict.get("name")
                    isSpecial = self.agu.isBreakPointSegmentSpecial(segInfoDict)
                    # Special procedure area is part of a break point segment so it does not need
                    # its own listing
                    if isSpecial and bpName not in specialAreaNames:
                        continue
                    locInfoDict = atomsProductInfoDict.get(bpName, {})
                    if isSpecial:
                        subRegionName = bpName
                    else:
                        subRegionName = locInfoDict.get("subregion")

                    if subRegionName not in subRegionInfoDict:
                        subRegionInfoDict[subRegionName] = {
                            "special": isSpecial,
                            "segInfoDict": [],
                            "includingAreas": [],
                            }
                    subRegionInfoDict[subRegionName]["segInfoDict"].append(segInfoDict)
                    
                    for geoKey in ["inclusionReferencePoints", "inclusionSpecialProcedures"]:
                        geoNames = locInfoDict.get(geoKey, [])
                        for geoName in geoNames:
                            if (geoName in hazardLocations and
                                geoName not in subRegionInfoDict[subRegionName]["includingAreas"]):
                                subRegionInfoDict[subRegionName]["includingAreas"].append(geoName)

                for subRegionName in subRegionInfoDict:
                    segInfoDicts = subRegionInfoDict[subRegionName]["segInfoDict"]
                    if subRegionName == "British Columbia":
                        fromToText = self.getAreaListTextForBritishColumbia(segInfoDicts, language)
                    else:
                        fromToText = self.getAreaListFromBreakPointSegments(segmentDict, segInfoDicts,
                                                                            language)
                    includingAreas = subRegionInfoDict[subRegionName]["includingAreas"]
                    if includingAreas:
                        includingConnector = f" {phraseDict['includingText']} "
                        includingText = self.tpc.joinStringsWithOxfordComma(includingAreas)
                        fromToText += f"{includingConnector}{includingText}"
                    if hazName not in hazardAreaDict:
                        hazardAreaDict[hazName] = {
                            "subregions": [],
                            "areaStrings": [],
                            }
                    hazardAreaDict[hazName]["subregions"].append(subRegionName)
                    hazardAreaDict[hazName]["areaStrings"].append(fromToText)

                if segmentEnding and partialCancel:
                    partialCancel = False
                    areaText += self.getCancelSegmentPrefix(language) + "\n\n"

                for hazName in hazardAreaDict:
                    subregions = hazardAreaDict[hazName]["subregions"]
                    areaStrings = hazardAreaDict[hazName]["areaStrings"]
                    if fullCancel:
                        subRegionString = self.tpc.joinStringsWithOxfordComma(subregions)
                        areaText += f" * The {hazNamePrefix}{coastAreaPrefix}{subRegionString}\n\n"
                    elif segmentEnding:
                        for i in range(len(subregions)):
                            subRegionName = subregions[i]
                            areaString = areaStrings[i]
                            if subRegionInfoDict[subRegionName]["special"]:
                                areaText += (f" * The {hazNamePrefix}{areaStrings[i]}\n\n")
                            else:
                                areaText += (f" * The {hazNamePrefix}"
                                             f"{subregions[i]} {areaStrings[i]}\n\n")
                    else:
                        areaText += f"{hazNamePrefix}\n\n"
                        areaListString = ""
                        for i in range(len(subregions)):
                            areaListString += f" * {subregions[i].upper()}, {areaStrings[i]}\n\n"
                        areaText += areaListString
            else:
                statesList = self.getStatesInProductSegment(segmentDict)
                includingAreas = []
                for segInfoDict in breakPointSegmentDicts:
                    bpName = segInfoDict.get("name")
                    isSpecial = self.agu.isBreakPointSegmentSpecial(segInfoDict)
                    if isSpecial and bpName not in specialAreaNames:
                        continue
                    locInfoDict = atomsProductInfoDict.get(bpName, {})
                    for geoKey in ["inclusionReferencePoints", "inclusionSpecialProcedures"]:
                        geoNames = locInfoDict.get(geoKey, [])
                        for geoName in geoNames:
                            if (geoName in hazardLocations and
                                geoName not in includingAreas):
                                includingAreas.append(geoName)

                if segmentEnding and partialCancel:
                    partialCancel = False
                    areaText += self.getCancelSegmentPrefix(language) + "\n\n"

                segmentString = self.tpc.joinStringsWithOxfordComma(statesList)
                if includingAreas:
                    includingConnector = f" {phraseDict['includingText']} "
                    includingText = self.tpc.joinStringsWithOxfordComma(includingAreas)
                    segmentString += f"{includingConnector}{includingText}"

                if segmentEnding:
                    areaText += f" * The {hazNamePrefix}"
                else:
                    areaText += f"{hazNamePrefix}\n\n"

                areaText += f"{coastAreaPrefix}{segmentString}\n\n"

        return areaText

    def getStatesInProductSegment(self, segmentDict):
        '''
        @summary: Get the states associated with the break point segments
        provided at the product segment-level dictionary
        @param segmentDict: The segment-level dictionary
        @return: List of strings
        '''
        atomsProductInfoDict = self.bridge.getAtomsProductLocationInfo()
        statesList = []
        breakPointSegmentDicts = segmentDict.get("breakPointSegmentDicts")
        for segInfoDict in breakPointSegmentDicts:
            bpName = segInfoDict.get("name")
            locInfoDict = atomsProductInfoDict.get(bpName, {})
            segmentStates = locInfoDict.get("states", [])
            for state in segmentStates:
                if state not in statesList:
                    statesList.append(state)
        return statesList

    def getCancelSegmentPrefix(self, language):
        if self.isSpanish(language):
            canPrefix = ("Alertas en las siguientes areas han sido canceladas porque\n"
                         "se ha definido mejor la amenaza en base a informacion y\n"
                         "analisis adicional.")
        else:
            canPrefix = ("Alerts in the following areas have been cancelled because\n"
                         "additional information and analysis have better defined\n"
                         "the threat.")
        return canPrefix

    def getAreaListTextSegment(self, segmentDict, productRegionAbbrev, language=""):
        '''
        @summary: Create text to describe the area list for a single segment
        @param segmentDict: The segment-level dictionary
        @param productRegionAbbrev: The product region abbreviation (e.g., Pr)
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        if productRegionAbbrev == "Pr":
            areaText = self.getAreaListTextForPuertoRico(language)
        else:
            breakPointSegmentDicts = segmentDict.get("breakPointSegmentDicts")
            # Use break point segment info for area list if there is at least one
            if len(breakPointSegmentDicts) >= 1:
                areaText = self.getAreaListFromBreakPointSegments(segmentDict, breakPointSegmentDicts,
                                                                  language)
            # Use ugcs information for area list
            else:
                areaDescription = self.tpc.formatUGC_names(segmentDict.get("ugcs"), separator=", ")
                # Replace last ', ' with '.'
                areaText = f"{areaDescription.rstrip(', ')}."
        return areaText

    def getAreaListTextForPuertoRico(self, language=""):
        '''
        @summary: Get the areaList string for the Puerto Rico subregion
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        return ("Coastal areas of Puerto Rico - the U.S. Virgin "
                "Islands and the British Virgin Islands")

    def getAreaListTextForBritishColumbia(self, breakPointSegmentDicts, language):
        '''
        @summary: Get the areaList string for the British Columbia subregion
        @param breakPointSegmentDicts: A dictionary of break point segment information from the segment-level
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        breakPointNumbers = [self.agu.getBreakPointInteger(brkptseg.get(HazardConstants.BP_NUM_ATTR_NAME))
                             for brkptseg in breakPointSegmentDicts]
        if 14 and 15 in breakPointNumbers:
            if self.isSpanish(language):
                areaText = ("la costa norte y Haida Gwaii, la costa central y la isla noreste de "
                            "Vancouver, la costa oeste exterior de la isla de Vancouver")
            else:
                areaText = ("the north coast and Haida Gwaii, the central coast and northeast "
                            "Vancouver Island, the outer west coast of Vancouver Island")
        elif 14 in breakPointNumbers:
            if self.isSpanish(language):
                areaText = "la costa norte y Haida Gwaii"
            else:
                areaText = "the north coast and Haida Gwaii"
        elif 15 in breakPointNumbers:
            if self.isSpanish(language):
                areaText = ("la costa central y la isla noreste de Vancouver, la costa oeste "
                            "exterior de la isla de Vancouver")
            else:
                areaText = ("the central coast and northeast Vancouver Island, the outer west "
                            "coast of Vancouver Island")
        return areaText

    def getAreaListFromBreakPointSegments(self, segmentDict, breakPointSegmentDicts, language):
        '''
        @summary: Get the areaList string from break points and break point segments
        @param segmentDict: The segment-level dictionary
        @param breakPointSegmentDicts: A dictionary of break point segment information from
        the segment-level dictionary
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        phraseDict = self.getEnglishSpanishDict(language)
        areaText = f"{phraseDict['coastalAreas']} "
        consecutiveNumGroups = self.agu.getConsecutiveSegmentGroups(breakPointSegmentDicts)
        spRegions = []
        for segDict in breakPointSegmentDicts:
            if self.agu.isBreakPointSegmentSpecial(segDict):
                spRegionName = segDict.get(HazardConstants.LOWER_BP_ATTR_NAME)
                if spRegionName not in spRegions:
                    spRegions.append(spRegionName)
        groupTexts = []
        for startNum, endNum in consecutiveNumGroups:
            fromText = toText = ""
            fromToDict = self.getFromToBreakpointInfo(segmentDict, breakPointSegmentDicts,
                                                      startNum, endNum)
            if fromToDict["fromName"] != "None":
                fromText = (f"{phraseDict['fromText']} {fromToDict['fromName']}, "
                            f"{fromToDict['fromState']}")
                if fromToDict["fromDescriptor"] != "None":
                    fromText += f" ({fromToDict['fromDescriptor']})"
            if fromToDict["toName"] != "None":
                toText = f" {phraseDict['toText']} {fromToDict['toName']}, {fromToDict['toState']}"
                if fromToDict["toDescriptor"] != "None":
                    toText += f" ({fromToDict['toDescriptor']})"
            if fromText and toText:
                groupTexts.append(f"{fromText}{toText}")
        if groupTexts:
            combinedGroupText = self.tpc.joinStringsWithOxfordComma(groupTexts)
            areaText += combinedGroupText
        if spRegions:
            combinedSPText = self.tpc.joinStringsWithOxfordComma(spRegions)
            if not groupTexts:
                areaText += f"{phraseDict['ofText']} "
            else:
                areaText += f" {phraseDict['includingText']} "
            areaText += f"{combinedSPText}"
        return areaText

    def getFromToBreakpointInfo(self, segmentDict, breakPointSegmentDicts, startIndex, endIndex):
        '''
        @summary: Given a list of dictionaries of break point segment information
        from the product segment-level dictionary, get the from/to phrase
        @param segmentDict: The segment-level dictionary
        @param breakPointSegmentDicts: A dictionary of break point segment information from the segment-level
        @param startIndex: The starting break point number
        @param endIndex: The ending break point number
        @return: Dictionary
        '''
        breakPointsDict = segmentDict.get("breakPointsDict")
        infoDict = {
            "fromName": "None",
            "fromState": "None",
            "fromDescriptor": "None",
            "toName": "None",
            "toState": "None",
            "toDescriptor": "None",
            }
        for segDict in breakPointSegmentDicts:
            if self.agu.isBreakPointSegmentSpecial(segDict):
                continue
            bpNum = self.agu.getBreakPointInteger(segDict.get(HazardConstants.BP_NUM_ATTR_NAME))
            if startIndex == bpNum:
                infoDict["fromName"] = segDict.get(HazardConstants.LOWER_BP_ATTR_NAME)
                infoDict["fromState"] = segDict.get(HazardConstants.STATE_NAME_ATTR_NAME)
                infoDict["fromDescriptor"] = breakPointsDict.get(infoDict["fromName"]).get("descriptor")
            if endIndex == bpNum:
                infoDict["toName"] = segDict.get(HazardConstants.UPPER_BP_ATTR_NAME)
                infoDict["toState"] = segDict.get(HazardConstants.STATE_NAME_ATTR_NAME)
                infoDict["toDescriptor"] = breakPointsDict.get(infoDict["toName"]).get("descriptor")
        return infoDict

    def getHazardNamePrefixText(self, hazName, vtecAction, language):
        '''
        @summary: Get the prefix string based on hazard name, action and language
        @param hazName: The hazard type
        @param vtecAction: CAN NEW EXA CON etc to determine the phraseology
        @param anguage: The language to produce the message in (default is English)
        @return: String
        '''
        prefix = ""
        if hazName == "Tsunami Warning":
            hazNameSpn = "Aviso de Tsunami"
        elif hazName == "Tsunami Advisory":
            hazNameSpn = "Advertencia de Tsunami"
        elif hazName == "Tsunami Watch":
            hazNameSpn = "Vigilancia de Tsunami"

        if self.isSpanish(language):
             hazName = hazNameSpn

        phraseDict = self.getEnglishSpanishDict(language)
        if vtecAction in ["CAN", "EXP", "UPG"]:
            prefix += f"{hazName} {phraseDict['isCancelledFor']}: "
        elif vtecAction == "NEW":
            prefix += f"{hazName} {phraseDict['isNowInEffectForText']}: "
        elif vtecAction == "CON":
            prefix += f"{hazName} {phraseDict['remainsInEffectForText']}: "
        elif vtecAction == "EXA":
            prefix += f"{hazName} {phraseDict['modifedAreaText']}: "
        else:
            prefix += f"{hazName}:"
        return prefix

    def getCoastAreaPrefixText(self, segmentCancelled, language):
        '''
        @summary: Get the coast area prefix string based on language
        @param segmentCancelled: Are all VTEC lines a CAN/EXP/UPG?
        @param language: The language to produce the message in (default is English)
        @return: String
        '''
        phraseDict = self.getEnglishSpanishDict(language)
        prefix = f"{phraseDict['coastalAreas']} {phraseDict['ofText']}"
        if not segmentCancelled:
            prefix = f"* {self.capitalizeFirstLetter(prefix)}"
        prefix += " "
        return prefix

    def getEnglishSpanishDict(self, language="English"):
        '''
        @summary: Get a dictionary of common phrases in either English
        or Spanish
        @param language: The optional language; default is English
        @return: Dictionary
        '''
        if self.isSpanish(language):
            phraseDict = {
                "advisoryText": "aviso de tsunami",
                "warningText": "advertencia de tsunami",
                "watchText": "vigilancia de tsunami",
                "aText": "una",
                "andText": "y",
                "areText": "están",
                "isText": "esta",
                "theText": "el",
                "fromText": "de",
                "ofText": "de",
                "toText": "a",
                "forText": "para",
                "issuedByText": "expedido por",
                "milesText": "millas",
                "northText": "norte",
                "northeastText": "nordeste",
                "eastText": "este",
                "southeastText": "sudeste",
                "southText": "sur",
                "southwestText": "suroeste",
                "westText": "oeste",
                "northwestText": "noroeste",
                "includingText": "incluido",
                "cancelText": "cancelado",
                "updatesText": "actualizaciones",
                "noUpdatesText": "no hay actualizaciones en este mensaje",
                "coastalAreas": "areas costeras",
                "isNowInEffectText": "esta ahora en efecto",
                "isNowInEffectForText": "esta ahora en efecto para",
                "remainsInEffectText": "permanece en efecto",
                "remainsInEffectForText": "permanece en efecto para",
                "modifedAreaText": "esta modificado para incluir",
                "isCancelledFor": "ha sido cancelado para"
                }
        else:
            phraseDict = {
                "advisoryText": "tsunami advisory",
                "warningText": "tsunami warning",
                "watchText": "tsunami watch",
                "aText": "a",
                "andText": "and",
                "areText": "are",
                "isText": "is",
                "theText": "the",
                "fromText": "from",
                "ofText": "of",
                "toText": "to",
                "forText": "for",
                "issuedByText": "issued by",
                "milesText": "miles",
                "northText": "north",
                "northeastText": "northeast",
                "eastText": "east",
                "southeastText": "southeast",
                "southText": "south",
                "southwestText": "southwest",
                "westText": "west",
                "northwestText": "northwest",
                "includingText": "including",
                "cancelText": "cancelled",
                "updatesText": "updates",
                "noUpdatesText": "there are no updates in this message",
                "coastalAreas": "coastal areas",
                "isNowInEffectText": "is now in effect",
                "isNowInEffectForText": "is now in effect for",
                "remainsInEffectText": "remains in effect",
                "remainsInEffectForText": "remains in effect for",
                "modifedAreaText": "is modified to include",
                "isCancelledFor": "is cancelled for"
                }
        return phraseDict

    def getNTWC_SummaryHeadlines(self, productDict, language=""):
        '''
        @summary: Get the summary headlines for non-VTEC NTWC products
        @param: productDict: The product-level Dictionary
        @param language: The optional language (e.g., "" for English
        or "Spanish" for Spanish)
        @return: String
        '''
        phraseDict = self.getEnglishSpanishDict(language)
        headlineText = ""
        # If all segments have CAN VTECs then write one cancellation headline
        if self.agu.areAllSegmentsEnding(productDict):
            sigs = self.agu.getSigList(productDict, True)
            typeList = []
            if "W" in sigs:
                typeList.append(phraseDict["warningText"])
            if "Y" in sigs:
                typeList.append(phraseDict["advisoryText"])
            if "A" in sigs:
                typeList.append(phraseDict["watchText"])
            if typeList:
                if len(typeList) < 2:
                    isAre = phraseDict["isText"]
                else:
                    isAre = phraseDict["areText"]
                typeText = self.tpc.joinStringsWithOxfordComma(typeList, separator=", ",
                                                               lastSeparator=f" {phraseDict['andText']} ")
                # Convert "tsunami warning, tsunami advisory" to "tsunami warning, advisory"
                if not self.isSpanish(language):
                    typeText = typeText.replace("tsunami ", "")
                    typeText = f"tsunami {typeText}"

                headlineText += f"...{phraseDict['theText']} {typeText} {isAre} {phraseDict['cancelText']}...\n\n"
        else:
            timingPhraseDict = {
                "W": {"prefix": phraseDict["aText"], "timing": phraseDict["isNowInEffectText"]},
                "Y": {"prefix": phraseDict["aText"], "timing": phraseDict["isNowInEffectText"]},
                "A": {"prefix": phraseDict["aText"], "timing": phraseDict["isNowInEffectText"]},
                }
            # If this is a follow-up revise the text to use continuation language
            for segmentDict in productDict.get("segments"):
                for vtec in segmentDict.get("vtecRecords"):
                    hazardSig = vtec.get("sig")
                    hazardAction = vtec.get("act")
                    if hazardAction in ["CAN", "EXA", "CON"]:
                        timingPhraseDict[hazardSig] = {"prefix": phraseDict["theText"], "timing": phraseDict["remainsInEffectText"]}
            if productDict.get("hasActiveWarnings"):
                headlineText += f"...{timingPhraseDict['W']['prefix']} {phraseDict['warningText']} {timingPhraseDict['W']['timing']}...\n\n"
            if productDict.get("hasActiveAdvisories"):
                headlineText += f"...{timingPhraseDict['Y']['prefix']} {phraseDict['advisoryText']} {timingPhraseDict['Y']['timing']}...\n\n"
            if productDict.get("hasActiveWatches"):
                headlineText += f"...{timingPhraseDict['A']['prefix']} {phraseDict['watchText']} {timingPhraseDict['A']['timing']}...\n\n"
        headlineText = headlineText.upper()
        return headlineText

    def getPTWC_HeadlineLocations(self, productRegion, locationList):
        '''
        @summary: Given a product region and list of locations, get the
        formatted phrase to put into the headline
        @param productRegionAbbrev: The product region abbreviation (e.g., Hi)
        @param locationList: A list of locations as Strings
        @return: String
        '''
        locationText = ""
        if productRegion == "Hi":
            countyNumber = len(locationList)
            if countyNumber == 4:
                locationText = "All counties in the state of Hawaii"
            elif countyNumber == 1:
                locationText = f"{locationList[0]} COUNTY"
            elif countyNumber == 2:
                locationText = f"{locationList[0]} AND {locationList[1]} COUNTIES"
            elif countyNumber == 3:
                locationText = f"{locationList[0]}...{locationList[1]}... AND {locationList[2]} COUNTIES"
        else:
            locationText = self.tpc.joinStringsWithOxfordComma(locationList)
        return locationText

    def getPTWC_SummaryHeadlines(self, productDict, language=""):
        '''
        @summary: Get the summary headlines for non-VTEC PTWC products
        @param: productDict: The product-level Dictionary
        @param language: The optional language (e.g., "" for English
        or "Spanish" for Spanish)
        @return: String
        '''
        headlineText = ""
        phraseDict = self.getEnglishSpanishDict(language)
        # Walk through segments and determine which local locations
        # are associated with a specific hazard type and VTEC action
        # (e.g., {"W": "NEW": [...], "CON": [...]}
        vtecInfoDict = {}
        for segmentDict in productDict.get("segments"):
            subRegionNames = segmentDict.get("subRegionLocations")
            vtecRecords = segmentDict.get("vtecRecords")
            for vtecRecord in vtecRecords:
                sig = vtecRecord["sig"]
                if sig not in vtecInfoDict:
                    vtecInfoDict[sig] = {}
                act = self.tpc.getVtecAction(vtecRecord)
                if act not in vtecInfoDict[sig]:
                    vtecInfoDict[sig][act] = []
                vtecInfoDict[sig][act] += subRegionNames
        # Loop over possible VTEC actions and create a headline
        # when a unique single location or multiple locations are found
        # Once a location is found, do not repeat it.
        for sig in vtecInfoDict:
            hazardDict = vtecInfoDict[sig]
            if sig == "W":
                hazardName = phraseDict["warningText"]
            if sig == "Y":
                hazardName = phraseDict["advisoryText"]
            if sig == "A":
                hazardName = phraseDict["watchText"]
            headlinedAreas = []
            for vtecAction in ["NEW", "CON", "EXA", "CAN"]:
                if vtecAction in hazardDict:
                    # Loop over locations with this VTEC action and see if any are unique
                    locationList = []
                    for localName in hazardDict[vtecAction]:
                        if localName not in headlinedAreas:
                            locationList.append(localName)
                            headlinedAreas.append(localName)
                    # Unique location(s) found, build headline phrase
                    if locationList:
                        connector = f" {phraseDict['forText']} "
                        if vtecAction == "NEW":
                            vtecDescriptor = phraseDict["isNowInEffectText"]
                            prefix = phraseDict["aText"]
                        elif vtecAction == "CON":
                            vtecDescriptor = phraseDict["remainsInEffectText"]
                            prefix = phraseDict["theText"]
                        elif vtecAction == "EXA":
                            connector = " "
                            vtecDescriptor = phraseDict["modifedAreaText"]
                            prefix = phraseDict["theText"]
                        elif vtecAction == "CAN":
                            vtecDescriptor = f"{phraseDict['isText']} {phraseDict['cancelText']}"
                            prefix = phraseDict["theText"]
                        # For Pr public product is different from Hi, As, and Gu, it has areaList product part
                        # instead of vtecString which is in segmented product, and summary headline will not
                        # have location text there
                        if productDict.get("productRegion") == "Pr":
                            connector = ""
                            locationText = ""
                        else:
                            locationText = self.getPTWC_HeadlineLocations(productDict.get("productRegion"), locationList)

                        headline = f"...{prefix} {hazardName} {vtecDescriptor}{connector}{locationText}...\n\n"
                        headlineText += headline
        headlineText = headlineText.upper()
        return headlineText

    # Help functions for TIS evaluation Bullet
    def isQuakeDeep(self, inputDict, suffix):
        '''
        @summary: Retrieves the quake depth from the event-level
        dictionary and determine if it is a deep quake
        @param inputDict: A tier of the product-level dictionary (product,
        segment, section, or event)
        @param suffix: The field name suffix
        @return: Boolean
        '''
        depthInKm = int(inputDict.get(f"originDepth{suffix}")) * GeneralConstants.KILOMETERS_PER_MILE
        return depthInKm > HazardConstants.DEEP_QUAKE_THRESHOLD_DEPTH

    def isPhysicalEventOnshore(self, inputDict, suffix):
        '''
        @summary: Retrieves the distance to the coastline of tsunamigenic event from the
        event-level dictionary and determine if it is an onshore (a negative number) or
        offshore (a positive number)
        @param inputDict: A tier of the product-level dictionary (product,
        segment, section, or event)
        @param suffix: The field name suffix
        @return: Boolean
        '''
        distanceToCoastKm = int(inputDict.get(f"distanceToCoastKm{suffix}"))
        return distanceToCoastKm < 0

    def isTisSignificantMagnitude(self, eventDict):
        '''
        @summary: Check if this physical event is seismic type and meet
        minimum magnitude where TIS High language is used, although a real
        TS.S.tisHigh is only appropriate if M >= 7.9.
        @param eventDict: The event-level dictionary
        @return: Boolean
        '''
        highMagnitude = False
        peType = eventDict.get("physicalEventType")
        magnitude = eventDict.get("magnitude")
        if self.agu.isPhysicalEventTypeSeismic(peType) and magnitude >= 6.5:
            highMagnitude = True
        return highMagnitude

    def isTisSupplementalMessage(self, sectionDict):
        '''
        @summary: Check that this message is supplemental
        @param sectionDict: The section-level dictionary
        @return: Boolean
        '''
        return self.tpc.getVtecAction(sectionDict.get("vtecRecord")) != "NEW"

    def getPhysicalEventTypeString(self, eventDict):
        '''
        @summary: Get a string descriptor based on the physical event type
        @param eventDict: The event-level dictionary
        @return: String
        '''
        peTypeString = ""
        physicalEventType = eventDict.get("physicalEventType")
        if self.agu.isPhysicalEventTypeSeismic(physicalEventType):
            peTypeString = "earthquake epicenter"
        elif self.agu.isPhysicalEventTypeVolcanic(physicalEventType):
            peTypeString = "volcano"
        elif self.agu.isPhysicalEventTypeLandslide(physicalEventType):
            peTypeString = "landslide"
        elif self.agu.isPhysicalEventTypeUnknown(physicalEventType):
            peTypeString = "unknown event"
        return peTypeString

    def getArcticOceanProcRegionText(self, language=""):
        '''
        @summary: Get the arctic ocean procedural region text
        @param language: The optional language (e.g., "" for English
        or "Spanish" for Spanish)
        @return: String
        '''
        if self.isSpanish(language):
            return "Alaska y la región ártica canadiense"
        else:
            return "Alaska and the Canadian Arctic region"

    def getTisUgcsBasedOnProductRegion(self, productRegion):
        '''
        @summary: Get the strings of the product region's UGCs
        @param productRegion: The product region abbreviation
        @return: String
        '''
        ugcStr = ""
        if productRegion == "Hi":
            ugcStr = "HIZ001-003-006>007-009-016>018-023-026-029>035-037>050-051>054"
        elif productRegion == "As":
            ugcStr = "ASZ001>004"
        elif productRegion == "Gu":
            ugcStr = "GUZ001>004"
        elif productRegion == "Pr":
            ugcStr = "AMZ712-715-725-735-742-745-PRZ001>003-005-007-008-010>013-VIZ001-002"
        return ugcStr

    def getAudienceBullet_text(self, productRegion):
        '''
        @summary: Supports the creation of the audienceBullet product part
        @param productRegion: The product region abbreviation
        @return: String
        '''
        text = ""
        if productRegion in self.nonUsProductRegions():
            text = f"{self.nonUsProductRegionsAudienceBullet_text(productRegion)}\n"
        elif productRegion in ["Hi", "As", "Gu", "Pr"]:
            text = ("AUDIENCE\n"
                    "--------\n")
            if productRegion == "Gu":
                text += "Guam and CNMI emergency managers, media, and general public."
            elif productRegion == "As":
                text += "American Samoa emergency managers, media, and general public."
            elif productRegion == "Hi":
                text += "Emergency management in the State of Hawaii."
            elif productRegion == "Pr":
                phrase = ("Government officials, media, and general public of Puerto "
                          "Rico, the U.S. Virgin Islands, and the British Virgin "
                          "Islands.")
                text += self.wrapText(phrase)
            text += "\n\n"
        return text

    def getEvalutionBulletLocation_text(self, productRegion):
        '''
        @summary: Get the location description for different product region
        @param productRegion: The product region abbreviation
        @return: String
        '''
        locationString = ""
        if productRegion == "Pr":
            locationString = "Puerto Rico and the Virgin Islands"
        elif productRegion == "Gu":
            locationString = "Guam... Rota... Tinian and Saipan"
        elif productRegion == "As":
            locationString = "American Samoa"
        if locationString:
            text = (f"The Tsunami threat to {locationString} from this "
                    "earthquake is still being evaluated.")
        elif productRegion == "Hi":
            text = ("Based on all available data a tsunami may have been generated by "
                    "this earthquake that could be destructive on coastal areas even "
                    "far from the epicenter. An investigation is underway to determine "
                    "if there is a tsunami threat to Hawaii.")
        return text

    def getEvaluationEarliestEstimatedArrivalTime_text(self, eventDict, suffix, productRegion, useReverseTTT=False):
        '''
        @summary: Get the earliest estimated arrival time of tsunami waves
        within this region
        @param eventDict: The event level dictionary
        @param suffix: The field name suffix
        @param productRegion: The product region abbreviation
        @param useReverseTTT: If True, we'll try to use reverse TTT data (HI, As, Gu, PR). Otherwise, dynamic TTT.
        @return: String
        '''
        arrivalTime = 0
        text = ""
        stations = eventDict.get(f"forecastRunTable{suffix}")
        if stations and not useReverseTTT:
            arrivalTime = stations[0][5]
        # Will get ETA from reverse TTT
        else:
            arrivalTime = self.getEarliestEstimatedArrivalTimeFromReverseTTT(eventDict, suffix, productRegion)
            if arrivalTime:
                arrivalTime = TimeUtil.epochTimeMillisToDatetime(arrivalTime).strftime("%H%M %m/%d/%y")
        if arrivalTime:
            arrivalTime = datetime.datetime.strptime(arrivalTime, "%H%M %m/%d/%y")
            timeZone = self.alu.getPrimaryTimezoneByProductRegionAbbreviation(productRegion)
            timeFormat = "%l%M %p %Z %A %b %e %Y"
            tzTimeDT = TimeUtil.changeTimezoneOfDatetimeObject(arrivalTime, timeZone)
            arrivalTimeText = tzTimeDT.strftime(timeFormat)
            regionNameText = self.alu.getProductRegionNameFromAbbreviation(productRegion)
            text = ("If a tsunami threat exists... the earliest "
                    "estimated arrival time of tsunami waves within "
                    f"{regionNameText} would be: "
                    f"                          {arrivalTimeText}")
        return text

    def getEarliestEstimatedArrivalTimeFromReverseTTT(self, eventDict, suffix, productRegion):
        '''
        @summary: Get the earliest arrival time from reverse TTT
        @param eventDict: The event level dictionary
        @param suffix: The field name suffix
        @param productRegion: The product region abbreviation
        @return: Arrival time in ms
        '''
        longitude = eventDict.get(f"originLongitude{suffix}")
        latitude = eventDict.get(f"originLatitude{suffix}")
        travelTimeHours = 0
        arrivalTimeMs = 0
        reverseTTTDict = ReverseTTTClientUtils.getAllTravelTimeHours(longitude, latitude)
        if productRegion == "Hi" and ReverseTTTRegion.HAWAII in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.HAWAII]
        elif productRegion == "As"and ReverseTTTRegion.AMSAM in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.AMSAM]
        elif productRegion == "Gu" and ReverseTTTRegion.GUAM in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.GUAM]
        elif productRegion == "Pr" and ReverseTTTRegion.PRVI in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.PRVI]
        if travelTimeHours:
            originTime = eventDict.get(f"originTime{suffix}")
            arrivalTimeMs = originTime + (travelTimeHours * GeneralConstants.MILLIS_PER_HOUR)
        return arrivalTimeMs

    def nonUsProductRegionsAudienceBullet_text(self, productRegion):
        '''
        @summary: Supports the creation of the audienceBullet product part
        @param inputDict: The input dictionary
        @return: String
        '''
        text = ""
        locationText = ""
        if productRegion == "Pac":
            locationText = "Pacific tsunami warning and mitigation system "
        elif productRegion == "Car":
            locationText = ("tsunami and other coastal hazards warning system for "
                            "the Caribbean and adjacent regions ")
        phraseList = [
            self.noticeText(),
            ("This message is issued for information only in support of the "
             f"UNESCO/IOC {locationText}and "
             "is meant for national authorities in each country of that system."),
             ("National authorities will determine the appropriate level of "
              "alert for each country and may issue additional or more "
              "refined information."),
             self.noticeText(),
             ]
        for phrase in phraseList:
            wrappedPhrase = self.wrapText(phrase, "", "")
            text += f"{wrappedPhrase}\n\n"
        return text

    def noticeText(self):
        '''
        @summary: The text for audienceBullet prefix and suffix
        @return: String
        '''
        return "**** NOTICE **** NOTICE **** NOTICE **** NOTICE **** NOTICE *****"

    def nonUsProductRegionsAdditionalInfo(self, productRegion):
        '''
        @summary: Get the additional text for non U.S. product region
        @param productRegion: The product region
        @return: A list of string
        '''
        if productRegion == "Pac":
            phraseList = [
                ("Coastal regions of Hawaii... American Samoa... Guam... and CNMI should "
                 "refer to Pacific Tsunami Warning Center messages specifically for "
                 "those places that can be found at www.tsunami.gov."),
                ("Coastal regions of California... Oregon... Washington... British "
                 "Columbia and Alaska should refer to U.S. National Tsunami "
                 "Warning Center messages that can be found at www.tsunami.gov.")]
        elif productRegion == "Car":
            phraseList = [("Coastal regions of the US gulf coast... US east coast... and "
                           "the maritime provinces of Canada should refer to U.S. "
                           "National Tsunami Warning Center messages that can be "
                           "found at www.tsunami.gov.")]
        return phraseList

    def puertoRicoAdditionalInfo(self):
        '''
        @summary: Get the additional text for Puerto Rico
        @return: A list of string
        '''
        phraseList = [
            ("Further information about this event and any tsunami threat "
             "to Puerto Rico and the Virgin Islands may be found at "
             "www.tsunami.gov."),
            ("Information regarding any tsunami threat to Gulf of America "
             "or Atlantic coasts will be issued by the US National Tsunami "
             "Warning Center and can be found at www.tsunami.gov."),
            ]
        return phraseList

    '''
    Other Local Helper Methods
    '''

    def isSpanish(self, language):
        '''
        @summary: Check if the language being produced is in Spanish or English
        @param language: The language string (e.g., "Spanish" for Spanish)
        @return: Boolean
        '''
        return language == "Spanish"

    def getAwipsInfoDict(self, regionAbbrev, productID, formatterType, siteID):
        '''
        @summary: Returns a local information dictionary that contains the AWIPS ID,
        WMO ID, and product description
        @param regionAbbrev: The product region abbreviation (e.g., Hi)
        @param productID: The AWIPS product ID (e.g., TSU or TIB)
        @param formatterType: The formatter type (e.g., Pub or Spanish)
        @param siteID: The site ID (i.e., NTWC or PTWC)
        '''
        # Get the correct info dict
        if siteID == "NTWC":
            infoDict = self.wmoAndAwipsInfoDict_NTWC()
        elif siteID == "PTWC":
            infoDict = self.wmoAndAwipsInfoDict_PTWC()
        else:
            infoDict = {}
        # Assemble a unique key to access the dictionary
        dictKey = f"{regionAbbrev}.{productID}.{formatterType}"
        # Retrieve dictionary contents
        resultDict = infoDict.get(dictKey)
        if not resultDict:
            resultDict = {
                "awipsID": "",
                "wmoID": "",
                "productDescr": "",
                }
        resultDict["officeID"] = self.getOfficeIdBySiteId(siteID)
        return resultDict

    def capitalizeFirstLetter(self, textString):
        '''
        @summary: Captialize the first letter of a text string
        @param textString: The input string
        @return: String
        '''
        if textString:
            return f"{textString[0].upper()}{textString[1:]}"
        return textString

    def wrapText(self, text, initialIndentText=" * ", nextIndentText="   "):
        '''
        @summary: Method to break string blocks longer than 65 characters into
        multi-line strings with indentation and sub-bullets
        @param text: The input text to process
        @param initialIndentText: The initial text to the first line of the text block
        @param nextIndentText: The subsequent indentation text
        @return: A formatted text string
        '''
        wrappedText = textwrap.fill(text, width=65, initial_indent=initialIndentText,
                                    subsequent_indent=nextIndentText)
        return wrappedText
