# *** Override behavior of TsunamiRecommenderCommon.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Common methods and variable for tsunami tools/recommenders
    
    @since: September 2023
    @author: GSL Hazard Services Team
'''

import copy
import logging, UFStatusHandler
import AtomsFcstObsUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMapUtilities
import EventFactory
import EventSetFactory
import GeneralConstants
import GeneralUtilities
import GeometryUtilities
import HazardConstants
import RecommenderTemplate
import TextProductCommon
import ThreatDB
import TimeUtil
from com.raytheon.viz.core.mode import CAVEMode
from com.raytheon.viz.gfe.ui.runtimeui import DisplayMessageDialog
from gov.noaa.gsl.common.dataplugin.pem import PhysicalEventManager
from gov.noaa.gsl.viz.atoms.trecs import TrecsExecInfo, TrecsExecProcedure, TrecsExecCategory, TrecsExecDialog, MessageDialogUtils
from gov.noaa.gsl.viz.atoms import ReverseTTTClientUtils
from gov.noaa.gsl.common.dataplugin.atoms import ReverseTTTRegion
from gov.noaa.gsl.common.dataplugin.atomsForecast import TsunamiForecastType, TsunamiForecast
from gov.noaa.gsl.viz.atomsSeaLevelObs import SeaLevelObsDao
from gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs import SLObsUtils


class TsunamiRecommenderCommon(RecommenderTemplate.Recommender):

    '''
    Shared methods between the TsunamiRecommender.py and TsunamiMessageTool.py
    '''

    def __init__(self):
        self.logger = logging.getLogger("TsunamiRecommenderCommon")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.common.recommenders.hydro", "TsunamiRecommenderCommon",
            level=logging.INFO))
        self.logger.setLevel(logging.INFO)

        self.MESSAGE_DIALOG_TITLE = "T-RECS Dialog"
        self.NO_TTT_AVAILABLE_ERROR = "ERROR - Procedure/Category requires a time-of-arrival-forecast (e.g., TTT) and none has been selected or none is available."
        self.TRACE_BREAK = "-------------------------------------------------------\n"

       # Instantiate shared instance variables
        self.practice = False
        self.siteID = None
        self.afou = AtomsFcstObsUtilities.AtomsFcstObsUtilities()
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amu = AtomsMapUtilities.AtomsMapUtilities()
        self.geomUtils = GeometryUtilities.GeometryUtilities()
        self.pem = PhysicalEventManager.getInstance()
        self.tpc = TextProductCommon.TextProductCommon()

        # Physical Event specific variables
        self.physicalEvent = None
        self.latitude = None
        self.longitude = None
        self.distanceToCoastKm = None
        self.physicalEventID = None
        self.physicalEventType = None
        self.procRegion = None

        # Tsunami Forecast Specific Variables
        self.amplitudeForecast = None
        self.timeOfArrivalForecast = None
        self.tsunamiForecastInfoDict = {}

        # Seismic specific variables
        self.depthInKm = 0
        self.depthInMi = 0
        self.magnitude = 0

        self.bypassThreatDB = False
        self.procsListDict = None

        self.selectedHazardTypes = []
        self.selectedRegionAbbreviations = []

        # Set to true when we do not want to open dialogs, such as the TrecsExecDialog
        self.isAutoTest = False
        # When autotesting, we should explicitly suppress errors when missing TTT forecasts
        self.suppressTTTMissingErrors = False
        self.executedProcCategories = []

    def initializeVariablesFromEventSetAttributes(self, eventSet):
        '''
        @summary: Read the eventSet attributes to define more instance variables
        @param eventSet: A set of hazard event objects
        @return: Defined self.siteID and self.practice variables
        '''
        self.siteID = eventSet.getAttribute("siteID")
        self.practice = GeneralUtilities.isPractice(eventSet.getAttribute("runMode"))

    def isCaveModeOperational(self):
        '''
        @summary: Check if CAVE was launched in operational mode
        @return: Boolean; True if mode is operational, False if mode is test or practice
        '''
        return CAVEMode.OPERATIONAL == CAVEMode.getMode()

    def initializeVariablesFromPhysicalEvent(self, selectedEvent):
        '''
        @summary: Read the eventSet attributes to define more instance variables
        @param selectedEvent: The selected physical event
        @return: Defined self.siteID and self.practice variables
        '''
        self.physicalEvent = selectedEvent
        self.physicalEventID = selectedEvent.getCustomId()
        self.physicalEventType = selectedEvent.getEventType().getLabel()
        self.latitude = selectedEvent.getLatitude()
        self.longitude = selectedEvent.getLongitude()
        self.distanceToCoastKm = selectedEvent.getDistanceToCoastKm()

        # Populate reverseTTTTravelTimesDict on a lazy basis, meaning when it is first needed
        self.reverseTTTTravelTimesDict = None
        self.executedProcCategories = []

        proceduralRegionResults = self.amu.getProceduralRegionsIntersectingPoint(self.latitude, self.longitude)
        self.procRegion = ""
        if proceduralRegionResults:
            smallestRegionResult = self.amu.getQueryResultWithTheSmallestArea(proceduralRegionResults)
            self.procRegion = self.amu.getStringFromQueryResult(smallestRegionResult, "name")
        self.tsunamiForecastInfoDict = self.agu.createForecastInfoDictionary(self.physicalEventID)
        if self.agu.isPhysicalEventTypeSeismic(self.physicalEventType):
            physicalEventData = self.physicalEvent.getData()
            self.magnitude = round(physicalEventData.getPrefMagnitude(), 2)
            self.depthInMi = physicalEventData.getDepth()
            self.depthInKm = self.depthInMi * GeneralConstants.KILOMETERS_PER_MILE

    def defineDialog(self, eventSet, **kwargs):
        '''
        @summary: Define the contents of the window that pops up when the tool is launched
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return
        @param kwargs: Additional key word arguments to this method.
        @return: MegaWidget dialog definition to solicit user input before running tool
        '''
        # For some reason, the timeOfArrivalForecast may be stale from the old selected physical event!!!
        # So adding this line to fix this bug (fixes the symptom, but not the problem!)
        self.timeOfArrivalForecast = None
        self.amplitudeForecast = None
        self.initializeVariablesFromEventSetAttributes(eventSet)

        # Determine the physical event that was selected from the PEM
        selectedEventList = list(self.pem.getSelectedPhysicalEvents())
        errorMsg = self.agu.validateSelectedPhysicalEvent(selectedEventList)
        if errorMsg:
            return {"resultsMessage": errorMsg}
        # Grab information from the single selected event
        self.selectedEvent = selectedEventList[0]
        self.initializeVariablesFromPhysicalEvent(self.selectedEvent)
        errorMsg = self.validateActivePhysicalEvent()
        if errorMsg:
            return {"resultsMessage": errorMsg}

        # Build initial dialogDict components
        dialogDict = {
            "title": f"Tsunami Recommender (T-RECS) ({self.siteID})",
            "fields": self.getDialogMegawidgets(),
            "valueDict": {},
            }

        return dialogDict

    def getDialogMegawidgets(self):
        '''
        @summary: Get a list of megawidget dictionaries that will populate the dialog window
        when this tool is run
        @return: A list of dictionaries of megawidget properties
        '''
        return [
            self.physicalEventMegawidget(self.selectedEvent),
            self.physicalEventLabelMegawidget(self.physicalEventLabelText_TRECS()),
            self.productRegionsMegawidget(),
            self.hazardTypesMegawidget(),
            self.bypassThreatDBMegawidget(),
            self.performSurgeryMegawidget(),
            self.forecastSelectionLabelMegawidget(),
            self.timeOfArrivalMegawidget(),
            self.amplitudeSelectionMegawidget(),
            ]

    def defaultHazardTypesToRecommend(self):
        '''
        @summary: The default hazard type groups that will be selected by default
        when the recommender dialog is launched
        @see: getHazardTypesToRecommend() has all possible options
        @return: A list of hazard type groups
        '''
        return []

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return.
        @param dialogInputMap: Map from call to defineDialog.
        @param spatialInputMap: Map from call to defineSpatialInfo. Ignored
        @return: List of objects that will be later converted to Java Event objects
        '''
        # The product regions being analyzed (e.g., ["AkBcWc"])
        self.selectedRegionAbbreviations = dialogInputMap.get("regionalSelections")
        # The hazard types being analyzed
        self.selectedHazardTypes = dialogInputMap.get("hazardTypeSelections")
        # Build the T-RECS Execution Dialog
        self.trecsExecInfo = self.buildTrecsExecInfo()
        # Pull the user-selected time of arrival and amplitude forecasts
        self.getForecastInfoFromDialogInput(dialogInputMap)
        # Determine if the 'Bypass Threat Database Lookups' checkbox was checked
        self.bypassThreatDB = dialogInputMap.get("bypassThreatDBCheckBox")
        # Determine if surgery will be performed with the active hazard events
        self.performSurgery = dialogInputMap.get("performSurgery")

        # Determine which, if any, product regions are having the initial message procedures run on them
        initialMessageRegions = [reg for reg in self.selectedRegionAbbreviations
                                 if dialogInputMap.get(f"{reg}_MessageType") == "initialMessage"]

        # Run the initial message procedures on all initial message regions at once
        proposedInitialEventSet = self.recommendInitialTsunamiEvents(initialMessageRegions)

        # Define the new eventSet that will be returned from this tool
        newEventSet = EventSetFactory.createEventSet()

        # Filter the input eventSet this tool run to only contain events associated with the selected physical event
        originalEventSet = self.getActiveEventsForPhysicalEvent(eventSet)

        # Determine the active product regions where events are currently issued
        activeProductRegions = [hazardEvent.get("productRegion") for hazardEvent in originalEventSet]

        # Walk through all selected product regions and either create new events or manipulate existing events
        for productRegion in self.selectedRegionAbbreviations:
            # The proposed eventSet for this product region
            proposedEventSet = EventSetFactory.createEventSet()

            # If product region was processed through the initial message framework then retrieve those events
            if productRegion in initialMessageRegions:
                for event in proposedInitialEventSet:
                    if event.get("productRegion") == productRegion:
                        proposedEventSet.add(event)
            else:
                # Run follow-up procedures
                proposedEventSet = self.recommendFollowUpTsunamiEvents(productRegion)

            # No proposed events for this product region. But we need surgery to set any
            # existing TS.WWYs for this region to ENDING. So dont just continue!
            # if len(proposedEventSet.getEvents()) < 1:
            #     continue

            # No hazards currently exist for this product region or surgery as not requested to be
            # performed, add whatever is found to the final eventSet with no surgery
            if productRegion not in activeProductRegions or not self.performSurgery:
                newEventSet.addAll(proposedEventSet.events)
                continue

            # There are active hazard events for this product region, perform surgery to blend the
            # existing and proposed areas
            postOpEventSet = self.performEventSurgery(originalEventSet, proposedEventSet, productRegion)
            newEventSet.addAll(postOpEventSet.events)

        newEventSet = self.summarizeUserMessages(newEventSet)
        return newEventSet

    def getStationsExceedingCriteria(self):
        '''
        @summary: Walk through the station forecast and sea level observations
        for this physical event and determine which stations exceed the advisory
        and warning criteria
        @return: Dictionary of station objects at the warning and advisory levels
        '''
        # Build dictionary to hold the stations exceeding warning or advisory criteria
        stationDict = {
            "warningStations": [],
            "advisoryStations": [],
            }
        # Look at forecast station amplitudes
        if self.amplitudeForecast is not None:
            for tsuStnFcst in self.amplitudeForecast.getStationFcsts():
                if tsuStnFcst.getAmplitude() > 1.0:
                    stationDict["warningStations"].append(tsuStnFcst.getStation())
                elif tsuStnFcst.getAmplitude() >= 0.3:
                    stationDict["advisoryStations"].append(tsuStnFcst.getStation())
        # Look at sea level observation station amplitudes
        slobs = SeaLevelObsDao.getInstance().getSeaLevelObservations(self.physicalEventID, None)
        mostRecentSlobs = SLObsUtils.getMostRecentSLObsSet(slobs)
        for ob in mostRecentSlobs:
            # Amplitude is missing so skip it
            if not ob.getAmplitude():
                continue
            if ob.getAmplitude() > 1.0:
                stationDict["warningStations"].append(ob.getStation())
            elif ob.getAmplitude() >= 0.4:
                stationDict["advisoryStations"].append(ob.getStation())
        return stationDict

    def recommendFollowUpTsunamiEvents(self, productRegion):
        '''
        @summary: Method to determine what hazard events should be created based on
        the follow-up message procedures
        @return: An eventSet with proposed hazard events
        '''
        proposedEventSet = EventSetFactory.createEventSet()
        self.trecsExecInfo.appendToTrace("Using Forecast/SLObs Follow-Up Procedures ....")

        # Get forecast and sea level obs stations that exceed advisory and warning criteria
        stationDict = self.getStationsExceedingCriteria()

        # Create point geometries for each advisory and warning station
        warningPointGeoms = self.afou.createPointsFromStations(stationDict["warningStations"])
        advisoryPointGeoms = self.afou.createPointsFromStations(stationDict["advisoryStations"])

        # Forecast or sea level observations exceed the criteria; make a proposed eventSet
        if advisoryPointGeoms or warningPointGeoms:
            # Get all break point segments in this product region and filter out special procedure areas
            breakPointSegmentResults = self.amu.getBreakPointSegmentsByProductRegionName(productRegion)
            breakPointSegmentResults = self.amu.filterResultsByNonSpecialProcedureAreas(breakPointSegmentResults)
            # Loop over stations and determine if any overlap with each break point segment
            warningQueryResults = []
            advisoryQueryResults = []
            for segmentResult in breakPointSegmentResults:
                segmentGeometry = segmentResult.getGeometry()
                segmentUsed = False
                for stationGeom in warningPointGeoms:
                    if segmentGeometry.contains(stationGeom):
                        warningQueryResults.append(segmentResult)
                        segmentUsed = True
                        break
                # Check advisory geometries if not found in the warning stations
                if not segmentUsed:
                    for stationGeom in advisoryPointGeoms:
                        if segmentGeometry.contains(stationGeom):
                            advisoryQueryResults.append(segmentResult)
                            break
            tsunamiEventDicts = []
            if warningQueryResults:
                tsunamiEventDicts.extend(self.createEventDictsByBrkptSegs("TS.W", warningQueryResults))
            if advisoryQueryResults:
                tsunamiEventDicts.extend(self.createEventDictsByBrkptSegs("TS.Y", advisoryQueryResults))
            proposedEventSet = self.createTsunamiWWAFromAreaDictList(tsunamiEventDicts, proposedEventSet)
        return proposedEventSet

    def isActivePhysicalEvent(self):
        '''
        @summary: Determine if the selected physical event is active
        @return: Boolean
        '''
        return self.physicalEvent.getIsActive()

    def isKnownPhysicalEvent(self, selectedEvent):
        '''
        @summary: Determine if the selected physical event is in the list of known physical event
        @return: Boolean
        '''
        return selectedEvent.getCustomId() in self.knownPhysicalEventList()

    def knownPhysicalEventList(self):
        '''
        @summary: List of known physical events
        @return: a list
        '''
        return ["Landslide_123"]

    # Abstract. Override this method.
    def buildTrecsProceduresDict(self):
        return {}

    def validateActivePhysicalEvent(self):
        '''
        @summary: Validate whether the physical event is active and if it is not then throw
        an error message to the user
        @return: An error string if the physical event is not active, otherwise None
        '''
        errorMsg = None
        if not self.isActivePhysicalEvent():
            errorMsg = ("The physical event must be active to run this tool or recommender."
                        "Optionally, return to the PEM Dialog and set the event to ACTIVE.")
        return errorMsg

    def physicalEventMegawidget(self, selectedEvent):
        '''
        @summary: Build HiddenField megawidget to pass the physical event to the execute() method
        @param selectedEvent: The selected physical event to pass
        @return: A dictionary
        '''
        return {
            "fieldType": "HiddenField",
            "fieldName": "physicalEvent",
            "values": selectedEvent,
            }

    def physicalEventLabelMegawidget(self, label):
        '''
        @summary: Build Label megawidget to pass the physical event to the execute() method
        @param label: The text to be displayed
        @return: A dictionary
        '''
        return {
            "fieldType": "Label",
            "fieldName": "physicalEventLabel",
            "labelBold": True,
            "label": label,
            }

    def knownPhysicalEventMegawidget(self, selectedEvent):
        '''
        @summary: Ask user if they want to use special procedure from threat database
        @param selectedEvent: The selected physical event
        @return: A dictionary
        '''
        physicalEventName = selectedEvent.getName()
        return {
            "fieldType": "Group",
            "fieldName": "knownPhysicalEventGroup",
            "topMargin": 10,
            "bottomMargin": 10,
            "expandHorizontally": True,
            "fields": [
                {
                    "fieldType": "CheckBox",
                    "fieldName": "useSpecialProcedure",
                    "label": (f"Use {physicalEventName} special procedure from threat "
                              "database, check this and click 'Run'"),
                    "labelColor": {"red": 0, "green": 0, "blue": 1},
                    "values": False,
                    }
                ]
            }

    def isPacificBasin(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Pacific region
        @return: Boolean
        '''
        regionsToCheck = ["Alaska/AK Pen/Aleutians", "American Samoa", "Arctic Ocean - AOR",
                          "Arctic non-AOR", "Bering Sea-deep", "Bering Sea-shallow",
                          "British Columbia", "Guam/CNMI", "Hawaii",
                          "Pacific event non-WC_ATWC AOR", "U.S. West Coast"]

        return self.isInCorrectProceduralRegions(regionsToCheck, bufferRadiusKm)

    def isAtlanticBasin(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Atlantic region
        @return: Boolean
        '''
        regionsToCheck = ["Atlantic Basin", "Atlantic Ridge", "Caribbean", "Eastern Canada",
                          "Gulf of America", "Gulf of Saint Lawrence", "Puerto Rico",
                          "U.S. East Coast"]
        return self.isInCorrectProceduralRegions(regionsToCheck, bufferRadiusKm)

    def isUsWestCoastProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is the U.S. West Coast region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["U.S. West Coast"], bufferRadiusKm)

    def isBritishColumbiaProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is is in the British Columbia region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["British Columbia"], bufferRadiusKm)

    def isPacificNonAORProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Pacific event non-WC_ATWC
        AOR region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Pacific event non-WC_ATWC AOR"], bufferRadiusKm)

    def isAtlanticRidgeProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Atlantic Ridge region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Atlantic Ridge"], bufferRadiusKm)

    def isAtlanticBasinProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Atlantic Basin region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Atlantic Basin"], bufferRadiusKm)

    def isCaribbeanProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Caribbean region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Caribbean"], bufferRadiusKm)

    def isAlaskaProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Alaska region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Alaska/AK Pen/Aleutians"], bufferRadiusKm)

    def isBeringSeaProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Bering Sea deep or shallow region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Bering Sea-deep", "Bering Sea-shallow"], bufferRadiusKm)

    def isBeringSeaDeepProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Bering Sea deep region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Bering Sea-deep"], bufferRadiusKm)

    def isBeringSeaShallowProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Bering Sea shallow region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Bering Sea-shallow"], bufferRadiusKm)

    def isArcticOceanProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Arctic AOR or Non-AOR region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Arctic Ocean - AOR", "Arctic non-AOR"], bufferRadiusKm)

    def isArcticAORProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Arctic AOR region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Arctic Ocean - AOR"], bufferRadiusKm)

    def isArcticNonAORProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Arctic Non-AOR region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Arctic non-AOR"], bufferRadiusKm)

    def isECoastOrECanProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Eastern Canada or
        U.S. East Coast region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Eastern Canada", "U.S. East Coast"], bufferRadiusKm)

    def isUsEastCoastProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the U.S. East Coast region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["U.S. East Coast"], bufferRadiusKm)

    def isEastCanadaProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Eastern Canada region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Eastern Canada"], bufferRadiusKm)

    def isGulfAmericaProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Gulf of America region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Gulf of America"], bufferRadiusKm)

    def isGulfStLawProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Gulf of Saint Lawrence region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Gulf of Saint Lawrence"], bufferRadiusKm)

    def isIndianOceanProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Indian Ocean region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Indian Ocean"], bufferRadiusKm)

    def isHawaiiProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Hawaii region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Hawaii"], bufferRadiusKm)

    def isGuamProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Guam region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Guam/CNMI"], bufferRadiusKm)

    def isAmSamProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the American Samoa region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["American Samoa"], bufferRadiusKm)

    def isPRVIProcRegion(self, bufferRadiusKm=1):
        '''
        @summary: Determine if the physical event is in the Puerto Rico region
        @return: Boolean
        '''
        return self.isInCorrectProceduralRegions(["Puerto Rico"], bufferRadiusKm)

    def lookupProductRegions(self, inputMessageRegion):
        '''
        @summary: Look up the product region or regions based on the input message region
        @param inputMessageRegion: The message region (e.g., "British Columbia")
        @return: String or list of strings
        '''
        if (inputMessageRegion in ["Bering Sea-shallow", "U.S. West Coast", "Bering Sea-deep",
                                   "Arctic Ocean - AOR", "British Columbia", "Alaska/AK Pen/Aleutians",
                                   "Pacific event non-WC_ATWC AOR", "Arctic non-AOR", "Hawaii",
                                   "American Samoa", "Guam/CNMI"]):
            return self.pacificProductRegions()
        elif (inputMessageRegion in ["Atlantic Basin", "U.S. East Coast", "Caribbean",
                                     "Atlantic Ridge", "Puerto Rico", "Gulf of America",
                                     "Gulf of Saint Lawrence", "Eastern Canada"]):
            return self.atlanticProductRegions()
        else:
            return self.getAllRegions()

    def getViableProductRegions(self):
        '''
        @summary: Look up the basin for the physical event and return the product regions that
        make sense for that basin
        @return: List of string product regions
        '''
        if self.isPacificBasin():
            return self.pacificProductRegions()
        else:
            return self.atlanticProductRegions()

    def executeThreatDatabaseQueries(self, productRegions):
        '''
        @summary: Query the threat database and build hazard
        event dictionaries
        @param productRegions: A list of product region names
        @return wwAreaDictList: A list of dictionaries containing
        information to create one or more hazard events
        @return remainingProductRegions: Outstanding product regions
        that will need to go through procedural steps
        '''
        remainingProductRegions = copy.deepcopy(productRegions)
        wwaAreaDictList = []
        if not self.bypassThreatDB:
            hitProductRegions = []
            for productRegion in productRegions:
                wwaAreaDictListForProductRegion = self.queryThreatDatabase(productRegion)
                wwaAreaDictList += wwaAreaDictListForProductRegion
                if wwaAreaDictListForProductRegion:
                    hitProductRegions.append(productRegion)
                    self.trecsExecInfo.setThreatDBHit(productRegion, True)
                    remainingProductRegions.remove(productRegion)
            if hitProductRegions:
                ext = ""
                if len(hitProductRegions) > 1:
                    ext = "s"
                hitRegions = self.tpc.joinStringsWithOxfordComma(hitProductRegions)
                self.trecsExecInfo.appendToTrace(f"ThreatDB hit{ext} for {hitRegions}!")
            if remainingProductRegions:
                ext = ""
                if len(remainingProductRegions) > 1:
                    ext = "es"
                missedRegions = self.tpc.joinStringsWithOxfordComma(remainingProductRegions)
                self.trecsExecInfo.appendToTrace(f"ThreatDB miss{ext} for {missedRegions}...")
        else:
            self.trecsExecInfo.appendToTrace("ThreatDB bypassed...")
        return wwaAreaDictList, remainingProductRegions

    def tsunamiRecommenderHazardEventCreation(self, wwaAreaDictList, newEventSet):
        '''
        @summary: Creates hazard events for the user selected hazard types
        and product regions in the Tsunami Recommender
        @param wwaAreaDictList: A dictionary of tsunami event information used
        to build the hazard event (e.g., hazard type, geometry, product region,
        attributes)
        @param newEventSet: The eventSet returned by the tool
        @return: An updated eventSet
        '''
        omittedHazardTypes = []
        omittedProductRegions = []
        for subDict in wwaAreaDictList:
            hazardType = subDict["hazardType"]
            productRegion = subDict["productRegion"]
            selectedHazardType = self.isHazardTypeAbleToBeCreated(hazardType, self.selectedHazardTypes)
            selectedProductRegion = productRegion in self.selectedRegionAbbreviations
            # Hazard event type and product region selected to be created
            if selectedHazardType and selectedProductRegion:
                newHazardEvent = self.buildNewHazardEvent(hazardType, subDict["geometry"],
                                                          productRegion, self.physicalEvent,
                                                          self.practice, subDict["hazardAttributes"])
                newEventSet.add(newHazardEvent)
            else:
                if not selectedHazardType:
                    omittedHazardTypes.append(hazardType)
                elif not selectedProductRegion:
                    omittedProductRegions.append(productRegion)

        if omittedHazardTypes:
            omittedTypes = self.tpc.joinStringsWithOxfordComma(omittedHazardTypes)
            self.trecsExecInfo.appendToTrace(f"Hazard Event(s) will NOT be created for {omittedTypes}.\n"
                                             "These hazard types were not selected in the T-RECS execution dialog.")
        if omittedProductRegions:
            omittedRegions = self.tpc.joinStringsWithOxfordComma(omittedProductRegions)
            self.trecsExecInfo.appendToTrace(f"Hazard Event(s) will NOT be created for {omittedRegions}.\n"
                                             "These product regions were not selected in the T-RECS execution dialog.")
        return newEventSet

    def summarizeUserMessages(self, newEventSet):
        '''
        @summary: Concatenate all user messages from the trecsExecInfo and attach it to the result
        eventSet as the "resultsMessage" attribute
        @param newEventSet: The eventSet to be returned
        @return: An updated newEventSet
        '''
        # Remember if we do not like the format of the getExecSummary(), you can
        # make your own phyEvent summary instead (adding strings to totalUserMsg)
        # and then just append trecsExecInfo.getTrace()
        totalUserMsg = ""
        for idx, userMsg in enumerate(self.trecsExecInfo.getExecSummary()):
            totalUserMsg += f"{userMsg}\n"

        newEventSet.addAttribute("resultsMessage", totalUserMsg)
        return newEventSet

    def isEarthquakeFelt(self):
        '''
        @summary: If not in auto test mode, input prompt for the user to specify if the earthquake
        was likely felt. If we are in test mode, then return true.
        @return: Boolean
        '''
        if self.isAutoTest:
            return True
        msg = "Was the earthquake likely felt?"
        return DisplayMessageDialog.openQuestion(self.MESSAGE_DIALOG_TITLE, msg)

    def isDangerLikely(self):
        '''
        @summary: If not in auto test mode, input prompt for the user to specify if danger is
        expected. If we are in test mode, then return true.
        @return: Boolean
        '''
        if self.isAutoTest:
            return True
        msg = "Is danger expected?"
        return DisplayMessageDialog.openQuestion(self.MESSAGE_DIALOG_TITLE, msg)

    def isReasonToExpectTsunami(self):
        '''
        @summary: If not in auto test mode, input prompt for the user to specify if the tsunami
        is expected to hit Alaska or Canada. If we are in test mode, then return true.
        @return: Boolean
        '''
        if self.isAutoTest:
            return True
        msg = ("Is there a reason to expect a tsunami impacting Alaska or Canada\n"
               "(e.g., very high magnitude, reports of wave)?")
        return DisplayMessageDialog.openQuestion(self.MESSAGE_DIALOG_TITLE, msg)

    def isHawaiiTsunamiWatch(self):
        '''
        @summary: If not in auto test mode, input prompt for the user to specify if Hawaii should
        be put into a tsunami watch (TS.A). If we are in test mode, then return true.
        @return: Boolean
        '''
        if self.isAutoTest:
            return True
        msg = ("No RIFT forecast exists (yet). \n"
               "At a minimum, a potential TS.S for Hawaii will be created.\n"
               "Should this be a TS.A (Watch) for Hawaii instead?")
        return DisplayMessageDialog.openQuestion(self.MESSAGE_DIALOG_TITLE, msg)

    def recommendEvent(self, productRegion, hazardType, hazardGeometry=None, hazardAttributes={}):
        '''
        @summary: Creates an event dictionary containing a hazard type, geometry, and
        product region
        @param productRegion: The product region where this event will be located (e.g., Hi)
        @param hazardType: The hazard type (e.g., TS.W)
        @param hazardGeometry: An optional hazard event geometry. If a geometry is not provided
        then create one using the self.trecsUtils.generalEventGeometry() method
        @return: Dictionary
        '''
        if not hazardGeometry:
            hazardGeometry = self.convertPhysicalEventPointToPolygon(5)
        return self.agu.createTsunamiEventDict(hazardType, hazardGeometry, productRegion,
                                               hazardAttributes)

    def createEventDictsByDistanceCriteria(self, criteriaDict):
        '''
        @summary: Given a dictionary of distance criteria ordered from most significant to least
        significant product type, build a set of potential hazard events for each type
        @param criteriaDict: A dictionary with a key being the hazard type and the value being a
        tuple defining a minimum and maximum distance (in km)
        Example: {"TS.W": [0, 500], "TS.Y": [500, 1000]}
        @return: A list of dictionaries with each dictionary representing a hazard event to create
        '''
        tsunamiEventDicts = []
        usedBrkptSegNames = []
        for hazardType in criteriaDict:
            minDistanceInKm, maxDistanceInKm = criteriaDict[hazardType]
            tsunamiEventDicts.extend(self.createEventDictsByDistanceRadius(minDistanceInKm,
                                                                           maxDistanceInKm,
                                                                           usedBrkptSegNames,
                                                                           None, hazardType))

        return tsunamiEventDicts

     # May be non-continuous
    def createEventDictsByBrkptSegs(self, hazardType, brkPtSegQueryResults):
        '''
        @summary: Creates a list of hazard events of the given hazard type and product region,
        and uses the given brkPtSegQueryResults to determine the hazard area.
        Each hazard's geometry consists of a continuous set of breakpoint segments determined by
        sorting the brkPtSegQueryResults by breakpoint number, and grouping them by continuous
        breakpoint number sequences. Then one hazard event is created/returned for each continuous
        number sequence.
        @param hazardType: The kind of hazard events to create
        @param brkPtSegQueryResults: The breakpoint segments to use as hazard area(s)
        @return: List of hazard event Dictionaries
        '''
        tsunamiEventDicts = []

        if brkPtSegQueryResults is None:
            return tsunamiEventDicts
        # Separate the query results by productRegion first
        brkPtSegQueryResultsByProductRegion = self.agu.organizeBreakPointSegmentsByProductRegion(brkPtSegQueryResults)

        # For each productRegion, sort the query results by breakpoint segment number first
        for productRegion in brkPtSegQueryResultsByProductRegion:
            brkPtSegQueryResults = brkPtSegQueryResultsByProductRegion[productRegion]
            contiguousSegmentsList = self.agu.orderBreakPointSegmentsByBreakPointNumber(brkPtSegQueryResults)
            for resultsList in contiguousSegmentsList:
                locationNames = self.amu.getNamesFromQueryResults(resultsList)
                unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(resultsList)
                attrDict = {
                    "hazardLocations": locationNames,
                    "wwaLocationCoverage": "segmentAreas"
                    }
                tsunamiEventDicts.append(self.agu.createTsunamiEventDict(hazardType,
                                                                         unionedGeometry,
                                                                         productRegion,
                                                                         attrDict))

        return tsunamiEventDicts

    def createEventDictsByClosestBreakPoint(self, productRegionAbbrev, hazardType):
        '''
        @summary: Collect all break points
        @param productRegionAbbrev: The product region abbreviation (e.g., AkBcWc)
        @param hazardType: The proposed hazard type to create
        @return: List of dictionaries
        '''
        resultsList = []
        breakPointsQueryResults = self.amu.getBreakPointsByProductRegion(productRegionAbbrev)
        minDistanceKm = 99999999
        closestResult = []
        for queryResult in breakPointsQueryResults:
            breakPointGeometry = queryResult.getGeometry()
            breakPointLat = breakPointGeometry.y
            breakPointLon = breakPointGeometry.x
            distanceKm = self.geomUtils.getDistanceBetweenPointsInKm(self.latitude, self.longitude,
                                                                     breakPointLat, breakPointLon)
            if distanceKm < minDistanceKm:
                minDistanceKm = distanceKm
                closestResult = [queryResult]
        if closestResult:
            resultsList = self.createEventDictsByBreakPointQueryResults(closestResult, [],
                                                                        [productRegionAbbrev],
                                                                        hazardType)
        return resultsList

    def createEventDictsByDistanceRadius(self, minRadiusKm, maxRadiusKm, usedBrkptSegNames,
                                         legalProductRegions, hazardType,
                                         includeEntireProductRegionForPTWC=True):
        '''
        @summary: Creates a list of hazard events of the given hazard type, and product region.
        Hazard area is determined by querying the breakpoints table for those that intersect a
        circle from self.lat/lon with radius minRadius to maxRadius. Then neighboring breakpoint
        *segments* are queried and used for the hazard area. Breakpoint segments found that are
        already in usedBrkptSegNames are omitted. New breakpoint segments used as hazard area(s)
        are added, in place, to the usedBrkptSegNames list to later avoid hazard area conflicts.
        @param minRadiusKm: The minimum radius (in km)
        @param maxRadiusKm: The maximum radius (in km)
        @param usedBrkptSegNames: The break point segments list, by name, for those that should be
        omitted from new hazard areas. NOTE that this list gets modified in place, where new
        breakpoint segments used to create hazard areas are added to this list.
        @param legalProductRegions An optional string or list of strings to restrict the
        productRegions of the results
        @param hazardType: The kind of hazard events to create
        @param includeEntireProductRegionForPTWC: For PTWC, we typically include brkpt segments for the entire product
        region, eg Hawaii. But for the TMT, maybe we just want one or two islands when using the distance or time radius.
        @return: List of hazard event Dictionaries
        '''
        resultsList = []
        breakPointsQueryResults = self.amu.getBreakPointsWithinDistanceRangeFromPoint(self.latitude,
                                                                                      self.longitude,
                                                                                      minRadiusKm,
                                                                                      maxRadiusKm,
                                                                                      self.siteID,
                                                                                      True, True)
        if breakPointsQueryResults:
            resultsList = self.createEventDictsByBreakPointQueryResults(breakPointsQueryResults,
                                                                        usedBrkptSegNames,
                                                                        legalProductRegions,
                                                                        hazardType,
                                                                        includeEntireProductRegionForPTWC)
        return resultsList

    def createEventDictsByBreakPointQueryResults(self, breakPointsQueryResults, usedBrkptSegNames,
                                                 legalProductRegions, hazardType,
                                                 includeEntireProductRegionForPTWC=True):
        '''
        @summary:
        @param breakPointsQueryResults: A list of MapsDatabaseAccessor query results
        @param usedBrkptSegNames: The break point segments list, by name, for those that should be
        omitted from new hazard areas. NOTE that this list gets modified in place, where new
        breakpoint segments used to create hazard areas are added to this list.
        @param legalProductRegions An optional string or list of strings to restrict the
        productRegions of the results
        @param hazardType: The kind of hazard events to create
        @param includeEntireProductRegionForPTWC: For PTWC, we typically include brkpt segments for the entire product
        region, eg Hawaii. But for the TMT, maybe we just want one or two islands when using the distance or time radius.
        @return: List of dictionaries
        '''
        # For PTWC, we are lighting up all break point segments in a matching procedural region
        breakPointSegmentResults = []
        if not breakPointsQueryResults:
            return []
        if self.siteID == "PTWC":
            if includeEntireProductRegionForPTWC:
                regionsToProcess = []
                for queryResult in breakPointsQueryResults:
                    region = self.alu.getProceduralRegionByBreakPointNumber(queryResult)
                    if region and region not in regionsToProcess:
                        regionsToProcess.append(region)
                # Get all break point segments for the regions to process
                breakPointSegmentResults = self.agu.getAllBreakPointSegmentsByProductRegionNames(regionsToProcess)
            else:
                # Get all break point names meeting the distance criteria
                breakPointNames = self.amu.getNamesFromQueryResults(breakPointsQueryResults)
                # Get +/- 1 break point beyond the current break points
                breakPointSegmentNames = self.amu.getExtendedBreakPointSegmentNames(breakPointNames)
                if breakPointSegmentNames:
                    breakPointSegmentResults = self.amu.getBreakPointSegmentsBySegmentNames(breakPointSegmentNames)
        else:
            # Get all break point names meeting the distance criteria
            breakPointNames = self.amu.getNamesFromQueryResults(breakPointsQueryResults)
            # Get +/- 1 break point beyond the current break points
            breakPointSegmentNames = self.amu.getExtendedBreakPointSegmentNames(breakPointNames)
            if breakPointSegmentNames:
                breakPointSegmentResults = self.amu.getBreakPointSegmentsBySegmentNames(breakPointSegmentNames)

        '''
        Subset the break point segments to those that have:
        1) Not already been used
        2) Are part of the legal product regions list (if defined)
        '''
        breakPointSegmentSubsetResults = []
        usedNamesToAdd = []
        for result in breakPointSegmentResults:
            bpName = self.amu.getStringFromQueryResult(result, "name")
            prName = self.amu.getStringFromQueryResult(result, HazardConstants.PRODUCT_REGION_ATTR_NAME)
            if ((bpName not in usedBrkptSegNames) and
                (not legalProductRegions or prName in legalProductRegions)):
                breakPointSegmentSubsetResults.append(result)
                usedNamesToAdd.append(bpName)

        tsunamiEventDicts = []
        if breakPointSegmentSubsetResults:
            # Create tsunamiEventDicts for all of these subsets
            tsunamiEventDicts.extend(self.createEventDictsByBrkptSegs(hazardType,
                                                                      breakPointSegmentSubsetResults))
            usedBrkptSegNames.extend(usedNamesToAdd)
        return tsunamiEventDicts

    def createEventDictsByTimeRadius(self, currentTime, travelTimeInHrs, timeOfArrivalForecast,
                                     usedBrkptSegNames, legalProductRegions, hazardType,
                                     includeEntireProductRegionForPTWC=True):
        '''
        @summary: Creates a list of hazard events of the given hazard type, and product region.
        Hazard area is determined by querying the breakpoint segment table (for the productRegion)
        for those that intersect forecast points within the given arrival time frame (currentTime +
        travelTimeInHrs). Breakpoint segments found that are already in usedBrkptSegNames are
        omitted. New breakpoint segments used as hazard area(s) are added, in place, to the
        usedBrkptSegNames list to later avoid hazard area conflicts
        @param currentTime: the origin time of the physical event
        @param travelTimeInHrs: Hours of travel time used to determine if arrival time(s) fall into
        the window
        @param timeOfArrivalForecast to use for the arrival times
        @param hazardType: The kind of hazard events to create
        @param legalProductRegions An optional string or list of strings to restrict the productRegions of the results
        @param usedBrkptSegNames: The breakpoint segments list, by name, for those that should be omitted from new hazard
        areas. NOTE that this list gets modified in place, where new breakpoint segments used to create hazard areas are
        added to this list.
        @param includeEntireProductRegionForPTWC: For PTWC, we typically include brkpt segments for the entire product
        region, eg Hawaii. But for the TMT, maybe we just want one or two islands when using the distance or time radius.
        @return: List of hazard event Dictionaries
        '''

        # Get all break point segments within some user-defined time range
        brkPtSegQueryResults = self.agu.getBreakPointSegmentsWithinTimeRange(currentTime,
                                                                             travelTimeInHrs,
                                                                             timeOfArrivalForecast,
                                                                             self.siteID,
                                                                             legalProductRegions)

        # No segments found so return an empty list
        if not brkPtSegQueryResults:
            return []

        breakPointSegmentSubsetResults = []
        usedNamesToAdd = []

        # For PTWC, we are lighting up all break point segments if a matching procedural region
        if self.siteID == "PTWC":
            allBreakPointSegmentResults = []
            if includeEntireProductRegionForPTWC:
                regionsToProcess = []
                for queryResult in brkPtSegQueryResults:
                    region = self.alu.getProceduralRegionByBreakPointSegmentState(queryResult)
                    if region and region not in regionsToProcess:
                        regionsToProcess.append(region)

                # Get all break point segments for the regions to process
                allBreakPointSegmentResults = self.agu.getAllBreakPointSegmentsByProductRegionNames(regionsToProcess)
            else:
                allBreakPointSegmentResults = brkPtSegQueryResults
            '''
            Subset the break point segments to those that have:
            1) Not already been used
            2) Are part of the legal product regions list (if defined)
            '''

            for result in allBreakPointSegmentResults:
                bpName = self.amu.getStringFromQueryResult(result, "name")
                prName = self.amu.getStringFromQueryResult(result, HazardConstants.PRODUCT_REGION_ATTR_NAME)
                if (bpName not in usedBrkptSegNames) and (not legalProductRegions or prName in legalProductRegions):
                    breakPointSegmentSubsetResults.append(result)
                    usedNamesToAdd.append(bpName)
        # For NTWC, we are lighting up only the matching break point segments that have not already been used
        else:
            for queryResult in brkPtSegQueryResults:
                bpName = self.amu.getStringFromQueryResult(queryResult, "name")
                if bpName not in usedBrkptSegNames:
                    breakPointSegmentSubsetResults.append(queryResult)
                    usedNamesToAdd.append(bpName)

        tsunamiEventDicts = []
        if breakPointSegmentSubsetResults:
            # Create tsunamiEventDicts for all of these subsets
            tsunamiEventDicts.extend(self.createEventDictsByBrkptSegs(hazardType,
                                                                      breakPointSegmentSubsetResults))
            usedBrkptSegNames.extend(usedNamesToAdd)
        return tsunamiEventDicts

    def getCurrentCAVETime(self):
        '''
        @summary: Returns the CAVE system time that is shown in the clock on the bottom of CAVE
        @return: A Java Date object
        '''
        return self.physicalEvent.getRefTime()
        # return TimeUtil.simulatedTime() # TO USE THE CAVE CLOCK

    def createWarningToSomeRangeAndWatchForRemainingAOR(self, maxRangeKm, productRegion):
        '''
        @summary: Create a Tsunami Warning (TS.W) for some distance from the physical event center
        and a Tsunami Watch (TS.A) for the remainder of the AOR
        @param maxRangeKm: The maximum range (in km) where the TS.W will be in effect
        @param productRegion: The product region where this event will be located (e.g., AkBcWc)
        @return: List of hazard event Dictionaries
        '''
        wwaDictList = []
        usedBrkptSegNames = []
        # Build a TS.W for all break point segments within 1000 km of the physical event center
        wwaDictList = self.createEventDictsByDistanceRadius(0, maxRangeKm, usedBrkptSegNames,
                                                            [productRegion], "TS.W")
        # Now do a TS.A for the remainder of the AOR
        aorRemainderQueryResults = self.agu.getAllOtherBreakPointSegmentsInProductRegion(productRegion,
                                                                                         usedBrkptSegNames,
                                                                                         True)
        contiguousResultsList = self.agu.orderBreakPointSegmentsByBreakPointNumber(aorRemainderQueryResults)
        for segmentResultsList in contiguousResultsList:
            breakPointSegmentNames = self.amu.getNamesFromQueryResults(segmentResultsList)
            unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(segmentResultsList)
            attrDict = {
                "hazardLocations": breakPointSegmentNames,
                "wwaLocationCoverage": "segmentAreas"
                }
            wwaDictList.append(self.recommendEvent(productRegion, "TS.A", unionedGeometry,
                                                   attrDict))
        return wwaDictList

    def createWarningToVariableHoursAndWatchForRemainingAOR(self, productRegion, numberOfHours):
        '''
        @summary: Creates a list of event dictionaries containing a hazard type, geometry, and
        product region
        @param productRegion: The product region where this event will be located (e.g., AkBcWc)
        @param numberOfHours: The number of hours from the physical event to produce a
        warning (e.g., 3)
        @return: List of hazard event Dictionaries
        '''
        wwaAreaDictList = []
        warningBreakPointSegments = self.agu.getBreakPointSegmentsWithinTimeRange(self.getCurrentCAVETime(),
                                                                                  numberOfHours,
                                                                                  self.timeOfArrivalForecast,
                                                                                  self.siteID,
                                                                                 [productRegion])
        warningSegmentNames = []
        if not warningBreakPointSegments:
            self.trecsExecInfo.appendToTrace("INFO: No stations within the timeOfArrivalForecast "
                                             f"had <= {numberOfHours} hour arrival times. As a "
                                             "result, no hazard area was determined for a "
                                             "Tsunami Warning (TS.W).")
        else:
            warningSegmentNames = self.amu.getNamesFromQueryResults(warningBreakPointSegments)
            contiguousWarningResultsList = self.agu.orderBreakPointSegmentsByBreakPointNumber(warningBreakPointSegments)
            for segmentList in contiguousWarningResultsList:
                breakPointSegmentNames = self.amu.getNamesFromQueryResults(segmentList)
                unionedBkptSegmentsGeom = self.amu.getUnionedGeometryFromQueryResults(segmentList)
                attrDict = {
                    "hazardLocations": breakPointSegmentNames,
                    "wwaLocationCoverage": "segmentAreas"
                    }
                wwaAreaDictList.append(self.recommendEvent(productRegion, "TS.W", unionedBkptSegmentsGeom,
                                                           attrDict))

        aorRemainderQueryResults = self.agu.getAllOtherBreakPointSegmentsInProductRegion(productRegion,
                                                                                         warningSegmentNames,
                                                                                         True)
        contiguousWatchResultsList = self.agu.orderBreakPointSegmentsByBreakPointNumber(aorRemainderQueryResults)
        for segmentResultsList in contiguousWatchResultsList:
            breakPointSegmentNames = self.amu.getNamesFromQueryResults(segmentResultsList)
            unionedGeometry = self.amu.getUnionedGeometryFromQueryResults(segmentResultsList)
            attrDict = {
                    "hazardLocations": breakPointSegmentNames,
                    "wwaLocationCoverage": "segmentAreas"
                    }
            wwaAreaDictList.append(self.recommendEvent(productRegion, "TS.A", unionedGeometry,
                                                       attrDict))
        return wwaAreaDictList

    def queryThreatDatabaseForKnownEvents(self):
        '''
        @summary: Access the ThreatDB.py and determine if the physical event matches any known
        event in threat database source regions and its associated attributes
        @return: A list of dictionaries with each entry containing the hazard type, geometry, and
        product region name for a single hazard event to be created
        @todo: This method needs to be able to handle multiple product regions (i.e., when PTWC
        configures its Threat DB)
        '''
        productRegion = self.lookupProductRegions(self.procRegion)
        if isinstance(productRegion, list) and len(productRegion) == 1:
            productRegion = productRegion[0]
        return ThreatDB.ThreatDB().queryThreatDBForKnownEvents(self.physicalEvent, productRegion,
                                                               self.siteID)

    def queryThreatDatabase(self, productRegion):
        '''
        @summary: Access the ThreatDB.py and determine if the physical event matches any threat
        database source regions and its associated attributes
        @param productRegion: The product region
        @return: A list of dictionaries with each entry containing the hazard type, geometry, and
        product region name for a single hazard event to be created
        '''
        return ThreatDB.ThreatDB().queryThreatDB(self.physicalEvent, productRegion, self.siteID)

    def parseHazardType(self, hazardType):
        '''
        @summary: Parse hazard type into three parts: [phen, sig, subType]. The latter may be None
        since the specified hazard type may only have the first two parts.
        @param hazardType: Hazard type string (e.g., TS.W).
        @return Tuple consisting of the two or three parts of the hazard type.
        '''
        hazardTypeSplit = [None, None, None]
        # Split hazard type by each period
        hazardTypeSlice = hazardType.split(".")
        for partIndex in range(len(hazardTypeSlice)):
            hazardTypeSplit[partIndex] = hazardTypeSlice[partIndex]
        return hazardTypeSplit

    def buildNewHazardEvent(self, hazardType, hazardGeometry, productRegion, physicalEvent,
                            practice, hazardAttributes={}):
        '''
        @summary: Method to create a new hazard event
        @param hazardType: A string representation of the hazard type (e.g., TS.W)
        @param hazardGeometry: The geometry as a shapely object
        @param productRegion: The product region name (e.g., AkBcWc)
        @param physicalEvent: The physical event object
        @param practice: A boolean determining whether CAVE is in practice mode (True) or not (False)
        @param hazardAttributes: An optional dictionary containing the attribute name (key) and the
        attribute value (value) (e.g., {"tisType": "tisHigh"})
        @return: A hazard event
        '''
        hazardEvent = EventFactory.createEvent(practice)
        for attributeName in hazardAttributes:
            hazardEvent.set(attributeName, hazardAttributes[attributeName])
        phen, sig, subType = self.parseHazardType(hazardType)
        hazardEvent.setPhenomenon(phen)
        hazardEvent.setSignificance(sig)
        hazardEvent.setSubType(subType)
        advancedGeometry = self.geomUtils.convertFromShapelyToAdvancedGeometry(hazardGeometry)
        hazardEvent.setGeometry(advancedGeometry)

        # This is how we invoke the CG predefined hazard areas, though we are not doing
        # hazardEvent.setHazardGeometryMode("predefinedUneditableWithHazardArea")
        # hazardEvent.setPredefinedHazardArea(hazardAreaDicts910)

        hazardEvent.setStatus("POTENTIAL")
        hazardEvent.set("productRegion", productRegion)

        self.populateOtherHazardAttributes(hazardEvent, physicalEvent)
        if hazardEvent.getHazardType() in ["TS.A", "TS.W", "TS.Y"]:
            self.populateAdditionalWWA_MessageAttributes(hazardEvent, physicalEvent, productRegion)
        if hazardEvent.getHazardType() == "TS.ThreatMessage":
            self.populateAdditionalThreatMessageAttributes(hazardEvent, physicalEvent)
        elif hazardEvent.getHazardType() == "TS.ObservatoryMessage":
            self.populateAdditionalObservatoryMessageAttributes(hazardEvent, physicalEvent)

        return hazardEvent

    def populateOtherHazardAttributes(self, hazardEvent, physicalEvent):
        '''
        @summary: Define and set other tsunami-specific attributes to the hazard event
        @param hazardEvent: The hazard event being created
        @param physicalEvent: The physical event used to create the hazard event
        @return: NoneType; the hazard event is updated in memory
        '''
        # set hazard event to be part of national mode
        hazardEvent.set("national", True)

        # Set physical event-specific attributes
        physicalEventType = physicalEvent.getEventType().getLabel()
        physicalEventCustomId = physicalEvent.getCustomId()
        hazardEvent.set("physicalEventType", physicalEventType)
        hazardEvent.set("customId", physicalEventCustomId)
        hazardEvent.set("physicalEventId", f"{physicalEventCustomId}-{physicalEventType}")

    def populateAdditionalWWA_MessageAttributes(self, hazardEvent, physicalEvent, productRegion):
        '''
        @summary: Define and set other tsunami-specific attributes to a watch/warning/advisory
        hazard event
        @param hazardEvent: The hazard event being created
        @param physicalEvent: The physical event used to create the hazard event
        @param productRegion: The product region abbreviation (e.g., AkBcWc)
        @return: NoneType; the hazard event is updated in memory
        '''
        physicalEventCustomId = physicalEvent.getCustomId()
        suffix = f"TSU_{physicalEventCustomId}_{productRegion}"
        # Pass forecast info specified in the defineDialog into the hazard event
        forecastList = [self.timeOfArrivalForecast, self.amplitudeForecast]
        attributeList = ["timeOfArrivalForecast", "amplitudeForecast"]
        for i in range(len(forecastList)):
            tsunamiForecast = forecastList[i]
            if tsunamiForecast:
                forecastType = tsunamiForecast.getFcstType().getLabel()
                runTimeStr = str(tsunamiForecast.getForecastRunTime())
                choiceLabel = f"{forecastType.ljust(7)} - {runTimeStr}"
            else:
                choiceLabel = "No Selection"
            hazardEvent.set(f"{attributeList[i]}_{suffix}", choiceLabel)

    def populateAdditionalThreatMessageAttributes(self, hazardEvent, physicalEvent):
        '''
        @summary: Define and set other tsunami-specific attributes to a threat
        message hazard event
        @param hazardEvent: The hazard event being created
        @param physicalEvent: The physical event used to create the hazard event
        @return: NoneType; the hazard event is updated in memory
        '''
        # Pass forecast info specified in the defineDialog into the hazard event
        forecastList = [self.timeOfArrivalForecast, self.amplitudeForecast]
        attributeList = ["timeOfArrivalForecast", "amplitudeForecast"]
        for i in range(len(forecastList)):
            tsunamiForecast = forecastList[i]
            if tsunamiForecast:
                forecastType = tsunamiForecast.getFcstType().getLabel()
                runTimeStr = str(tsunamiForecast.getForecastRunTime())
                choiceLabel = f"{forecastType.ljust(7)} - {runTimeStr}"
            else:
                choiceLabel = "No Selection"
            hazardEvent.set(attributeList[i], choiceLabel)

    def populateAdditionalObservatoryMessageAttributes(self, hazardEvent, physicalEvent):
        '''
        @summary: Define and set other tsunami-specific attributes to an observatory
        message hazard event
        @param hazardEvent: The hazard event being created
        @param physicalEvent: The physical event used to create the hazard event
        @return: NoneType; the hazard event is updated in memory
        '''
        physicalEventType = physicalEvent.getEventType().getLabel()
        hazardEvent.set("createdByOMT", False)
        hazardEvent.set("originTime", physicalEvent.getRefTime().getTime())
        hazardEvent.set("originLongitude", physicalEvent.getLongitude())
        hazardEvent.set("originLatitude", physicalEvent.getLatitude())
        # The following field is related with physical event type
        if physicalEventType == "Seismic":
            hazardEvent.set("magnitude", round(physicalEvent.getData().getPrefMagnitude(), 1))
            hazardEvent.set("magnitudeType", physicalEvent.getData().getPrefMagnitudeType().getLabel())
            hazardEvent.set("originDepth", physicalEvent.getData().getDepth())
            hazardEvent.set("numStationAverage", physicalEvent.getData().getNumStations())
        elif physicalEventType in ["Volcanic", "Landslide"]:
            hazardEvent.set("peName", physicalEvent.getName())

    '''
    Methods solely used in TsunamiRecommender.py
    '''

    def physicalEventLabelText_TRECS(self):
        '''
        @summary: The physical event label provided to the user with the Tsunami Recommender
        @return: String
        '''
        return f"Select information for {self.physicalEventType} Event ID {self.physicalEventID}:"

    def getAllRegions(self):
        '''
        @summary: Assemble all of the Atlantic and Pacific Ocean regions into a single list
        @return: List
        '''
        return self.pacificProductRegions() + self.atlanticProductRegions()

    def atlanticProductRegions(self):
        '''
        @summary: The product region(s) to be analyzed in the Atlantic Ocean
        @return: List
        '''
        if self.siteID == "NTWC":
            return ["EcGc"]
        else:  # PTWC
            return ["Pr", "Car"]

    def pacificProductRegions(self):
        '''
        @summary: The product region(s) to be analyzed in the Pacific Ocean
        @return: List
        '''
        if self.siteID == "NTWC":
            return ["AkBcWc"]
        else:  # PTWC
            return ["Hi", "Gu", "As", "Pac"]

    def getProductRegionAbbreviations(self, onlyGetPossibleRegions=False):
        '''
        @summary: Get a list of product region labels
        @param onlyGetPossibleRegions: Boolean that determines if all possible regions in multiple
        ocean basins should be returned (False) or only in the ocean basin where the physical event
        resides (True)
        @return: List of strings (e.g., ["Hi", "Gu", "As", "Pac"])
        '''
        if onlyGetPossibleRegions:
            possibleProductRegions = self.lookupProductRegions(self.procRegion)
        else:
            possibleProductRegions = self.getAllRegions()
        return possibleProductRegions

    def getProductRegionLabel(self, regionAbbreviation):
        '''
        @summary: Given a product region label (e.g., "Hi"), build a
        label for it that will go in the tool defineDialog() windows
        @param regionAbbreviation: A string of a region abbreviation (e.g., "Hi")
        @return: String (e.g., "Hawaii (Hi)")
        '''
        fullRegionName = self.alu.getProductRegionNameFromAbbreviation(regionAbbreviation)
        return f"{fullRegionName} ({regionAbbreviation})"

    def getProductRegionLabels(self, onlyGetPossibleRegions=False):
        '''
        @summary: Create a list of labels corresponding to the possible product regions for this site
        @param onlyGetPossibleRegions: Boolean that determines if all possible regions in multiple
        ocean basins should be returned (False) or only in the ocean basin where the physical event
        resides (True)
        @return: A list of strings
        '''
        labelList = []
        productRegionsAbbrevs = self.getProductRegionAbbreviations(onlyGetPossibleRegions)
        for regionAbbrev in productRegionsAbbrevs:
            label = self.getProductRegionLabel(regionAbbrev)
            labelList.append(label)
        return labelList

    def productRegionsMegawidget(self):
        '''
        @summary: Builds the regionalSelections Group megawidget
        @return: A dictionary of megawidget properties
        '''
        # Get all possible product regions for this office
        possibleRegions = self.getProductRegionAbbreviations(False)
        # Select the ones based on the physical event location.
        # But if we're near both basins, select them all.
        selectedRegions = []
        if self.isInCentralAmericaDualProcRegion() or self.isInSouthAmericaDualProcRegion():
            selectedRegions = self.getProductRegionAbbreviations(False)
        else:
            selectedRegions = self.getProductRegionAbbreviations(True)

        if not selectedRegions:
            selectedRegions = possibleRegions
        # Build a nested list of Checkboxes
        choiceList = []
        for regionAbbrev in possibleRegions:
            choiceDict = {
                "identifier": f"{regionAbbrev}",
                "displayString": self.getProductRegionLabel(regionAbbrev),
                "detailFields": [self.getMessageTypeMegawidget(regionAbbrev)],
                }
            choiceList.append(choiceDict)
        # Return megawidget
        return {
            "fieldType":"CheckBoxes",
            "fieldName": "regionalSelections",
            "label": "Select product regions to run this tool on:",
            "choices": choiceList,
            "values": selectedRegions
            }

    def getMessageTypeMegawidget(self, keyPrefix):
        '''
        @summary: Build a set of radio buttons that defines whether the
        user wants to issue a initial message or a follow-up message
        @param keyPrefix: A prefix added to the field name to distinguish
        the fields between different product regions
        @return: Dictionary of megawidget properties
        '''
        # Get list of possible choices
        choiceList = [
                {"identifier": "initialMessage", "displayString": "Initial Message"},
                {"identifier": "followupMessage", "displayString": "Follow-up Message"},
                ]
        # Determine whether to select initial or follow-up based on whether non-TTT
        # amplitude forecasts exist for this physical event
        selectionIndex = 0
        if self.doesAmplitudeForecastExist() or self.doSeaLevelObsExist():
            selectionIndex = 1
        # Return megawidget dictionary
        return {
            "fieldType": "RadioButtons",
            "fieldName": f"{keyPrefix}_MessageType",
            "choices": choiceList,
            "values": choiceList[selectionIndex]["identifier"],
            }

    def doesAmplitudeForecastExist(self):
        '''
        @summary: Check if a non-TTT forecast exists for this physical event
        @return: Boolean
        '''
        nonTravelTimeModels = [fk for fk in self.tsunamiForecastInfoDict
                               if self.tsunamiForecastInfoDict[fk]["forecastType"].strip() != "TTT"]
        if nonTravelTimeModels:
            return True
        return False

    def doSeaLevelObsExist(self):
        '''
        @summary: Check if sea level observations exist for this physical event
        @return: Boolean
        '''
        slobs = SeaLevelObsDao.getInstance().getSeaLevelObservations(self.physicalEventID, None)
        if slobs.size() != 0:
            return True
        return False

    def amplitudeFcstSelectedOrSLObsExist(self):

        if (self.amplitudeForecast is not None and
            self.amplitudeForecast.getFcstType().getLabel().strip() != "TTT"):
            return True
        slobs = SeaLevelObsDao.getInstance().getSeaLevelObservations(self.physicalEventID, None)
        if slobs.size() != 0:
            return True

        return False

    def hazardTypesMegawidget(self):
        '''
        @summary: Builds the hazardTypeSelections CheckList megawidget
        @return: A dictionary of megawidget properties
        '''
        choiceList = self.getHazardTypesToRecommend()
        defaultList = self.defaultHazardTypesToRecommend()
        valueList = list(set(choiceList) & set(defaultList))
        if not valueList:
            valueList = choiceList
        return {
            "fieldType": "CheckList",
            "fieldName": "hazardTypeSelections",
            "label": "What hazard events would you like to be recommended?",
            "choices": choiceList,
            "values": valueList,
            }

    def isHazardTypeAbleToBeCreated(self, hazardType, hazardTypeLabels):
        '''
        @summary: Is the hazard type that is about to be created selected by the
        forecaster to be created in the hazardTypeSelections megawidget
        @param hazardType: The hazard type (e.g., TS.W)
        @param hazardTypeLabels: A list of hazard type labels selected by the forecaster
        in the defineDialog() hazardTypeSelections megawidget
        Example: ["Tsunami Watch/Warning/Advisory (TS.A/TS.W/TS.Y)"]
        @return: Boolean
        '''
        for hazardTypeLabel in hazardTypeLabels:
            if hazardType in hazardTypeLabel:
                return True
        return False

    def forecastSelectionLabelMegawidget(self):
        '''
        @summary: Builds the forecastSelectionLabel Label megawidget
        @return: A dictionary of megawidget properties
        '''
        return {
            "fieldType": "Label",
            "fieldName": "forecastSelectionLabel",
            "label": ("Select the forecast runs to use for 'Time of Arrival'\n"
                      "and 'Amplitude' calculations:"),
            }

    def timeOfArrivalMegawidget(self):
        '''
        @summary: Builds the timeOfArrivalSelection ComboBox megawidget
        @return: A dictionary of megawidget properties
        '''
        fieldName = "timeOfArrivalSelection"
        tttForecastChoices = self.getForecastChoicesWithType(self.tsunamiForecastInfoDict,
                                                             "timeOfArrival")
        tttDefaultChoice = ""
        if tttForecastChoices:
            tttDefaultChoice = tttForecastChoices[0]
        widgetDict = {}
        if tttForecastChoices:
            widgetDict = {
                "fieldType": "ComboBox",
                "fieldName": fieldName,
                "label": "Time of Arrival: ",
                "choices": tttForecastChoices,
                "values": tttDefaultChoice,
                "expandHorizontally": True,
                }
        else:
            widgetDict = {
                "fieldType": "HiddenField",
                "fieldName": fieldName,
                "values": "",
                }
        return widgetDict

    def amplitudeSelectionMegawidget(self):
        '''
        @summary: Builds the amplitudeSelection ComboBox megawidget
        @return: A dictionary of megawidget properties
        '''
        fieldName = "amplitudeSelection"
        amplitudeForecastChoices = self.getForecastChoicesWithType(self.tsunamiForecastInfoDict,
                                                                   "amplitude")
        amplitudeDefaultChoice = ""
        if amplitudeForecastChoices:
            amplitudeDefaultChoice = amplitudeForecastChoices[0]
        widgetDict = {}
        if amplitudeForecastChoices:
            widgetDict = {
                "fieldType": "ComboBox",
                "fieldName": fieldName,
                "label": "Amplitude: ",
                "choices": amplitudeForecastChoices,
                "values": amplitudeDefaultChoice,
                "expandHorizontally": True,
                }
        else:
            widgetDict = {
                "fieldType": "HiddenField",
                "fieldName": fieldName,
                "values": "",
                }
        return widgetDict

    def getForecastChoicesWithType(self, tsunamiInfoDict, selectType):
        '''
        @summary: Get the list of forecast choices of the forecast type (timeOfArrival or amplitude)
        @param forecastChoices: The whole list of forecast choices
        @param forecastType: Either timeOfArrival or amplitude
        @return: The list of choices
        '''
        runChoices = []
        for forecastKey in tsunamiInfoDict:
            forecastType = tsunamiInfoDict[forecastKey]["forecastType"].strip()
            if ((selectType == "timeOfArrival" and forecastType in ["TTT", "Hybrid", "Derived"]) or
                (selectType == "amplitude" and forecastType != "TTT")):
                runChoices.append(forecastKey)
        if runChoices:
            runChoices.append("No Selection")
        return runChoices

    def getForecastInfoFromDialogInput(self, dialogInputMap):
        '''
        @summary: Given user selections provided from the defineDialog() window,
        set the self.timeOfArrivalForecast and self.amplitudeForecast from it
        @param dialogInputMap: A dictionary of user-selections from the defineDialog() window
        @return: Updated self.timeOfArrivalForecast and self.amplitudeForecast
        '''
        toaChoice = dialogInputMap.get("timeOfArrivalSelection")
        if toaChoice and toaChoice != "No Selection":
            self.timeOfArrivalForecast = self.getTsunamiForecast(toaChoice)
        ampChoice = dialogInputMap.get("amplitudeSelection")
        if ampChoice and ampChoice != "No Selection":
            self.amplitudeForecast = self.getTsunamiForecast(dialogInputMap.get("amplitudeSelection"))

    def bypassThreatDBMegawidget(self):
        '''
        @summary: CheckBox megawidget that, when checked, will skip checking the ThreatDB
        during the Tsunami Recommender message determination process
        @return: A dictionary of megawidget properties
        '''
        return {
            "fieldType": "CheckBox",
            "fieldName": "bypassThreatDBCheckBox",
            "label": "Bypass Threat Database Lookups",
            "values": False
            }

    def performSurgeryMegawidget(self):
        '''
        @summary: CheckBox megawidget that will checked will combine active and proposed hazard events
        via surgery.
        @return: A dictionary of megawidget properties
        '''
        return {
            "fieldType": "CheckBox",
            "fieldName": "performSurgery",
            "label": "Perform surgery / Combine tool results with active events",
            "values": True
            }

    def getTsunamiForecast(self, userSelectionLabel):
        '''
        @summary: Retrieve the tsunami forecast based on the user selection in the defineDialog()
        window
        @param userSelectionLabel: The selection from the timeOfArrivalSelection or amplitudeSelection
        megawidgets
        @return: A TsunamiForecast object
        '''
        return self.afou.getTsunamiForecastFromLabel(userSelectionLabel, self.tsunamiForecastInfoDict)

    def buildTrecsExecInfo(self):
        '''
        @summary: Establishes the contents of the T-RECS Execution Dialog window that allows a user
        to see what the Tsunami Recommender is recommending for each product region and allows the
        user to nudge it to a different category
        @return: None
        '''

        trecsInfo = TrecsExecInfo(self.physicalEvent)

        allProductRegions = self.procsListDict.keys()

        megaProceduresDict = {}
        selectedProductRegion = None
        for prodReg in allProductRegions:
            procedures = []
            for procDict in self.procsListDict[prodReg]:
                procedure = TrecsExecProcedure(procDict["procName"])
                # SELECT BY PRODUCT REGION!!!!!!
                if "selected" in procDict and procDict["selected"]:
                    procedure.setSelected(True)
                categories = []
                selectedCateg = None
                for catDict in procDict["categories"]:
                    category = TrecsExecCategory(catDict["name"])
                    category.setPythonExecClassname(catDict["pythonExecClassName"])
                    if catDict.get("selected"):
                        selectedCateg = category
                    category.setConditions(catDict.get("conditions", []))
                    category.setActions(catDict.get("actions", []))
                    categories.append(category)
                procedure.setCategories(categories)
                if selectedCateg:
                    procedure.setSelectedCategory(selectedCateg)
                    selectedProductRegion = prodReg
                procedures.append(procedure)
            megaProceduresDict[prodReg] = procedures

        trecsInfo.setProcedures(megaProceduresDict)
        if selectedProductRegion is not None:
            trecsInfo.setSelectedProductRegion(selectedProductRegion)

        return trecsInfo

    def reinitializeTrecsExecInfo(self):
        '''
        @summary: Re-initialize the TrecsExecInfo() instance by:
        1) Clearing the trace log
        2) De-selecting all procedures
        @return: An updated self.trecsExecInfo() in memory
        '''
        self.trecsExecInfo.clearTrace()
        self.trecsExecInfo.deselectAllProcedures()

    def executeCategoryActions(self, selectedCategories):
        '''
        @summary: For all selectedCategories given, this method instantiates the PythonExecClass
        specified by the category, and calls its applyActions() method. Any hazardEventDicts
        created by those calls area added to the returned list of hazardEventDicts.
        @param selectedCategories:
        @return A list of hazardEventDicts
        '''
        wwaAreaDictList = []
        if selectedCategories is not None:
            for category in selectedCategories:
                if category.getPythonExecClassname() is not None:
                    thePythonClassName = category.getPythonExecClassname()
                    klass = self.getTrecsExecClass(thePythonClassName)
                    pyExector = klass(category.getConditions(), category.getActions())
                    wwaAreaDictList.extend(pyExector.applyActions(self))
                    self.executedProcCategories.append(pyExector)
        return wwaAreaDictList

    def handleFollowUpMessageWarning(self):
        '''
        @summary: Message thrown to the user that the Tsunami Recommender only has procedures
        for initial messages and cannot follow-up existing hazard events (for now).
        @return: None
        '''
        self.trecsExecInfo.appendToTrace("No Hazard Events were created for the Physical Event.\n"
                                         "T-RECS only creates HazardEvents\n"
                                         "for *initial* messages, and not follow-up messages, for\n"
                                         "a particular EQ / Product Region.")

    def handleNonSeismicPhysicalEventWarning(self):
        '''
        @summary: Message thrown to the user that the Tsunami Recommender only has procedures
        for Seismic physical events and will not run for other physical event types
        @return: None
        '''
        self.trecsExecInfo.appendToTrace("No Hazard Events were created for the Physical Event.\n"
                                         "T-RECS only has non-ThreatDB procedures for SEISMIC events.")

    def handleNoEventsCreatedWarning(self):
        '''
        @summary: Message thrown to the user that no hazard events were created
        @return: None
        '''
        self.trecsExecInfo.appendToTrace(f"{self.TRACE_BREAK}"
                                         "No Hazard Event(s) were created for the Physical Event.\n"
                                         "Currently, hazard events are only created when there is a\n"
                                         "Threat Database hit or if the EQ occurs in a Procedural Region\n"
                                         "and satisfies the procedural conditions to create a Hazard Event.")

    def isInitialMessage(self, productRegionAbbrev):
        '''
        @summary: Determine whether or not product messages have already been issued for this
        physical event
        @param
        @return: Boolean
        '''
        numMessages = self.agu.getTsunamiMessageCount(self.physicalEventID, self.practice,
                                                      productRegionAbbrev)
        return numMessages == 0

    '''
    Methods solely used in TsunamiMessageTool.py
    '''

    def showNoTimeOfArrivalForecastMessage(self):
        '''
        @summary: Message thrown when no TTT information exists for this physical event
        @return: A DisplayMessageDialog window
        '''
        return DisplayMessageDialog.openWarning("TMT Dialog",
                                                ("There is no TTT information, therefore no time "
                                                 "based TS.WWY can be created."))

    def showInvalidDistanceTimeRadius(self):
        '''
        @summary: Message thrown when less severe hazards are being created over a smaller
        area/closer time of arrival than more severe hazards (e.g., TS.Y out to 500 km, TS.W out
        to 1000 km)
        @return: A DisplayMessageDialog window
        '''
        return DisplayMessageDialog.openWarning("TMT Dialog",
                                                ("Less severe hazards must have distance/time "
                                                 "radii that are GREATER than\nthe radii for more "
                                                 "severe hazards. Please verify distance/time "
                                                 "radius."))

    def physicalEventLabelText_TMT(self):
        '''
        @summary: The physical event label provided to the user with the Tsunami Message Tool
        @return: String
        '''
        return f"For {self.physicalEventType} {self.physicalEventID}, select hazards to be created:"

    def createTsunamiInfoStatDialog(self, choices):
        '''
        @summary: Creates the section of the Tsunami Message Tool to potentially generate
        Tsunami Information Statement (TS.S) hazard events
        @param choices: The possible TS.S choices
        @return: A dictionary of megawidget properties
        '''
        return {
            "fieldType": "Group",
            "fieldName": "tssGroup",
            "fields": [
                {
                    "fieldType": "CheckBoxes",
                    "fieldName": "tsuInfoStat",
                    "label": "Create TS.S for:",
                    "choices": choices,
                    "values": [],
                    }
                ]
            }

    # Common functions for Tsunami Message Tool
    def createTsunamiWarningAdvisoryWatchDialog(self):
        '''
        @summary: Creates the section of the Tsunami Message Tool potentially generate
        Tsunami Warning (TS.W), Tsunami Advisory (TS.Y), and Tsunami Watch (TS.A) hazard events
        @param keyPrefix: The prefix appended to the megawidget identifiers to make them unique
        @param defaultDistanceInKm: The default distance (in km)
        @param defaultTimeInHrs: The default time (in hrs)
        @return: A dictionary of megawidget properties
        '''
        # Get the configurable distances and times
        distTimeDict = self.defaultTMT_DistancesAndTimes()
        return {
            "fieldType": "Group",
            "fieldName": "tswwaGroup",
            "fields": [
                {
                "fieldName": "tsuWWA",
                "fieldType":"CheckBoxes",
                "label": "And/Or create the following radius-based Hazard Events:",
                "choices": [
                    {
                        "identifier": "tsuWarning",
                        "displayString": "Warning (TS.W)",
                        "detailFields": [self.createDistanceTimeDetailField("tsw",
                                                                            distTimeDict["TS.W"]["distanceInKm"],
                                                                            distTimeDict["TS.W"]["timeInHrs"])],
                    },
                    {
                        "identifier": "tsuAdvisory",
                        "displayString": "Advisory (TS.Y)",
                        "detailFields": [self.createDistanceTimeDetailField("tsy",
                                                                            distTimeDict["TS.Y"]["distanceInKm"],
                                                                            distTimeDict["TS.Y"]["timeInHrs"])],
                    },
                    {
                        "identifier": "tsuWatch",
                        "displayString": "Watch (TS.A)",
                        "detailFields": [self.createDistanceTimeDetailField("tsa",
                                                                            distTimeDict["TS.A"]["distanceInKm"],
                                                                            distTimeDict["TS.A"]["timeInHrs"])],
                    },
                    ]
                }
                ]
            }

    def createDistanceTimeDetailField(self, keyPrefix, defaultDistanceInKm, defaultTimeInHrs):
        '''
        @summary: Creates distance and time megawidgets used to potentially generate Tsunami Warning (TS.W),
        Tsunami Advisory (TS.Y), and Tsunami Watch (TS.A) from the Tsunami Message Tool
        @param keyPrefix: The prefix appended to the megawidget identifiers to make them unique
        @param defaultDistanceInKm: The default distance (in km)
        @param defaultTimeInHrs: The default time (in hrs)
        @return: A dictionary of megawidget properties
        '''
        return {
            "fieldType": "RadioButtons",
            "fieldName": f"{keyPrefix}CreateType",
            "choices": [
                {
                    "identifier": f"{keyPrefix}Distance",
                    "displayString": "Distance",
                    "detailFields": [
                        {
                            "fieldType": "IntegerSpinner",
                            "fieldName": f"{keyPrefix}Radius",
                            "minValue": 50,
                            "maxValue": 50000,
                            "values": defaultDistanceInKm,
                            "incrementDelta": 50,
                            "precision": 10
                            },
                        {
                            "fieldType": "Label",
                            "fieldName": f"{keyPrefix}RadiusUnit",
                            "label": "km",
                            },
                        ],
                                },
                {
                    "identifier": f"{keyPrefix}Time",
                    "displayString": "Time      ",
                    "detailFields": [
                        {
                            "fieldType": "IntegerSpinner",
                            "fieldName": f"{keyPrefix}Hour",
                            "minValue": 1,
                            "maxValue": 24,
                            "values": defaultTimeInHrs,
                            "incrementDelta": 1,
                            "precision": 1
                            },
                        {
                            "fieldType": "Label",
                            "fieldName": f"{keyPrefix}TimeUnit",
                            "label": "hr",
                            }
                        ]
                    }
                ],
            }

    def defaultTMT_DistancesAndTimes(self):
        '''
        @summary: The default distances (in km) and times (in hrs) to be
        provided for the Tsunami Warning (TS.W), Tsunami Advisory (TS.Y),
        and Tsunami Watch (TS.A) hazard types
        @return: A dictionary
        '''
        return {
            "TS.W": {
                "distanceInKm": 500,
                "timeInHrs": 3,
                },
            "TS.Y": {
                "distanceInKm": 1000,
                "timeInHrs": 6,
                },
            "TS.A": {
                "distanceInKm": 1500,
                "timeInHrs": 9,
                },
            }

    def createTsunamiTestMessagesDialog(self, commuChoices):
        '''
        @summary: Create the megawidget group with CheckBoxes options for
        creating and issuing test tsunami messages
        @return: A dictionary of megawidget properties
        '''
        return {
            "fieldType": "Group",
            "fieldName": "tsuTestGroup",
            "fields": [
                {
                    "fieldType": "CheckBoxes",
                    "fieldName": "tsuTestMsgs",
                    "label": "Test messages",
                    "choices": [
                        {
                        "identifier": "TS.CommunicationTest",
                        "displayString": "Communication Test",
                        "detailFields": [self.createCommuTestDetailField(commuChoices)],
                        },
                        ]
                    }
                ]
            }

    def createCommuTestDetailField(self, choices):
        '''
        @summary: Create the megawidget group with CheckBoxes options for
        creating and issuing test tsunami messages
        @param choices: The possible TS.CommunicationTest choices
        @return: A dictionary of megawidget properties
        '''
        defaultValues = [c.get("identifier") for c in choices]
        return {
                "fieldType": "CheckBoxes",
                "fieldName": "tsuCommuTestMsgs",
                "choices": choices,
                "values": defaultValues,
                }

    def getHazardAttributesByMagnitude(self, magnitude):
        '''
        @summary: Determine the kind of the Tsunami Information Statement (TS.S) to be issued
        which will depend on the magnitude
        @param magnitude: The seismic magnitude
        @return: A string that will be parsed to set the hazard type
        '''
        hazardAttributes = {}
        if magnitude >= 7.9:
            hazardAttributes["tisType"] = "tisHigh"
        else:
            hazardAttributes["tisType"] = "tisLow"

        return hazardAttributes

    def getTsunamiWWAParameters(self, dialogInputMap):
        '''
        @summary: Organize a subset of the user selections from the
        defineDialog() window to pull out what the user chose for the
        Tsunami Warning (TS.W), Tsunami Advisory (TS.Y), and Tsunami Watch (TS.A)
        distance/time section
        @return: A dictionary
        '''
        return {
            "tsuWarning": {
                "createType": dialogInputMap.get("tswCreateType"),
                "distance": dialogInputMap.get("tswRadius"),
                "tsuTime": dialogInputMap.get("tswHour"),
                },
            "tsuAdvisory": {
                "createType": dialogInputMap.get("tsyCreateType"),
                "distance": dialogInputMap.get("tsyRadius"),
                "tsuTime": dialogInputMap.get("tsyHour"),
                },
            "tsuWatch": {
                "createType": dialogInputMap.get("tsaCreateType"),
                "distance": dialogInputMap.get("tsaRadius"),
                "tsuTime": dialogInputMap.get("tsaHour"),
                }
            }

    def createTsunamiWWAManually(self, tsuWWA, newEventSet, tsuParamsDict):
        '''
        @summary: Create tsunami hazard events using inputs from the Tsunami
        Message Tool
        @param tsuWWA: A list of Watch/Warning/Advisory selections made by the user
        (e.g., ["tsuWarning", "tsuAdvisory"])
        @param newEventSet: The eventSet the hazard events will be written to
        @param tsuParamsDict: A dictionary of distance/time parameters provided by
        the user (e.g., "tsuWatch": {"createType": tsaDistance, "distance": 600})
        @return: An updated eventSet
        '''
        createWarning = createAdvisory = createWatch = False
        w_radius = y_radius = a_radius = 0
        w_time = y_time = a_time = 0
        usedBrkptSegNames = []
        wwaAreaDictList = []
        # First go through tsuWWA, set up all variables
        for tsuType in tsuWWA:
            tsuParams = tsuParamsDict.get(tsuType)
            createType = tsuParams.get("createType")
            tsuRadius = tsuParams.get("distance")
            tsuTimeHrs = tsuParams.get("tsuTime")
            if tsuType == "tsuWarning":
                createWarning = True
                if createType == "tswDistance":
                    w_radius = tsuRadius
                elif createType == "tswTime":
                    w_time = tsuTimeHrs
            elif tsuType == "tsuAdvisory":
                createAdvisory = True
                if createType == "tsyDistance":
                    y_radius = tsuRadius
                elif createType == "tsyTime":
                    y_time = tsuTimeHrs
            elif tsuType == "tsuWatch":
                createWatch = True
                if createType == "tsaDistance":
                    a_radius = tsuRadius
                elif createType == "tsaTime":
                    a_time = tsuTimeHrs

        # Check if there is need to create hazard event based on time, if yes, first check
        # if timeOfArrivalForecast information is available, if not, log the error
        if (w_time or y_time or a_time) and self.timeOfArrivalForecast is None:
            self.showNoTimeOfArrivalForecastMessage()
            return newEventSet

        '''
        Distance & Time validation:
        - If the TS.W distance radius is defined:
            - Validate that its distance is smaller than the TS.Y and TS.A distances
        - Is the TS.Y distance radius is defined:
            - Validate that its distance is smaller than the TS.A distances
        - If the TS.W time (in hours) is defined:
            - Validate that this time is smaller than the TS.Y and TS.A time
        - Is the TS.Y time (in hours) is defined:
            - Validate that this time is smaller than the TS.A time
        '''
        if ((w_radius and ((y_radius and y_radius <= w_radius) or (a_radius and a_radius <= w_radius))) or
           (y_radius and a_radius and a_radius <= y_radius)):
            self.showInvalidDistanceTimeRadius()
            return newEventSet
        elif ((w_time and ((y_time and y_time <= w_time) or (a_time and a_time <= w_time))) or
            (y_time and a_time and a_time <= y_time)):
            self.showInvalidDistanceTimeRadius()
            return newEventSet

        if createWarning:
            if w_radius:
                wwaAreaDictList.extend(self.createEventDictsByDistanceRadius(0, w_radius,
                                                                             usedBrkptSegNames, None,
                                                                             "TS.W", False))
            elif w_time:
                wwaAreaDictList.extend(self.createEventDictsByTimeRadius(self.getCurrentCAVETime(),
                                                                         w_time,
                                                                         self.timeOfArrivalForecast,
                                                                         usedBrkptSegNames, [],
                                                                         "TS.W", False))
        if createAdvisory:
            if y_radius:
                wwaAreaDictList.extend(self.createEventDictsByDistanceRadius(0, y_radius,
                                                                             usedBrkptSegNames,
                                                                             None, "TS.Y", False))
            elif y_time:
                wwaAreaDictList.extend(self.createEventDictsByTimeRadius(self.getCurrentCAVETime(),
                                                                         y_time,
                                                                         self.timeOfArrivalForecast,
                                                                         usedBrkptSegNames, [],
                                                                         "TS.Y", False))
        if createWatch:
            if a_radius:
                wwaAreaDictList.extend(self.createEventDictsByDistanceRadius(0, a_radius,
                                                                             usedBrkptSegNames, None,
                                                                             "TS.A", False))
            elif a_time:
                wwaAreaDictList.extend(self.createEventDictsByTimeRadius(self.getCurrentCAVETime(),
                                                                         a_time,
                                                                         self.timeOfArrivalForecast,
                                                                         usedBrkptSegNames, [],
                                                                         "TS.A", False))
        newEventSet = self.createTsunamiWWAFromAreaDictList(wwaAreaDictList, newEventSet)

        return newEventSet

    def createTsunamiWWAFromAreaDictList(self, wwaAreaDictList, newEventSet):
        for subDict in wwaAreaDictList:
            newHazardEvent = self.buildNewHazardEvent(subDict["hazardType"], subDict["geometry"],
                                                      subDict["productRegion"], self.physicalEvent,
                                                      self.practice, subDict["hazardAttributes"])
            newEventSet.add(newHazardEvent)
        return newEventSet

    def createTsunamiMessages(self, hazardType, productRegions, newEventSet, hazardAttributes={}):
        '''
        @summary: Create broad geographical tsunami messages
        @param hazardType: The hazard type (e.g., TS.S)
        @param productRegions: A list of product regions (e.g., ["EcGc"])
        @param newEventSet: The eventSet being returned by the tool
        @param hazardAttributes: An optional dictionary of hazard attributes
        @return: An updated eventSet
        '''
        physicalEventBuffer = self.convertPhysicalEventPointToPolygon(5)
        for productRegion in productRegions:
            newHazardEvent = self.buildNewHazardEvent(hazardType, physicalEventBuffer,
                                                      productRegion, self.physicalEvent,
                                                      self.practice, hazardAttributes)
            newEventSet.add(newHazardEvent)
        return newEventSet

    '''
    Condition Building Blocks
    '''

    def isInMagnitudeRange(self, minMag, maxMag=100, minInclusive=True, maxInclusive=True):
        '''
        @summary: Determines if an input magnitude falls between a minimum and maximum
        magnitude
        @param minMag: The minimum magnitude
        @param maxMag: The maximum magnitude
        @param minInclusive: Is the minMag also included in the check
        @param maxInclusive: Is the maxMag also included in the check
        @return: Boolean
        '''
        # Exit if not in range
        if self.magnitude < minMag or self.magnitude > maxMag:
            return False
        magBuffer = 0.05
        realMinMag = minMag
        realMaxMag = maxMag
        if minInclusive:
            realMinMag -= magBuffer
        else:
            realMinMag += magBuffer

        if maxInclusive:
            realMaxMag += magBuffer
        else:
            realMaxMag -= magBuffer
        return (self.magnitude >= realMinMag and self.magnitude <= realMaxMag)

    def isWithinKmOfCoast(self, maxDistance):
        '''
        @summary: Determine if the tsunamigenic event is some user-defined distance (km)
        from the coast
        @param: The maximum inclusive distance from the coastline (km)
        @return: Boolean
        '''
        distanceFromCoast = abs(self.distanceToCoastKm)
        return distanceFromCoast <= maxDistance

    def isGreaterThanKmFromCoast(self, minDistance):
        '''
        @summary: Determine if the tsunamigenic event is some user-defined distance (km) or more
        from the coast
        @param: The minDistance inclusive distance from the coastline (km)
        @return: Boolean
        '''
        distanceFromCoast = abs(self.distanceToCoastKm)
        return distanceFromCoast >= minDistance

    def isOffshore(self, eventDistance=None):
        '''
        @summary: Determine if the tsunamigenic event is offshore (i.e., the distance to coastline
        is a positive number)
        @param: An optional user-defined event distance (km)
        @return: Boolean
        '''
        if not eventDistance:
            eventDistance = self.distanceToCoastKm
        return eventDistance >= 0

    def isOnshore(self, eventDistance=None):
        '''
        @summary: Determine if the tsunamigenic event is onshore (i.e., the distance to coastline
        is a negative number)
        @param: An optional user-defined event distance (km)
        @return: Boolean
        '''
        if not eventDistance:
            eventDistance = self.distanceToCoastKm
        return eventDistance < 0

    def isOffshoreWithinKm(self, maxDistance):
        '''
        @summary: Determine if the tsunamigenic event is within some user-defined distance
        (km) offshore
        @param maxDistance: The maximum inclusive distance away from the coastline offshore (km)
        @return: Boolean
        '''
        distanceFromCoast = self.distanceToCoastKm
        return (self.isOffshore(distanceFromCoast) and
                maxDistance >= 0 and
                distanceFromCoast <= maxDistance)

    def isOnshoreWithinKm(self, maxDistance):
        '''
        @summary: Determine if the tsunamigenic event is within some user-defined distance
        (km) onshore
        @param maxDistance: The maximum inclusive distance away from the coastline onshore (km)
        @return: Boolean
        '''
        distanceFromCoast = self.distanceToCoastKm
        return (self.isOnshore(distanceFromCoast) and
                maxDistance > 0 and
                abs(distanceFromCoast) <= maxDistance)

    def isFarOnshoreKm(self, minDistance=100):
        '''
        @summary: Determine if the tsunamigenic event is greater than some user-defined distance
        (km) onshore
        @param minDistance: The minimum distance away from the coastline onshore (km)
        '''
        distanceFromCoast = self.distanceToCoastKm
        return (self.isOnshore(distanceFromCoast) and
                minDistance > 0 and
                abs(distanceFromCoast) > minDistance)

    def isWithinDepthKm(self, maxDepth):
        '''
        @summary: Determine if the tsunamigenic event is within some user-defined depth (km)
        @param maxDepth: The depth to check (km)
        @return: Boolean
        '''
        eventDepth = self.depthInKm
        return eventDepth <= maxDepth

    def isShallowKm(self, maxDepth=100):
        '''
        @summary: Determine if the tsunamigenic event is shallower than some user-defined depth (km)
        @param maxDepth: The depth to check (km)
        @return: Boolean
        '''
        return self.isWithinDepthKm(maxDepth)

    def isDeepKm(self, maxDepth=100):
        '''
        @summary: Determine if the tsunamigenic event is deeper than some user-defined depth (km)
        @param maxDepth: The depth to check (km)
        @return: Boolean
        '''
        return not self.isWithinDepthKm(maxDepth)

    def isWestOfLongitude(self, longitudeBoundary=-155):
        '''
        @summary: Return whether a location's longitude is west of a
        user-defined longitude
        @param longitudeBoundary: The longitudinal boundary
        @return: Boolean
        '''
        longitude = self.longitude + 360
        longitudeBoundary += 360
        return longitude <= longitudeBoundary

    def isEastOfLongitude(self, longitudeBoundary=-155):
        '''
        @summary: Return whether a location's longitude is east of a
        user-defined longitude
        @param longitudeBoundary: The longitudinal boundary
        @return: Boolean
        '''
        longitude = self.longitude + 360
        longitudeBoundary += 360
        return longitude >= longitudeBoundary

    def isNorthOfLatitude(self, latitudeBoundary=75):
        '''
        @summary: Return whether a location's latitude is north of a
        user-defined latitude
        @param latitudeBoundary: The latitudinal boundary
        @return: Boolean
        '''
        return self.latitude >= latitudeBoundary

    def isSouthOfLatitude(self, latitudeBoundary=75):
        '''
        @summary: Return whether a location's latitude is south of a
        user-defined latitude
        @param latitudeBoundary: The latitudinal boundary
        @return: Boolean
        '''
        return self.latitude <= latitudeBoundary

    def isInCentralAmericaDualProcRegion(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine if the physical event lat/lon plus radius is within Central America dual proc region
        @param bufferRadiusKm: Optional Radius around the lat/lon
        @return: Boolean
        '''
        queryResults = self.amu.getDualProceduralRegionsIntersectingPoint(self.latitude, self.longitude, bufferRadiusKm)
        for result in queryResults:
            regionName = self.amu.getStringFromQueryResult(result, "region")
            if regionName in ["Central America"]:
                return True
        return False

    def isInSouthAmericaDualProcRegion(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine if the physical event lat/lon plus radius is within South America dual proc region
        @param bufferRadiusKm: Optional Radius around the lat/lon
        @return: Boolean
        '''
        queryResults = self.amu.getDualProceduralRegionsIntersectingPoint(self.latitude, self.longitude, bufferRadiusKm)
        for result in queryResults:
            regionName = self.amu.getStringFromQueryResult(result, "region")
            if regionName in ["South America"]:
                return True
        return False

    def isInAkBcWcWarningRegion(self):
        '''
        @summary: Determine whether the earthquake exists inside a predefined warning region
        defined in the tsunami_analysis_regions shapefile and exists along the coastlines of
        Alaska, Western Canada, and the U.S. West Coast
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon()
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["AkBcWcProcedureZone"],
                                                       sourceNames=["warningregion"])

    def isInAkBcWcAdvisoryRegion(self):
        '''
        @summary: Determine whether the physical event exists inside a predefined advisory region
        defined in the tsunami_analysis_regions table and exists along the coastlines of
        Alaska, Western Canada, and the U.S. West Coast
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon()
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["AkBcWcProcedureZone"],
                                                       sourceNames=["advisoryregion"])

    def isInNorthPacificEarthquakeSourceZone(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine whether the physical event exists inside a predefined
        North Pacific Earthquake Source Zone defined in the tsunami_analysis_regions table
        with a sourcetype of PTWCPacificDomain
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon(bufferRadiusKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["HawaiiProcedure"],
                                                       sourceNames=["NorthPacificHawaiiSourceZoneWest",
                                                                    "NorthPacificHawaiiSourceZoneEast"])

    def isInPacificEarthquakeSourceZone(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine whether the physical event exists inside a predefined
        Pacific Earthquake Source Zone defined in the tsunami_analysis_regions table
        with a sourcetype of PTWCPacificDomain
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon(bufferRadiusKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["PTWCPacificDomain"],
                                                       sourceNames=["WesternPacific", "EasternPacific"])

    def isInCaribbeanEarthquakeSourceZone(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine whether the physical event exists inside a predefined
        Caribbean Earthquake Source Zone defined in the tsunami_analysis_regions table
        with a sourcetype of CARIBEProcedure and name of CaribbeanSourceZone
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon(bufferRadiusKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["CARIBEProcedure"],
                                                       sourceNames=["CaribbeanSourceZone"])

    def isInAtlanticEarthquakeSourceZone(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine whether the physical event exists inside a predefined
        Caribbean Earthquake Source Zone defined in the tsunami_analysis_regions table
        with a sourcetype of CARIBEProcedure and name of AtlanticSourceZone
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon(bufferRadiusKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["CARIBEProcedure"],
                                                       sourceNames=["AtlanticSourceZone"])

    def isInSoutheastHawaiiSourceZone(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine whether the physical event exists inside a predefined
        Hawaii Earthquake Source Zone defined in the tsunami_analysis_regions table
        with a sourcetype of HawaiiProcedure and name of SoutheastHawaiiSourceZone
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon(bufferRadiusKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["HawaiiProcedure"],
                                                       sourceNames=["SoutheastHawaiiSourceZone"])

    def isInSouthwestHawaiiSourceZone(self, bufferRadiusKm=0.1):
        '''
        @summary: Determine whether the physical event exists inside a predefined
        Hawaii Earthquake Source Zone defined in the tsunami_analysis_regions table
        with a sourcetype of HawaiiProcedure and name of SouthwestHawaiiSourceZone
        @return: Boolean
        '''
        physicalEventPolygon = self.convertPhysicalEventPointToPolygon(bufferRadiusKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=physicalEventPolygon,
                                                       sourceTypes=["HawaiiProcedure"],
                                                       sourceNames=["SouthwestHawaiiSourceZone"])

    def getBreakPointSegmentsByIslandNames(self, nameList):
        '''
        @summary: Get break point segment query results that consists of break point segments
        that intersect geometries corresponding to a list of analysis region names
        @param nameList: A list of analysis region names (e.g., ["Maui", "Kahoolawe"])
        @return: Query results of break point segments
        '''
        analysisRegionResults = self.amu.getAnalysisRegionsByNames(nameList)
        analysisRegionGeometry = self.amu.getUnionedGeometryFromQueryResults(analysisRegionResults)
        breakPointSegmentResults = self.amu.getBreakPointSegmentsByGeometry(analysisRegionGeometry)
        return breakPointSegmentResults

    def getUnionedBreakPointSegmentGeometryByIslandNames(self, nameList):
        '''
        @summary: Get a singular geometry that consists of unioned break point segments
        that intersect geometries corresponding to a list of analysis region names
        @param nameList: A list of analysis region names (e.g., ["Maui", "Kahoolawe"])
        @return: A shapely geometry
        '''
        breakPointSegmentResults = self.getBreakPointSegmentsByIslandNames(nameList)
        resultGeometry = self.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return resultGeometry

    def getClosestHawaiianIsland(self):
        '''
        @summary: Determine the closest Hawaiian island from the physical event location
        @return: String of the Hawaiian island name (e.g., Oahu)
        '''
        # Get all Hawaiian islands from the tsunami_analysis_regions table
        queryResults = self.amu.getAnalysisRegionsBySourceType("HawaiiIslandProcedure")
        # Get shortest distance to each island
        distanceDict = self.alu.getDistancesToQueryGeometries(queryResults, self.latitude,
                                                              self.longitude)
        # Get closest island name
        closestIsland = self.alu.getClosestLocationFromDistanceDictionary(distanceDict)
        return closestIsland

    def isClosestHawaiianIslandGroup(self, matchingIslands):
        '''
        @summary: Determine if the physical event location is closest to the
        user-defined island names
        @param matchingIslands: List of island names
        @return: Boolean
        '''
        closestIsland = self.getClosestHawaiianIsland()
        return closestIsland in matchingIslands

    def isWithinDistanceKmOfHawaii(self, minDistanceKm, maxDistanceKm):
        '''
        @summary: Determine if the physical event is within some distance range of the
        Hawaii domain
        @param minDistanceKm: The minimum distance to check (in km)
        @param maxDistanceKm: The maximum distance to check (in km)
        @return: Boolean
        '''
        queryGeometry = self.geomUtils.getDonutGeometryFromPoint(self.latitude, self.longitude,
                                                                 minDistanceKm, maxDistanceKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=queryGeometry,
                                                       sourceTypes=["HawaiiIslandProcedure"])

    def isWithinDistanceKmOfPRVI(self, minDistanceKm, maxDistanceKm):
        '''
        @summary: Determine if the physical event is within some distance range of the
        Puerto Rico/U.S. Virgin Islands domain
        @param minDistanceKm: The minimum distance to check (in km)
        @param maxDistanceKm: The maximum distance to check (in km)
        @return: Boolean
        '''
        queryGeometry = self.geomUtils.getDonutGeometryFromPoint(self.latitude, self.longitude,
                                                                 minDistanceKm, maxDistanceKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=queryGeometry,
                                                       sourceTypes=["PRVIProcedure"])

    def isWithinDistanceKmOfGuam(self, minDistanceKm, maxDistanceKm):
        '''
        @summary: Determine if the physical event is within some distance range of the
        Guam domain
        @param minDistanceKm: The minimum distance to check (in km)
        @param maxDistanceKm: The maximum distance to check (in km)
        @return: Boolean
        '''
        queryGeometry = self.geomUtils.getDonutGeometryFromPoint(self.latitude, self.longitude,
                                                                 minDistanceKm, maxDistanceKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=queryGeometry,
                                                       sourceTypes=["GuamProcedure"])

    def isWithinDistanceKmOfAmSam(self, minDistanceKm, maxDistanceKm):
        '''
        @summary: Determine if the physical event is within some distance range of the
        American Samoa domain
        @param minDistanceKm: The minimum distance to check (in km)
        @param maxDistanceKm: The maximum distance to check (in km)
        @return: Boolean
        '''
        queryGeometry = self.geomUtils.getDonutGeometryFromPoint(self.latitude, self.longitude,
                                                                 minDistanceKm, maxDistanceKm)
        return self.isGeometryInCorrectAnalysisRegions(inputGeometry=queryGeometry,
                                                       sourceTypes=["AmSamProcedure"])

    def getReverseTTTTravelTimesDict(self):
        '''
        @summary: Returns the reverseTTTTravelTimesDict, populated on a lazy basis, meaning when
        it is first needed.
        @return: Boolean
        '''
        if self.reverseTTTTravelTimesDict is None:
            self.reverseTTTTravelTimesDict = ReverseTTTClientUtils.getAllTravelTimeHours(self.longitude,
                                                                                         self.latitude)
        return self.reverseTTTTravelTimesDict

    def isWithinTimeRange(self, travelTimeHours, minHours, maxHours):
        '''
        @summary: Determine if the time remaining between CAVE time and the anticipated arrival time
        (e.g., originTime + travelTimeHours) is between minHours and maxHours
        @param travelTimeHours: The travel time in hours to target region (e.g., Hawaii)
        @param minHours: The minimum time (in hours) of arrival
        @param maxHours: The maximum time (in hours) of arrival
        @return: Boolean
        '''
        hrsToMillis = travelTimeHours * GeneralConstants.MILLIS_PER_HOUR
        arrivalTimeMs = self.physicalEvent.getRefTime().getTime() + hrsToMillis
        msRemainingUntilArrival = arrivalTimeMs - self.getCurrentCAVETime().getTime()
        hoursRemainingUntilArrival = msRemainingUntilArrival / GeneralConstants.MILLIS_PER_HOUR
        return (minHours < hoursRemainingUntilArrival and hoursRemainingUntilArrival <= maxHours)

    def isWithinTimeRangeFromHawaii(self, minHours, maxHours):
        '''
        @summary: Determine if the physical event is within some time range of
        arriving to the coast of Hawaii
        @param minHours: The minimum time (in hours) of arrival
        @param maxHours: The maximum time (in hours) of arrival
        @return: Boolean
        '''
        reverseTTTDict = self.getReverseTTTTravelTimesDict()
        if ReverseTTTRegion.HAWAII in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.HAWAII]
            return self.isWithinTimeRange(travelTimeHours, minHours, maxHours)
        return False
        # hawaiiGeometry = self.alu.getHawaiiAnalysisGeometry()
        # return self.isRegionWithinTravelTime(hawaiiGeometry, minHours, maxHours)

    def isWithinTimeRangeFromGuam(self, minHours, maxHours):
        '''
        @summary: Determine if the physical event is within some time range of
        arriving to the coast of Guam
        @param minHours: The minimum time (in hours) of arrival
        @param maxHours: The maximum time (in hours) of arrival
        @return: Boolean
        '''
        reverseTTTDict = self.getReverseTTTTravelTimesDict()
        if ReverseTTTRegion.GUAM in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.GUAM]
            return self.isWithinTimeRange(travelTimeHours, minHours, maxHours)
        return False
        # guamGeometry = self.alu.getGuamAnalysisGeometry()
        # return self.isRegionWithinTravelTime(guamGeometry, minHours, maxHours)

    def isWithinTimeRangeFromAmSam(self, minHours, maxHours):
        '''
        @summary: Determine if the physical event is within some time range of
        arriving to the coast of American Samoa
        @param minHours: The minimum time (in hours) of arrival
        @param maxHours: The maximum time (in hours) of arrival
        @return: Boolean
        '''
        reverseTTTDict = self.getReverseTTTTravelTimesDict()
        if ReverseTTTRegion.AMSAM in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.AMSAM]
            return self.isWithinTimeRange(travelTimeHours, minHours, maxHours)
        return False
        # amsamGeometry = self.alu.getAmSamAnalysisGeometry()
        # return self.isRegionWithinTravelTime(amsamGeometry, minHours, maxHours)

    def isWithinTimeRangeFromPRVI(self, minHours, maxHours):
        '''
        @summary: Determine if the physical event is within some time range of
        arriving to the coast of PRVI
        @param minHours: The minimum time (in hours) of arrival
        @param maxHours: The maximum time (in hours) of arrival
        @return: Boolean
        '''
        reverseTTTDict = self.getReverseTTTTravelTimesDict()
        if ReverseTTTRegion.PRVI in reverseTTTDict:
            travelTimeHours = reverseTTTDict[ReverseTTTRegion.PRVI]
            return self.isWithinTimeRange(travelTimeHours, minHours, maxHours)
        return False
        # prviGeometry = self.alu.getPRVIAnalysisGeometry()
        # return self.isRegionWithinTravelTime(prviGeometry, minHours, maxHours)

    def isWithinDistanceKmOfWarningPoints(self, minDistanceKm, maxDistanceKm, domainName):
        '''
        @summary: Determine if the physical event is within some distance (in km)
        of PTWC warning points for either the PTWS or CARIBE domain
        @param minDistanceKm: The minimum distance (in km) to search from the physical event location
        @param maxDistanceKm: The maximum distance (in km) to search from the physical event location
        @param domainName: The PTWC warning points domain (either PTWS or CARIBE)
        @return: Boolean
        '''
        queryGeometry = self.geomUtils.getDonutGeometryFromPoint(self.latitude, self.longitude,
                                                         minDistanceKm, maxDistanceKm)
        queryResults = self.amu.queryPtwcWarningPointsByGeometry(queryGeometry)
        # Walk through the results and verify at least one result is from the correct domain
        for result in queryResults:
            if result.getString("domain") == domainName:
                return True
        return False

    def isWithinTimeOfArrivalOfWarningPoints(self, timeInHours, domainName):
        '''
        @summary: Determine if the physical event is within some distance (in km)
        of PTWC warning points for either the PTWS or CARIBE domain
        @param timeInHours: The minimum time (in hours) of arrival
        @param domainName: The PTWC warning points domain (either PTWS or CARIBE)
        @return: Boolean
        '''
        # Get all warning points within the domain of interest (e.g., PTWS)
        validWarningPoints = self.amu.getPtwcWarningPointsByDomainName(domainName)
        # Get all stations within the user-specified travel time
        tsunamiForecastTable = self.afou.getForecastStationsWithinArrivalTimeInHours(self.getCurrentCAVETime(),
                                                                                    self.timeOfArrivalForecast,
                                                                                    timeInHours)
        matchingStationIds = [forecastStation.getCustomId() for forecastStation in tsunamiForecastTable.getStations()]
        # Get list of stations that coexist in both datasets
        intersectingStations = list(set(validWarningPoints) & set(matchingStationIds))
        # Return True if any stations found
        return len(intersectingStations) > 0

    '''
    Conditional Helper Methods
    '''

    def isRegionWithinTravelTime(self, inputGeometry, minTime, maxTime):
        '''
        @summary: Determine if the physical event is within some time range of
        arriving at stations near the coasts of some input geometry
        @param inputGeometry: A shapely geometry to check if any forecast stations
        have arrival times meeting the time criteria within its boundaries
        @param minHours: The minimum time (in hours) of arrival
        @param maxHours: The maximum time (in hours) of arrival
        @return: Boolean
        '''
        # If no time of arrival forecast exists then there is nothing to process
        if not self.afou.doesForecastExist(self.timeOfArrivalForecast):
            return False

        # Get the current CAVE time
        currentTime = self.getCurrentCAVETime()

        # Determine if any stations have arrival times closer than the max time
        maxTsunamiForecastTable = self.afou.getForecastStationsWithinArrivalTimeInHours(currentTime,
                                                                                       self.timeOfArrivalForecast,
                                                                                       maxTime)
        # Determine if any station locations overlap with the input geometry
        maxStationsOverlap = self.afou.getStationsThatOverlapWithGeometry(maxTsunamiForecastTable,
                                                                          inputGeometry)

        # If no stations found within the max time then no need to process further
        if not maxStationsOverlap:
            return False
        # If no minimum time specified, determine outcome here if stations were found
        elif minTime == 0 and maxStationsOverlap:
            return True

        # Determine the stations within the minimum travel time
        minTsunamiForecastTable = self.afou.getForecastStationsWithinArrivalTimeInHours(currentTime,
                                                                                       self.timeOfArrivalForecast,
                                                                                       minTime)
        # Determine if any station locations overlap with the input geometry
        minStationsOverlap = self.afou.getStationsThatOverlapWithGeometry(minTsunamiForecastTable,
                                                                          inputGeometry)

        # Get unique stations that only exist in the max list
        uniqueStations = set(maxStationsOverlap).difference(set(minStationsOverlap))
        if uniqueStations:
            return True
        else:
            return False

    def convertPhysicalEventPointToPolygon(self, bufferRadiusInKm=0.1):
        '''
        @summary: Buffer the physical event point by some distance (in km) to create a polygon
        @param bufferRadiusInKm: An optional radius (in km) to buffer the point by (Default = 0.1 km)
        @return: A shapely Polygon geometry
        '''
        return self.geomUtils.bufferPoint(self.latitude, self.longitude, bufferRadiusInKm)

    def isInCorrectProceduralRegions(self, regionsToCheck, bufferRadiusKm=1):
        '''
        @summary: Determine which procedural region(s) a physical event lat/lon is within
        @param regionsToCheck: A list of procedural region names to check
        @param bufferRadiusKm: Optional Radius around the lat/lon
        @return: Boolean
        '''
        queryResults = self.amu.getProceduralRegionsIntersectingPoint(self.latitude, self.longitude, bufferRadiusKm)
        for result in queryResults:
            regionName = self.amu.getStringFromQueryResult(result, "name")
            if regionName in regionsToCheck:
                return True
        return False

    def isGeometryInCorrectAnalysisRegions(self, inputGeometry, sourceTypes, sourceNames=[]):
        '''
        @summary: Determine if a user-geometry is in the correct procedural region specified by
        a list of source types and an optional list of source names
        @param inputGeometry: The geometry fed into the MapsDatabaseAccessor() query
        @param sourceTypes: A list of The analysis source type(s) (e.g., ["CARIBEProcedure"])
        @param sourceNames: An optional list of analysis dataset name(s) (e.g., ["AtlanticSourceZone"] )
        @return: Boolean
        '''
        queryResults = self.amu.getAnalysisRegionsByGeometry(inputGeometry)
        for result in queryResults:
            querySourceName = self.amu.getStringFromQueryResult(result, "name")
            querySourceType = self.amu.getStringFromQueryResult(result, "sourcetype")
            if ((querySourceType in sourceTypes) and
                (not sourceNames or querySourceName in sourceNames)):
                return True
        return False

    def recommendInitialTsunamiEvents(self, productRegions):
        '''
        @summary: Method to determine what hazard events should be created based on
        the initial message procedures
        @param productRegions: A list of product region abbreviations to run initial messages on
        @return: An eventSet with proposed hazard events
        '''
        proposedEventSet = EventSetFactory.createEventSet()
        self.reinitializeTrecsExecInfo()

        if not productRegions:
            return proposedEventSet

        # Run the threat database for all selected regions
        wwaAreaDictList, remainingProductRegions = self.executeThreatDatabaseQueries(productRegions)

        # If we have product regions that still need to have procedures
        # run on them then execute those procedural steps if the physical
        # event type is Seismic
        if remainingProductRegions:
            self.trecsExecInfo.setEnabledProductRegions(remainingProductRegions)
            self.trecsExecInfo.appendToTrace(f"Initial Messages for {self.physicalEventID}")
            if not self.agu.isPhysicalEventTypeSeismic(self.physicalEventType):
                self.handleNonSeismicPhysicalEventWarning()
                # return proposedEventSet
            else:
                self.setSelectedTrecsExecProcsAndCategs(remainingProductRegions)
                trecsDialogResult = self.trecsExecInfo
                if not self.isAutoTest:
                    trecsDialogResult = TrecsExecDialog.open(self.trecsExecInfo)
                if trecsDialogResult is None:
                    self.trecsExecInfo.appendToTrace("Cancelled.")
                    return proposedEventSet
                selectedCategories = self.trecsExecInfo.getSelectedCategories()
                wwaAreaDictList += self.executeCategoryActions(selectedCategories)
        if not wwaAreaDictList:
            self.handleNoEventsCreatedWarning()
        else:
            proposedEventSet = self.tsunamiRecommenderHazardEventCreation(wwaAreaDictList,
                                                                          proposedEventSet)

        return proposedEventSet

    def performEventSurgery(self, originalEventSet, proposedEventSet, productRegion):
        '''
        @summary: Combine information from the eventSet that came into this tool with
        proposed events that came from the initial or follow-up message procedures to
        get a new set of events that will be returned by the tool
        @param originalEventSet: The original event set containing active events
        @param proposedEventSet: The proposed event set created within this tool run
        @param productRegion: The product region abbreviation (e.g., AkBcWc)
        @return: An eventSet containing post-surgery hazard events for this product region
        '''
        # An eventSet containing the events post-surgery
        postOpEventSet = EventSetFactory.createEventSet()

        # List of instructions messages
        messages = []

        # Parse information from the original eventSet; only returning events for this product region
        origInfoDicts = []  # A list of dictionaries containing information about each active hazard event
        originalSegmentNames = []  # A list of all break point segment names with active events
        for origEvent in originalEventSet:
            infoDict = self.getInformationFromHazardEvent(origEvent, productRegion)
            if infoDict:
                origInfoDicts.append(infoDict)
                originalSegmentNames += infoDict["hazardLocations"]
        originalSegmentNames = list(set(originalSegmentNames))

        # Parse information from the proposed eventSet which only contains events for this product region
        newInfoDicts = []
        newSegmentNames = []
        for propEvent in proposedEventSet:
            infoDict = self.getInformationFromHazardEvent(propEvent)
            newInfoDicts.append(infoDict)
            newSegmentNames += infoDict["hazardLocations"]
        newSegmentNames = list(set(newSegmentNames))

        # Combine all possible segments being modified into a single list
        allTouchableSegments = list(set(originalSegmentNames + newSegmentNames))

        # Build a dictionary containing a mapping of break point segment names to numbers
        breakPointSegmentNumberDict = self.amu.getBPNumbersByBrkptSegmentNames(allTouchableSegments)

        '''
        Determine which break point segment names exist in both the old
        and new set of hazards
        '''
        modifiedCandidates = list(set(originalSegmentNames) & set(newSegmentNames))
        # Dict of brkpt segment name to tuple (oldDict, newType)
        modifiedSegmentDict = {}
        surgeryResults = SurgeryResults()
        # Walk through the modified candidates and determine if the phensig changes
        for candidateSegment in modifiedCandidates:
            oldDict = self.getEventInformationBySegmentName(origInfoDicts, candidateSegment)
            newDict = self.getEventInformationBySegmentName(newInfoDicts, candidateSegment)
            # Check if phensigs match
            oldType = oldDict.get("hazardType")
            newType = newDict.get("hazardType")
            if oldType != newType:
                if ((oldType == "TS.A" and newType in ["TS.Y", "TS.W"]) or
                    (oldType == "TS.Y" and newType == "TS.W")):
                    surgeryResults.recordSurgeryResult("UP", oldType, newType, candidateSegment)
                else:
                    surgeryResults.recordSurgeryResult("DOWN", oldType, newType, candidateSegment)
                modifiedSegmentDict[candidateSegment] = {
                    "infoDict": oldDict,
                    "newHazardType": newType,
                    }
            else:
                surgeryResults.recordSurgeryResult("CON", oldType, oldType, candidateSegment)

        '''
        Determine which break point segment names are being added in the new proposed eventSet
        but have no current hazard events out for them
        '''
        addedCandidates = list(set(newSegmentNames) - set(originalSegmentNames))
        for candidateSegment in addedCandidates:
            infoDict = self.getEventInformationBySegmentName(newInfoDicts, candidateSegment)
            newType = infoDict.get("hazardType")
            surgeryResults.recordSurgeryResult("NEW", newType, newType, candidateSegment)
        '''
        Determine which break point segment names are being removed in the new proposed eventSet
        and are currently in an active hazard event
        '''
        removedCandidates = list(set(originalSegmentNames) - set(newSegmentNames))
        for candidateSegment in removedCandidates:
            infoDict = self.getEventInformationBySegmentName(origInfoDicts, candidateSegment)
            oldType = infoDict.get("hazardType")
            surgeryResults.recordSurgeryResult("CAN", oldType, oldType, candidateSegment)

        messages = self.createSurgeryResultsMessages(surgeryResults)
        resultsMsg = "\n".join(messages)
        self.trecsExecInfo.appendToTrace(resultsMsg)

        '''
        Surgery Step #1: Remove all active break point segments that are not in the
                         proposed eventSet
        '''
        for origInfoDict in origInfoDicts:
            origInfoDict["hazardLocations"] = [bpName for bpName in origInfoDict["hazardLocations"]
                                               if bpName not in removedCandidates]

        '''
        Surgery Step #2: Remove all active break point segments that are being either upgraded
                         or downgraded to a different hazard type in the proposed eventSet
        '''
        for origInfoDict in origInfoDicts:
            origInfoDict["hazardLocations"] = [bpName for bpName in origInfoDict["hazardLocations"]
                                               if bpName not in modifiedSegmentDict.keys()]

        '''
        Surgery Step #3: Add upgraded/downgraded break point segments. If the segment being changed
                         has a neighbor that also has this hazard type then add it to the existing
                         event. If it does not have a neighbor, create a new event for it to be
                         created from scratch later.
        '''
        newHazardEventCount = 0
        for modifiedSegmentName in modifiedSegmentDict:
            newHazardType = modifiedSegmentDict[modifiedSegmentName]["newHazardType"]
            segmentAdded = False
            # If there's a hazard event with the same phensig and has a neighbor, EXA it
            for origInfoDict in origInfoDicts:
                if (origInfoDict["hazardType"] == newHazardType and
                    self.hasNeighboringBrkptSegment(modifiedSegmentName,
                                                    origInfoDict["hazardLocations"],
                                                    breakPointSegmentNumberDict)):
                    origInfoDict["hazardLocations"].append(modifiedSegmentName)
                    # print(f"TRECS Surgery   Appended {breakPointSegmentNumberDict[brkptSegment]} to eventID = {origInfoDict['eventID']}")
                    segmentAdded = True
                    break
            if not segmentAdded:
                newHazardEventCount += 1
                # print(f"  TRECS Surgery   Adding new UPG/DNG psuedo hazard event {modifiedBkptSegsFromTo[brkptSegment][1]} id = {newHazardEventCount} for {breakPointSegmentNumberDict[brkptSegment]} {brkptSegment}")
                newOrigInfoDict = {
                    "event": None,
                    "eventID": f"{newHazardEventCount}",
                    "hazardType": newHazardType,
                    "productRegion": productRegion,
                    "hazardLocations": [modifiedSegmentName],
                    "wwaLocationCoverage": modifiedSegmentDict[modifiedSegmentName]["infoDict"].get("wwaLocationCoverage")
                    }
                origInfoDicts.append(newOrigInfoDict)
        '''
        Surgery Step #4: Add brand new break point segments to the map. If the new break point segment
                         has the same hazard type as a neighboring break point segment then add it to
                         that event's infoDict. If it does not have a neighbor, create a new event for
                         it to be created from scratch later.
        '''
        for addSegment in addedCandidates:
            segmentAdded = False
            infoDict = self.getEventInformationBySegmentName(newInfoDicts, addSegment)
            newType = infoDict.get("hazardType")
            # If there's a hazard event with the same phensig and has a neighbor, EXA it
            for origInfoDict in origInfoDicts:
                if (origInfoDict["hazardType"] == newType and
                    self.hasNeighboringBrkptSegment(addSegment, origInfoDict["hazardLocations"],
                                                    breakPointSegmentNumberDict)):
                    origInfoDict["hazardLocations"].append(addSegment)
                    segmentAdded = True
                    break
            if not segmentAdded:
                newHazardEventCount += 1
                # print(f"TRECS Surgery Adding brand new brkptSegment {brkptSegment} for brand new psuedo hazard event {modifiedBkptSegsFromTo[brkptSegment][1]} id = {newHazardEventCount}")
                newOrigInfoDict = {
                    "event": None,
                    "eventID": f"{newHazardEventCount}",
                    "hazardType": newType,
                    "productRegion": productRegion,
                    "hazardLocations": [addSegment],
                    "wwaLocationCoverage": infoDict.get("wwaLocationCoverage")
                    }
                origInfoDicts.append(newOrigInfoDict)

        '''
        Surgery Step #5: Loop over all info dictionaries modified during surgery steps 1-4 and
                         split up any hazard event into two if there are discontinuous break
                         point segments
        '''
        additionalInfoDicts = []
        for origInfoDict in origInfoDicts:
            # Build sorted list of tuples containing the break point number and name in ascending order
            bpNumAndSegTuples = [(breakPointSegmentNumberDict[segmentName], segmentName)
                                 for segmentName in origInfoDict["hazardLocations"]]
            bpNumAndSegTuples = sorted(bpNumAndSegTuples, key=lambda x: x[0])

            # Walk up break point list and if non-contiguous number is found then add contiguous set to final list
            currentNumber = None
            resultList = []
            subList = []
            for bpNum, bpSeg in bpNumAndSegTuples:
                if not currentNumber or (currentNumber + 1 == bpNum):
                    subList.append(bpSeg)
                else:
                    resultList.append(subList)
                    subList = [bpSeg]
                currentNumber = bpNum
            if subList:
                resultList.append(subList)

            # If more than 1 resultList was made then we have a discontinuity
            for i in range(1, len(resultList)):
                newHazardEventCount += 1
                # Remove all segments in the discontinuous event from the original event
                origInfoDict["hazardLocations"] = list(set(origInfoDict["hazardLocations"]) - set(resultList[i]))
                # Make a new (psuedo) hazard event with the remaining brkpt segments
                newEventDict = {
                    "event": None,
                    "eventID": f"{newHazardEventCount}",
                    "hazardType": origInfoDict["hazardType"],
                    "productRegion": origInfoDict["productRegion"],
                    "hazardLocations": resultList[i],
                    "wwaLocationCoverage": origInfoDict["wwaLocationCoverage"]
                    }
                additionalInfoDicts.append(newEventDict)
        # Add any new events that were spun out of the discontinuity checks to the set of original events
        origInfoDicts.extend(additionalInfoDicts)

        '''
        Surgery Step #6: Merge any hazard events together that have the same hazard type and
                         have neighboring break point segments. If one of these events existed
                         before the tool was run, merge into that event.
        '''
        for outerIndex in range(len(origInfoDicts)):
            for innerIndex in range(len(origInfoDicts)):
                # Do not compare equal events
                if innerIndex == outerIndex:
                    continue
                # Get the information dictionaries for each event
                outerDict = origInfoDicts[outerIndex]
                innerDict = origInfoDicts[innerIndex]
                # print(f"TRECS Surgery Comparing outer id = {outerDict['eventID']} and inner id = {innerDict['eventID']}")
                # Check if the hazard types for these events match before proceeding
                if outerDict["hazardType"] == innerDict["hazardType"]:
                    isNeighboring = self.hasNeighboringBrkptSegments(outerDict["hazardLocations"],
                                                                     innerDict["hazardLocations"],
                                                                     breakPointSegmentNumberDict)
                    # print(f"TRECS Surgery   outer {self.getBPSegNumsString(outerDict['hazardLocations'], breakPointSegmentNumberDict)} and inner {self.getBPSegNumsString(innerDict['hazardLocations'], breakPointSegmentNumberDict)}")
                    if isNeighboring:
                        # Union. Merge into the one with an existing hazard event if there is one.
                        mergeIntoDict = outerDict
                        mergeOutOfDict = innerDict
                        # The outer event is new so make sure we merge into the inner dict
                        if outerDict["event"] is None:
                            mergeIntoDict = innerDict
                            mergeOutOfDict = outerDict
                        # print(f"TRECS Surgery   -- Merging into {mergeIntoDict['hazardType']} where mergeIntoDict id = {mergeIntoDict['eventID']} and mergeOutOfDict id = {mergeOutOfDict['eventID']}")
                        mergeIntoDict["hazardLocations"] = list(set(outerDict["hazardLocations"]) | set(innerDict["hazardLocations"]))
                        mergeOutOfDict["hazardLocations"] = []

        print(f"TRECS Surgery ====================================RESULT FOR {productRegion}===========================================================")
        self.dumpInfoDicts(origInfoDicts, breakPointSegmentNumberDict)

        '''
        If there is an existing HazardEvent to CON/EXA, then change its geometry.
        If we're CANing it, then just change its status.
        If it's a NEW hazardEvent, we do that in the Else.
        '''
        for origInfoDict in origInfoDicts:
            hazardEvent = origInfoDict["event"]
            hazardType = origInfoDict["hazardType"]
            if hazardEvent is not None:
                # print(f"TRECS Surgery Mucking existing {origInfoDict['eventID']} {origInfoDict['hazardType']} to {self.getBPSegNumsString(origInfoDict['hazardLocations'], breakPointSegmentNumberDict)}")
                # If there are no more brkpt segments, end the existing hazard event
                if not origInfoDict["hazardLocations"]:
                    if hazardType != "TS.S" and hazardType != "TS.ThreatMessage":
                        # print(f"TRECS Surgery scuttle ending it")
                        hazardEvent.setStatus("ending")
                # Otherwise, change the existing hazard event's geometry
                else:
                    brkptSegQueryResults = self.amu.getBreakPointSegmentsBySegmentNames(origInfoDict["hazardLocations"])
                    newGeometry = self.amu.getUnionedGeometryFromQueryResults(brkptSegQueryResults)
                    # print(f"TRECS Surgery modified geometry = {newGeometry.wkt}")
                    # NOTE I think this has km projection problems eventually on occasion.
                    # Gotta kill the LatLonConverter else this doesnt work sometimes!!
                    advancedGeometry = self.geomUtils.convertFromShapelyToAdvancedGeometry(newGeometry)
                    hazardEvent.setGeometry(advancedGeometry)
                    brkptSegNames = self.amu.getNamesFromQueryResults(brkptSegQueryResults)
                    hazardEvent.set("hazardLocations", brkptSegNames)
                postOpEventSet.add(hazardEvent)
            # This case is for NEW hazard events
            else:
                # Careful, for some reason the getBreakPointSegmentsBySegmentNames returns ALL of em
                # if you pass it a None or empty list of names. So check if not None and not empty.
                hazardLocations = origInfoDict["hazardLocations"]
                if hazardLocations:
                    brkptSegQueryResults = self.amu.getBreakPointSegmentsBySegmentNames(hazardLocations)
                    newGeometry = self.amu.getUnionedGeometryFromQueryResults(brkptSegQueryResults)
                    # print(f"TRECS Surgery new geometry = {newGeometry.wkt}")
                    attrDict = {
                        "hazardLocations": hazardLocations,
                        "wwaLocationCoverage": origInfoDict["wwaLocationCoverage"]
                        }
                    newHazardEvent = self.buildNewHazardEvent(origInfoDict["hazardType"],
                                                              newGeometry, origInfoDict["productRegion"],
                                                              self.physicalEvent, self.practice,
                                                              attrDict)
                    postOpEventSet.add(newHazardEvent)
        return postOpEventSet

    def createSurgeryResultsMessages(self, surgeryResults):

        '''
        @summary: Create a list of messages on what actions will be taken
        on this run of the tool
        @param surgeryResults: A SurgeryResults object
        @return: List of strings
        '''
        messages = []
        actions = [("UP", "The following are being UPGRADED from a "),
                   ("DOWN", "The following are being DOWNGRADED from a "),
                   ("NEW", "The following are being ADDED to a "),
                   ("CON", "The following are being CONTINUED for a "),
                   ("CAN", "The following are being REMOVED from a ")]
        for action in actions:
            surgeryDict = surgeryResults.getSurgeryResultsDict(action[0])
            for surgery in surgeryDict:
                if action[0] == "UP" or action[0] == "DOWN":
                    msg = action[1] + surgery[0] + " to a " + surgery[1] + ":"
                else:
                    msg = action[1] + surgery[0] + ":"
                messages.append(msg)
                for brkptSeg in surgeryDict[surgery]:
                    messages.append("    " + brkptSeg)
        if messages:
            messages.insert(0, "\n\nFollow-Up Action Summary:")
        else:
            messages.append("\n\nNo Follow-Up Actions Required.")
        return messages

    def hasNeighboringBrkptSegment(self, candidateBrkptSegment, brkPtSegmentsList,
                                   allBrkptSegNamesToBPNumDict):
        '''
        @summary: Returns true if the given candidateBrkptSegment has a brkpt number that is
        neighboring any of the brkpt segments in the given brkPtSegmentsList. Brkpt segment
        numbers are determined by what is given in the allBrkptSegNamesToBPNumDict for lack of a
        better OO way
        @param candidateBrkptSegment: The brkpt segment that may be a neighbor to the hazard event
        @param brkPtSegmentsList: The brkPtSegmentsList with the brkpt segment hazard area
        @return: Boolean indicating if it's a neighbor
        '''
        if candidateBrkptSegment not in allBrkptSegNamesToBPNumDict:
            return False
        candidateBPNumber = allBrkptSegNamesToBPNumDict[candidateBrkptSegment]
        neighbors = [candidateBPNumber - 1, candidateBPNumber + 1]
        for bkptSeg in brkPtSegmentsList:
            if allBrkptSegNamesToBPNumDict[bkptSeg] in neighbors:
                return True
        return False

    def hasNeighboringBrkptSegments(self, brkPtSegmentsListA, brkPtSegmentsListB,
                                    allBrkptSegNamesToBPNumDict):
        '''
        @summary: Returns true if the given brkPtSegmentsListA has any brkpt numbers that are
        neighboring any of the brkpt segments in the given brkPtSegmentsListB. Brkpt segment
        numbers are determined by what is given in the allBrkptSegNamesToBPNumDict for lack of a
        better OO way
        @param brkPtSegmentsListA: The brkpt segments that may be a neighbor to the other list
        @param brkPtSegmentsListB: The brkpt segments that may be a neighbor to the other list
        @return: Boolean indicating if there's at least one neighbor
        '''
        for brkptSegA in brkPtSegmentsListA:
            if self.hasNeighboringBrkptSegment(brkptSegA, brkPtSegmentsListB,
                                               allBrkptSegNamesToBPNumDict):
                return True
        return False

    def getActiveEventsForPhysicalEvent(self, eventSet):
        '''
        @summary: Given an input event set that contains all hazard events in
        this session, filter this down to only contain events that are pertinent
        to this physical event
        @param eventSet: The eventSet brought into this execution of the tool
        @return: A filtered down eventSet
        '''
        # Return eventSet if it is empty
        if len(eventSet.getEvents()) < 1:
            return eventSet
        # Otherwise, filter it down
        filteredEventSet = EventSetFactory.createEventSet()
        filteredEventSet.setAttributes(eventSet.getAttributes())
        for event in eventSet:
            if (event.get("customId") == self.physicalEventID and
                event.getHazardStatus().upper() not in ["ENDED", "ELAPSED", "POTENTIAL", "PENDING", "ENDING", "PROPOSED"]):
                filteredEventSet.add(event)
        return filteredEventSet

    def getInformationFromHazardEvent(self, hazardEvent, productRegion=None):
        '''
        @summary: Get relevant information from the hazard event
        @param hazardEvent: The hazard event being analyzed
        @param productRegion: The product region abbreviation to filter
        the event on
        @return: Dictionary
        '''
        eventProductRegion = hazardEvent.get("productRegion")
        if productRegion and productRegion != eventProductRegion:
            return None
        hazardLocations = hazardEvent.get("hazardLocations")
        if not hazardLocations:
            hazardLocations = []
        wwaLocationCoverage = hazardEvent.get("wwaLocationCoverage")
        if not wwaLocationCoverage:
            wwaLocationCoverage = "segmentAreas"
        return {
            "event": hazardEvent,  # May be a NoneType if the hazard event does not exist yet
            "eventID": hazardEvent.getEventID(),  # May be a NoneType if hazard event does not exist yet
            "hazardType": hazardEvent.getHazardType(),
            "productRegion": eventProductRegion,
            "hazardLocations": hazardLocations,
            "wwaLocationCoverage": wwaLocationCoverage
            }

    def getEventInformationBySegmentName(self, infoDicts, segmentName):
        '''
        @summary: Given a list of information dictionaries from an eventSet,
        get the infomation dictionary corresponding to a particular break point
        segment
        @param infoDicts: The list of information dictionaries from an eventSet
        @param segmentName: The break point segment name
        @return: A single information dictionary
        '''
        for infoDict in infoDicts:
            if segmentName in infoDict["hazardLocations"]:
                return infoDict

    def getBPSegNumsString(self, hazardLocations, allBrkptSegNamesToBPNumDict):
        bpNumAndSegTupleList = [(allBrkptSegNamesToBPNumDict[loc], loc) for loc in hazardLocations]
        bpNumAndSegTupleList = sorted(bpNumAndSegTupleList, key=lambda x: x[0])
        printLine = ""
        for thing in bpNumAndSegTupleList:
            printLine += f"{thing[0]} "
        return printLine

    def dumpInfoDicts(self, infoDicts, allBrkptSegNamesToBPNumDict):
        for infoDict in infoDicts:
            print(f"TRECS Surgery   event = {infoDict['event'] is not None} ===================================")
            print(f"TRECS Surgery   eventID = {infoDict['eventID']}")
            print(f"TRECS Surgery   hazardType = {infoDict['hazardType']}")
            print(f"TRECS Surgery   productRegion = {infoDict['productRegion']}")
            print(f"TRECS Surgery   hazardLocations = {self.getBPSegNumsString(infoDict['hazardLocations'], allBrkptSegNamesToBPNumDict)}")
            print(f"TRECS Surgery   wwaLocationCoverage = {infoDict['wwaLocationCoverage']}")


class TRECSPythonExecCateg():
    '''
    Abstract-ish Base class
    '''

    def __init__(self, someConditions, someActions):
        '''
        @param someConditions: A list of Strings describing conditions for this category to be
        satisfied.
        @param someActions: A list of Strings describing what the successfully executed category
        will do.
        '''
        self.conditions = someConditions
        self.actions = someActions

    def conditionsSatisfied(self, theTRECSTool):
        '''
        @summary: Checks the conditions for executing this concrete subclass, based on the attributes
                 maintained by theTRECSTool, such as the physical event's type, magnitude, depth,
                 location, etc
        @param theTRECSTool: the TsunamiRecommender.
        @return: Boolean; True or False depending on if the conditions for this class are satisfied
        '''
        return False

    def applyActions(self, theTRECSTool):
        '''
        @summary: Applies the TRECS Procedure, typically by creating hazard events, the types and
        geometries as defined by the concrete subclass
        @param theTRECSTool: the TsunamiRecommender.
        @return: The list of wwa event dicts that look like so:
            "hazardType": hazardType,
            "geometry": hazardGeometry,
            "productRegion": productRegion
        '''
        return []

    def appendToTrace(self, theTRECSTool):
        '''
        @summary: Append text to the trace log within the TrecsInfo object
        @param theTRECSTool: The T-RECS tool being run
        @return: An updated trecsExecInfo in memory
        '''
        theTRECSTool.trecsExecInfo.appendToTrace(f"Executed actions for {type(self).__name__}:")
        theTRECSTool.trecsExecInfo.appendToTrace("   ", self.actions)

    def assertActions(self, theTRECSTool, eventSet):
        return True

    def assertEmptyHazardEvents(self, eventSet):
        if eventSet is None:
            return True

        return (eventSet.events is None or len(eventSet.events) == 0)

    def assertHazardEvent(self, eventSet, productRegion, phensig):
        if eventSet is None:
            return False
        hazardEvents = eventSet.getEvents()
        for hazardEvent in hazardEvents:
            if hazardEvent.getPhensig() == phensig and hazardEvent.get("productRegion") == productRegion:
                return True
        return False

    def assertHazardEventAndAttribute(self, eventSet, productRegion, phensig, attributeName, attributeValue):
        if eventSet is None:
            return False
        hazardEvents = eventSet.getEvents()
        for hazardEvent in hazardEvents:
            if (hazardEvent.getPhensig() == phensig and hazardEvent.get("productRegion") == productRegion and
               hazardEvent.get(attributeName) == attributeValue):
                return True
        return False

'''
A class to help us record Surgery Results
'''


class SurgeryResults:

    def __init__(self):
        self.upgrades = {}
        self.downgrades = {}
        self.cans = {}
        self.cons = {}
        self.news = {}

    def recordSurgeryResult(self, action, fromPhensig, toPhensig, brkptSeg):
        '''
        @summary: Appends an upgrade, downgrade, new, can, or con for the given brkpt segment
        @param action: The action of the surgery result, either UP, DOWN, CAN, CON, NEW
        @param fromPhensig:
        @param toPhensig: phensig for the new state, and only applicable for UP or DOWN
        @param brkptSeg: the break point segment that has been surgerized
        @return nothing
        '''
        dictKey = (fromPhensig, toPhensig)
        dictToUse = self.getSurgeryResultsDict(action)
        listOfBrkptSegs = []
        if dictToUse.get(dictKey) is not None:
            listOfBrkptSegs = dictToUse.get(dictKey)
        listOfBrkptSegs.append(brkptSeg)
        dictToUse[dictKey] = listOfBrkptSegs

    def getSurgeryResultsDict(self, action):
        '''
        @summary: Returns upgrade, downgrade, new, can, or con surgery results
        @param action: The action of the surgery result, either UP, DOWN, CAN, CON, NEW
        @return a dictionary with (fromPhensig, toPhensig) tuple keys, mapping to a list of break
        point segments
        '''
        if action == "UP":
            return self.upgrades
        elif action == "DOWN":
            return self.downgrades
        elif action == "CAN":
            return self.cans
        elif action == "CON":
            return self.cons
        elif action == "NEW":
            return self.news
        else:
            return {}
