# *** Override behavior of TsunamiEventUpdateNotificationTool.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Tool to determine if any active tsunami hazard
    events are issued with potentially out-of-date information
    referenced from an older physical event information
    
    @since: May 2024
    @author: GSL Hazard Services Team
'''

import logging, UFStatusHandler
import EventSetFactory
import JUtil
import TextProductCommon
import TimeUtil
import TsunamiRecommenderCommon
from gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs import SLObsUtils
from gov.noaa.gsl.viz.atomsForecast import TsunamiForecastDao
from gov.noaa.gsl.viz.atomsSeaLevelObs import SeaLevelObsDao


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()

        self.logger = logging.getLogger("TsunamiEventUpdateNotificationTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsl.common.atoms.hazardservices",
            "TsunamiEventUpdateNotificationTool",
            level=logging.INFO))
        self.logger.setLevel(logging.INFO)

        self.slo = SeaLevelObsDao.getInstance()
        self.tfd = TsunamiForecastDao.getInstance()

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiEventUpdateNotificationTool",
            "author": "GSL",
            "version": "1.0",
            "description": ("Alerts the user if active hazard events are out with older "
                            "physical event information")
            }
        return metaDict

    def defineDialog(self, eventSet):
        '''
        @return: MegaWidget dialog definition to solicit user input before running tool
        '''
        pass

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        @summary: Main method for this tool after the 'Run' button is pushed
        @param eventSet: A set of event objects that the user can use to help determine
        new objects to return.
        @param dialogInputMap: Map from call to defineDialog.
        @param visualFeatures: Ignored
        @return: NoneType if no action taken or a modified eventSet
        '''
        # Initialize variables
        self.initializeVariablesFromEventSetAttributes(eventSet)

        # Retrieve all active hazard events
        self.activeHazardsDict = self.getActiveHazardEvents(eventSet)

        # No active events so skip the remainder of the tool
        if not self.activeHazardsDict:
            self.logger.info(("TsunamiEventUpdateNotificationTool - No active "
                              "hazard events found, exiting tool..."))
            return

        # Retrieve all physical events and store only the active ones
        self.activePhysicalEventsList = self.getActivePhysicalEvents()

        # No active physical events so skip the remainder of the tool
        if not self.activePhysicalEventsList:
            self.logger.info(("TsunamiEventUpdateNotificationTool - No active "
                              "physical events found, exiting tool..."))
            return

        # Contains information about what events need to be updated
        self.alertDictionary = {}

        # Check if a physical event was updated in some way
        self.checkForUpdatedPhysicalEventParameters()

        # No events need alerting so exit tool
        if not self.alertDictionary:
            self.logger.info(("TsunamiEventUpdateNotificationTool - No out-of-date "
                              "events found, exiting tool..."))
            return

        # Format the message to be thrown to the user
        resultsMessage = self.formatAlertMessage()
        if resultsMessage:
            # Create empty event set to return
            resultEventSet = EventSetFactory.createEventSet()

            # Add message to be thrown
            resultEventSet.addAttribute("resultsMessage", resultsMessage)

            # Update hazard events to block duplicate notification message
            for customId in self.alertDictionary:
                for newHazardEvent in self.alertDictionary[customId]["hazardEvents"]:
                    newHazardEvent.addHazardAttribute(self.getUpdateToolAttribute(),
                                                      newHazardEvent.getIssuanceCount())
                    metadataRefreshCount = newHazardEvent.get("tsunamiMetadataRefreshCounter")
                    if metadataRefreshCount:
                        newHazardEvent.set("tsunamiMetadataRefreshCounter", metadataRefreshCount + 1)
                    resultEventSet.add(newHazardEvent)
            return resultEventSet

    def getActiveHazardEvents(self, eventSet):
        '''
        @summary: Get all active hazard events, these are events that meet the following criteria:
        1) The event has a hazard status of "ISSUED", "ENDING", or "ELAPSING"
        2) The event has a hazard type of "TS.A", "TS.W", or "TS.Y"
        3) The event's site ID matches the localized site ID
        4) The event has a physical event associated with it
        5) The current event iteration has not already been checked and notified by this tool
        @param eventSet: The set of events seen by the tool
        @return: A dictionary of active events by physical event ID
        '''
        activeEventsDict = {}
        for hazardEvent in eventSet:
            hazardAlreadyChecked = hazardEvent.get(self.getUpdateToolAttribute())
            customId = hazardEvent.get("customId")
            if (self.hasValidHazardStatus(hazardEvent) and
                self.isIssuedByCurrentSite(hazardEvent) and
                self.hasPhysicalEventId(customId) and
                (hazardAlreadyChecked is None or
                hazardAlreadyChecked < hazardEvent.getIssuanceCount())):
                if customId not in activeEventsDict:
                    activeEventsDict[customId] = []
                activeEventsDict[customId].append(hazardEvent)
        return activeEventsDict

    def getActivePhysicalEvents(self):
        '''
        @summary: Get a list of all physical events that meet the following criteria:
        1) Has its 'isActive' attribute set to True
        2) Has active hazard events issued for them as determined by looking at the self.activeHazardsDict
        @return: A list of physical event objects
        '''
        activePhysicalEvents = []
        javaPhysicalEventDict = JUtil.javaObjToPyVal(self.pem.getPhysicalEvents())
        for physicalEventType in javaPhysicalEventDict:
            for javaPhysicalEvent in javaPhysicalEventDict[physicalEventType]:
                # If there are hazards out for this physical event and it is active then store it
                if (javaPhysicalEvent.getCustomId() in self.activeHazardsDict and
                    javaPhysicalEvent.getIsActive()):
                    activePhysicalEvents.append(javaPhysicalEvent)
        return activePhysicalEvents

    def checkForUpdatedPhysicalEventParameters(self):
        '''
        @summary: Determine if any hazard events were issued before a new physical event was put into the database
        @return: NoneType; self.alertDictionary is updated in memory
        '''
        for javaPhysicalEvent in self.activePhysicalEventsList:
            # Get physical event ID
            customId = javaPhysicalEvent.getCustomId()
            # Get the insert time for this physical event
            physicalEventInsertTime = self.getTfsInsertTime(javaPhysicalEvent)
            # Get the insert time for the latest forecast
            forecastInsertTime = None
            forecastList = self.tfd.getMostRecentTsunamiForecast(customId)
            if forecastList:
                forecastInsertTime = self.getTfsInsertTime(forecastList[0])
            # Get the latest sea-level observation set
            latestObsSetInsertTime = None
            allObsSets = self.slo.getSeaLevelObservations(customId, None)
            if allObsSets:
                # latestObs = SLObsUtils.getMostRecentSLObsSet(allObsSets)
                obsSetTimes = sorted([TimeUtil.datetimeToEpochTimeMillis(self.getTfsInsertTime(obsSet)) for obsSet in allObsSets])
                latestObsSetInsertTime = TimeUtil.epochTimeMillisToDatetime(obsSetTimes[-1])
            # Check the hazard issuance time against the reference times
            for hazardEvent in self.activeHazardsDict[customId]:
                issueTime = hazardEvent.getIssueTime()
                # The hazard event was issued prior to the latest physical event time
                if issueTime and self.isIssueTimeBeforeTfsTime(issueTime, physicalEventInsertTime):
                    self.populateAlertDictionary(customId, "New Physical Event Information", hazardEvent)
                # The hazard event was issued prior to the latest forecast run
                if forecastInsertTime and self.isIssueTimeBeforeTfsTime(issueTime, forecastInsertTime):
                    self.populateAlertDictionary(customId, "New Forecast Run(s)", hazardEvent)
                # The hazard event was issued prior to a new set of sea level observations
                if latestObsSetInsertTime and self.isIssueTimeBeforeTfsTime(issueTime, latestObsSetInsertTime):
                    self.populateAlertDictionary(customId, "New Sea Level Observations Set(s)", hazardEvent)

    def populateAlertDictionary(self, customId, updateType, hazardEvent):
        '''
        @summary: Populate the self.alertDictionary when an old hazard event is found
        @param customId: The physical event unique id (e.g., HumboldtDec2024)
        @param updateType: A string notifying what alert needs to be thrown (e.g., physicalEventUpdate,
        forecastUpdate, or seaLevelObsUpdate)
        @param hazardEvent: The hazard event object that is old
        @return: NoneType; self.alertDictionary is updated in memory
        '''
        if customId not in self.alertDictionary:
            self.alertDictionary[customId] = {
                "updateTypes": [],
                "hazardEvents": [],
                }
        if updateType not in self.alertDictionary[customId]["updateTypes"]:
            self.alertDictionary[customId]["updateTypes"].append(updateType)
        eventIDs = [he.getEventID() for he in self.alertDictionary[customId]["hazardEvents"]]
        if hazardEvent.getEventID() not in eventIDs:
            self.alertDictionary[customId]["hazardEvents"].append(hazardEvent)

    def formatAlertMessage(self):
        '''
        @summary: Create the message that will be thrown to the alert dialog window
        @return: String
        '''
        # Get list of physical event IDs and a total number of physical events
        customIDs = list(self.alertDictionary.keys())
        numberOfPhysicalEvents = len(customIDs)

        # Get proper grammar based on number of physical events
        if numberOfPhysicalEvents > 1:
            eventString = "events were"
        else:
            eventString = "event was"

        # Build initial message
        msg = (f"The following physical {eventString} updated after the\n"
                "issuance of one or more hazard events.\n\n")

        # Add to message
        for i in range(numberOfPhysicalEvents):
            customId = customIDs[i]
            updateList = sorted(self.alertDictionary[customId]["updateTypes"])
            hazardEvents = self.alertDictionary[customId]["hazardEvents"]
            parameterUpdates = TextProductCommon.TextProductCommon().joinStringsWithOxfordComma(updateList)
            msg += (f"For physical event ({customId}), the following "
                    f"parameters were updated:\n\n-{parameterUpdates}\n\n"
                    "This affects the following hazard event(s):\n")
            for hazardEvent in hazardEvents:
                msg += f"  - {hazardEvent.getEventID()} ({hazardEvent.getHazardType()})\n"
                msg += "\n"
        msg += "Please re-issue these hazards when appropriate to relay this new information."

        return msg

    def getTfsInsertTime(self, javaObject):
        '''
        @summary: Get the insertion time of a physical event or tsunami forecast
        @param javaObject: A java object being either a PhysicalEvent or TsunamiForecast
        @return: A datetime object
        '''
        tfsCreationTimeEpochMillis = JUtil.javaObjToPyVal(javaObject.getInsertTime().toZonedDateTime().toInstant().toEpochMilli())
        tfsTime = TimeUtil.epochTimeMillisToDatetime(tfsCreationTimeEpochMillis)
        return tfsTime

    def hasValidHazardStatus(self, hazardEvent):
        '''
        @summary: Determine if the hazard event has a valid hazard status in order for
        it to be checked by this tool
        @param hazardEvent: The hazard event being examined
        @return: Boolean
        '''
        return hazardEvent.getStatus().upper() in ["ISSUED", "ENDING", "ELAPSING"]

    def isIssueTimeBeforeTfsTime(self, issueTime, tfsTime):
        '''
        @summary: Check if the issue time is before the physical event parameter insert time
        @param issueTime: The hazard event issue time as a python datetime
        @param tfsTime: The TFS insertion time as a python datetime
        @return: Boolean
        '''
        return issueTime < tfsTime

    def isIssuedByCurrentSite(self, hazardEvent):
        '''
        @summary: Determine if the hazard event was issued by the current site
        @param hazardEvent: The hazard event being examined
        @return: Boolean
        '''
        return hazardEvent.getSiteID() == self.siteID

    def hasPhysicalEventId(self, customId):
        '''
        @summary: Determine if the hazard event has a physical event ID associated with it
        @param customId: The contents of the 'customId' hazard attribute access call
        @return: Boolean
        '''
        if customId:
            return True
        return False

    def getUpdateToolAttribute(self):
        '''
        @summary: Attribute assigned to the hazard event when it has already been examined by this tool
        @return: String
        '''
        return "hazardUpdateToolChecked"


def __str__(self):
    return "Tsunami Event Update Notification Tool"
