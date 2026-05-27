# *** Override behavior of AtomsTableForecastRuns.py ***
# -- Override ability: Class-based
# -- Levels: All

'''
    Description: Creates a table containing tsunami forecast run information
    @author: GSL Hazard Services Team
    @version 1.0
    @since: December 2022
'''

import datetime
import TableText
import TimeUtil
from AtomsFcstObsUtilities import AtomsFcstObsUtilities
from AtomsLocationUtilities import AtomsLocationUtilities


class Table(TableText.Table):

    def makeColumns(self):
        '''
        @summary: Constructs the Columns that will be used in the table
        @return returns a list of Column objects
        '''
        if not self.language:
            language = "English"
        else:
            language = self.language
        columnInfoDict = self.getColumnInfoDict()
        columns = []
        for key in ["name", "coordinates", "arrivalTime"]:
            columnWidth = columnInfoDict[key]["width"]
            labelName = columnInfoDict[key][f"{language}_Label"]
            columns.append(TableText.Column(key, width=columnWidth, align="<",
                                            labelLine1=labelName, labelAlign1="<"))

        # Add amplitude column if forecast was selected
        eventDict = self.eventDicts[0]
        ampForecast = eventDict.get(f"amplitudeForecast{self.suffix}")
        hasAmplitude = AtomsFcstObsUtilities().isForecastSelected(ampForecast)
        if hasAmplitude and self.doesProductRegionDisplayAmplitudes(eventDict):
            key = "amplitude"
            columnWidth = columnInfoDict[key]["width"]
            labelName = columnInfoDict[key][f"{language}_Label"]
            columns.append(TableText.Column(key, width=columnWidth, align="<",
                                            labelLine1=labelName, labelAlign1="<",
                                            labelLine2="   (m)", labelAlign2="<"))
        return columns

    def createDataDictForTable(self, eventDicts):
        '''
        @summary: Constructs a dictionary that holds the required data to populate each
        row/column of the Tsunami Forecast Run table
        @param eventDicts: A list of event-level dictionaries
        @returns formatted table
        '''
        tableValuesDict = {}
        stateGroups, stations = self.getStateStationsInfo(eventDicts, self.suffix)
        if not stateGroups:
            return tableValuesDict
        for state in stateGroups:
            listOfValueDicts = []
            # Could have multiple rows/stations for the same state
            stationIds = stateGroups.get(state)
            for station in stations:
                if station[1] in stationIds:
                    if self.isThreatMessage:
                        arrivalTime = station[5]
                        nameValue = f"  {station[2]}"
                    else:
                        arrivalTime = self.formatArrivalTime(station[5], station[3])
                        nameValue = station[2]
                    valueDictionary = {
                        "name": nameValue,
                        "state": station[3],
                        "coordinates": station[4],
                        "arrivalTime": arrivalTime,
                        "amplitude": station[6]
                        }
                    listOfValueDicts.append(valueDictionary)
            if listOfValueDicts:
                tableValuesDict[state] = listOfValueDicts

        return tableValuesDict

    def getStateStationsInfo(self, eventDicts, suffix):
        '''
        @summary: Get the proper station information according to input eventDicts,
                  here are a few cases:
                  first, if this is threat message, get the stations with amplitude >= 0.3
                  or for Tsunami Warning, Watch , Advisory:
                      eventIDsFromInput - get a list of eventID from input eventDicts
                      eventIDsFromMetaData - get keys from eventForecastStations
                      if number of these two are same, then return stations from forecastRunTable,
                      otherwise, return stations from eventForecastStations with the specified eventID
        @param eventDicts: A list of event-level dictionaries
        @param suffix: The product suffix as a string, for TS WWAs, the suffix
        will be the "{self.productID}_{self.customId}_{self.productRegion}"
        @return: a dictionary with state name or country name as key with a list of stations.
        '''
        stateGroups = {}
        stations = eventDicts[0].get(f"forecastRunTable{suffix}")
        if not stations:
            return stateGroups, stations
        # Threat message only list the stations with amplitude >= 0.3
        if self.isThreatMessage:
            for station in stations:
                if station[0]:
                    stateGroups.setdefault(station[3], []).append(station[1])
        else:
            eventIdsAndStations = eventDicts[0].get(f"eventForecastStations{suffix}")
            if not eventIdsAndStations:
                return stateGroups, stations
            eventIDs = [e[0] for e in eventIdsAndStations]
            if len(eventDicts) == len(eventIDs):
                for station in stations:
                    if station[0]:
                        stateGroups.setdefault(station[3], []).append(station[1])
            else:
                for eventDict in eventDicts:
                    idFromEventDict = eventDict.get("eventID")
                    for eventIdstation in eventIdsAndStations:
                        if idFromEventDict == eventIdstation[0]:
                            eventStations = eventIdstation[1]
                            for eventStation in eventStations:
                                for station in stations:
                                    if station[1] == eventStation and station[0]:
                                        stateGroups.setdefault(station[3], []).append(station[1])
        return stateGroups, stations

    def doesProductRegionDisplayAmplitudes(self, eventDict):
        '''
        @summary: Only certain product regions display the amplitude
        column. Check if the product occurs in a product region that
        requires this 
        @param eventDict: An event-level dictionary
        @return: Boolean
        '''
        return eventDict.get("productRegion") in ["AkBcWc", "EcGc", "Pr"]

    def formatArrivalTime(self, arrivalTime, state):
        '''
        @summary: Format the arrival time with proper time zone
        @param arrivalTime: The arrival time as a string (e.g., 1215 01/28/25)
        @param state: The state/country where the station is located
        @return: Formatted arrival time
        '''
        timeText = ""
        arrivalTime = datetime.datetime.strptime(arrivalTime, "%H%M %m/%d/%y")
        timeZone = AtomsLocationUtilities().getTimezonesByState(state)
        timeFormat = "%H%M %Z %b %d"
        if timeZone != "UTC":
            tzTimeDT = TimeUtil.changeTimezoneOfDatetimeObject(arrivalTime, timeZone)
            timeText = tzTimeDT.strftime(timeFormat)
        return timeText

    def getColumnInfoDict(self):
        '''
        @summary: Get information about each table column
        @param columnName: The name of the column as a string
        @return: Dictionary
        '''
        columnInfoDict = {
            "name": {
                "English_Label": "Location",
                "Spanish_Label": "Ubicación",
                "width": 26,
                },
            "coordinates": {
                "English_Label": "Coordinates",
                "Spanish_Label": "Coordenadas",
                "width": 14,
                },
            "arrivalTime": {
                "English_Label": "ETA(UTC)" if self.isThreatMessage else "ETA",
                "Spanish_Label": "ETA",
                "width": 18,
                },
            "amplitude": {
                "English_Label": "Amplitude",
                "Spanish_Label": "Amplitud",
                "width": 10,
                },
            }
        return columnInfoDict

    def getColumnWidth(self, columnName):
        '''
        @summary: A dictionary containing the character widths for
        each column in the table
        @param columnName: The name of the column as a string
        @return: Integer
        '''
        widthDict = {
            "name": 26,
            "coordinates": 14,
            "arrivalTime": 18,
            "amplitude":10
        }
        return widthDict.get(columnName, 0)
