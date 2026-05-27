# *** Override behavior of AtomsFcstObsUtilities.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Contains methods for accessing/parsing forecast
    and observation tables

    @since: April 2025
    @author: GSL Hazard Services Team
'''

import GeneralConstants
import GeometryUtilities
from gov.noaa.gsl.viz.atomsForecast import TsunamiForecastDao, TsunamiForecastTable, TsunamiForecastUtils
from org.locationtech.jts.geom import Coordinate


class AtomsFcstObsUtilities(object):

    def __init__(self):
        self.geomUtils = GeometryUtilities.GeometryUtilities()
        self.tfd = TsunamiForecastDao.getInstance()

    def isForecastSelected(self, forecastLabel):
        '''
        @summary: If a forecast label is not empty or 'No Selection'
        then a forecast was chosen from the megawidget
        @param forecastLabel: The forecast label
        @return: Boolean
        '''
        return forecastLabel not in ["", "No Selection"]

    def doesForecastExist(self, tsunamiForecast):
        '''
        @summary: Was a TsunamiForecast object retrieved?
        @param tsunamiForecast: A TsunamiForecast object or None
        @return: Boolean
        '''
        return tsunamiForecast is not None

    def createPointsFromStations(self, stationList):
        '''
        @summary: Given a list of observation stations, return a list of point geometries
        @param stationList: A list of station objects
        @return: A list of shapely point geometries
        '''
        return [self.geomUtils.createShapelyPoint(s.getLatitude(), s.getLongitude())
                for s in stationList]

    def createBufferedGeometriesFromStations(self, stationList, bufferKm):
        '''
        @summary: Given a list of observation stations, return a list of buffered polygon
        geometries
        @param stationList: A list of station objects
        @param bufferKm: A buffer (in kilometers)
        @return: A list of shapely point geometries
        '''
        return [self.geomUtils.bufferPoint(s.getLatitude(), s.getLongitude(), bufferKm)
                for s in stationList]

    def createBufferedGeometriesFromForecastRunTable(self, forecastRunTableList, bufferKm):
        '''
        @summary: Using the forecast stations, represented as
        as list of lists from the TsunamiForecastTable, get a list of all
        station IDs deselected by the user
        @param forecastRunTableList: The contents of the forecastRunTable attribute
        Contents: Checked, ID, Name, State/Country, Location, Arrival Time, Amplitude
        Example: [[true,"BAR","Baracoa","Cuba","20.4N 74.5W","1441 09/07","0.6"], ...]
        @param bufferKm: A buffer (in kilometers)
        @return: List of Shapely geometry objects
        '''
        geometryList = []
        for stationInfo in forecastRunTableList:
            if stationInfo[0] is not True:
                continue
            lat, lon = self.convertLatLonStringToFloats(stationInfo[4])
            geometryList.append(self.geomUtils.bufferPoint(lat, lon, bufferKm))
        return geometryList

    def getStationsInsideGeometry(self, forecastRunTableList, inputGeometry):
        '''
        @summary: Using the forecast stations, represented as
        as list of lists from the TsunamiForecastTable, get a list of all
        station IDs deselected by the user
        @param forecastRunTableList: The contents of the forecastRunTable attribute
        Contents: Checked, ID, Name, State/Country, Location, Arrival Time, Amplitude
        Example: [[true,"BAR","Baracoa","Cuba","20.4N 74.5W","1441 09/07","0.6"], ...]
        @param inputGeometry: A shapely geometry
        @return: List of lists with each entry representing one forecast station
        '''
        filteredStationList = []
        for stationInfo in forecastRunTableList:
            if stationInfo[0] is not True:
                continue
            lat, lon = self.convertLatLonStringToFloats(stationInfo[4])
            stationPoint = self.geomUtils.createShapelyPoint(lat, lon)
            if inputGeometry.contains(stationPoint):
                filteredStationList.append(stationInfo)
        return filteredStationList

    def getAllForecastStationLocations(self, tsunamiForecastTable, asPolygon=False):
        '''
        @summary: Get all stations from a TsunamiForecastTable object and return its
        geometries as either shapely Points or Polygons
        @param tsunamiForecastTable: The TsunamiForecastTable object
        @param asPolygon: Boolean where True will return a list of Polygon shapely objects
        and False will return a list of Point shapely objects
        @return: A list of shapely geometries
        '''
        stationList = tsunamiForecastTable.getStations()
        if asPolygon:
            geomList = [self.geomUtils.bufferPoint(s.getLatitude(), s.getLongitude(), 0.01)
                        for s in stationList]
        else:
            geomList = self.createPointsFromStations(stationList)
        return geomList

    def getStationsThatOverlapWithGeometry(self, tsunamiForecastTable, inputGeometry):
        '''
        @summary: Check if any station locations overlap with a user-defined geometry (e.g., an
        analysis region geometry for Guam)
        @param tsunamiForecastTable: A TsunamiForecastTable object containing stations
        @param inputGeometry: A shapely geometry object
        @return: A list of station identifiers as strings
        '''
        stationIds = []
        for forecastStation in tsunamiForecastTable.getStations():
            stationPoint = self.geomUtils.createShapelyPoint(forecastStation.getLatitude(), forecastStation.getLongitude())
            if stationPoint.intersects(inputGeometry):
                stationIds.append(forecastStation.getCustomId())
        return stationIds

    def getForecastStationsWithinArrivalTimeInHours(self, inputJavaDate, tttForecast, numberOfHours):
        '''
        @summary: Build a forecast station table populated with stations that have an arrival time within
        some user-defined hours from the physical event time
        @param inputJavaDate: A Java Date object
        @param tttForecast: A TsunamiForecast object corresponding to the Tsunami Travel Time (TTT) forecast
        @param numberOfHours: A user-defined number of hours as an integer
        @return: A TsunamiForecastTable object with stations with arrival times within the user-defined time interval
        '''
        timeLimitInMillis = numberOfHours * GeneralConstants.MILLIS_PER_HOUR
        stnFcstTable = TsunamiForecastUtils.getStationFcstsWithinTravelTime(inputJavaDate, timeLimitInMillis, tttForecast, None)
        return stnFcstTable

    def areETAsDisplayedInProduct(self, arrivalTime, currentTime, siteID):
        '''
        @summary: Determine if ETAs need to be displayed in the product
        @param arrivalTime: The forecst arrival time
        @param currentTime: The origin time of the physical event or actual cave time
        @param siteID: The warning center site ID (e.g., NTWC or PTWC)
        @return: Boolean
        '''
        if siteID == "NTWC":
            return arrivalTime >= currentTime
        elif siteID == "PTWC":
            return arrivalTime - currentTime >= -GeneralConstants.MILLIS_PER_HOUR

    def isStationInternational(self, station):
        '''
        @summary: Check a station's country and if it is not in a pre-defined list of
        U.S./Canada/territory areas then it is international
        @param station: A Java ForecastStation object
        @return: Boolean
        '''
        return station.getCountry() not in ["United States", "Canada"]

    def initializeThreatMessageCategoryDictionary(self):
        '''
        @summary: Initialize the category dictionary used to bin
        countries by amplitude
        @return: Dictionary
        '''
        return {
            "high": [],
            "medium": [],
            "low": [],
            "veryLow": []
            }

    def getCountriesByThreatMessageCategory(self, forecastRunTableList):
        '''
        @summary: Using the user-selected forecast stations, represented as
        as list of lists from the TsunamiForecastTable, determine the highest
        amplitude for each country and then sort that information into four
        categories:
        "high" -> Greater than 3 meters
        "medium" -> 1 to 3 meters
        "low" -> 0.3 to 1 meter
        "veryLow" -> less than 0.3 meters
        @param forecastRunTableList: The contents of the forecastRunTable attribute
        Contents: Checked, ID, Name, State/Country, Location, Arrival Time, Amplitude
        Example: [[true,"BAR","Baracoa","Cuba","20.4N 74.5W","1441 09/07","0.6"], ...]
        @return: Dictionary
        '''
        amplitudeDict = {}
        for stationInfo in forecastRunTableList:
            # If de-selected by the user, skip it
            if stationInfo[0] is not True:
                continue
            # Access amplitude and convert NA to zero amplitude
            amplitude = float(stationInfo[-1].replace("NA", "0.0"))
            stateOrCountry = stationInfo[3]
            if (amplitude > 0 and (stateOrCountry not in amplitudeDict or
                                   amplitude > amplitudeDict[stateOrCountry])):
                amplitudeDict[stateOrCountry] = amplitude
        categoryDict = self.initializeThreatMessageCategoryDictionary()
        for stateOrCountry in amplitudeDict:
            amplitude = amplitudeDict[stateOrCountry]
            if amplitude > 3:
                categoryDict["high"].append(stateOrCountry)
            elif amplitude > 1:
                categoryDict["medium"].append(stateOrCountry)
            elif amplitude >= 0.3:
                categoryDict["low"].append(stateOrCountry)
            else:
                categoryDict["veryLow"].append(stateOrCountry)
        return categoryDict

    def getAllCountriesFromRunTable(self, forecastRunTableList):
        '''
        @summary: Using the user-selected forecast stations, represented as
        as list of lists from the TsunamiForecastTable, get a list of all
        states/countries
        @param forecastRunTableList: The contents of the forecastRunTable attribute
        Contents: Checked, ID, Name, State/Country, Location, Arrival Time, Amplitude
        Example: [[true,"BAR","Baracoa","Cuba","20.4N 74.5W","1441 09/07","0.6"], ...]
        @return: String
        '''
        stateOrCountryList = []
        for stationInfo in forecastRunTableList:
            # If de-selected by the user, skip it
            if stationInfo[0] is not True:
                continue
            stateOrCountry = stationInfo[3]
            if stateOrCountry not in stateOrCountryList:
                stateOrCountryList.append(stateOrCountry)
        return stateOrCountryList

    def getDeselectedStationFromForecastRunTable(self, forecastRunTableList):
        '''
        @summary: Using the forecast stations, represented as
        as list of lists from the TsunamiForecastTable, get a list of all
        station IDs deselected by the user
        @param forecastRunTableList: The contents of the forecastRunTable attribute
        Contents: Checked, ID, Name, State/Country, Location, Arrival Time, Amplitude
        Example: [[true,"BAR","Baracoa","Cuba","20.4N 74.5W","1441 09/07","0.6"], ...]
        @return: List of strings
        '''
        deselectedStations = []
        for stationInfo in forecastRunTableList:
            if stationInfo[0] is not True:
                deselectedStations.append(stationInfo[1])
        return deselectedStations

    def getStationsExceedingSomeAmplitudeFromForecastRunTable(self, forecastRunTableList,
                                                              amplitudeThreshold):
        '''
        @summary: Using the forecast stations, represented as
        as list of lists from the TsunamiForecastTable, get a list of all station
        rows exceeding some amplitude
        @param forecastRunTableList: The contents of the forecastRunTable attribute
        Contents: Checked, ID, Name, State/Country, Location, Arrival Time, Amplitude
        Example: [[true,"BAR","Baracoa","Cuba","20.4N 74.5W","1441 09/07","0.6"], ...]
        @param amplitudeThreshold: A float value
        @return: List of lists
        '''
        stationList = []
        for stationInfo in forecastRunTableList:
            if stationInfo[0] is not True:
                continue
            amplitude = float(stationInfo[-1].replace("NA", "0.0"))
            if amplitude >= amplitudeThreshold:
                stationList.append(stationInfo)
        return stationList

    def convertLatLonStringToFloats(self, latLonString):
        '''
        @summary: Given a lat/lon location of a station (e.g., "20.4N 74.5W"),
        convert this to two floats (e.g., 20.4 and -74.5)
        @param latLonString: The lat/lon information as a string
        @return: Two floats
        '''
        # Split into lat/lon strings
        latString, lonString = latLonString.split(" ")
        # Latitude conversion
        mult = 1
        if "S" in latString:
            mult = -1
        lat = float(latString[:-1]) * mult
        # Longitude conversion
        mult = 1
        if "W" in lonString:
            mult = -1
        lon = float(lonString[:-1]) * mult
        return lat, lon

    def getStationsExceedingSomeDefinedAmplitude(self, forecastRunTableList, amplitudeThreshold):
        '''
        @summary: Using the forecast stations, represented as
        as list of lists from the TsunamiForecastTable, get a list of all station
        rows exceeding some amplitude
        @param forecastRunTableList: The contents of the forecastRunTable attribute
        Contents: Checked, ID, Name, State/Country, Location, Arrival Time, Amplitude
        Example: [[true,"BAR","Baracoa","Cuba","20.4N 74.5W","1441 09/07","0.6"], ...]
        @param amplitudeThreshold: A float value
        @return: List of lists
        '''
        stationList = []
        for stationInfo in forecastRunTableList:
            if stationInfo[0] is not True:
                continue
            amplitude = float(stationInfo[-1].replace("NA", "0.0"))
            if amplitude >= amplitudeThreshold:
                stationList.append(stationInfo)
        return stationList

    def convertLatLonStringToFloats(self, latLonString):
        '''
        @summary: Given a lat/lon location of a station (e.g., "20.4N 74.5W"),
        convert this to two floats (e.g., 20.4 and -74.5)
        @param latLonString: The lat/lon information as a string
        @return: Two floats
        '''
        # Split into lat/lon strings
        latString, lonString = latLonString.split(" ")
        # Latitude conversion
        mult = 1
        if "S" in latString:
            mult = -1
        lat = float(latString[:-1]) * mult
        # Longitude conversion
        mult = 1
        if "W" in lonString:
            mult = -1
        lon = float(lonString[:-1]) * mult
        return lat, lon

    def getStateOrCountryFromStation(self, station):
        '''
        @summary: Given a ForecastStation object, get either the state name
        or country name if state name does not exist
        @param station: The ForecastStation object
        @return: String
        '''
        stateOrCountry = station.getState()
        if not stateOrCountry:
            stateOrCountry = station.getCountry()
        return stateOrCountry

    def getWarningPointsDomain(self, productRegionAbbrev):
        '''
        @summary: Get the appropriate warning points domain from the
        hazard event
        @param productRegionAbbrev: The abbreviated product region
        @return: String
        '''
        if productRegionAbbrev == "Car":
            warningPointsDomain = "CARIBE"
        else:
            warningPointsDomain = "PTWS"
        return warningPointsDomain

    def getTsunamiForecastFromLabel(self, forecastSelection, tsunamiForecastInfoDict):
        '''
        @summary: Retrieve the tsunami forecast based on the user selection in the defineDialog()
        window
        @param forecastSelection: The selection from the timeOfArrivalSelection or amplitudeSelection
        megawidgets
        @return: A TsunamiForecast object
        '''
        tsunamiForecast = None
        if forecastSelection in tsunamiForecastInfoDict:
            tsunamiForecast = self.tfd.getTsunamiForecast(tsunamiForecastInfoDict[forecastSelection]["forecast"])
        return tsunamiForecast

    def isStationOnShortList(self, stationID, siteID):
        '''
        @summary: Determine if the provided station is on the short list of stations for inclusion into the product text
        @param stationID: The station ID (e.g., ABY)
        @param siteID: The warning center site ID (e.g., NTWC or PTWC)
        @return: Boolean
        '''
        if siteID == "NTWC":
            return stationID in self.tsunamiStationShortListNTWC()
        else:
            # All stations from PTWC will be shown in the forecast table
            return True

    def tsunamiStationShortListNTWC(self):
        '''
        @summary: A list of forecast station IDs that are on
        NTWC's short list for inclusion in the product text
        @return: List
        '''
        return ["ABY", "ADK", "AGD", "AGN", "ALA", "ALI", "ATL", "AVT", "BBE",
                "BBY", "BIO", "BKG", "BMA", "BOP", "BPT", "BSK", "BTL", "BVA",
                "BVI", "BXM", "CAM", "CAR", "CBE", "CBL", "CBM", "CCX", "CDB",
                "CDV", "CHN", "COO", "CPR", "CPT", "CRE", "CRG", "CRP", "CRS",
                "CSC", "CST", "CVI", "DPO", "EFC", "ELK", "EMP", "ENC", "ENG",
                "EUR", "EVT", "FBG", "FBY", "FLP", "FPT", "GAV", "GMN", "GOL",
                "GPT", "GUS", "GVX", "HAT", "HCV", "HMB", "HMR", "HOO", "HUN",
                "IBY", "ICY", "JVB", "KBC", "KOD", "KRM", "KSI", "KWF", "KZI",
                "LAB", "LAJ", "LAN", "LAX", "LBE", "LGU", "LIO", "LKP", "MAY",
                "MBF", "MCL", "MEN", "MHR", "MIF", "MLB", "MNT", "MNY", "MOR",
                "MPT", "MSL", "MTG", "MTN", "MYR", "MZT", "NAN", "NBY", "NEA",
                "PAC", "PBE", "PCF", "PGL", "PIS", "PLN", "PME", "POR", "PRB",
                "PSL", "PTW", "PVT", "RBE", "RDM", "RWY", "SAM", "SAU", "SBB",
                "SBY", "SCI", "SCT", "SCZ", "SDG", "SDV", "SEL", "SEW", "SFC",
                "SHB", "SIT", "SIU", "SJP", "SKA", "SLB", "SLW", "SMY", "SNK",
                "SPF", "SPT", "SRM", "SSD", "SSP", "STL", "STP", "SUF", "SVG",
                "TEN", "TLK", "TND", "TOF", "TOK", "UNA", "URM", "VBH", "VEN",
                "VLD", "WAI", "WIT", "WPT", "WPW", "YAK", "YAQ", "YCH"]
