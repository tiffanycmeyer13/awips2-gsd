# *** Override behavior of TsunamiEventChronologyTool.py ***
# -- Override ability: class-based
# -- Levels: All
'''
    Description: Tool to create a event chronology history from a
    selected physical event

    @since: January 2024
    @author: GSL Hazard Services Team
'''

import datetime
import logging, UFStatusHandler
import GeneralUtilities
import HazardDataAccess
import TsunamiRecommenderCommon


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()

        self.logger = logging.getLogger("TsunamiEventChronologyTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.recommenders.hydro", "TsunamiEventChronologyTool",
            level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiEventChronologyTool",
            "author": "GSL",
            "version": "1.0",
            "description": "Creates an event chronology report for the selected physical event"
            }
        return metaDict

    def defineDialog(self, eventSet):
        '''
        @return: MegaWidget dialog definition to solicit user input before running tool
        '''
        self.initializeVariablesFromEventSetAttributes(eventSet)
        self.magnitude = 0
        self.depthInMi = 0
        self.selectedEvent = None
        dialogDict = {
            "title": "Tsunami Event Chronology Tool",
            "fields": [],
            "valueDict": {}
            }

        informationLabelDict = {
            "fieldName": "informationLabel",
            "fieldType": "Label",
            }

        # Determine that a physical event that was selected from the PEM
        selectedEventList = list(self.pem.getSelectedPhysicalEvents())
        errorMsg = self.agu.validateSelectedPhysicalEvent(selectedEventList)

        # No single physical event was selected
        if errorMsg:
            informationLabelDict["label"] = errorMsg
            dialogDict["buttons"] = [{"identifier": "close", "label": "OK", "cancel": True}]
        # A single physical event was selected
        else:
            selectedPhysicalEvent = selectedEventList[0]
            physicalEventName = selectedPhysicalEvent.getName()
            if not physicalEventName:
                physicalEventName = selectedPhysicalEvent.getCustomId()
            informationLabelDict["label"] = ("An event chronology report will be run for the "
                                             f"following physical event:\n\n{physicalEventName}\n\n"
                                             "Do you wish to proceed?")
            dialogDict["fields"].append(self.physicalEventMegawidget(selectedPhysicalEvent))

        dialogDict["fields"].append(informationLabelDict)
        return dialogDict

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        @summary: Main method for this tool after the 'Run' button is pushed
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return.
        @param dialogInputMap: Map from call to defineDialog.
        @param visualFeatures: Ignored
        @return:
        '''
        # Determine CAVE mode
        self.practice = GeneralUtilities.isPractice(eventSet.getAttributes().get("runMode"))

        # Retrieve the selected physical event
        physicalEvent = dialogInputMap.get("physicalEvent")

        # Determine which events from the whole eventSet were issued under this physical event
        matchingEvents = self.getMatchingHazardEvents(physicalEvent, eventSet)

        # Get hazard histories for each matching hazard event
        hazardChronologyDict = self.getHazardEventChronology(matchingEvents)

        # Assemble results message
        resultsMessageList = [f"Physical Event ID: {physicalEvent.getCustomId()}\n"]
        for issueTime in sorted(list(hazardChronologyDict.keys())):
            resultsMessageList.append(f"Time (UTC): {issueTime}\n")
            for hazardRecord in hazardChronologyDict[issueTime]:
                resultsMessageList.append(f"{hazardRecord}\n")
            resultsMessageList.append("---------------------------------------------------\n")

        # Default message if no hazard events were issued for this physical event
        if not hazardChronologyDict:
            resultsMessageList.append("No tsunami hazard events were issued for this physical event.")

        # Convert list of messages into a single string and add it to the eventSet
        resultsMessage = "\n".join(resultsMessageList)
        eventSet.addAttribute("resultsMessage", resultsMessage)
        return eventSet

    def getMatchingHazardEvents(self, physicalEvent, eventSet):
        '''
        @summary: Determine the hazard events that are linked to the selected physical event
        @param physicalEvent: The selected physical event
        @param eventSet: All events in the Hazard Services registry
        @return: A list of Hazard Events
        '''
        physicalEventCustomID = physicalEvent.getCustomId()
        matchingEvents = [hazardEvent for hazardEvent in eventSet
                          if hazardEvent.get("customId") == physicalEventCustomID]
        return matchingEvents

    def getHazardEventChronology(self, matchingEvents):
        '''
        @summary: Get chronology of all matching events and organize them into a dictionary
        by issuance time
        @param matchingEvents: A list of hazardEvent objects
        @return: Dictionary
        '''
        chronologyDict = {}
        for hazardEvent in matchingEvents:
            eventID = hazardEvent.getEventID()
            hazardType = hazardEvent.getHazardType()
            hazardHistoryList = HazardDataAccess.getHistoricalHazardEvents(eventID, self.practice)
            for historicalEvent in hazardHistoryList:
                issueTime = historicalEvent.getIssueTime().strftime("%Y-%m-%d %H:%M:%S")
                ugcString = historicalEvent.get("ugcString")
                status = historicalEvent.getStatus()
                if issueTime not in chronologyDict:
                    chronologyDict[issueTime] = []
                entryString = f"  Event: {eventID}\n  Type: {hazardType} ({status})\n  Area: {ugcString}"
                chronologyDict[issueTime].append(entryString)
        return chronologyDict


def __str__(self):
    return "Tsunami Event Chronology Tool"
