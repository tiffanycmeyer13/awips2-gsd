# *** Override behavior of TsunamiCommTestMessageTool.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
Tsunami Comms Test Message Tool (PTWC)

The TsunamiCommTestMessageTool allows for creation of tsunami communications test messages.

@since: August 2025
@author: GSL Hazard Services Team
"""
import logging, UFStatusHandler
import EventSetFactory
import TsunamiRecommenderCommon
from gov.noaa.gsl.common.dataplugin.pem import PhysicalEvent, PhysicalEventType


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()
        self.logger = logging.getLogger("TsunamiCommTestMessageTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.recommenders.hydro", "TsunamiCommTestMessageTool", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiCommTestMessageTool (PTWC)",
            "author": "GSL",
            "version": "1.0",
            "description": "Creates Communication Test hazard events"
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

        # Fake the physical event
        selectedEvent = PhysicalEvent()
        selectedEvent.setName("CommTestFakeEvent")
        selectedEvent.setEventType(PhysicalEventType.UNKNOWN)
        selectedEvent.setCustomId("CommTestFakeEvent")
        selectedEvent.setSource("PTWC")
        selectedEvent.setLatitude(20.0)
        selectedEvent.setLongitude(-105.0)
        selectedEvent.setIsKnownEvent(True)
        selectedEvent.setIsActive(True)

        self.initializeVariablesFromPhysicalEvent(selectedEvent)

        dialogDict = {
            "title": f"Tsunami Comm Test Message Tool ({self.siteID})",
            "fields": [],
            "valueDict": {}
            }

        dialogDict["fields"] += [
            self.physicalEventMegawidget(selectedEvent),
            self.physicalEventLabelMegawidget(f"For {self.physicalEventID}, select hazards to be created:")
            ]

        # If cave mode is practice or test, not operational mode, create test messages dialog
        choices = self.getTsunamiCommTestMessageRegionChoices()
        dialogDict["fields"].append(self.createTsunamiTestMessagesDialog(choices))

        return dialogDict

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return.
        @param dialogInputMap: Map from call to defineDialog.
        @param spatialInputMap: Map from call to defineSpatialInfo. Ignored
        @return: List of objects that will be later converted to Java Event objects
        '''
        newEventSet = EventSetFactory.createEventSet()

        # Create Test messages if there is selected type
        testMsgTypes = dialogInputMap.get("tsuTestMsgs")
        if len(testMsgTypes) > 0:
            for hazardType in testMsgTypes:
                hazardAttributes = {}
                if hazardType == "TS.CommunicationTest":
                    hazardAttributes["createdByTMT"] = True
                    tssTestRegions = dialogInputMap.get("tsuCommuTestMsgs")
                    if len(tssTestRegions) > 0:
                        hazardAttributes["createdByTMT"] = True
                        newEventSet = self.createTsunamiMessages("TS.CommunicationTest", tssTestRegions, newEventSet, hazardAttributes)

        if not newEventSet.getEvents():
            newEventSet.addAttribute("resultsMessage", "No Hazard Events were created with the specified TCTMT parameters.")

        return newEventSet

    def getTsunamiCommTestMessageRegionChoices(self):
        return [
            {"identifier": "IntlPacCommTest", "displayString": "Pacific"},
            {"identifier": "IntlCarCommTest", "displayString": "Caribbean"},
            ]


def __str__(self):
    return "TsunamiCommTestMessageTool"
