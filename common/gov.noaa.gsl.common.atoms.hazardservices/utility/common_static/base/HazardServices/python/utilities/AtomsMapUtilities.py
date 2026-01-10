# *** Override behavior of AtomsMapUtilities.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Contains methods that supports querying the mapdata tables

    @since: April 2025
    @author: GSL Hazard Services Team
'''

import GeometryUtilities
import HazardConstants
import MapsDatabaseAccessor


class AtomsMapUtilities(object):

    def __init__(self):
        self.geomUtils = GeometryUtilities.GeometryUtilities()
        self.mapsAccessor = MapsDatabaseAccessor.MapsDatabaseAccessor()

    ###############################################################
    # Main query and data access methods
    ###############################################################

    def mapDataQueryResults(self, tableName, mapQueryColumns, queryGeometry,
                            intersect, queryMatch="", matchColumn=""):
        '''
        @summary: A general method to access a maps database table with some
        and filter the results by some query constraints
        @param tableName: The name of the mapdata table (e.g., county)
        @param mapQueryColumns: The columns to retrieve in the query results
        @param queryGeometry: The geometry the query should be bounded by
        @param intersect: A boolean determining whether the results can intersect (True)
                          the queryGeometry or must be completely within (False)
                          the queryGeometry
        @param queryMatch: An optional string or list of string that must be matched in
                           the database record
        @param matchColumn: An optional database column where the queryMatch phrase
                            will reside
        @return: A list of query results
        '''
        queryResults = self.mapsAccessor.mapDataQuery(tableName=tableName,
                                                      columns=mapQueryColumns,
                                                      geometry=queryGeometry,
                                                      intersect=intersect,
                                                      queryMatch=queryMatch,
                                                      matchColumn=matchColumn)
        return queryResults

    def getStringFromQueryResult(self, queryResult, fieldName):
        '''
        @summary: Access the column which could either be from .getLocationName()
        or .getString(fieldName) depending on how the initial database query was performed
        @param queryResult: A single MapsDatabaseAccessor query result
        @param fieldName: The string fieldName of the column
        @return: A string
        '''
        value = queryResult.getString(fieldName)

        # Be careful, if there is no string for fieldName, the API returns a STRING "None"
        if not value or value == "None":
            value = queryResult.getLocationName()
        return value

    def getGeometryFromQueryResult(self, queryResult):
        '''
        @summary: Get the geometry from the MapsDatabaseAccessor query result
        @param queryResult: A single MapsDatabaseAccessor query result
        @return: A shapely geometry
        '''
        geometry = None
        if queryResult is not None:
            geometry = queryResult.getGeometry()
        return geometry

    def getAllGeometriesFromQueryResults(self, queryResults):
        '''
        @summary: Build a list of location names from the MapsDatabaseAccessor query results
        @param queryResults: A list of MapsDatabaseAccessor query results
        @return: A list of shapely geometries
        '''
        if not queryResults:
            return []
        geometryList = [self.getGeometryFromQueryResult(queryResult) for queryResult in queryResults]
        # Filter out all NoneType entries
        filteredList = list(filter(lambda x: x is not None, geometryList))
        return filteredList

    def getUnionedGeometryFromQueryResults(self, queryResults):
        '''
        @summary: Build single unioned geometry from the MapsDatabaseAccessor query results
        @param queryResults: A list of MapsDatabaseAccessor query results
        @return: A shapely geometry
        '''
        geometryList = self.getAllGeometriesFromQueryResults(queryResults)
        return self.geomUtils.getUnionFromListOfGeometries(geometryList)

    def getFieldFromQueryResults(self, queryResults, fieldName):
        '''
        @summary: Given a list of query results and some column name that you wish to
        extract information from and return a list of those field values
        @param queryResults: A list of MapsDatabaseAccessor query results
        @param fieldName: A column name contained within the query results
        @return: List of strings
        '''
        if not queryResults:
            return []
        return [self.getStringFromQueryResult(queryResult, fieldName) for queryResult in queryResults]

    def getNamesFromQueryResults(self, queryResults):
        '''
        @summary: Get a list of the "name" column entry from the query results
        @param queryResults: A list of MapsDatabaseAccessor query results
        @return: List of strings
        '''
        return self.getFieldFromQueryResults(queryResults, "name")

    def isQueryResultSpecial(self, queryResult):
        '''
        @summary: Determine if the 'is_special' entry in the query result
        is equal to 'Y'
        @param queryResult: A single MapsDatabaseAccessor query result
        @return: Boolean
        '''
        return queryResult.getString(HazardConstants.IS_SPECIAL) == "Y"

    def isQueryResultKnown(self, queryResult):
        '''
        @summary: Determine if the 'is_known' entry in the query result
        is equal to 'Y'
        @param queryResult: A single MapsDatabaseAccessor query result
        @return: Boolean
        '''
        return queryResult.getString("is_known") == "Y"

    def isQuakeInArcticOceanProcRegion(self, inputDict, suffix):
        '''
        @summary: Determine if the physical event is in the Arctic AOR or Non-AOR region
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param suffix: The field name suffix
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(inputDict, suffix, ["Arctic Ocean - AOR", "Arctic non-AOR"])

    def isQuakeInIndianOceanProcRegion(self, inputDict, suffix):
        '''
        @summary: Determine if the physical event is in the Indian O region
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param suffix: The field name suffix
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(inputDict, suffix, ["Indian Ocean"])

    def isQuakeInMidAtlanticRidgeRegion(self, inputDict, suffix):
        '''
        @summary: Determine if the physical event is in the mid-atlantic ridge region
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param suffix: The field name suffix
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(inputDict, suffix, ["Atlantic Ridge"])

    def isInCorrectProceduralRegions(self, inputDict, suffix, regionsToCheck, bufferRadiusKm=1):
        '''
        @summary: Determine which procedural region(s) a physical event lat/lon is within
        @param inputDict: A product-level dictionary or a sub-dictionary of it
        @param suffix: The field name suffix
        @param regionsToCheck: A list of procedural region names to check
        @param bufferRadiusKm: Radius in km
        @return: Boolean
        '''
        peLat = inputDict.get(f"originLatitude{suffix}")
        peLon = inputDict.get(f"originLongitude{suffix}")
        queryResults = self.getProceduralRegionsIntersectingPoint(peLat, peLon, bufferRadiusKm)
        for result in queryResults:
            regionName = self.getStringFromQueryResult(result, "name")
            if regionName in regionsToCheck:
                return True
        return False

    ###############################################################
    # Table-specific query methods
    ###############################################################

    ###############################################################
    # county
    ###############################################################

    def countyTableName(self):
        '''
        @summary: The name of the county table
        @return: String
        '''
        return "county"

    def countyColumnsToQuery(self):
        '''
        @summary: The mandatory columns to query from the zone table
        @return: List
        '''
        return ["countyname", "fips"]

    def getCountiesByGeometry(self, inputGeometry):
        '''
        @summary: Return the counties that intersect an input geometry
        @param inputGeometry: The input shapely geometry
        @return: List of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.countyTableName(),
                                                mapQueryColumns=self.countyColumnsToQuery(),
                                                queryGeometry=inputGeometry, intersect=True)
        return queryResults

    ###############################################################
    # flinn_engdahl
    ###############################################################

    def flinnEngdahlTableName(self):
        '''
        @summary: The name of the Flinn-Engdahl table
        @return: String
        '''
        return "flinn_engdahl"

    def flinnEngdahlColumnsToQuery(self):
        '''
        @summary: The default columns to always be queried when retrieving information from the
        flinn_engdahl table.
        @return: List
        '''
        return ["name", "prep"]

    def getFlinnEngdahlByPhysicalEventLocation(self, peLat, peLon):
        '''
        @summary: Get the matching threat database source regions within the physical event
        location
        @param peLat: The latitude of the physical event
        @param peLon: The longitude of the physical event
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryGeometry = self.geomUtils.bufferPoint(peLat, peLon, 0.1)
        queryResults = self.mapDataQueryResults(tableName=self.flinnEngdahlTableName(),
                                                mapQueryColumns=self.flinnEngdahlColumnsToQuery(),
                                                queryGeometry=queryGeometry, intersect=True)
        smallestResult = self.getQueryResultWithTheSmallestArea(queryResults)
        return smallestResult

    ###############################################################
    # ptwc_alert_regions
    ###############################################################

    def ptwcAlertTableName(self):
        '''
        @summary: The name of the PTWC alert regions table
        @return: String
        '''
        return "ptwc_alert_regions"

    def ptwcAlertRegionColumnsToQuery(self):
        '''
        @summary: The default columns to always be queried when retrieving information from the
        flinn_engdahl table.
        @return: List
        '''
        return ["name"]

    def getPtwcAlertRegionsByGeometry(self, queryGeometry):
        '''
        @summary: Query the ptwc_alert_regions table and get the rows
        that intersect the input query geometry
        @param queryGeometry: A shapely geometry object
        @return: A list of MapsDatabaseAccessor query results
        '''
        return self.mapDataQueryResults(tableName=self.ptwcAlertTableName(),
                                        mapQueryColumns=self.ptwcAlertRegionColumnsToQuery(),
                                        queryGeometry=queryGeometry,
                                        intersect=True)

    ###############################################################
    # ptwc_warning_points
    ###############################################################

    def ptwcWarningPointsTableName(self):
        '''
        @summary: The name of the PTWC warning points table
        @return: String
        '''
        return "ptwc_warning_points"

    def ptwcWarningPointsColumnsToQuery(self):
        '''
        @summary: The default columns to always be queried when retrieving information from the
        flinn_engdahl table.
        @return: List
        '''
        return ["customid", "domain"]

    def queryPtwcWarningPointsByGeometry(self, queryGeometry):
        '''
        @summary: Query the ptwc_warning_points table and return results that intersect
        an input geometry
        @param queryGeometry: A shapely geometry polygon object
        @return: A list of MapsDatabaseAccessor query results
        '''
        return self.mapDataQueryResults(tableName=self.ptwcWarningPointsTableName(),
                                        mapQueryColumns=self.ptwcWarningPointsColumnsToQuery(),
                                        queryGeometry=queryGeometry,
                                        intersect=True)

    def getPtwcWarningPointsByDomainName(self, domainName):
        '''
        @summary: Get a list of warning point IDs within a specific domain (e.g., PTWC)
        @param domainName: The PTWC warning points domain (either PTWS or CARIBE)
        @return: List of strings
        '''
        warningPointIds = self.mapsAccessor.singleColumnQuery(tableName=self.ptwcWarningPointsTableName(),
                                                              matchColumn="domain",
                                                              matchValue=domainName,
                                                              returnColumn="customid")
        return warningPointIds

    ###############################################################
    # state
    ###############################################################

    def statesTableName(self):
        '''
        @summary: The name of the states table
        @return: String
        '''
        return "states"

    def stateColumnsToQuery(self):
        '''
        @summary: The mandatory columns to query from the state table
        @return: List
        '''
        return ["state", "name"]

    def getStateByStateName(self, stateName):
        '''
        @summary: Retrieve a MapsDatabaseAccessor entry for a state by its full name
        @param stateName: The state name (e.g., Hawaii)
        @return: A single MapsDatabaseAccessorEntry
        '''
        return self.mapDataQueryResults(tableName=self.statesTableName(),
                                        mapQueryColumns=self.stateColumnsToQuery(),
                                        queryGeometry=None, intersect=False,
                                        queryMatch=stateName, matchColumn="name")

    ###############################################################
    # tsunami_analysis_regions
    ###############################################################

    def tsunamiAnalysisTableName(self):
        '''
        @summary: The name of the tsunami analysis regions table
        @return: String
        '''
        return "tsunami_analysis_regions"

    def tsunamiAnalysisRegionsColumnsToQuery(self):
        '''
        @summary: The mandatory columns to query from the tsunami_analysis_regions table
        @return: List
        '''
        return ["name", "sourcetype"]

    def getAnalysisRegionsByNames(self, nameList):
        '''
        @summary: Retrieve the MapsDatabaseAccessor records based on a user-defined
        list of names
        @param nameList: A list of names (e.g., ["Guam", "Rota"])
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.tsunamiAnalysisTableName(),
                                                mapQueryColumns=self.tsunamiAnalysisRegionsColumnsToQuery(),
                                                queryMatch=nameList,
                                                queryGeometry=None,
                                                intersect=False,
                                                matchColumn="name")
        return queryResults

    def getAnalysisRegionsBySourceType(self, sourceType):
        '''
        @summary: Retrieve the MapsDatabaseAccessor records for a single tsunami analysis
        region source type
        @param sourceType: The source type name (e.g., AmSamProcedure)
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.tsunamiAnalysisTableName(),
                                                mapQueryColumns=self.tsunamiAnalysisRegionsColumnsToQuery(),
                                                queryMatch=[sourceType],
                                                queryGeometry=None,
                                                intersect=False,
                                                matchColumn="sourcetype")
        return queryResults

    def getAnalysisRegionsByGeometry(self, inputGeometry):
        '''
        @summary: Get all analysis locations intersecting a user-defined geometry
        @param inputGeometry: A shapely geometry
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.tsunamiAnalysisTableName(),
                                                mapQueryColumns=self.tsunamiAnalysisRegionsColumnsToQuery(),
                                                queryGeometry=inputGeometry,
                                                intersect=True)
        return queryResults

    ###############################################################
    # tsunami_break_points
    ###############################################################

    def breakPointTableName(self):
        '''
        @summary: The name of the break point table
        @return: String
        '''
        return "tsunami_break_points"

    def breakPointColumnsToQuery(self):
        '''
        @summary: The mandatory columns to receive results from within the
        tsunami_break_points table
        @return: List of strings
        '''
        return ["name", "site_id", HazardConstants.BP_NUM_ATTR_NAME,
                "latitude", "longitude", "descriptor", HazardConstants.IS_SPECIAL,
                HazardConstants.PRODUCT_REGION_ATTR_NAME]

    def getBreakPointsByProductRegion(self, productRegionAbbrev, filterOutSpecialRegions=True):
        '''
        @summary: Given a product region abbreviation, get all break point segments associated with that
        product region
        @param productRegionAbbrev: The product region abbreviation (e.g., AkBcWc)
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.breakPointTableName(),
                                                mapQueryColumns=self.breakPointColumnsToQuery(),
                                                queryMatch=[productRegionAbbrev],
                                                queryGeometry=None,
                                                intersect=False,
                                                matchColumn="product_re")
        if filterOutSpecialRegions:
            queryResults = self.filterResultsByNonSpecialProcedureAreas(queryResults)
        return queryResults

    def getBreakPointsByGeometry(self, queryGeometry, siteID="", filterBySite=True,
                                filterOutSpecialRegions=True):
        '''
        @summary: Query the tsunami_break_points table and return results that intersect
        an input geometry
        @param queryGeometry: A shapely geometry polygon object
        @param siteID: The site ID to filter the results by
        @param filterBySite: Filter results to only return break points for the current site
        @param filterOutSpecialRegions: Filter results to only return break points that are not from special
        procedure regions
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.breakPointTableName(),
                                                mapQueryColumns=self.breakPointColumnsToQuery(),
                                                queryGeometry=queryGeometry,
                                                intersect=True)
        if filterBySite and siteID:
            queryResults = self.filterQueryResultsBySite(queryResults, siteID)
        if filterOutSpecialRegions:
            queryResults = self.filterResultsByNonSpecialProcedureAreas(queryResults)
        return queryResults

    def getBreakPointsByNameList(self, nameList):
        '''
        @summary: Retrieve all break points that match a list of user-defined names
        @param nameList: A list of names that match the contents of the 'name' column
        @return: A list of MapsDatabaseAccessor query results
        '''
        return self.mapDataQueryResults(tableName=self.breakPointTableName(),
                                        mapQueryColumns=self.breakPointColumnsToQuery(),
                                        queryGeometry=None, intersect=False,
                                        queryMatch=nameList, matchColumn="name")

    def getBreakPointsWithinDistanceRangeFromPoint(self, latitude, longitude, minDistanceInKm,
                                                   maxDistanceInKm, siteID="", filterBySite=True,
                                                   filterOutSpecialRegions=True):
        '''
        @summary: Get break points within a user-defined multi-distance range from a point
        @param latitude: The latitude (in decimal degrees)
        @param longitude: The longitude (in decimal degrees)
        @param minDistanceInKm: A user-defined minimum distance (in km)
        @param maxDistanceInKm: A user-defined minimum distance (in km)
        @param siteID: The site ID to filter the results by
        @param filterBySite: Filter results to only return break points for the current site
        @param filterOutSpecialRegions: Filter results to only return break points that are not from special
        procedure regions
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryGeometry = self.geomUtils.getDonutGeometryFromPoint(latitude, longitude, minDistanceInKm, maxDistanceInKm)
        queryResults = self.getBreakPointsByGeometry(queryGeometry, siteID, filterBySite, filterOutSpecialRegions)
        return queryResults

    ###############################################################
    # tsunami_break_point_segments
    ###############################################################

    def breakPointSegmentsTableName(self):
        '''
        @summary: The name of the break point segments table
        @return: String
        '''
        return "tsunami_break_point_segments"

    def breakPointSegmentColumnsToQuery(self):
        '''
        @summary: The mandatory columns to query from the tsunami_break_point_segments table
        @return: List
        '''
        return ["name", "site_id", HazardConstants.IS_SPECIAL, HazardConstants.SUBREGION_ATTR_NAME,
                HazardConstants.PRODUCT_REGION_ATTR_NAME, HazardConstants.BP_NUM_ATTR_NAME,
                HazardConstants.UPPER_BP_ATTR_NAME, HazardConstants.LOWER_BP_ATTR_NAME,
                HazardConstants.STATE_NAME_ATTR_NAME]

    def getBreakPointSegmentsByProductRegionName(self, productRegionAbbrevName):
        '''
        @summary: Get all break point segments as MapsDatabaseAccessor query results that match
        the user-defined product region abbreviation name
        @param productRegionAbbrevName: The product region abbreviation (e.g., EcGc)
        @return: A list of MapsDatabaseAccessor results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.breakPointSegmentsTableName(),
                                                mapQueryColumns=self.breakPointSegmentColumnsToQuery(),
                                                queryGeometry=None, intersect=False,
                                                queryMatch=productRegionAbbrevName,
                                                matchColumn=HazardConstants.PRODUCT_REGION_ATTR_NAME)
        return queryResults

    def getBreakPointSegmentsBySiteId(self, siteID):
        '''
        @summary: Get all break point segments as MapsDatabaseAccessor query results that match
        the user-defined site ID
        @param siteID: The center site ID (e.g., NTWC or PTWC)
        @return: A list of MapsDatabaseAccessor results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.breakPointSegmentsTableName(),
                                                mapQueryColumns=self.breakPointSegmentColumnsToQuery(),
                                                queryGeometry=None, intersect=False,
                                                queryMatch=siteID,
                                                matchColumn="site_id")
        return queryResults

    def getBreakPointSegmentsByGeometry(self, inputGeometry, pruneSmallAreas=False):
        '''
        @summary: Return the break point segments that intersect
        an input geometry
        @param inputGeometry: The input shapely geometry
        @param pruneSmallAreas: Boolean; Remove results that have an area less than some small threshold
        @return: List of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.breakPointSegmentsTableName(),
                                                mapQueryColumns=self.breakPointSegmentColumnsToQuery(),
                                                queryGeometry=inputGeometry, intersect=True)
        if pruneSmallAreas:
            self.filterResultsWithSmallOverlapAreas(inputGeometry, queryResults)
        return queryResults

    def getBreakPointSegmentsBySegmentNames(self, breakPointNameList):
        '''
        @summary: Get all break point segments as MapsDatabaseAccessor query results that match
        the user-defined product region abbreviation names
        @param breakPointNameList: A list of break point segment names (e.g.,
        ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"])
        @return: A list of MapsDatabaseAccessor results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.breakPointSegmentsTableName(),
                                                mapQueryColumns=self.breakPointSegmentColumnsToQuery(),
                                                queryGeometry=None, intersect=False,
                                                queryMatch=breakPointNameList,
                                                matchColumn="name")
        return queryResults

    def getExtendedBreakPointSegmentNames(self, initialBreakPointNames):
        '''
        @summary: Given a list of break point names, determine the neighboring
        break points and return a unique list that will contain the break point
        name one break point length beyond the initial name list in both directions
        @param initialBreakPointNames: A list of break point names
        @return: List of strings
        '''
        extendedBreakPoints = []
        for bpName in initialBreakPointNames:
            for matchColumn in [HazardConstants.LOWER_BP_ATTR_NAME,
                                HazardConstants.UPPER_BP_ATTR_NAME]:
                extendedBreakPoints += self.mapsAccessor.singleColumnQuery(self.breakPointSegmentsTableName(),
                                                                           matchColumn, bpName, "name")
        # Remove duplicates
        extendedBreakPoints = list(set(extendedBreakPoints))
        return extendedBreakPoints

    def getBPNumbersByBrkptSegmentNames(self, listOfBrkptSegmentNames):
        '''
        @summary: Return breakpoint numbers (bp_num) for each of the given break point segment names
        @param listOfBrkptSegmentNames: The list of brkpt segment names to query for
        @return: Dict of brkpt segment name TO the bo_num integer
        '''
        resultDict = self.mapsAccessor.getFilteredDatabaseRows(tableName=self.breakPointSegmentsTableName(),
                                                               matchColumn="name",
                                                               matchValues=listOfBrkptSegmentNames,
                                                               returnColumn=HazardConstants.BP_NUM_ATTR_NAME)
        # Convert all break point numbers to integers
        for segmentName in resultDict:
            bpNum = resultDict[segmentName]
            if "." in bpNum:
                bpNum = bpNum.split(".")[0]
            if bpNum.isdigit():
                resultDict[segmentName] = int(bpNum)
        return resultDict

    ###############################################################
    # tsunami_procedural_regions
    ###############################################################

    def proceduralRegionsTableName(self):
        '''
        @summary: The name of the procedural regions table
        @return: String
        '''
        return "tsunami_procedural_regions"

    def dualProceduralRegionsTableName(self):
        '''
        @summary: The name of the dual procedural regions table
        @return: String
        '''
        return "tsunami_dual_procedure_regions"

    def proceduralRegionsColumnsToQuery(self):
        '''
        @summary: The default columns to always be queried when retrieving information from the
        flinn_engdahl table.
        @return: List
        '''
        return ["name"]

    def dualProceduralRegionsColumnsToQuery(self):
        '''
        @summary: The default columns to always be queried when retrieving information from the
        dual procedure regions table.
        @return: List
        '''
        return ["region"]

    def getProceduralRegionsIntersectingPoint(self, latitude, longitude, bufferRadiusKm=1):
        '''
        @summary: Given the latitude and longitude of the physical event, buffer it to create a tiny
        polygon as the MapsDatabaseAccessor needs a non-point geometry to do its querying and determine
        which procedural region the physical event is located in
        @param latitude: The latitude of the physical event
        @param longitude: The longitude of the physical event
        @param radiusKm: Radius in km centered on the point to test intersection of area
        @return: String corresponding to the procedural region name or None if no region found
        '''
        pointBuffer = self.geomUtils.bufferPoint(latitude, longitude, bufferRadiusKm)
        queryResults = self.mapDataQueryResults(tableName=self.proceduralRegionsTableName(),
                                                mapQueryColumns=self.proceduralRegionsColumnsToQuery(),
                                                queryGeometry=pointBuffer,
                                                intersect=True)
        return queryResults

    def getDualProceduralRegionsIntersectingPoint(self, latitude, longitude, bufferRadiusKm=0.1):
        '''
        @summary: Given the latitude and longitude of the physical event, buffer it to create a tiny
        polygon as the MapsDatabaseAccessor needs a non-point geometry to do its querying and determine
        which DUAL procedural region the physical event is located in
        @param latitude: The latitude of the physical event
        @param longitude: The longitude of the physical event
        @param radiusKm: Radius in km centered on the point to test intersection of area
        @return: String corresponding to the DUAL procedural region name or None if no region found
        '''
        pointBuffer = self.geomUtils.bufferPoint(latitude, longitude, bufferRadiusKm)
        queryResults = self.mapDataQueryResults(tableName=self.dualProceduralRegionsTableName(),
                                                mapQueryColumns=self.dualProceduralRegionsColumnsToQuery(),
                                                queryGeometry=pointBuffer,
                                                intersect=True)
        return queryResults

    ###############################################################
    # tsunami_threat_db_source_regions
    ###############################################################

    def threatDbSourceTableName(self):
        '''
        @summary: The name of the threat database source regions table
        @return: String
        '''
        return "tsunami_threat_db_source_regions"

    def threatDbSourceColumnsToQuery(self):
        '''
        @summary: The default columns to always be queried when retrieving information from the
        tsunami_threat_db_source_regions table.

        NOTE: The first entry in this list will be retrieved using .getLocationName() while the
        others will use .getString("someString").

        Example: ["name", "descriptor"]
        To get "name": queryResult.getLocationName()
        To get "descriptor": queryResult.getString("descriptor")

        @return: A list of column names
        '''
        return ["name", "descriptor", "sourcetype", "is_known", "site_id"]

    def getSourceRegionsByPhysicalEventLocation(self, physicalEvent, siteID):
        '''
        @summary: Get the matching threat database source regions within the physical event
        location
        @param physicalEvent: The physical event object
        @param siteID: The center site ID (e.g., NTWC or PTWC)
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryGeometry = self.geomUtils.bufferPoint(physicalEvent.getLatitude(),
                                                   physicalEvent.getLongitude(), 5)
        queryResults = self.mapDataQueryResults(tableName=self.threatDbSourceTableName(),
                                                mapQueryColumns=self.threatDbSourceColumnsToQuery(),
                                                queryGeometry=queryGeometry, intersect=True)
        return self.filterQueryResultsBySite(queryResults, siteID)

    def getSourceRegionsByPhysicalEventLocationAndEventType(self, physicalEvent, siteID):
        '''
        @summary: Get the matching threat database source regions within the physical event
        location and match the physical event type (e.g., Seismic)
        @param physicalEvent: The physical event object
        @param siteID: The center site ID (e.g., NTWC or PTWC)
        @return: A list of MapsDatabaseAccessor query results
        '''
        queryGeometry = self.geomUtils.bufferPoint(physicalEvent.getLatitude(),
                                                   physicalEvent.getLongitude(), 5)
        queryResults = self.mapDataQueryResults(tableName=self.threatDbSourceTableName(),
                                                mapQueryColumns=self.threatDbSourceColumnsToQuery(),
                                                queryGeometry=queryGeometry, intersect=True,
                                                queryMatch=physicalEvent.getEventType().getLabel(),
                                                matchColumn="sourcetype")
        return self.filterQueryResultsBySite(queryResults, siteID)

    ###############################################################
    # zone
    ###############################################################

    def zoneTableName(self):
        '''
        @summary: The name of the forecast zones table
        @return: String
        '''
        return "zone"

    def zoneColumnsToQuery(self):
        '''
        @summary: The mandatory columns to query from the zone table
        @return: List
        '''
        return ["state_zone"]

    def getForecastZonesByStateZoneList(self, stateZoneList):
        '''
        @summary: Retrieve a MapsDatabaseAccessor entry for a forecast zone by its
        state-zone codes
        @param stateZoneList: The state-zone code list (e.g., ["OR103", "OR104"])
        @return: A single MapsDatabaseAccessorEntry
        '''
        return self.mapDataQueryResults(tableName=self.zoneTableName(),
                                        mapQueryColumns=self.zoneColumnsToQuery(),
                                        queryGeometry=None, intersect=False,
                                        queryMatch=stateZoneList, matchColumn="state_zone")

    def getForecastZonesByGeometry(self, inputGeometry):
        '''
        @summary: Return the forecast zones that intersect an input geometry
        @param inputGeometry: The input shapely geometry
        @return: List of MapsDatabaseAccessor query results
        '''
        queryResults = self.mapDataQueryResults(tableName=self.zoneTableName(),
                                                mapQueryColumns=self.zoneColumnsToQuery(),
                                                queryGeometry=inputGeometry, intersect=True)
        return queryResults

    ###############################################################
    # Results filtering methods
    ###############################################################

    def filterResultsWithSmallOverlapAreas(self, inputGeometry, queryResults):
        '''
        @summary: Filter the query results to remove results that only slightly
        overlapped with the input geometry
        @param inputGeometry: The input shapely geometry
        @param queryResults: A list of results from the MapsDatabaseAccessor
        @return: Filtered list of query results
        '''
        for i in range(len(queryResults) - 1, -1, -1):
            intersectionArea = inputGeometry.intersection(queryResults[i].getGeometry()).area
            if intersectionArea < 0.01:
                queryResults.pop(i)

    def filterResultsByNonSpecialProcedureAreas(self, queryResults):
        '''
        @summary: Filter the query results so only rows with a 'is_special' column
        equal to 'N' remains
        @param queryResults: A list of results from the MapsDatabaseAccessor
        @return: Filtered list of query results
        '''
        for i in range(len(queryResults) - 1, -1, -1):
            if self.isQueryResultSpecial(queryResults[i]):
                queryResults.pop(i)
        return queryResults

    def filterQueryResultsBySite(self, queryResults, siteID):
        '''
        @summary: Filter the query results by its 'site_id' column so it matches the
        user-provided site ID
        @param queryResults: A list of results from the MapsDatabaseAccessor
        @param siteID: The site ID (e.g., NTWC or PTWC)
        @return: Filtered list of query results
        '''
        # Return back results if no results to check
        if not queryResults:
            return queryResults

        # Do not check if the 'site_id' field was not queried
        siteIdExists = queryResults[0].getString("site_id")
        if not siteIdExists or siteIdExists == "None":
            return queryResults

        # Walk backwards through list and remove entries that do not match the site ID
        for i in range(len(queryResults) - 1, -1, -1):
            queryResult = queryResults[i]
            querySiteId = queryResult.getString("site_id")
            if querySiteId and querySiteId not in ["None", siteID]:
                queryResults.pop(i)
        return queryResults

    def getQueryResultWithTheSmallestArea(self, queryResults):
        '''
        @summary: Given a list of MapsDatabaseAccessor query results,
        determine the result with the smallest geometry and return it
        @param queryResults: A list of MapsDatabaseAccessor query results
        @return: A single MapsDatabaseAccessor query result
        '''
        # No results found, exit method
        if not queryResults:
            return None
        # Only one result, use it
        elif len(queryResults) == 1:
            return queryResults[0]
        # Loop over results and return one with smallest area
        matchingResult = None
        smallestArea = None
        for result in queryResults:
            geometryArea = result.getGeometry().area
            if not matchingResult or geometryArea < smallestArea:
                matchingResult = result
                smallestArea = geometryArea
        return matchingResult

