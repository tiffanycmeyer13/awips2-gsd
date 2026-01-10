# *** Override behavior of AtomsTableSeaLevelObservations.py ***
# -- Override ability: Class-based
# -- Levels: All

'''
    Description: Creates a table containing sea level observation information
    @author: GSL Hazard Services Team
    @version 1.0
    @since: December 2022
'''

import TableText


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
        for key in columnInfoDict:
            columnWidth = columnInfoDict[key]["width"]
            labelName = columnInfoDict[key][f"{language}_Label"]
            columns.append(TableText.Column(key, width=columnWidth, align="<",
                                            labelLine1=labelName, labelAlign1="<"))
        return columns

    def createDataDictForTable(self, eventDicts):
        '''
        @summary: Constructs a dictionary that holds the required data to populate each
        row/column of the Tsunami Forecast Run table.
        @param eventDicts: A list of event-level dictionaries
        @returns formatted title
        '''
        tableValuesDict = {}
        stations = eventDicts[0].get(f"seaLevelObs{self.suffix}")
        if not stations:
            return tableValuesDict
        listOfValueDicts = []
        for station in stations:
            if station[0]:
                valueDictionary = {
                    "site": station[1],
                    "coordinates": station[2],
                    "startTime": station[3],
                    "maxHeight": station[4],
                    "period": station[5]
                    }
                listOfValueDicts.append(valueDictionary)
        if listOfValueDicts:
             tableValuesDict["slobs"] = listOfValueDicts
        return tableValuesDict

    def getColumnInfoDict(self):
        '''
        @summary: Get information about each table column
        @param columnName: The name of the column as a string
        @return: Dictionary
        '''
        columnInfoDict = {
            "site": {
                "English_Label": "Site",
                "Spanish_Label": "Sitio",
                "width": 16,
                },
            "coordinates": {
                "English_Label": "Coordinates",
                "Spanish_Label": "Coordenadas",
                "width": 14,
                },
            "startTime": {
                "English_Label": "Start Time",
                "Spanish_Label": "Hora de inicio",
                "width": 16,
                },
            "maxHeight": {
                "English_Label": "Max Height",
                "Spanish_Label": "Altura maxima",
                "width": 14,
                },
            "period": {
                "English_Label": "Period",
                "Spanish_Label": "Periodo",
                "width": 8,
                },
            }
        return columnInfoDict
