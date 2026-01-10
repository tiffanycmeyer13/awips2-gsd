# *** Override behavior of ModifyTsunamiTool.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: The Modify Tsunami Tool will run in response to changes
    to the following hazard types:
    - TS.W/TS.A/TS.Y Change Triggers:
        - The hazard event geometry
        - Initial hazard type selection or change
    
    @since: October 2024
    @author: GSL Hazard Services Team
'''

import logging, UFStatusHandler
import Bridge
import GeneralUtilities
import GeometryUtilities
import TsunamiRecommenderCommon


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()

        self.logger = logging.getLogger("ModifyTsunamiTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.recommenders.hydro",
            "ModifyTsunamiTool", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def defineScriptMetadata(self):
        '''
        @return: A dictionary containing information about this
                 tool
        '''
        return {
            "toolName": "Modify Tsunami Tool",
            "author": "GSL",
            "version": "1.0",
            "description": ''' ''',
            "onlyIncludeTriggerEvents": True,
            "getDialogInfoNeeded": False,
            "getSpatialInfoNeeded": False,
            }

    def defineDialog(self, eventSet):
        '''
        @return: A dialog definition to solicit user input before running tool
        '''
        return None

    def initializeOtherVariables(self, eventSet):
        '''
        @summary: Initialize variables here that will be used widely in the execute and
        subsequent methods
        @param eventSet: A set of events passed into the tool along with session attributes
        @return: None
        '''
        sessionAttributes = eventSet.getAttributes()
        self.trigger = sessionAttributes.get("trigger")
        self.attributeIDs = sessionAttributes.get("attributeIDs")
        self.practice = GeneralUtilities.isPractice(sessionAttributes.get("runMode"))
        self.metadataRefreshCounter = "tsunamiMetadataRefreshCounter"
        self.hazardEvent = list(eventSet.events)[0]

        # Current hazard info
        self.hazardType = self.hazardEvent.getHazardType()
        self.specialProcedureSelections = self.hazardEvent.get("specialProcedureSelections")
        self.specialProcedureOptions = self.hazardEvent.get("specialProcedureOptions")
        self.specialRemoved = False

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        Runs the Modify Aviation Tool
        @param eventSet: A set of events which include session
                         attributes
        @param dialogInputMap: A map of information retrieved from
                               a user's interaction with a dialog;
                               not used by this tool.
        @param visualFeatures: Input gathering visual features; not
                               used by this tool.
        @return: Set of events that were input.
        '''
        # Initialize variables that will be used widely
        self.initializeOtherVariables(eventSet)
        if self.hazardType in ["TS.A", "TS.W", "TS.Y"]:
            self.handleTSU_Changes()
        return eventSet

    def handleTSU_Changes(self):
        '''
        @summary: Logic called when the Tsunami Watch (TS.A), Tsunami Advisory (TS.Y),
        or Tsunami Warning (TS.W) is modified in some way
        @return: NoneType
        '''
        if self.trigger == "hazardEventModification":
            # Update the attribute 'hazardLocations' based a change
            # in the geometry or a hazard type change
            if "geometry" in self.attributeIDs:
                # The geometry has been modified, update the 'hazardLocations' attribute
                self.updateHazardLocatonsAttributeByGeometry()
                if self.specialRemoved:
                    # Update the selections attribute
                    self.hazardEvent.set("specialProcedureSelections",
                                         self.specialProcedureSelections)
                    # Update the wwaLocationCoverage attribute
                    self.updateCoverageAttributeFromLocations()
                    # Update the hazard event geometry by the hazardLocations attribute
                    self.updateGeometryFromLocations()
                # Refresh the metadata in the Hazard Information Dialog
                self.incrementMetadataRefreshCounter()
            elif "type" in self.attributeIDs:
                # The type has changed, update the 'hazardLocations' attribute
                self.updateHazardLocatonsAttributeByGeometry()
                # Refresh the metadata in the Hazard Information Dialog
                self.incrementMetadataRefreshCounter()
            # Update the geometry based on a modification to the 'specialProcedureReferences'
            elif "specialProcedureSelections" in self.attributeIDs:
                # Update the hazardLocations attribute
                self.updateHazardLocationsAttributeFromSpecialChange()
                # Update the wwaLocationCoverage attribute
                self.updateCoverageAttributeFromLocations()
                # Update the hazard event geometry by the hazardLocations attribute
                self.updateGeometryFromLocations()
                # Refresh the metadata in the Hazard Information Dialog
                self.incrementMetadataRefreshCounter()

    def incrementMetadataRefreshCounter(self):
        '''
        @summary: Increment a HiddenField megawidget by 1 to trigger a metadata refresh
        @return: NoneType; The hazard event is updated in memory
        '''
        metaDataRefreshCount = self.hazardEvent.get(self.metadataRefreshCounter, 0)
        self.hazardEvent.set(self.metadataRefreshCounter, metaDataRefreshCount + 1)

    def updateHazardLocationsAttributeFromSpecialChange(self):
        '''
        @summary: Look at the hazard event metadata and update the 'hazardLocations'
        hazard attribute
        @return: NoneType; 'hazardLocations' is updated in memory
        '''
        currentLocations = self.getCurrentHazardLocationsAttribute()
        # Add special areas checked on, removed special areas checked off
        for area in self.specialProcedureOptions:
            # Area not selected, remove it from hazardLocations list if it exists
            if area not in self.specialProcedureSelections:
                if area in currentLocations:
                    currentLocations.remove(area)
            else:
                # Area selected, add it to hazardLocations if it is not already there
                if area not in currentLocations:
                    currentLocations.append(area)
        self.hazardEvent.set("hazardLocations", currentLocations)

    def updateCoverageAttributeFromLocations(self):
        '''
        @summary: Look at the hazard event metadata and update the 'hazardLocations'
        hazard attribute
        @return: NoneType; 'wwaLocationCoverage' is updated in memory
        '''
        currentLocations = self.getCurrentHazardLocationsAttribute()
        locInfoDict = self.getProductLocationDict()
        isSegment = False
        isSpecial = False
        for loc in currentLocations:
            if loc in locInfoDict:
                locIsSpecial = locInfoDict[loc]["special"]
                if locIsSpecial:
                    isSpecial = True
                else:
                    isSegment = True
        if isSegment and isSpecial:
            self.hazardEvent.set("wwaLocationCoverage", "allAreas")
        elif isSegment:
            self.hazardEvent.set("wwaLocationCoverage", "segmentAreas")
        elif isSpecial:
            self.hazardEvent.set("wwaLocationCoverage", "specialAreas")

    def updateGeometryFromLocations(self):
        '''
        @summary: Access the 'hazardLocations' attribute and rebuild the geometry
        based on the locations in that list
        @return: NoneType; the hazard event geometry is updated in memory
        '''
        currentLocations = self.getCurrentHazardLocationsAttribute()
        queryResults = self.amu.getBreakPointSegmentsBySegmentNames(currentLocations)
        unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(queryResults)
        cleanGeometry = GeometryUtilities.GeometryUtilities().cleanupPolygon(unionedGeometry, True)
        advancedGeom = GeometryUtilities.GeometryUtilities().convertFromShapelyToAdvancedGeometry(cleanGeometry)
        self.hazardEvent.setGeometry(advancedGeom)

    def updateHazardLocatonsAttributeByGeometry(self):
        '''
        @summary: Determine if the change in geometry has changed break point segments
        associated with this hazard event
        @return: An updated 'hazardLocations' hazard attribute
        '''
        currentLocations = self.getCurrentHazardLocationsAttribute()
        breakPointSegmentResults = self.getBreakPointSegmentsByHazardEventGeometry()
        self.filterResultsByLocationCoverage(breakPointSegmentResults)
        updatedLocations = self.amu.getNamesFromQueryResults(breakPointSegmentResults)
        if currentLocations != updatedLocations:
            self.hazardEvent.set("hazardLocations", updatedLocations)

    def getBreakPointSegmentsByHazardEventGeometry(self):
        '''
        @summary: Get a list of MapsDatabaseAccessor query results of break point segments
        based on the hazard event geometry
        @return: A list of break point segments MapsDatabaseAccessor query results
        '''
        hazardEventGeometry = self.hazardEvent.getFlattenedGeometry()
        breakPointSegmentResults = self.amu.getBreakPointSegmentsByGeometry(hazardEventGeometry,
                                                                            pruneSmallAreas=True)
        return breakPointSegmentResults

    def filterResultsByLocationCoverage(self, breakPointSegmentResults):
        '''
        @summary: Filter the break point segment query results based on the
        'wwaLocationCoverage' megawidget selection
        @param breakPointSegmentResults: MapsDatabaseAccessor query results of break
        point segments
        @return: Updated list of breakPointSegmentResults
        '''
        wwaCoverage = self.getWWA_LocationCoverageAttribute()
        resultsDict = {}
        checkSpecials = False
        for i in range(len(breakPointSegmentResults) - 1, -1, -1):
            breakPointSegmentName = self.amu.getStringFromQueryResult(breakPointSegmentResults[i],
                                                                      "name")
            isSpecial = self.amu.isQueryResultSpecial(breakPointSegmentResults[i])
            # Standard filter when dealing with only segments or specials
            if ((wwaCoverage == "segmentAreas" and isSpecial) or
                (wwaCoverage == "specialAreas" and not isSpecial)):
                breakPointSegmentResults.pop(i)
            elif wwaCoverage == "allAreas":
                writeResult = True
                if isSpecial:
                    checkSpecials = True
                    if (breakPointSegmentName not in self.specialProcedureSelections or
                        breakPointSegmentName not in self.specialProcedureOptions):
                        breakPointSegmentResults.pop(i)
                        writeResult = False
                if writeResult:
                    resultsDict[breakPointSegmentName] = {
                        "result": breakPointSegmentResults[i],
                        "special": isSpecial,
                        }
        if checkSpecials:
            locInfoDict = self.getProductLocationDict()
            allPossibleSpecials = []
            for bpName in resultsDict:
                if not resultsDict[bpName]["special"]:
                    locations = locInfoDict[bpName]["inclusionSpecialProcedures"]
                    for location in locations:
                        if location not in allPossibleSpecials:
                            allPossibleSpecials.append(location)
            for bpName in resultsDict:
                if resultsDict[bpName]["special"] and bpName not in allPossibleSpecials:
                    breakPointSegmentResults.remove(resultsDict[bpName]["result"])
                    self.specialRemoved = True
                    if bpName in self.specialProcedureSelections:
                        self.specialProcedureSelections.remove(bpName)

    def getCurrentHazardLocationsAttribute(self):
        '''
        @summary: Retrieves the 'hazardLocations' attribute from the hazard event
        @return: List of strings
        '''
        return self.hazardEvent.get("hazardLocations")

    def getWWA_LocationCoverageAttribute(self):
        '''
        @summary: Retrieves the 'wwaLocationCoverage' attribute from the hazard event
        @return: String
        '''
        return self.hazardEvent.get("wwaLocationCoverage")

    def getProductLocationDict(self):
        '''
        @summary: Get the contents of the AtomsProductLocationInfo.py
        @return: Dictionary
        '''
        return Bridge.Bridge().getAtomsProductLocationInfo()


def __str__(self):
    return "ModifyTsunamiTool"
