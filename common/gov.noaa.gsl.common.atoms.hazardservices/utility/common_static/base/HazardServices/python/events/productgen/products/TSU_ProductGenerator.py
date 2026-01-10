# *** Override behavior of TSU_ProductGenerator.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Product Generator for the Tsunami products.

    @author: GSL Hazard Services Team
    @version 1.0
    @since Feb. 2022

'''

import copy
import collections
import AtomsFcstObsUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMapUtilities
import HazardConstants
import HazardDataAccess
import NWS_Base_Generator
from gov.noaa.gsl.common.dataplugin.pem import PhysicalEventManager


class Product(NWS_Base_Generator.Product):

    def __init__(self):
        super(Product, self).__init__()

        self.afou = AtomsFcstObsUtilities.AtomsFcstObsUtilities()
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amu = AtomsMapUtilities.AtomsMapUtilities()

        # Used by the VTECEngineWrapper to access the productGeneratorTable
        self.productGeneratorName = "TSU_ProductGenerator"
        self.pem = PhysicalEventManager.getInstance()

    def initialize(self):
        super(Product, self).initialize()
        self.productID = "TSU"
        self.productCategory = "TSU"
        self.productName = "Tsunami Watch/Warning/Advisory"
        self.productLabel = "Tsunami Watch/Warning/Advisory"

        # Polygon-based, so locations listed will be limited to within the polygon rather than county area
        self.polygonBased = True

    def getPurgeHours(self, hazardType):
        '''
        @summary: Get the purge hours to use for events with the given hazard type. This is the
        number of hours past issuance that the event's expiration time should be.
        @param hazardType: The hazard type (e.g., FA.W) to determine purge hours for
        @return: The purge hours, or -1.0 to indicate that the purge time should
        match the event's end time
        '''
        return -1.0

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the product generator, such as author,
        description, and script version.
        @return: A dictionary
        '''
        return {
            "author": "GSL",
            "description": "Product generator for the Tsunami Watch/Warning/Advisory",
            "version": "1.0",
            }

    def defineDialog(self, eventSet):
        '''
        @return: dialog definition to solicit user input before running tool
        '''
        self.initialize()
        cancel_dict = {}
        productSegmentGroups = self.previewProductSegmentGroups(eventSet)
        dialogDict = self.organizeByProductLabel(self.productLevelMetaData_dict, cancel_dict , "TSU_tab")

        return dialogDict

    def execute(self, eventSet, dialogInputMap):
        self.initialize()

        # Extract information for execution
        self.getVariables(eventSet, dialogInputMap)
        eventSetAttributes = eventSet.getAttributes()

        # Get physical event selection; block product generation if zero or multiple are selected
        selectedEvents = list(self.pem.getSelectedPhysicalEvents())
        errorMessage = self.agu.validateSelectedPhysicalEvent(selectedEvents)
        if errorMessage:
            self.addErrorThatBlocksIssuance(errorMessage)
            return [], []

        # Filter out events that are not associated with the currently selected physical event
        selectedPhysicalEvent = selectedEvents[0]
        physicalEventID = selectedPhysicalEvent.getCustomId()
        physicalEventType = selectedPhysicalEvent.getEventType().getLabel()
        eventsToProcess = set()
        otherPhysicalEvents = []
        for event in self.inputHazardEvents:
            eventCustomId = event.get("customId")
            if (eventCustomId == physicalEventID and
                event.get("physicalEventType") == physicalEventType):
                eventsToProcess.add(event)
            elif eventCustomId not in otherPhysicalEvents:
                otherPhysicalEvents.append(eventCustomId)
        self.inputHazardEvents = copy.deepcopy(eventsToProcess)
        if not self.inputHazardEvents:
            otherEventsString = "\n".join(otherPhysicalEvents)
            errorMessage = ("No hazard events associated with the selected physical event:\n\n"
                            f"{physicalEventID}\n\n"
                            "The hazard event(s) were associated with the following physical event(s):\n\n"
                            f"{otherEventsString}\n\n"
                            "Please choose one of these physical event(s) and re-run product generation")
            self.addErrorThatBlocksIssuance(errorMessage)
            return [], []

        productDicts, hazardEvents = self.makeProducts_FromHazardEvents(self.inputHazardEvents,
                                                                        eventSetAttributes)

        return productDicts, hazardEvents

    def limitGeoZones(self, hazardEvents):
        '''
        @summary: Method to limit the Valid Time Event Code (VTEC) engine to only produce and
        return segments based on the Universal Geographic Codes (UGCs) of the filtered hazard
        events being brought in via product generation for the selected physical event
        @param hazardEvents: The hazard event(s) being brought into this iteration of product
        generation
        @return: A list of Universal Geographic Codes (UGCs) to constrain the VTEC Engine results to
        (e.g., ["ASZ001", "ASZ002", "ASZ003"])
        '''
        geoZones = []
        for hazardEvent in hazardEvents:
            # Get the ugcs for this current event and add them
            for ugc in hazardEvent.getUGCs():
                if ugc not in geoZones:
                    geoZones.append(ugc)
            # If the event was issued previously, get its UGCs too to account for break point segment removals
            lastIssuedEvent = HazardDataAccess.getLastIssuedHazardEvent(hazardEvent.getEventID(), self.practice)
            if lastIssuedEvent is not None:
                # Get the ugcs for this current event and add them
                for ugc in lastIssuedEvent.getUGCs():
                    if ugc not in geoZones:
                        geoZones.append(ugc)
        return geoZones

    def getMetadata(self):
        return self.metadata

    def getSegments(self, hazardEvents):
        return self.getSegments_ForProductRegion(hazardEvents)

    def groupSegments(self, segments):
        productSegmentGroups = []

        for (customId, region), segments in self.regionProductSegments.items():
            vtecEngine = self.regionVtecEngines[(customId, region)]
            regionSegmentGroup = TSU_ProductSegmentGroup(self.productID, self.productName, "polygon",
                                                         vtecEngine, "publicZones", True,
                                                         segments, customId, region)
            productSegmentGroups.append(regionSegmentGroup)
        self.productLevelMetaData_dict = self.getProductLevelMetaData(self.inputHazardEvents, "MetaData_TSU",
                                                                      productSegmentGroups)
        return productSegmentGroups

    def getSegments_ForProductRegion(self, hazardEvents):
        self.regionHazardEvents = collections.defaultdict(list)
        for hazardEvent in hazardEvents:
            customId = hazardEvent.get("customId")
            region = hazardEvent.get("productRegion")
            self.regionHazardEvents[(customId, region)].append(hazardEvent)

        self.generatedHazardEvents = []
        self.regionProductSegments = {}
        self.regionVtecEngines = {}

        for (customId, region), events in self.regionHazardEvents.items():
            if not events:
                continue
            self.setAdditionalHazardAttributes(events)
            self.generatedHazardEvents += list(events)
            self.getVtecEngine(events)
            if self.correctionFlag:
                segments = self.getSegmentsForCOR(events)
            else:
                segments = self.vtecEngine.getSegments()
            inputEventIDs = [event.getEventID() for event in events]
            productSegments = []
            for segment in segments:
                vtecRecords = self.getVtecRecords(segment)
                eventFound = False
                for vtecRecord in vtecRecords:
                    for eventID in vtecRecord["eventID"]:
                        if eventID in inputEventIDs:
                            eventFound = True
                if eventFound:
                    productSegments.append(self.createProductSegment(segment, vtecRecords))
            self.regionProductSegments[customId, region] = productSegments
            self.regionVtecEngines[customId, region] = self.vtecEngine

        allSegments = []
        for segments in self.regionProductSegments.values():
            allSegments.extend(segments)
        return allSegments

    def createProductLevelProductDictionaryData(self, productDict, hazardEvents):
        '''
        @summary: Add additional attributes to the product-level of the product
        dictionary
        @param productDict: The product dictionary
        @param hazardEvents: A list of hazard events brought into product generation
        @return: An updated productDict in memory
        '''
        hazardEvent = hazardEvents[0]
        productDict["productRegion"] = hazardEvent.get("productRegion")
        productDict["customId"] = hazardEvent.get("customId")
        productDict["physicalEventType"] = hazardEvent.get("physicalEventType")

    def updateOtherVtecHazardAttributes(self, productDict, inputHazardEvents):
        '''
        @summary: Given a product dictionary and a list of input hazard events, update
        the hazard events with information from the product dictionary
        @param productDict: The product-level dictionary
        @param inputHazardEvents: A list of HazardEvent objects
        @return: NoneType; inputHazardEvents is updated in memory
        '''
        eventDicts = self.agu.getAllEventDicts(productDict)
        for eventDict in eventDicts:
            eventID = eventDict.get("eventID")
            for hazardEvent in inputHazardEvents:
                if hazardEvent.getEventID() != eventID:
                    continue
                suffix = f"{self.productID}_{eventDict.get('customId')}_{eventDict.get('productRegion')}"
                forecastRunTableList = eventDict.get(f"forecastRunTable_{suffix}")
                deselectedStations = self.afou.getDeselectedStationFromForecastRunTable(forecastRunTableList)
                hazardEvent.set("deselectedForecastStations", deselectedStations)

    def addGeneratorSpecificHazardEventDictionary(self, eventDict, hazardEvent, vtecRecord, metaData):
        '''
        @summary: Get the list of break point segments this hazard event covers,
        This will populate to location which will be included area list and
        summary headline
        @param  hazardEvent: The input hazard event
        @return: eventDict["breakPointSegmentDicts"] and eventDict["breakPointsDict"]
        '''
        breakPointSegmentAOIs = self.getBreakPointSegmentAOIsUnderneathHazardEvent(hazardEvent)
        sortedBreakPointSegments = []
        pointNames = []
        if breakPointSegmentAOIs:
            sortedBreakPointSegments = self.sortBreakPointSegmentsByNumber(breakPointSegmentAOIs, False)
            # Get lower_bkpt, upper_bkpt for each break point segment, put them into a list and remove duplicates
            for breakPointSegment in sortedBreakPointSegments:
                for attr in [HazardConstants.LOWER_BP_ATTR_NAME, HazardConstants.UPPER_BP_ATTR_NAME]:
                    segmentName = breakPointSegment.get(attr)
                    if segmentName not in pointNames:
                        pointNames.append(segmentName)
        # Add break point segment information
        eventDict["breakPointSegmentDicts"] = sortedBreakPointSegments

        # Collect geospatial information about the remaining break points
        eventDict["breakPointsDict"] = self.getBreakPointInformationByNames(pointNames)

    def getBreakPointSegmentAOIsUnderneathHazardEvent(self, hazardEvent):
        '''
        @summary: Get the break point segment AOIs for this hazard event
        @param hazardEvent: The input hazard event
        @return: A list of AOI coverage objects
        '''
        # Get the AOI coverage objects that overlap with the geometry
        breakPointSegmentAOIs = self.agu.getBreakPointSegmentCoveragesFromHazardEvent(hazardEvent)
        # Get the break point segments & special procedure areas defined in the event
        hazardLocationNames = hazardEvent.get("hazardLocations")
        if not hazardLocationNames:
            # Trim the collected break point segment areas based on whether this hazard event
            # is for only break point segments or special procedure areas
            locationCoverage = hazardEvent.get("wwaLocationCoverage")
            if locationCoverage and locationCoverage != "allAreas":
                for i in range(len(breakPointSegmentAOIs) - 1, -1, -1):
                    if ((locationCoverage == "segmentAreas" and
                        self.agu.isBreakPointSegmentSpecial(breakPointSegmentAOIs[i])) or
                        (locationCoverage == "specialAreas" and
                        not self.agu.isBreakPointSegmentSpecial(breakPointSegmentAOIs[i]))):
                        breakPointSegmentAOIs.pop(i)

        else:
            for i in range(len(breakPointSegmentAOIs) - 1, -1, -1):
                if breakPointSegmentAOIs[i].get("name") not in hazardLocationNames:
                    breakPointSegmentAOIs.pop(i)
        return breakPointSegmentAOIs

    def postProcessProductDicts(self, productDicts):
        '''
        @summary: Write additional parameters to the product dictionary
        @param productDicts: A list of product dictionaries
        @return: The productDicts entry passed in is updated
        '''
        for productDict in productDicts:
            productRegionAbbrev = productDict.get("productRegion")
            siteID = productDict.get("siteID")
            ##################################
            # Product-level dictionary updates
            ##################################
            # Add booleans to show if the productDict has any active watches, warnings, or advisories
            self.getSignificancesInProductDict(productDict)

            ##################################
            # Segment-level dictionary updates
            ##################################
            eventDicts = self.agu.getAllEventDicts(productDict)
            # Determine all break points and break point segments associated with each product segment
            breakPointSegmentDict = self.getAllUniqueBreakPointSegmentCoverages(eventDicts)
            for segmentDict in productDict.get("segments"):
                segmentBreakPointSegmentDicts = []
                matchedSegmentNames = []
                pointNames = []
                zoneGeometries = self.getForecastZoneGeometriesFromSegmentDict(segmentDict)
                for zoneGeometry in zoneGeometries:
                    bestSegmentName = self.getBreakPointSegmentThatBestOverlapsTheUGC(zoneGeometry, breakPointSegmentDict)
                    if bestSegmentName and bestSegmentName not in matchedSegmentNames:
                        matchedSegmentNames.append(bestSegmentName)
                        # Add break point segment information to list
                        bpDict = breakPointSegmentDict[bestSegmentName]
                        segmentBreakPointSegmentDicts.append(bpDict)
                        # Add upper and lower break points to a list of names
                        for attr in [HazardConstants.LOWER_BP_ATTR_NAME, HazardConstants.UPPER_BP_ATTR_NAME]:
                            if bpDict[attr] not in pointNames:
                                pointNames.append(bpDict[attr])
                # Set timezone information for this segment
                segmentDict["timeZones"] = self.getTimezoneInformation(productRegionAbbrev,
                                                                       segmentBreakPointSegmentDicts)
                # Determine and set break point segments for this product segment
                breakPointSegmentDicts = self.sortBreakPointSegmentsByNumber(segmentBreakPointSegmentDicts, True)
                segmentDict["breakPointSegmentDicts"] = breakPointSegmentDicts

                if siteID == "PTWC":
                    subRegionLocations = self.getSubRegionLocations(productRegionAbbrev, breakPointSegmentDicts)
                    if subRegionLocations:
                        segmentDict["subRegionLocations"] = subRegionLocations

                # Get break points within this segment
                segmentDict["breakPointsDict"] = self.getBreakPointInformationByNames(pointNames)

            # Get the location description information for this product type
            locationInformation = self.agu.getLocationInformation(productDict, onlyFE=False)

            ##################################
            # Event-level dictionary updates
            ##################################
            productLabel = productDict.get("productLabel")
            for eventDict in eventDicts:
                # Remove excess information from the event-level breakPointSegment dictionaries
                eventDict["breakPointSegmentDicts"] = self.pruneBreakPointSegmentDictionaries(eventDict["breakPointSegmentDicts"])
                # Add location description information
                eventDict[f"locationDescription_{productLabel}"] = locationInformation

    def getSubRegionLocations(self, productRegionAbbrev, breakPointSegmentDicts):
        '''
        @summary: For PTWC hazards, we may need to know information inside specific product region
        (e.g., counties in Hawaii), so retrieve this information here
        @param productRegionAbbrev: The product region abbreviation (e.g., Hi)
        @param breakPointSegmentDicts: The break point segments visible at the product segment-level
        @return: List of strings
        '''
        subRegionLocations = []
        # For Hawaii products, get the county names affected by each hazard event
        if productRegionAbbrev == "Hi":
            # Determine which counties exist at the segment-level and add this to the segmentDict
            breakPointSegmentNames = [bpSegDict["name"] for bpSegDict in breakPointSegmentDicts]
            countyDescriptors = self.agu.getCountyNamesByBreakPointSegmentNames(breakPointSegmentNames)
            for countyDescriptor in countyDescriptors:
                countyName = countyDescriptor.split(" in ")[-1]  # Kahoolawe in Maui --> Maui
                if countyName not in subRegionLocations:
                    subRegionLocations.append(countyName)
        elif productRegionAbbrev == "As":
            subRegionLocations = ["American Samoa"]
        elif productRegionAbbrev == "Gu":
            subRegionLocations = ["Guam and CNMI"]
        elif productRegionAbbrev == "Pr":
            subRegionLocations = ["Puerto Rico...The U.S. Virgin Islands...and The British Virgin Islands"]
        return subRegionLocations

    def getTimezoneInformation(self, productRegionAbbrev, segmentBreakPointSegmentDicts):
        '''
        @summary: Get timezone information using information from the break point segments table
        @param productRegionAbbrev: The product region abbreviation (e.g., Hi)
        @param segmentBreakPointSegmentDicts: Dictionary containing break point segment info
        @return: NoneType; timezoneCountDict is updated in memory
        '''
        segmentTimezones = []
        if productRegionAbbrev in ["Hi", "As", "Gu", "Pac", "Car", "Pr"]:
            tzNameList = self.alu.getTimezonesByProductRegionAbbreviation(productRegionAbbrev)
            segmentTimezones = tzNameList
        else:
            countDict = {}
            for bpSegmentDict in segmentBreakPointSegmentDicts:
                stateText = bpSegmentDict.get("state")
                tzName = self.alu.getTimezonesByState(stateText)
                if not tzName:
                    segName = bpSegmentDict.get("name")
                    tzName = self.alu.getTimezonesByBreakPointSegmentName(segName)
                if tzName not in segmentTimezones:
                    countDict[tzName] = 0
                countDict[tzName] += 1
            # Sort results in descending order
            countDict = {k: v for k, v in sorted(countDict.items(), key=lambda item: item[1], reverse=True)}
            segmentTimezones = list(countDict.keys())
        return segmentTimezones

    def getSignificancesInProductDict(self, productDict):
        '''
        @summary: Determine if the product has some combination of watches,
        warnings, and/or advisories and add these as booleans at the product-level
        dictionary
        @param productDict: The product-level dictionary
        @return: NoneType; The productDict is updated in memory
        '''
        activeSigs = self.agu.getSigList(productDict, False)
        productDict["hasActiveWarnings"] = "W" in activeSigs
        productDict["hasActiveAdvisories"] = "Y" in activeSigs
        productDict["hasActiveWatches"] = "A" in activeSigs

    def getBreakPointInformationByNames(self, breakPointNames):
        '''
        @summary: Given a list of break point names, return a dictionary that
        with the break point name as the key and contains latitude, longitude,
        and descriptor information
        @param breakPointNames: A list of break point names
        @return: A list of dictionaries
        '''
        breakPointInfoDict = {}
        if not breakPointNames:
            return breakPointInfoDict
        queryResults = self.amu.getBreakPointsByNameList(breakPointNames)
        for bkptQueryResult in queryResults:
            bkptName = self.amu.getStringFromQueryResult(bkptQueryResult, "name")
            breakPointInfoDict[bkptName] = {
                "latitude": bkptQueryResult.getNumber("latitude"),
                "longitude": bkptQueryResult.getNumber("longitude"),
                "descriptor": bkptQueryResult.getString("descriptor"),
                }
        return breakPointInfoDict

    def breakPointSegmentInformationToRemove(self):
        '''
        @summary: Defines a list of information to remove from the break point segment
        AOI coverages dictionary when populating the "breakPointSegmentDicts" entries at
        the segment and event-level
        @return: List
        '''
        return ["numAoisWithSameUgc", "geometry", "id", "type"]

    def pruneBreakPointSegmentDictionaries(self, breakPointSegmentDicts):
        '''
        @summary: Prune unused excess information from list of break point segment
        dictionaries to not clutter up the product dictionary
        @return: A pruned list of break point segment dictionaries
        '''
        return [{k: v for k, v in d.items() if k not in self.breakPointSegmentInformationToRemove()}
                for d in breakPointSegmentDicts]

    def sortBreakPointSegmentsByNumber(self, breakPointSegmentDicts, purgeExcessFields):
        '''
        @summary: Sort a list of break point segment dictionaries by the break point
        number of each entry
        @param breakPointSegmentDicts: A list of break point segment dictionaries
        @param purgeExcessFields: Boolean to determine if certain column entries should be purged
        @return: A sorted list of dictionaries
        '''
        if purgeExcessFields:
            prunedDicts = self.pruneBreakPointSegmentDictionaries(breakPointSegmentDicts)
        else:
            prunedDicts = breakPointSegmentDicts
        return sorted(prunedDicts, key=lambda x: self.agu.getBreakPointInteger(x[HazardConstants.BP_NUM_ATTR_NAME]))

    def getAllUniqueBreakPointSegmentCoverages(self, eventDicts):
        '''
        @summary: Get all break point segment AOI coverages as python dictionaries from
        the event-level dictionaries
        @param eventDicts: A list of event-level dictionaries
        @return: A dictionary with the key being the break point segment name and the values
        being the AOI coverage entries
        '''
        breakPointSegmentDict = {}
        for eventDict in eventDicts:
            for bpsDict in eventDict.get("breakPointSegmentDicts", []):
                bpsName = bpsDict.get("name")
                if bpsName not in breakPointSegmentDict:
                    breakPointSegmentDict[bpsName] = bpsDict
        return breakPointSegmentDict

    def getForecastZoneGeometriesFromSegmentDict(self, segmentDict):
        '''
        @summary: Assemble a list of shapely geometries based on the Universal Geographic
        Codes (UGCs) associated with a segment
        @param segmentDict: The segment-level dictionary
        @return: List of shapely geometries
        '''
        # Convert ugc code to state_zone names (e.g., ORZ103 --> OR103)
        stateZoneList = []
        for stateZone in segmentDict.get("ugcs", []):
            if stateZone[2] == "Z":
                stateZone = f"{stateZone[0:2]}{stateZone[3:]}"
            stateZoneList.append(stateZone)
        # Get the geometry for each state_zone and put it into a list
        queryResults = self.amu.getForecastZonesByStateZoneList(stateZoneList)
        zoneGeometries = self.amu.getAllGeometriesFromQueryResults(queryResults)
        return zoneGeometries

    def getBreakPointSegmentThatBestOverlapsTheUGC(self, zoneGeometry, breakPointSegmentDict):
        '''
        @summary: Determine which break point segment geomety best overlaps a single forecast
        zone geometry
        @param zoneGeometry: The shapely geometry for a single forecast zone
        @param breakPointSegmentDict: All possible break point segment AOI coverage dictionaries
        associated with this product
        @return: The break point segment name that best overlaps with this zone geometry
        '''
        maxArea = 0
        bestSegmentName = None
        for bpsName in breakPointSegmentDict:
            bpsGeometry = breakPointSegmentDict[bpsName]["geometry"]
            geomIntersection = zoneGeometry.intersection(bpsGeometry)
            geoArea = geomIntersection.area
            if geoArea > maxArea:
                bestSegmentName = bpsName
                maxArea = geoArea
        return bestSegmentName


class TSU_ProductSegmentGroup(NWS_Base_Generator.ProductSegmentGroup):

    def __init__(self, productID, productName, geoType, vtecEngine, mapType, segmented, productSegments,
                 customId, region, etn=None, formatPolygon=None, actions=[]):
        self.customId = customId
        self.productRegion = region
        super().__init__(productID, productName, geoType, vtecEngine, mapType, segmented,
                         productSegments, etn, formatPolygon, actions)

    def determineProductLabel(self):
        return f"{self.productID}_{self.customId}_{self.productRegion}"

