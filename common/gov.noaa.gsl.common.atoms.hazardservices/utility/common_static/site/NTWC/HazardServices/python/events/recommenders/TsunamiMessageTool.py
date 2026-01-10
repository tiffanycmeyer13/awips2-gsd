# *** Override behavior of TsunamiMessageTool.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
Tsunami Message Tool (NTWC)

The TsunamiMessageTool displays a menu of physical event types, a list of active physical
event Id, Tsunami message types and locations. This will create Tsunami information statement,
Tsunami conference call and other Tsunami messages.

@since: April 2022
@author: GSL Hazard Services Team
"""
import TsunamiRecommenderCommon
import EventSetFactory
import logging, UFStatusHandler


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()
        self.logger = logging.getLogger("TsunamiMessageTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.recommenders.hydro", "TsunamiMessageTool", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiMessageTool (NTWC)",
            "author": "GSL",
            "version": "1.0",
            "description": "Creates hazard events for selected physical event and message types/location"
            }
        return metaDict

    def defineDialog(self, eventSet, **kwargs):
        '''
        @summary: Define the contents of the window that pops up when the tool is launched
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return
        @param kwargs: Additional key word arguments to this method.
        @return: MegaWidget dialog definition to solicit user input before running tool
        '''
        self.timeOfArrivalForecast = None
        self.amplitudeForecast = None
        self.initializeVariablesFromEventSetAttributes(eventSet)

        # Determine the physical event that was selected from the PEM
        selectedEventList = list(self.pem.getSelectedPhysicalEvents())
        errorMsg = self.agu.validateSelectedPhysicalEvent(selectedEventList)
        if errorMsg:
            return {"resultsMessage": errorMsg}

        # Grab information from the single selected event
        selectedEvent = selectedEventList[0]
        self.initializeVariablesFromPhysicalEvent(selectedEvent)
        errorMsg = self.validateActivePhysicalEvent()
        if errorMsg:
            return {"resultsMessage": errorMsg}

        dialogDict = {
            "title": f"Tsunami Message Tool ({self.siteID})",
            "fields": [],
            "valueDict": {}
            }

        dialogDict["fields"] += [
            self.physicalEventMegawidget(selectedEvent),
            self.physicalEventLabelMegawidget(self.physicalEventLabelText_TMT())
            ]

        # Check if selected physical event is a known event, if yes, display known event Megawidget
        if self.isKnownPhysicalEvent(selectedEvent):
            dialogDict["fields"].append(self.knownPhysicalEventMegawidget(selectedEvent))

        # Create TS.S
        tssChoices = self.getTsunamiInfoStatRegionChoices()
        dialogDict["fields"].append(self.createTsunamiInfoStatDialog(tssChoices))

        # Create ConferenceCall
        choices = self.getTsunamiConferenceCallRegionChoices()
        tsunamiConferenceCallDict = {
            "fieldType": "Group",
            "fieldName": "tsccGroup",
            "fields": [
               {
                "fieldType": "CheckBoxes",
                "fieldName": "tsuConfCall",
                "label": "Create TS.ConferenceCall for:",
                "choices": choices,
                "values": []
                }
               ]
            }
        dialogDict["fields"].append(tsunamiConferenceCallDict)

        # Create dialog for TS.WWY, and forecast megawidgets
        dialogDict["fields"] += [
            self.createTsunamiWarningAdvisoryWatchDialog(),
            self.performSurgeryMegawidget(),
            self.forecastSelectionLabelMegawidget(),
            self.timeOfArrivalMegawidget(),
            self.amplitudeSelectionMegawidget(),
            ]

        return dialogDict

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return.
        @param dialogInputMap: Map from call to defineDialog.
        @param spatialInputMap: Map from call to defineSpatialInfo. Ignored
        @return: List of objects that will be later converted to Java Event objects
        '''
        self.procsListDict = {}
        self.trecsExecInfo = self.buildTrecsExecInfo()
        # Filter the input eventSet this tool run to only contain events associated with the selected physical event
        originalEventSet = self.getActiveEventsForPhysicalEvent(eventSet)
        # Determine the active product regions where events are currently issued
        activeProductRegions = set([hazardEvent.get("productRegion") for hazardEvent in originalEventSet if hazardEvent.getHazardType() in ["TS.W", "TS.Y", "TS.A"]])

        # Define the new eventSet that will be returned from this tool
        newEventSet = EventSetFactory.createEventSet()
        # Define the proposed new event set, without surgery applied.
        # One for WWAs and one for non-WWAs
        proposedNewNonWWAEventSet = EventSetFactory.createEventSet()
        proposedNewWWAEventSet = EventSetFactory.createEventSet()

        # First check if this physical event is a known event
        if self.isKnownPhysicalEvent(self.physicalEvent):
            useSpecialProcedure = dialogInputMap.get("useSpecialProcedure")
            if useSpecialProcedure:
                wwaAreaDictList = self.queryThreatDatabaseForKnownEvents()
                proposedNewWWAEventSet = self.createTsunamiWWAFromAreaDictList(wwaAreaDictList, proposedNewWWAEventSet)
                return proposedNewWWAEventSet
        # Pull the user-selected time of arrival and amplitude forecasts
        self.getForecastInfoFromDialogInput(dialogInputMap)

        # Create TS.S for the selected regions
        tssRegions = dialogInputMap.get("tsuInfoStat")
        if len(tssRegions) > 0:
            hazardAttributes = self.getHazardAttributesByMagnitude(self.magnitude)
            proposedNewNonWWAEventSet = self.createTsunamiMessages("TS.S", tssRegions, proposedNewNonWWAEventSet, hazardAttributes)
        # Create Conference call for NTWC if there is selected region
        confCallRegions = dialogInputMap.get("tsuConfCall")
        if len(confCallRegions) > 0:
            proposedNewNonWWAEventSet = self.createTsunamiMessages("TS.ConferenceCall", confCallRegions, proposedNewNonWWAEventSet)
        # Create TS.WWA for NTWC if there is selected region
        tsuWWA = dialogInputMap.get("tsuWWA")
        if len(tsuWWA) > 0:
            tsuParamsDict = self.getTsunamiWWAParameters(dialogInputMap)
            proposedNewWWAEventSet = self.createTsunamiWWAManually(tsuWWA, proposedNewWWAEventSet, tsuParamsDict)

        # Determine if surgery will be performed with the active hazard events
        self.performSurgery = dialogInputMap.get("performSurgery")

        if not proposedNewWWAEventSet.getEvents() and not proposedNewNonWWAEventSet.getEvents():
            newEventSet.addAttribute("resultsMessage", "No Hazard Events were created with the specified TMT parameters.")
        elif not self.performSurgery:
            newEventSet.addAll(proposedNewNonWWAEventSet.events)
            newEventSet.addAll(proposedNewWWAEventSet.events)
        elif self.performSurgery:
            # There are active hazard events for this product region, perform surgery to blend the
            # existing and proposed areas
            # If we find matching product region, do surgery and remove from original set.
            proposedNewEventList = list(proposedNewWWAEventSet.events)
            # We are about to do surgery on WWAs. But if the TMT does not want to create any 
            # (from the UI selections), then surgery will END any existing WWAs. So make sure
            # the user wants to create WWAs first, otherwise we'll inadvertently END existing ones.
            if len(tsuWWA) > 0:
                for productRegion in activeProductRegions:
                    # The proposed eventSet for this product region
                    proposedProdRegionEventSet = EventSetFactory.createEventSet()
                    for i in range(len(proposedNewEventList) - 1, -1, -1):
                        event = proposedNewEventList[i]
                        if event.get("productRegion") == productRegion:
                            proposedProdRegionEventSet.add(event)
                            proposedNewEventList.pop(i)
                    postOpEventSet = self.performEventSurgery(originalEventSet, proposedProdRegionEventSet, productRegion)
                    newEventSet.addAll(postOpEventSet.events)
            # Now add the leftovers (events without active product region)
            newEventSet.addAll(proposedNewEventList)
            newEventSet.addAll(proposedNewNonWWAEventSet)
        return newEventSet

    def getTsunamiInfoStatRegionChoices(self):
        return [
            {"identifier": "AkBcWc", "displayString": "Alaska/British Columbia/U.S. West Coast"},
            {"identifier": "EcGc", "displayString": "U.S. East Coast/Gulf of America/Canada"},
            ]

    def getTsunamiConferenceCallRegionChoices(self):
        return [
            {"identifier": "Atlantic", "displayString": "Atlantic"},
            {"identifier": "Pacific", "displayString": "Pacific"},
            ]


def __str__(self):
    return "TsunamiMessageTool"
