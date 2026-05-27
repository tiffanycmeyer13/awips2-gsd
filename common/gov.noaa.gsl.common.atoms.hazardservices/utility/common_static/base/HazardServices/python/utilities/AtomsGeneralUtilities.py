# *** Override behavior of AtomsGeneralUtilities.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Contains general utility methods for ATOMS

    @since: April 2022
    @author: GSL Hazard Services Team
'''

import AtomsFcstObsUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMapUtilities
import AtomsTableForecastRuns
import Bridge
import GeneralConstants
import GeneralUtilities
import GenericRegistryObjectDataAccess as GRODA
import GeometryUtilities
import HazardConstants
import TextProductCommon
from gov.noaa.gsl.common.dataplugin.atoms import PrefMagnitudeType
from gov.noaa.gsl.common.dataplugin.pem import PhysicalEventManager, PhysicalEventType
from gov.noaa.gsl.viz.atomsForecast import TsunamiForecastDao


class AtomsGeneralUtilities(object):

    def __init__(self):
        self.afou = AtomsFcstObsUtilities.AtomsFcstObsUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amu = AtomsMapUtilities.AtomsMapUtilities()
        self.geomUtils = GeometryUtilities.GeometryUtilities()
        self.pem = PhysicalEventManager.getInstance()
        self.tfd = TsunamiForecastDao.getInstance()
        areaDict = Bridge.Bridge().getAreaDictionary()
        self.tpc = TextProductCommon.TextProductCommon()
        self.tpc.setUp(areaDict)

    ###############################################################
    # Product metadata/megawidget parsing methods
    ###############################################################
    def getMagnitudeTypeChoices(self):
        '''
        @summary: Build a list of megawidget choices for using the
        information defined in PrefMagnitudeType.java
        @return: List of megawidget choice dictionaries
        '''
        choices = []
        for label in PrefMagnitudeType.getValidLabels():
            abbev = PrefMagnitudeType.fromString(label).getAbbreviation()
            choice = {"identifier": label, "displayString": f"{label} ({abbev})"}
            choices.append(choice)
        return choices

    ###############################################################
    # Product generation dictionary parsing methods
    ###############################################################

    def isSegmentCancelExpire(self, segmentDict):
        '''
        @summary: Method that checks if all Valid Time Event Code (VTEC) lines in a single
        segment contain either CAN, EXP, or UPG  actions (returns True)
        @param segmentDict: The segment-level dictionary
        @return: Boolean
        '''
        is_CAN_EXP_UPG = True
        for vtecRecord in segmentDict.get("vtecRecords"):
            is_CAN_EXP_UPG = is_CAN_EXP_UPG and self.tpc.getVtecAction(vtecRecord) in ["CAN", "EXP", "UPG"]
        return is_CAN_EXP_UPG

    def areAllSegmentsEnding(self, productDict):
        '''
        @summary: Method that checks if all segments in a product message contain either CAN,
        EXP, or UPG Valid Time Event Code (VTEC) actions (returns True)
        @param productDict: The product dictionary created by the product generator
        @return: Boolean
        '''
        allCAN = True
        for segmentDict in productDict.get("segments"):
            if not self.isSegmentCancelExpire(segmentDict):
                allCAN = False
                break
        return allCAN

    def getAllEventDicts(self, inputDict):
        '''
        @summary: Given a product dictionary or some sub-dictionary inside it (i.e.,
        segment or section level), retrieve all event-level dictionaries
        @param inputDict: The product or segment or section-level dictionary
        @return: A list of event-level dictionaries
        '''
        eventDicts = []
        sectionDicts = self.getAllSectionDicts(inputDict)
        for sectionDict in sectionDicts:
            eventDicts += sectionDict.get("eventDicts")
        return eventDicts

    def getSectionDict(self, inputDict):
        '''
        @summary: Given a product dictionary or some sub-dictionary inside it (i.e.,
        segment or section level), retrieve the section-level dictionary
        @param inputDict: The product or segment or section-level dictionary
        @return: The section-level dictionary
        '''
        if "segments" in inputDict:
            sectionDict = inputDict.get("segments")[0].get("sections")[0]
        elif "sections" in inputDict:
            sectionDict = inputDict.get("sections")[0]
        else:
            sectionDict = inputDict
        return sectionDict

    def getActiveSectionDicts(self, inputDict):
        '''
        @summary: Get a list of section dictionaries with active VTEC codes
        @param inputDict: The product or segment or section-level dictionary
        @return: List of section-level dictionaries
        '''
        activeSectionDicts = []
        sectionDicts = self.getAllSectionDicts(inputDict)
        for sectionDict in sectionDicts:
            vtecRecord = sectionDict.get("vtecRecord")
            action = self.tpc.getVtecAction(vtecRecord)
            if action not in ["CAN", "EXP", "UPG"]:
                activeSectionDicts.append(sectionDict)
        return activeSectionDicts

    def getAllSectionDicts(self, inputDict):
        '''
        @summary: Given a product dictionary or some sub-dictionary inside it (i.e.,
        segment or section level), retrieve all section-level dictionaries
        @param inputDict: The product or segment or section-level dictionary
        @return: A list of section-level dictionaries
        '''
        sectionDicts = []
        if "segments" in inputDict:
            for segmentDict in inputDict.get("segments"):
                sectionDicts += segmentDict.get("sections")
        elif "sections" in inputDict:
            sectionDicts += inputDict.get("sections")
        else:
            sectionDicts.append(inputDict)

        return sectionDicts

    def getSigList(self, inputDict, allSigs=True):
        '''
        @summary: Given a product dictionary or some sub-dictionary inside it (i.e.,
        segment or section level), retrieve all or active sigs
        @param inputDict: The product or segment or section-level dictionary
        @param allSigs: Boolean; True means grab all significance codes, even ones
        that are part of CAN/EXP VTEC actions. False means only grab significance codes
        associated with non-CAN/EXP events.
        @return: A list of section-level dictionaries
        '''
        sigList = []
        if allSigs:
            sectionDicts = self.getAllSectionDicts(inputDict)
        else:
            sectionDicts = self.getActiveSectionDicts(inputDict)
        for section in sectionDicts:
            for eventDict in section.get("eventDicts"):
                sig = eventDict.get("sig")
                if sig not in sigList:
                    sigList.append(sig)
        return sigList

    def getPhysicalEventLatLon(self, eventDict, productLabel):
        '''
        @summary: Get the physical event latitude and longitude from
        the event-level dictionary
        @param eventDict: The event-level dictionary
        @param productLabel: The 'productLabel' parameter from the productDict
        @return: Tuple containing the latitude and longitude
        '''
        peLat = eventDict.get(f"originLatitude_{productLabel}")
        peLon = eventDict.get(f"originLongitude_{productLabel}")
        if not peLat:
            peLat = eventDict.get("originLatitude")
            peLon = eventDict.get("originLongitude")
        return peLat, peLon

    def getLocationInformation(self, productDict, onlyFE):
        '''
        @summary: Given a productDict, get the relevant location description
        information
        @param productDict: The product-level dictionary
        @param onlyFE: Boolean to determine whether to only grab the
        Flinn-Engdahl location (True) or site-specific locations (False)
        @return: String
        '''
        siteID = productDict.get("siteID")
        productLabel = productDict.get("productLabel")
        productRegion = productDict.get("productRegion")
        eventDict = self.getAllEventDicts(productDict)[0]
        physicalEvent = self.retrievePhysicalEventFromInputDict(productDict)
        if physicalEvent is None:
            peLat, peLon = self.getPhysicalEventLatLon(eventDict, productLabel)
        else:
            peLat = physicalEvent.getLatitude()
            peLon = physicalEvent.getLongitude()
        locationInfoDict = {
            "primary": None,
            "secondary": None,
            "flinn-engdahl": None
            }
        locationInfoList = []

        if not onlyFE:
            if siteID == "NTWC":
                locationInfoList = self.alu.getNearestCities(peLat, peLon, productRegion)
                if locationInfoList:
                    locationInfoDict["primary"] = locationInfoList[0]
                    if len(locationInfoList) > 1:
                        locationInfoDict["secondary"] = locationInfoList[1]
            elif siteID == "PTWC":
                peGeometry = self.geomUtils.bufferPoint(peLat, peLon, 0.1)
                distanceResultDict = {
                    "genericName": None,
                    "name": None,
                    "distanceMiles": None,
                    "bearingString": None,
                    }
                if productRegion == "Hi":
                    locationInfoDict["primary"] = self.alu.getHawaiiLocationInformation(peGeometry)
                elif productRegion == "As":
                    distanceResultDict = self.alu.getAmSamLocationInformation(peGeometry, distanceResultDict)
                elif productRegion == "Gu":
                    distanceResultDict = self.alu.getGuamLocationInformation(peGeometry, distanceResultDict)
                elif productRegion == "Pr":
                    distanceResultDict = self.alu.getPRVI_LocationInformation(peGeometry, distanceResultDict)
                if not locationInfoDict["primary"]:
                    if distanceResultDict.get("genericName"):
                        locationInfoDict["primary"] = distanceResultDict["genericName"]
                    elif distanceResultDict["name"]:
                        locationInfoDict["primary"] = (f"{distanceResultDict['distanceMiles']} miles {distanceResultDict['bearingString']} "
                                                       f"of {distanceResultDict['name']}")
        # Get Flinn-Engdahl region
        queryResult = self.amu.getFlinnEngdahlByPhysicalEventLocation(peLat, peLon)
        if queryResult:
            regionText = queryResult.getString("prep")
            locationInfoDict["flinn-engdahl"] = regionText
            if not locationInfoDict["primary"]:
                locationInfoDict["primary"] = regionText
        return [locationInfoDict]

    ###############################################################
    # Registry/Message number access methods
    ###############################################################

    def getTsunamiMessageCount(self, customId, isPractice, productRegionAbbrev=None):
        '''
        @summary: Returns the count of hazard events that have been issued for a given
        physical event customId and optional productRegionAbbrev
        @param customId: The customId of the physical event (e.g., HumboldtDec2024)
        @param productRegionAbbrev: The product region abbreviation (e.g., Hi)
        @param isPractice: Boolean determining if we are in practice mode (True) or not (False)
        @return: An integer
        '''
        queryDict = [
                ("objectType", "TsunamiMessageNumber"),
                ("customId", customId)
                ]
        # First query generic registry object database to see if entry exists
        if productRegionAbbrev is not None:
            queryDict += [
                ("region", productRegionAbbrev)
            ]
        results = GRODA.queryObjects(queryDict, isPractice)
        messageNumber = 0
        for result in results:
            messageNumber = messageNumber + result["messageNumber"]

        return messageNumber

    def getTsunamiMessageNumber(self, productDict):
        '''
        @summary: Generate Tsunami message number
        @param productDict: Dictionary created by the TSU_ProductGenerator
        @return: An integer
        getTsunamiMessageNumber() is called in the formatter instead of the
        generator is to ensure it only calls storeObject() to the registry
        when the issueFlag is set to True. Setting the issueFlag occurs in
        the following method call chain:
        updateProductDictionariesForIssue() -> updateProductsForIssue() ->
        executeGeneratorUpdate() -> executeGeneratorFrom().
        '''
        customId = productDict.get("customId")
        region = productDict.get("productRegion")
        uniqueId = f"ATOMS_Message_{customId}_{region}"
        issueFlag = productDict.get("issueFlag")
        practice = GeneralUtilities.isPractice(productDict.get("runMode"))
        messageNumber = productDict.get("messageNumber")
        if not messageNumber:
            # First query generic registry object database to see if entry exists
            queryDict = [
                ("objectType", "TsunamiMessageNumber"),
                ("customId", customId),
                ("region", region)
                ]
            results = GRODA.queryObjects(queryDict, practice)
            if results:
                for result in results:
                    messageNumber = result["messageNumber"]
            else:
                messageNumber = 1
        productDict["messageNumber"] = messageNumber
        objectDict = {
            "uniqueID": uniqueId,
            "objectType": "TsunamiMessageNumber",
            "region": region,
            "customId": customId,
            "messageNumber": messageNumber + 1,
            }

        if issueFlag:
            GRODA.storeObject(objectDict, practice)
        return messageNumber

    ###############################################################
    # Product dictionary lookup & general methods
    ###############################################################

    def validateSelectedPhysicalEvent(self, selectedEventList):
        '''
        @summary: Determine if only one physical event was selected. If not, throw
        message
        @param selectedEventList: The list of selected events
        @return: String error message if zero or multiple physical events are selected
        or None if only one event is selected
        '''
        errorMsg = None
        if len(selectedEventList) < 1:
            errorMsg = "Error: Select a physical event from the PEM Dialog first.\n"
        elif len(selectedEventList) > 1:
            errorMsg = "Error: Only one physical event must be selected.\n"
        return errorMsg

    def isPhysicalEventTypeSeismic(self, peTypeString):
        '''
        @summary: Retrieves the physical event type from the event-level
        dictionary and determine if it is of type 'Seismic'
        @param peTypeString: A string representation of the physical event type
        @return: Boolean
        '''
        return peTypeString == "Seismic"

    def isPhysicalEventTypeVolcanic(self, peTypeString):
        '''
        @summary: Retrieves the physical event type from the event-level
        dictionary and determine if it is of type 'Volcanic'
        @param peTypeString: A string representation of the physical event type
        @return: Boolean
        '''
        return peTypeString == "Volcanic"

    def isPhysicalEventTypeLandslide(self, peTypeString):
        '''
        @summary: Retrieves the physical event type from the event-level
        dictionary and determine if it is of type 'Landslide'
        @param peTypeString: A string representation of the physical event type
        @return: Boolean
        '''
        return peTypeString == "Landslide"

    def isPhysicalEventTypeUnknown(self, peTypeString):
        '''
        @summary: Retrieves the physical event type from the event-level
        dictionary and determine if it is of type 'Unknown'
        @param peTypeString: A string representation of the physical event type
        @return: Boolean
        '''
        return peTypeString == "Unknown"

    def retrievePhysicalEventFromInputDict(self, inputDict):
        '''
        @summary: Retrieve the physical event based on id and type
        @param inputDict: A tier of the product-level dictionary (product,
        segment, section, or event)
        @return: The physical event
        '''
        customId = inputDict.get("customId")
        peTypeStr = inputDict.get("physicalEventType")
        peType = PhysicalEventType.fromString(peTypeStr)
        peEvent = self.pem.retrievePhysicalEvent(customId, peType)
        return peEvent

    def getConsecutiveSegmentGroups(self, breakPointSegmentDicts):
        '''
        @summary: Given a list of dictionaries of break point segment
        information, usually from the product dictionary, group into
        consecutive numbers (e.g., [[1, 3], [7,9]])
        @param breakPointSegmentDicts: A dictionary of break point segment information from
        the segment-level dictionary
        @return: Nested list of integers
        '''
        coastSortNums = [self.getBreakPointInteger(brkptseg.get(HazardConstants.BP_NUM_ATTR_NAME))
                         for brkptseg in breakPointSegmentDicts]
        consecutiveNumGroups = self.groupConsecutiveNum(coastSortNums)
        return consecutiveNumGroups

    def getBreakPointInteger(self, bpNumString):
        '''
        @summary: Convert the string of the break point number to
        an integer and account for non-numeric values
        @param bpNumString: The break point number as a string
        @return: Integer
        '''
        return int(float(bpNumString.strip()))

    def groupConsecutiveNum(self, nums):
        '''
        @summary: Group the consecutive numbers
        @param: Numbers to group
        @return: The groups of consecutive numbers
        '''
        gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s + 1 < e]
        edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
        return list(zip(edges, edges))

    ###############################################################
    # Hazard event / AOI methods
    ###############################################################

    def getBreakPointSegmentCoveragesFromHazardEvent(self, hazardEvent):
        '''
        @summary: Get the break point segment AOI coverages from a hazard
        event
        @param hazardEvent: The selected hazard event
        @return: List of dictionaries
        '''
        return [coverage for coverage in hazardEvent.getAOICoverages()
                if coverage.get("type") == "BrkptSeg_NoClip"]

    def isBreakPointSegmentSpecial(self, breakPointSegment):
        '''
        @summary: Is the break point segment a special procedure region
        or not?
        @param breakPointSegment: A dictionary representation containing
        attributes associated with the break point segment. This could either
        be an AOI from the hazard event or from a part of the product dictionary
        @return: Boolean
        '''
        return breakPointSegment.get(HazardConstants.IS_SPECIAL) == "Y"

    ###############################################################
    # Product formatting/Recommender support methods
    ###############################################################

    def getTsunamiForecastRunsTable(self, inputDict, tz, suffix, language="English"):
        '''
        @summary: Retrieve the Tsunami forecast run table based on inputs.
        @param inputDict: Either product level dictionary or section level dictionary
        @param tz: Time zone
        @param suffix: Suffix
        @param language: The language of the Table text (default is "English")
        @return: A tsunami forecast run table
        '''
        fcstRunTable = None
        eventDicts = self.getAllEventDicts(inputDict)
        fcstRunTable = AtomsTableForecastRuns.Table(eventDicts=eventDicts,
                                                    timeZone=tz,
                                                    suffix=suffix,
                                                    language=language)
        return fcstRunTable

    def createForecastInfoDictionary(self, physicalEventID):
        '''
        @summary: Create a lookup of TsunamiForecastInfo objects mapped to possible selections
        in the timeOfArrivalSelection or amplitudeSelection megawidgets and ordered in reverse
        chronological order
        @return: A dictionary
        '''
        resultDict = {}
        typeTimeTuple = []
        for tfi in self.tfd.getTsunamiForecastInfos(physicalEventID):
            typeLabel = tfi.getForecastType().getLabel().ljust(7)
            timeLabel = f"{tfi.getRunTime()}"
            typeTimeTuple.append((timeLabel, typeLabel, tfi))
        if typeTimeTuple:
            # Sort in reverse chronological order
            typeTimeTuple = sorted(typeTimeTuple, key=lambda t: t[0], reverse=True)
            for singleTuple in typeTimeTuple:
                forecastKey = f"{singleTuple[1]} - {singleTuple[0]}"
                resultDict[forecastKey] = {
                "forecastTime": singleTuple[0],
                "forecastType": singleTuple[1],
                "forecast": singleTuple[2],
                }
        return resultDict

    def createTsunamiEventDict(self, hazardType, hazardGeometry, productRegion, hazardAttributes):
        '''
        @summary: Organize the hazard type, geometry, and product region into a dictionary
        @param hazardType: The hazard type name (e.g., TS.W)
        @param hazardGeometry: The hazard geometry as a shapely object
        @param productRegion: The The product region name (e.g., Hi)
        @param hazardAttributes: An dictionary containing the attribute name (key) and the
        attribute value (value) (e.g., {"tisType": "tisHigh"})
        @return: Dictionary
        '''
        # Determine the break point segment names under the hazard event geometry
        if hazardType in ["TS.W", "TS.Y", "TS.A"] and "hazardLocations" not in hazardAttributes:
            breakPointSegmentResults = self.amu.getBreakPointSegmentsByGeometry(hazardGeometry, pruneSmallAreas=False)
            if hazardAttributes.get("wwaLocationCoverage") == "segmentAreas":
                breakPointSegmentResults = self.amu.filterResultsByNonSpecialProcedureAreas(breakPointSegmentResults)
            hazardAttributes["hazardLocations"] = self.amu.getNamesFromQueryResults(breakPointSegmentResults)

        return {
            "hazardType": hazardType,
            "geometry": hazardGeometry,
            "productRegion": productRegion,
            "hazardAttributes": hazardAttributes,
            }

    ###############################################################
    # Query result manipulation / analysis methods
    ###############################################################

    def getCoverageTypeFromQueryResults(self, queryResults):
        '''
        @summary: Given a set of break point segment query results, determine
        if the results contains:
        (1) Only break point segments
        (2) Only special procedure regions
        (3) Both
        and assign a 'coverageType' string to the result
        @param queryResults: A list of MapsDatabaseAccessor query results
        @return: String
        '''
        hasSegment = False
        hasSpecial = False
        for queryResult in queryResults:
            if self.amu.isQueryResultSpecial(queryResult):
                hasSpecial = True
            else:
                hasSegment = True
        if hasSegment and hasSpecial:
            coverageType = "allAreas"
        elif hasSegment:
            coverageType = "segmentAreas"
        else:
            coverageType = "specialAreas"
        return coverageType

    ###############################################################
    # county
    ###############################################################

    def getCountyNamesByBreakPointSegmentNames(self, breakPointSegmentNames):
        '''
        @summary: Given a list of break point segment names, get the county names that intersect
        with this area
        @param breakPointSegmentNames: A list of break point segment names (e.g., ["Kona", "Big Island South"])
        @return: List of strings
        '''
        countyNames = []
        segmentQueryResults = self.amu.getBreakPointSegmentsBySegmentNames(breakPointSegmentNames)
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(segmentQueryResults)
        countyQueryResults = self.amu.getCountiesByGeometry(unionedGeometry)
        for queryResult in countyQueryResults:
            countyNames.append(self.amu.getStringFromQueryResult(queryResult, "countyname"))
        # Remove duplicates
        countyNames = list(set(countyNames))
        return countyNames

    ###############################################################
    # ptwc_warning_points
    ###############################################################

    def getPtwcWarningPointsWithinDistanceRangeFromPoint(self, latitude, longitude,
                                                         minDistanceInKm, maxDistanceInKm):
        '''
        @summary: Get break points within a user-defined multi-distance range from a point
        @param latitude: The latitude (in decimal degrees)
        @param longitude: The longitude (in decimal degrees)
        @param minDistanceInKm: A user-defined minimum distance (in km)
        @param maxDistanceInKm: A user-defined minimum distance (in km)
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryGeometry = self.geomUtils.getDonutGeometryFromPoint(latitude, longitude, minDistanceInKm, maxDistanceInKm)
        queryResults = self.amu.queryPtwcWarningPointsByGeometry(queryGeometry)
        return queryResults

    ###############################################################
    # tsunami_threat_db_source_regions
    ###############################################################

    def filterOutSourceRegionResultsForKnownEvents(self, sourceRegionQueryResults):
        '''
        @summary: Check if any source region query results are for known events and remove them
        @param sourceRegionQueryResults: A list of MapsDatabaseAccessor query results
        @return: A list of MapsDatabaseAccessor query results
        '''
        return [result for result in sourceRegionQueryResults if not self.amu.isQueryResultKnown(result)]

    ###############################################################
    # tsunami_break_point_segments
    ###############################################################

    def getAllBreakPointSegmentsByProductRegionNames(self, productRegionAbbrevNames):
        '''
        @summary: Get all break point segments as MapsDatabaseAccessor query results that match
        the user-defined product region abbreviation names
        @param productRegionAbbrevNames: A list of product region abbreviations (e.g., ["AkBcWc", "EcGc"])
        @return: A list of MapsDatabaseAccessor results
        '''
        allQueryResults = []
        for productRegionAbbrevName in productRegionAbbrevNames:
            queryResults = self.amu.getBreakPointSegmentsByProductRegionName(productRegionAbbrevName)
            if queryResults:
                allQueryResults += queryResults
        return allQueryResults

    def getBreakPointNamesFromProductRegion(self, productRegionAbbrevName):
        '''
        @summary: Get a list of all MapsDatabaseAccessor query results containing all break point
        segments within a single product region and extract out the name column from the query results
        @param productRegionAbbrevName: The product region abbreviation (e.g., EcGc)
        @return: List of strings
        '''
        queryResults = self.amu.getBreakPointSegmentsByProductRegionName(productRegionAbbrevName)
        nameList = self.amu.getNamesFromQueryResults(queryResults)
        return nameList

    def getAllOtherBreakPointSegmentsInProductRegion(self, productRegionAbbrevName, namesToSkip,
                                                     filterOutSpecialRegions=True):
        '''
        @summary: Return all break point segments in a single product region that do not match
        the list of user-provided names
        @param productRegionAbbrevName: The product region abbreviation (e.g., EcGc)
        @param namesToSkip: Break point segments to skip
        @param filterOutSpecialRegions: Filter out the special procedure region names
        @return: List of MapsDatabaseAccessor query results
        '''
        allNamesInRegion = self.getBreakPointNamesFromProductRegion(productRegionAbbrevName)
        otherNamesList = [name for name in allNamesInRegion if name not in namesToSkip]
        remainingQueryResults = self.amu.getBreakPointSegmentsBySegmentNames(otherNamesList)
        if filterOutSpecialRegions:
            remainingQueryResults = self.amu.filterResultsByNonSpecialProcedureAreas(remainingQueryResults)
        return remainingQueryResults

    def orderBreakPointSegmentsByBreakPointNumber(self, segmentQueryResults):
        '''
        @summary: Order the break point segment query results into a nested list so contiguous segments
        are grouped together into the same hazard event
        @param segmentQueryResults: A list of MapsDatabaseAccessor query results
        @return: A single list (if contiguous) or a nested list of contiguous results
        '''

        # Pull out break point number from query results and sort in ascending order
        bpNumTuple = []
        for queryResult in segmentQueryResults:
            bpNum = queryResult.getNumber(HazardConstants.BP_NUM_ATTR_NAME)
            bpRegion = self.amu.getStringFromQueryResult(queryResult, HazardConstants.PRODUCT_REGION_ATTR_NAME)
            bpNumTuple.append((bpNum, bpRegion, queryResult))
        bpNumTuple = sorted(bpNumTuple, key=lambda x: x[0])

        # Walk up break point list and if non-contiguous number is found then add contiguous set to final list
        currentNumber = None
        currentBpRegion = None
        resultList = []
        subList = []
        for bpNum, bpRegion, result in bpNumTuple:
            if currentNumber is None or (currentNumber + 1 == bpNum and currentBpRegion == bpRegion):
                subList.append(result)
            else:
                resultList.append(subList)
                subList = [result]
            currentNumber = bpNum
            currentBpRegion = bpRegion
        if subList:
            resultList.append(subList)
        return resultList

    def organizeBreakPointSegmentsByProductRegion(self, segmentQueryResults):
        '''
        @summary: Order the break point segment query results into a dictionary where the key
        is the abbreviated product region name and the value is a list of break point segments
        @param segmentQueryResults: A list of MapsDatabaseAccessor query results
        @return: A dictionary where the key is the abbreviated product region name and the value
        is a list of break point segments
        '''
        regionDict = {}
        for queryResult in segmentQueryResults:
            bpRegion = self.amu.getStringFromQueryResult(queryResult, HazardConstants.PRODUCT_REGION_ATTR_NAME)
            if bpRegion not in regionDict:
                regionDict[bpRegion] = []
            regionDict[bpRegion].append(queryResult)
        return regionDict

    def getUnionedBreakPointSegmentGeometriesByProductRegionName(self, productRegionAbbrevName):
        '''
        @summary: Get all break point segments for a single product region and union those geometries
        together
        @param productRegionAbbrevName: The product region abbreviation (e.g., EcGc)
        @return: A shapely geometry
        '''
        listOfNames = self.getBreakPointNamesFromProductRegion(productRegionAbbrevName)
        queryResults = self.amu.getBreakPointSegmentsBySegmentNames(listOfNames)
        return self.amu.getUnionedGeometryFromQueryResults(queryResults)

    def getBreakPointSegmentsWithinTimeRange(self, currentTime, travelTimeHrs, timeOfArrivalForecast,
                                             siteID, subsetProductRegions=[], filterOutSpecialRegions=True):
        '''
        @summary: Determine which break point segments have stations with forecast times of arrival
        within a user-defined time range
        @param currentTime: The current time as a Java date
        @param travelTimeHrs: The maximum travel time window (in hours)
        @param timeOfArrivalForecast: TsunamiForecast object
        @param siteID: The center site ID (e.g., NTWC or PTWC)
        @param subsetProductRegions: An optional list of product region abbreviations that we will subset
        the results to
        @param filterOutSpecialRegions: Filter out the special procedure region names
        @return: A list of MapsDatabaseAccessor query results
        '''
        # Verify time of arrival forecast exists
        if not self.afou.doesForecastExist(timeOfArrivalForecast):
            return []

        # Get all station geometries that fall within the user-specified travel time
        forecastTable = self.afou.getForecastStationsWithinArrivalTimeInHours(currentTime, timeOfArrivalForecast, travelTimeHrs)
        stationGeometryList = self.afou.getAllForecastStationLocations(forecastTable)

        # Verify at least one geometry was returned
        if not stationGeometryList:
            return []

        # Get all break point segments for a subset of product regions or an entire site
        if subsetProductRegions:
            siteSegmentResults = self.getAllBreakPointSegmentsByProductRegionNames(subsetProductRegions)
        else:
            siteSegmentResults = self.amu.getBreakPointSegmentsBySiteId(siteID)

        # Filter out special procedure locations
        if filterOutSpecialRegions:
            siteSegmentResults = self.amu.filterResultsByNonSpecialProcedureAreas(siteSegmentResults)

        # Loop over stations and determine if any overlap with each break point segment
        queryResults = []
        for segmentResult in siteSegmentResults:
            segmentGeometry = segmentResult.getGeometry()
            for stationGeom in stationGeometryList:
                if segmentGeometry.contains(stationGeom):
                    queryResults.append(segmentResult)
                    break

        return queryResults

