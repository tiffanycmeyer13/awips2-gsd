# *** Override behavior of AbstractThreatDB.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Methods to support accessing the threat database

    @since: Sept 2023
    @author: GSL Hazard Services Team
'''

import abc
import AtomsGeneralUtilities
import AtomsMapUtilities
import GeneralConstants
from gov.noaa.gsl.common.dataplugin.pem import PhysicalEventType
from com.raytheon.viz.gfe.ui.runtimeui import DisplayMessageDialog


class AbstractThreatDB(object, metaclass=abc.ABCMeta):

    def __init__(self):
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.amu = AtomsMapUtilities.AtomsMapUtilities()

    @abc.abstractmethod
    def getThreatDBConfigDict(self):
        return

    def thresholdQueryByPhysicalEventType(self):
        '''
        @summary: User-configurable method that determines if you want the initial threat database
        query to:
        True: Return only threat sources and overlap the physical event location AND
              match the physical event type (i.e., Seismic, Landslide)
        False: Return only threat sources that overlap the physical event location
        @return: Boolean
        '''
        return True

    def getSourceRegionByPhysicalEvent(self, phyEvent, siteID):
        '''
        @summary: A method returning zero or more source regions which the physical event is located inside.
        @param phyEvent: The physical event
        @param siteID: The localized site (i.e., NTWC)
        @return: A list of query results
        '''
        # Determine if the physical event is located inside any threat source regions
        if self.thresholdQueryByPhysicalEventType():
            queryResults = self.amu.getSourceRegionsByPhysicalEventLocationAndEventType(phyEvent, siteID)
        else:
            queryResults = self.amu.getSourceRegionsByPhysicalEventLocation(phyEvent, siteID)
        return queryResults

    def checkAndAlertForKnownEvents(self, matchingSourceRegions, phyEvent):
        '''
        @summary: Check if any of the matching threat source regions correspond to known events and if necessary,
        alert the user as to whether or not they want to pursue creating hazard events for it
        @param matchingSourceRegions: The query results from the tsunami_threat_db_source_regions table
        @param phyEvent: The phyEvent. If we find a knownSourceRegion and the phyEvent is already isKnown, then we do not
        have to ask the user. If the phyEvent is not already *flagged* as known, we do indeed ask the user.
        @return: A matching known event that a forecaster wishes to create hazard events
        '''
        knownSourceRegion = None
        for sourceRegion in matchingSourceRegions:
            if self.amu.isQueryResultKnown(sourceRegion):
                userInput = False
                if not phyEvent.getIsKnownEvent():
                    descriptor = sourceRegion.getString("descriptor")
                    userInput = DisplayMessageDialog.openQuestion("Known Event Found", f"Is this the {descriptor} special procedure?")
                if userInput or phyEvent.getIsKnownEvent():
                    knownSourceRegion = sourceRegion
                    break
        return knownSourceRegion

    def filterBySeismicAttributes(self, sourceRegion, phyEventData, threatDBConfig, filteredSourceRegions):
        '''
        @summary: Method that determines if the selected physical event has attributes that meet the criteria
        for triggering the creation of hazard events using the target regions defined by this Seismic source region
        @param sourceRegion: The source region
        @param phyEventData: The physical event data
        @param threatDBConfig: A dictionary of attributes configured in ThreatDB.py for the regionName
        @param filteredSourceRegions: A list of matching source region names that is updated in memory
        @return: An updated filteredSourceRegions in memory
        '''
        regionName = self.amu.getStringFromQueryResult(sourceRegion, "name")
        minMag = threatDBConfig.get("minMagnitude")
        maxMag = threatDBConfig.get("maxMagnitude")
        maxDepthKm = threatDBConfig.get("maxDepthKm")

        if minMag is None:
            msg = (f"ERROR: in AbstractThreatDB.py: The ThreatDB.py configuration for {regionName} "
                   "requires (at least) a minMagnitude.")
            print(msg)
            return

        if any(val is None for val in [maxMag, maxDepthKm]):
            msg = (f"WARNING: in AbstractThreatDB.py: The ThreatDB.py configuration for {regionName} "
                   "is missing one of minMagnitude, maxMagnitude, and/or maxDepthKm. Assuming it's intentional.")
            print(msg)

        if (minMag <= phyEventData.getPrefMagnitude() and
            (maxMag is None or maxMag >= phyEventData.getPrefMagnitude()) and
            (maxDepthKm is None or maxDepthKm >= (phyEventData.getDepth() * GeneralConstants.KILOMETERS_PER_MILE))):
            filteredSourceRegions.append(sourceRegion)

    def filterByLandslideAttributes(self, sourceRegion, phyEventData, threatDBConfig, filteredSourceRegions):
        '''
        @summary: Method that determines if the selected physical event has attributes that meet the criteria
        for triggering the creation of hazard events using the target regions defined by this Landslide source region
        @param sourceRegion: The source region
        @param phyEventData: The physical event data
        @param threatDBConfig: A dictionary of attributes configured in ThreatDB.py for the regionName
        @param filteredSourceRegions: A list of matching source region names that is updated in memory
        @return: An updated filteredSourceRegions in memory
        '''
        filteredSourceRegions.append(sourceRegion)

    def filterByVolcanicAttributes(self, sourceRegion, phyEventData, threatDBConfig, filteredSourceRegions):
        '''
        @summary: Method that determines if the selected physical event has attributes that meet the criteria
        for triggering the creation of hazard events using the target regions defined by this Volcanic source region
        @param sourceRegion: The source region
        @param phyEventData: The physical event data
        @param threatDBConfig: A dictionary of attributes configured in ThreatDB.py for the regionName
        @param filteredSourceRegions: A list of matching source region names that is updated in memory
        @return: An updated filteredSourceRegions in memory
        '''
        filteredSourceRegions.append(sourceRegion)

    def filterByUnknownAttributes(self, sourceRegion, phyEventData, threatDBConfig, filteredSourceRegions):
        '''
        @summary: Method that determines if the selected physical event has attributes that meet the criteria
        for triggering the creation of hazard events using the target regions defined by this Unknown source region
        @param sourceRegion: The source region
        @param phyEventData: The physical event data
        @param threatDBConfig: A dictionary of attributes configured in ThreatDB.py for the regionName
        @param filteredSourceRegions: A list of matching source region names that is updated in memory
        @return: An updated filteredSourceRegions in memory
        '''
        filteredSourceRegions.append(sourceRegion)

    def filterSourceRegionsByPhyEventAttributes(self, queryResults, phyEvent):
        '''
        @summary: A method returning the set of zero or more of the given source regions whose conditions are satisfied by the given events'
        attributes. Seismic events are filtered by minMag, maxMag, and maxDepth, and Volcanic/Landslide/Unknown are not filtered/omitted at all
        currently. Note it is presumed that the given regions/queryResults already geographically contain the physical event and have
        the correct type (i.e., phy event type).
        @param queryResults are the candidateSourceRegions which is a List of Dicts (keys being name, sourcetype, geometry) that already
        geographically contain the physical event and have the correct type (i.e., phy event type).
        @param phyEvent: The seismic event
        @return: A list of query results, being dictionaries with name, sourcetype, and geometry
        '''
        filteredSourceRegions = []
        phyEventData = phyEvent.getData()
        for sourceRegion in queryResults:
            regionName = self.amu.getStringFromQueryResult(sourceRegion, "name")
            threatDBConfigForRegion = self.getThreatDBConfigDict().get(regionName)
            if threatDBConfigForRegion:
                threatDBConfigForRegion = self.getThreatDBConfigDict()[regionName]
                if (phyEvent.getEventType() == PhysicalEventType.SEISMIC):
                    self.filterBySeismicAttributes(sourceRegion, phyEventData, threatDBConfigForRegion, filteredSourceRegions)
                elif (phyEvent.getEventType() == PhysicalEventType.LANDSLIDE):
                    self.filterByLandslideAttributes(sourceRegion, phyEventData, threatDBConfigForRegion, filteredSourceRegions)
                elif (phyEvent.getEventType() == PhysicalEventType.VOLCANIC):
                    self.filterByVolcanicAttributes(sourceRegion, phyEventData, threatDBConfigForRegion, filteredSourceRegions)
                elif (phyEvent.getEventType() == PhysicalEventType.UNKNOWN):
                    self.filterByUnknownAttributes(sourceRegion, phyEventData, threatDBConfigForRegion, filteredSourceRegions)
            else:
                print(f"ERROR: No entry in ThreatDB.py for {regionName}")
        return filteredSourceRegions

    def queryThreatDBForKnownEvents(self, phyEvent, productRegion, siteID):
        '''
        @summary: A method to query the threat DB for physical events, first checking the source region(s), then conditions
        (e.g., minMag, etc), and returns a wwaAreaDictList (a list of dicts, with hazardType, geometry, and productRegion)
        @param phyEvent: The physical event
        @param productRegion: The product region
        @param siteID: The localized site (i.e., NTWC)
        @return: A list of dictionaries with each entry containing the hazard type, geometry, and product region name
        for a single hazard event to be created
        '''
        wwaDictList = []
        knownSourceRegion = None
        matchingSourceRegions = self.getSourceRegionByPhysicalEvent(phyEvent, siteID)
        if not matchingSourceRegions:
            return wwaDictList

        # Check for known events and allow the user to choose to pursue creating events for them
        for sourceRegion in matchingSourceRegions:
            if self.amu.isQueryResultKnown(sourceRegion):
                knownSourceRegion = sourceRegion
                break
        if knownSourceRegion:
            sourceRegionName = self.amu.getStringFromQueryResult(knownSourceRegion, "name")
            wwaDictList = self.getWWAsForSourceRegion(sourceRegionName, productRegion)
        return wwaDictList

    def queryThreatDB(self, phyEvent, productRegion, siteID):
        '''
        @summary: A method to query the threat DB for physical events, first checking the source region(s), then conditions
        (e.g., minMag, etc), and returns a wwaAreaDictList (a list of dicts, with hazardType, geometry, and productRegion).
        Only target regions belonging to the given productRegion are included. So if a sourceRegion (eg DBRegion_005 or
        AmSamSourceRegion) maps to target regions in more than one product region (eg regionX in AmSam and regionY in Guam),
        then only WWYs including target regions for the given product region (eg AmSam) are included.
        @param phyEvent: The physical event
        @param productRegion: The product region
        @param siteID: The localized site (i.e., NTWC)
        @return: A list of dictionaries with each entry containing the hazard type, geometry, and product region name
        for a single hazard event to be created
        '''
        wwaAreaDictList = []

        queryResults = self.getSourceRegionByPhysicalEvent(phyEvent, siteID)
        # No results found, exit method
        if not queryResults:
            return wwaAreaDictList

        # Check for known events and allow the user to choose to pursue creating events for them
        matchingKnownSourceRegion = self.checkAndAlertForKnownEvents(queryResults, phyEvent)
        if matchingKnownSourceRegion is not None:
            sourceRegionName = self.amu.getStringFromQueryResult(matchingKnownSourceRegion, "name")
            wwaDictList = self.getWWAsForSourceRegion(sourceRegionName, productRegion)
            return wwaDictList
        # If it's not known, then remove any isKnown == True regions so we do not
        # inadvertently use their target regions
        else:
            queryResults = self.agu.filterOutSourceRegionResultsForKnownEvents(queryResults)

        # Filter the query results by the attributes defined in ThreatDB.py
        filteredResults = self.filterSourceRegionsByPhyEventAttributes(queryResults, phyEvent)
        if filteredResults is None:
            return wwaAreaDictList
        '''
        Walk through the matching regions. If there are more than one, then they are
        nested, and so let's find the smallest (in area) region and use that one.
        '''
        # Filter remaining regions and return the one with the smallest area if there are multiple regions remaining
        smallestSourceRegion = self.amu.getQueryResultWithTheSmallestArea(filteredResults)

        # Now get the hazard event descriptors for the smallestRegion
        if smallestSourceRegion is not None:
            sourceRegionName = self.amu.getStringFromQueryResult(smallestSourceRegion, "name")
            wwaAreaDictList = self.getWWAsForSourceRegion(sourceRegionName, productRegion)

        return wwaAreaDictList

    def getWWAsForSourceRegion(self, sourceRegionName, productRegion):
        '''
        @summary: Given a source region name, create a list of eventDicts with each dictionary containing the hazard type,
        geometry, and product region. The hazard type will come from the entries in ThreatDB.py, the geometries will come
        from the tsunami_threat_db_target_regions (matching on the given productRegion), the productRegion will be passed
        into this method
        @param sourceRegionName: The source region name (e.g., Augustine_SP)
        @param productRegion: The product region name (e.g., AkBcWc)
        @return: A list of dictionaries with each entry containing the hazard type, geometry, and product region name
        for a single hazard event to be created
        '''
        wwaAreaDictList = []
        threatDBConfigForRegion = self.getThreatDBConfigDict().get(sourceRegionName)
        if threatDBConfigForRegion is not None:
            for hazTypeDesc in threatDBConfigForRegion["hazardTypes"]:
                hazardAreas = hazTypeDesc["hazardAreas"]
                # Get results from the tsunami_break_point_segments table
                queryResults = self.amu.getBreakPointSegmentsBySegmentNames(hazardAreas)
                # Only include queryResults within the appropriate productRegion
                queryResultsInProductRegion = [qr for qr in queryResults if qr.getString("product_re") == productRegion]
                if not queryResultsInProductRegion:
                    continue
                # Union the geometry together
                unionedGeom = self.amu.getUnionedGeometryFromQueryResults(queryResultsInProductRegion)
                # Determine coverage type and add break point segment names
                attrDict = {
                    "wwaLocationCoverage": self.agu.getCoverageTypeFromQueryResults(queryResultsInProductRegion),
                    "hazardLocations": hazardAreas,
                    }
                wwaAreaDictList.append(self.agu.createTsunamiEventDict(hazTypeDesc["hazardType"], unionedGeom,
                                                                       productRegion, attrDict))
        else:
            print(f"ERROR in AbstractThreatDB - a region with name {sourceRegionName} was not found in the threatDBConfig!!!")
        return wwaAreaDictList
