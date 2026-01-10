# *** Override behavior of AtomsLocationUtilities.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Contains methods that supports accessing and parsing
    location information

    @since: April 2025
    @author: GSL Hazard Services Team
'''

import math
import AtomsMapUtilities
import Bridge
import GeneralConstants
import GeometryFactory
import GeometryUtilities
import HazardConstants


class AtomsLocationUtilities(object):

    def __init__(self):
        self.amu = AtomsMapUtilities.AtomsMapUtilities()
        self.bridge = Bridge.Bridge()
        self.geomUtils = GeometryUtilities.GeometryUtilities()
        self.cityLocationsDict = self.bridge.getAtomsCityLocations()

    def cardinalDirectionDictionary(self):
        '''
        @summmary: A dictionary of cardinal direction abbreviations mapped
        to the full cardinal direction name
        @return: Dictionary
        '''
        return {
            "N": "north",
            "NE": "northeast",
            "E": "east",
            "SE": "southeast",
            "S": "south",
            "SW": "southwest",
            "W": "west",
            "NW": "northwest"
            }

    def getProductRegionNameFromAbbreviation(self, regionAbbreviation):
        '''
        @summary: Get the full product region name from an input procedural
        region name abbreviation
        @param regionAbbreviation: A product region abbreviation (e.g., Hi)
        @return: String
        '''
        regionDictionary = {
            "AkBcWc": "Alaska, British Columbia, and U.S. West Coast",
            "EcGc": "U.S. East Coast, Gulf of America, and Eastern Canada",
            "Hi": "Hawaii",
            "As": "American Samoa",
            "Gu": "Guam/CNMI",
            "Pr": "Puerto Rico, Virgin Islands",
            "Pac": "Non U.S. Pacific",
            "Car": "Non U.S. Caribbean",
            }
        return regionDictionary.get(regionAbbreviation)

    def getProductRegionAbbreviationFromName(self, regionName):
        '''
        @summary: Get the product region abbreviation from an input product
        region name abbreviation
        @param regionName: A product region name (e.g., Hawaii)
        @return: String
        '''
        regionDictionary = {
            "Alaska/British Columbia/U.S. West Coast": "AkBcWc",
            "U.S. East Coast/Gulf of America/Canada": "EcGc",
            "Hawaii": "Hi",
            "American Samoa": "As",
            "Guam/CNMI": "Gu",
            "Puerto Rico/Virgin Islands": "Pr",
            "Non U.S. Pacific": "Pac",
            "Non U.S. Caribbean": "Car",
            }
        return regionDictionary.get(regionName)

    def getTimezonesByState(self, stateText):
        '''
        @summary: Get all time zones listed for state
        @param stateText: A state abbreviation (e.g., AK) or full name (e.g., Alaska)
        @return: A string of the UNIX time zone
        '''
        if stateText in ["California", "Oregon", "Washington", "British Columbia",
                                 "CA", "OR", "WA", "BC"]:
            return "PST8PDT"
        elif stateText in ["Alaska", "AK"]:
            return "AKST9AKDT"
        elif stateText in ["Hawaii", "HI"]:
            return "HST10"
        elif stateText in ["American Samoa", "AS", "Tutuila", "Samoa"]:
            return "SST11"
        elif stateText in ["Guam", "Northern Mariana Islands", "GU", "MP",
                           "Northern Marianas", "Tinian"]:
            return "CHST-10"
        elif stateText in ["Virgin Islands", "Puerto Rico", "VI", "PR",
                           "Us Virgin Is", "Br Virgin Is", "British Virgin Is."]:
            return "AST4"
        elif stateText in ["New Brunswick", "Nova Scotia", "Newfoundland and Labrador",
                           "Prince Edward Island", "NB", "NS", "NL"]:
            return "AST4ADT"
        elif stateText in ["Florida", "Georgia", "South Carolina", "North Carolina",
                           "Virginia", "Delaware", "New Jersey", "Connecticut",
                           "Massachusetts", "Maine", "Quebec", "FL", "GA", "SC", "NC",
                           "VA", "DE", "NJ", "CT", "MA", "ME", "QB"]:
            return "EST5EDT"
        elif stateText in ["Texas", "Louisiana", "Alabama", "TX", "LA", "AL"]:
            return "CST6CDT"
        else:
            return "UTC"

    def getTimezonesByBreakPointSegmentName(self, bpSegmentName):
        '''
        @summary: Get all time zones listed for state
        @param bpSegmentName: The break point segment name (e.g., Gulf of Saint Lawrence)
        @return: A string of the UNIX time zone
        '''
        if bpSegmentName == "Gulf of Saint Lawrence":
            return "AST4ADT"
        else:
            return "UTC"

    def getPrimaryTimezoneByProductRegionAbbreviation(self, regionAbbreviation):
        '''
        @summary: Get all time zones listed for a specific product region
        @param regionAbbreviation: A product region abbreviation (e.g., Hi)
        @return: List of UNIX time zone strings
        '''
        if regionAbbreviation == "Pr":
            return "AST4"
        elif regionAbbreviation == "EcGc":
            return "EST5EDT"
        elif regionAbbreviation == "AkBcWc":
            return "AKST9AKDT"
        elif regionAbbreviation == "Hi":
            return "HST10"
        elif regionAbbreviation == "As":
            return "SST11"
        elif regionAbbreviation == "Gu":
            return "CHST-10"
        else:
            return "UTC"

    def getTimezonesByProductRegionAbbreviation(self, regionAbbreviation):
        '''
        @summary: Get all time zones listed for a specific product region
        @param regionAbbreviation: A product region abbreviation (e.g., Hi)
        @return: List of UNIX time zone strings
        '''
        if regionAbbreviation == "Pr":
            return ["AST4"]
        elif regionAbbreviation == "EcGc":
            return ["CST6CDT", "EST5EDT", "AST4ADT", "UTC"]
        elif regionAbbreviation == "AkBcWc":
            return ["AKST9AKDT", "PST8PDT", "UTC"]
        elif regionAbbreviation == "Hi":
            return ["HST10"]
        elif regionAbbreviation == "As":
            return ["SST11"]
        elif regionAbbreviation == "Gu":
            return ["CHST-10"]
        else:
            return ["UTC"]

    def getProductRegionTimeZone(self, regionAbbreviation):
        '''
        @summary: Get the main time zone for a product region from an input
        product region name abbreviation
        @param regionAbbreviation: A product region abbreviation (e.g., Hi)
        @return: String
        '''
        regionTimeZone = {
            "AkBcWc": "America/Anchorage",
            "EcGc": "US/Eastern",
            "Hi": "US/Hawaii",
            "As": "US/Samoa",
            "Gu": "Pacific/Guam",
            "Pr": "America/Puerto_Rico",
            "Pac": "UTC",
            "Car": "UTC",
            }
        return regionTimeZone.get(regionAbbreviation)

    def getProceduralRegionByBreakPointNumber(self, queryResult):
        '''
        @summary: Return the product region a break point resides in
        based on the bp_num attribute in the "tsunami_break_points" table
        @param queryResult: A single MapsDatabaseAccessor query result
        @return: String
        '''
        # Get the break point number
        bpNum = queryResult.getNumber(HazardConstants.BP_NUM_ATTR_NAME)
        # Break point number lookup
        if bpNum >= 200 and bpNum <= 299:
            return "Hi"
        elif bpNum >= 300 and bpNum <= 300:
            return "Gu"
        elif bpNum >= 400 and bpNum <= 499:
            return "As"
        elif bpNum >= 500 and bpNum <= 599:
            return "Pr"

    def getProceduralRegionByBreakPointSegmentState(self, queryResult):
        '''
        @summary: Return the product region a break point segment resides in
        based on the state_name attribute in the "tsunami_break_point_segments" table
        @param queryResult: A single MapsDatabaseAccessor query result
        @return: String
        '''

        # Determine which PTWC product region(s) match the results
        stateToProceduralRegions = {
            "Guam": "Gu",
            "Northern Mariana Islands": "Gu",
            "American Samoa": "As",
            "Puerto Rico": "Pr",
            "Hawaii": "Hi",
            }
        return stateToProceduralRegions.get(queryResult.getString(HazardConstants.STATE_NAME_ATTR_NAME))

    def cityLocationDistanceLimitMiles(self):
        '''
        @summary: The maximum distance (in miles) in which a city should
        be included as the closest major or minor city
        @return: Integer
        '''
        return 200

    def getCompassBearingText(self, bearingValue):
        '''
        @summary: Determine the compass bearing text descriptor
        @param bearingValue: The bearing value in degrees (e.g., 208)
        @return: String
        '''
        bearingTextList = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]
        numberOfPoints = len(bearingTextList)
        i = int(numberOfPoints * bearingValue / 360.0 + 0.5) % numberOfPoints
        return bearingTextList[i]

    def buildCityDistanceString(self, cityDict, peLat, peLon):
        '''
        @summary: Given a physical event lat/lon, build a string that
        contains the location of the closest city
        @param cityDict: A dictionary containing a single bit of city
        information from the AtomsCityLocations.py file
        @param peLat: The physical event latitude
        @param peLon: The physical event longitude
        @return: String
        '''
        closestDict = {}
        closestDistanceMi = None
        for cityName in cityDict:
            cityLat = cityDict[cityName]["lat"]
            cityLon = cityDict[cityName]["lon"]
            distanceKm, bearing = self.geomUtils.getDistanceAndBearingBetweenPointsInKm(peLat, peLon,
                                                                                        cityLat, cityLon)
            distanceMi = distanceKm / GeneralConstants.KILOMETERS_PER_MILE
            if closestDistanceMi is None or distanceMi < closestDistanceMi:
                closestDistanceMi = distanceMi
                closestDict = cityDict[cityName]
                closestDict["distanceMiles"] = math.floor(distanceMi)
                closestDict["bearingString"] = self.getCompassBearingText(bearing)
        return closestDict

    def getNearestCities(self, peLat, peLon, productRegionAbbrev):
        '''
        @summary: Read the AtomsCityLocations.py file and get the
        nearest major and minor cities for this product region
        @param peLat: The latitude of the physical event
        @param peLon: The longitude of the physical event
        @param productRegionAbbrev: The product region Abbreviation (e.g., AkBcWc)
        @return: String of city locations
        '''
        locationList = []
        majorDict = self.cityLocationsDict.get(productRegionAbbrev).get("major")
        minorDict = self.cityLocationsDict.get(productRegionAbbrev).get("minor")
        if not majorDict or not minorDict:
            return locationList
        closestMajorDict = self.buildCityDistanceString(majorDict, peLat, peLon)
        closestMinorDict = self.buildCityDistanceString(minorDict, peLat, peLon)
        cityDictList = []
        # If either closest minor or major city <= 200km, show both distances/bearings. Otherwise, Flinn.
        if (closestMinorDict["distanceMiles"] <= self.cityLocationDistanceLimitMiles() or
            closestMajorDict["distanceMiles"] <= self.cityLocationDistanceLimitMiles()):
            cityDictList = [closestMinorDict, closestMajorDict]
        # Assemble text string
        for closestDict in cityDictList:
            distanceString = (f"{closestDict['distanceMiles']} miles {closestDict['bearingString']} "
                              f"of {closestDict['name']}, {closestDict['state']}")
            locationList.append(distanceString)
        # Return location strings
        return locationList

    def getDistancesToQueryGeometries(self, mapQueryResults, eventLat, eventLon):
        '''
        @summary: Given a list of MapsDatabaseAccessor query results, determine the closest distance from
        a physical event location to each geometry
        @param mapQueryResults: A list of MapsDatabaseAccessor query results
        @param eventLat: The event latitude
        @param eventLon: The event longitude
        @return: A dictionary of geometry names and the closest distance
        '''
        resultDict = {}
        for queryResult in mapQueryResults:
            featureName = self.amu.getStringFromQueryResult(queryResult, "name")
            featureGeometry = queryResult.getGeometry()

            # Get coordinate list from the geometry
            geometryCoordinateList = self.geomUtils.getExteriorCoordinatesFromGeometry(featureGeometry)
            if featureGeometry.type != "MultiPolygon":
                geometryCoordinateList = [geometryCoordinateList]

            # Walk through each set of coordinates (most likely just one set) and get all distances
            distanceList = []
            for singleCoordinateList in geometryCoordinateList:
                distanceList += [self.geomUtils.getDistanceBetweenPointsInKm(eventLat, eventLon, featureLat, featureLon)
                                 for featureLon, featureLat in singleCoordinateList]

            # Add shortest distance to result dictionary
            resultDict[featureName] = sorted(distanceList)[0]
        return resultDict

    def getClosestLocationFromDistanceDictionary(self, distanceDictionary):
        '''
        @summary: Given a result dictionary from self.getDistancesToQueryGeometries(),
        return the key that has the closest distance associated with it
        @param distanceDictionary: The result dictionary from self.getDistancesToQueryGeometries()
        @return: String
        '''
        sortedDistanceList = list(sorted(distanceDictionary.items(), key=lambda item: item[1]))
        closestResult = sortedDistanceList[0][0]
        return closestResult

    def getDistanceToClosestIsland(self, queryResults, physicalEventGeometry):
        '''
        @summary: Given a list of MapsDatabaseAccessor results from the
        tsunami_analysis_regions table, get the closest result to the physical event
        @param queryResults: A list of MapsDatabaseAccessor results
        @param physicalEventGeometry: The physical event geometry buffered by 0.1 km
        @return: A dictionary containing the island name, distance in miles, and bearing
        '''
        resultDict = {}
        peLon = physicalEventGeometry.centroid.x
        peLat = physicalEventGeometry.centroid.y
        distanceDict = self.getDistancesToQueryGeometries(queryResults, peLat, peLon)
        closestIsland = self.getClosestLocationFromDistanceDictionary(distanceDict)
        for queryResult in queryResults:
            islandName = self.amu.getStringFromQueryResult(queryResult, "name")
            if islandName == closestIsland:
                islandGeometry = self.amu.getGeometryFromQueryResult(queryResult)
                islandLon = islandGeometry.centroid.x
                islandLat = islandGeometry.centroid.y
                distanceKm, bearing = self.geomUtils.getDistanceAndBearingBetweenPointsInKm(peLat, peLon,
                                                                                            islandLat, islandLon)
                resultDict = {
                    "genericName": None,
                    "name": islandName,
                    "distanceMiles": math.floor(distanceKm / GeneralConstants.KILOMETERS_PER_MILE),
                    "bearingString": self.getCompassBearingText(bearing)
                    }
        return resultDict

    def getGenericLocationName(self, productRegionAbbrev):
        '''
        @summary: Get a generic location descriptor for a product region
        @param productRegionAbbrev: The product region abbreviation (e.g., Hi)
        @return: String
        '''
        genericDict = {
            "As": "in the vicinity of American Samoa",
            "Gu": "in the vicinity of Guam",
            "Pr": "in the vicinity of Puerto Rico"
            }
        return genericDict.get(productRegionAbbrev)

    def getHawaiiLocationInformation(self, physicalEventGeometry):
        '''
        @summary: Get the location information for a product for the 'Hi' product region
        @param physicalEventGeometry: The physical event geometry buffered by 0.1 km
        @return: String
        '''
        locationString = None
        analysisRegionResults = self.amu.getAnalysisRegionsByGeometry(physicalEventGeometry)
        # Loop over analysis regions results, look for HawaiiLocationDescription
        for result in analysisRegionResults:
            if self.amu.getStringFromQueryResult(result, "sourcetype") == "HawaiiLocationDescription":
                locationString = self.amu.getStringFromQueryResult(result, "name")
        return locationString

    def getAmSamLocationInformation(self, physicalEventGeometry, distanceResultDict):
        '''
        @summary: Get the location information for a product for the 'As' product region
        @param physicalEventGeometry: The physical event geometry buffered by 0.1 km
        @param distanceResultDict: A dictionary containing a generic location name, name,
        distance in miles, and compass direction
        @return: String
        '''
        queryResults = self.amu.getAnalysisRegionsBySourceType("AmSamProcedure")
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        union10kmBuffer = self.geomUtils.bufferShapelyGeometry(unionedGeometry, 10, unionedGeometry.centroid)
        if union10kmBuffer.contains(physicalEventGeometry):
            distanceResultDict["genericName"] = self.getGenericLocationName("As")
        else:
            union300kmBuffer = self.geomUtils.bufferShapelyGeometry(unionedGeometry, 300, unionedGeometry.centroid)
            if union300kmBuffer.contains(physicalEventGeometry):
                distanceResultDict = self.getDistanceToClosestIsland(queryResults, physicalEventGeometry)
        return distanceResultDict

    def getGuamLocationInformation(self, physicalEventGeometry, distanceResultDict):
        '''
        @summary: Get the location information for a product for the 'Gu' product region
        @param physicalEventGeometry: The physical event geometry buffered by 0.1 km
        @param distanceResultDict: A dictionary containing a generic location name, name,
        distance in miles, and compass direction
        @return: String
        '''
        queryResults = self.amu.getAnalysisRegionsBySourceType("GuamProcedure")
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        union10kmBuffer = self.geomUtils.bufferShapelyGeometry(unionedGeometry, 10, unionedGeometry.centroid)
        if union10kmBuffer.contains(physicalEventGeometry):
            distanceResultDict["genericName"] = self.getGenericLocationName("Gu")
        else:
            union300kmBuffer = self.geomUtils.bufferShapelyGeometry(unionedGeometry, 300, unionedGeometry.centroid)
            if union300kmBuffer.contains(physicalEventGeometry):
                distanceResultDict = self.getDistanceToClosestIsland(queryResults, physicalEventGeometry)
        return distanceResultDict

    def getPRVI_LocationInformation(self, physicalEventGeometry, distanceResultDict):
        '''
        @summary: Get the location information for a product for the 'Pr' product region
        @param physicalEventGeometry: The physical event geometry buffered by 0.1 km
        @param distanceResultDict: A dictionary containing a generic location name, name,
        distance in miles, and compass direction
        @return: String
        '''
        queryResults = self.amu.getAnalysisRegionsBySourceType("PRVIProcedure")
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        union10kmBuffer = self.geomUtils.bufferShapelyGeometry(unionedGeometry, 10, unionedGeometry.centroid)
        if union10kmBuffer.contains(physicalEventGeometry):
            distanceResultDict["genericName"] = self.getGenericLocationName("Pr")
        else:
            union300kmBuffer = self.geomUtils.bufferShapelyGeometry(unionedGeometry, 300, unionedGeometry.centroid)
            if union300kmBuffer.contains(physicalEventGeometry):
                distanceResultDict = self.getDistanceToClosestIsland(queryResults, physicalEventGeometry)
        return distanceResultDict

    '''
    Accessor Helper Methods
    '''

    def getHawaiiAnalysisGeometry(self):
        '''
        @summary: Retrieve the Hawaii Islands analysis region geometry
        @return: A shapely geometry
        '''
        queryResults = self.amu.getAnalysisRegionsBySourceType("HawaiiIslandProcedure")
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        return unionedGeometry

    def getGuamAnalysisGeometry(self):
        '''
        @summary: Retrieve the Guam analysis region geometry
        @return: A shapely geometry
        '''
        queryResults = self.amu.getAnalysisRegionsBySourceType("GuamProcedure")
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        return unionedGeometry

    def getAmSamAnalysisGeometry(self):
        '''
        @summary: Retrieve the AmSam analysis region geometry
        @return: A shapely geometry
        '''
        queryResults = self.amu.getAnalysisRegionsBySourceType("AmSamProcedure")
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        return unionedGeometry

    def getPRVIAnalysisGeometry(self):
        '''
        @summary: Retrieve the PRVI analysis region geometry
        @return: A shapely geometry
        '''
        queryResults = self.amu.getAnalysisRegionsBySourceType("PRVIProcedure")
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        return unionedGeometry

    def navigationalAreaDictionary(self, returnAsShapely=False):
        '''
        @summary: A dictionary containing the geographical footprint(s) of
        different navigational areas (NAVAREAS)
        @param returnAsShapely: Boolean where True means return a dictionary
        of shapely geometries
        @return: Dictionary of well-known text representations of
        shapely geometries (returnAsShapely = False) or shapely geometries
        (returnAsShapely = True)
        '''
        wktDict = {
            "VI": "POLYGON ((-66.06895 -31.63486, -53.41270 -33.55989, -50.07285 -35.80017, -19.92637 -35.87143, -19.92637 -84.14968, -67.12363 -84.14968, -67.12363 -56.37754, -65.80527 -56.37754, -65.71738 -55.44160, -68.52988 -54.88937, -68.79356 -52.38914, -71.60606 -51.30328, -66.06895 -31.63486))",
            "X": "POLYGON ((95.03457 -12.06102, 127.02676 -12.14696, 127.11465 -10.25028, 141.08926 -9.99071, 141.00137 0.00000, 170.00527 0.00000, 170.00527 -29.01794, 159.98574 -45.04263, 159.98574 -84.93028, 80.04922 -84.93028, 80.04922 -30.46780, 94.99062 -30.46780, 95.03457 -12.06102))",
            "XI": "POLYGON ((117.91978 41.38610, 130.61998 42.36769, 135.32212 42.56220, 138.31041 44.84907, 180.00000 44.84907, 180.00000 0.00000, 141.00137 0.00000, 141.08926 -9.99071, 127.11465 -10.25028, 127.02676 -12.14696, 95.03457 -12.06102, 95.03457 5.89065, 98.62779 10.19737, 102.84654 20.19134, 117.91978 41.38610))",
            "XII": "MULTIPOLYGON (((-168.91127 67.02084, -101.76284 66.95212, -101.76284 21.17803, -86.20620 14.06334, -84.36049 10.28386, -81.54799 8.28898, -79.35073 9.33121, -76.45034 6.63325, -74.69252 2.25301, -79.96596 -3.63265, -119.86831 -3.63265, -119.86831 0.00000, -180.00000 0.00000, -180.00000 58.70621, -168.91127 65.49988, -168.91127 67.02084)), ((172.01646 53.15419, 180.00000 58.70621, 180.00000 49.98745, 172.01646 53.15419)))",
            "XIII": "MULTIPOLYGON (((154.08677 67.02084, 179.99990 67.02084, 180.00000 58.70621, 172.01646 53.15419, 180.00000 49.98745, 180.00000 44.84907, 138.31041 44.84907, 135.32212 42.56220, 130.61998 42.36769, 134.22349 55.68456, 154.08677 67.02084)), ((-179.99990 67.02084, -169.04311 67.02084, -169.04311 65.49988, -180.00000 58.70621, -179.99990 67.02084)))",
            "XIV": "MULTIPOLYGON (((170.00527 0.00000, 180.00000 0.00000, 180.00000 -85.00000, 159.98574 -85.00000, 159.98574 -45.04263, 170.00527 -29.01794, 170.00527 0.00000)), ((-180.00000 0.00000, -119.86831 0.00000, -119.86831 -85.00000, -180.00000 -85.00000, -180.00000 0.00000)))",
            "XV": "POLYGON ((-119.86831 -18.44630, -68.83884 -18.44630, -66.06895 -31.63486, -71.60606 -51.30328, -68.79356 -52.38914, -68.52988 -54.88937, -65.71738 -55.44160, -65.80527 -56.37754, -67.12363 -56.37754, -67.12363 -84.14968, -119.86831 -84.14968, -119.86831 -18.44630))",
            "XVI": "POLYGON ((-119.86831 -3.65381, -79.95701 -3.65381, -68.79490 -18.44630, -119.86831 -18.44630, -119.86831 -3.65381))",
            }
        if returnAsShapely:
            shapelyDict = {}
            for region in wktDict:
                shapelyDict[region] = GeometryFactory.loadWellKnownText(wktDict[region])
            return shapelyDict
        return wktDict
