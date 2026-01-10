# *** Override behavior of ObservatoryMessageTool.py ***
# -- Override ability: class-based
# -- Levels: All
'''
    Description: Tool to create an observatory message product

    @since: November 2023
    @author: GSL Hazard Services Team
'''

import logging, UFStatusHandler
import AtomsGeneralUtilities
import EventFactory
import EventSetFactory
import GeometryUtilities
import TimeUtil
import TsunamiRecommenderCommon


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()

        self.logger = logging.getLogger("ObservatoryMessageTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.recommenders.hydro", "ObservatoryMessageTool",
            level=logging.INFO))
        self.logger.setLevel(logging.INFO)

        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.geomUtils = GeometryUtilities.GeometryUtilities()

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        return {
            "toolName": "ObservatoryMessageTool",
            "author": "GSL",
            "version": "1.0",
            "description": "Creates an observatory message for the physical event"
            }

    def defineDialog(self, eventSet):
        '''
        @return: MegaWidget dialog definition to solicit user input before running tool
        '''
        self.initializeVariablesFromEventSetAttributes(eventSet)
        self.magnitude = 0
        self.depthInMi = 0
        self.selectedEvent = None
        self.physicalEventID = "No_Event_ID"
        dialogDict = {
            "title": "Observatory Message Tool",
            "fields": [],
            "valueDict": {}
            }
        # Determine the physical event that was selected from the PEM
        selectedEventList = list(self.pem.getSelectedPhysicalEvents())
        # There is no physical event selected, reminder user to enter physical event parameters manually
        fieldEditable = False
        if len(selectedEventList) < 1:
            fieldEditable = True
            enterParamtersDict = {
                "fieldType": "Group",
                "fieldName": "enterParametersGroup",
                "topMargin": 10,
                "bottomMargin": 10,
                "expandHorizontally": True,
                "fields": [
                    {
                    "fieldType": "Label",
                    "fieldName": "enterParametersLabel",
                    "label": ("Manually enter physical event parameters or select a physical event from "
                              "the PEM Dialog and rerun OMT"),
                    "labelColor": {"red": 0, "green": 0, "blue": 1},
                    "bold": True,
                    }
                ]
            }
            dialogDict["fields"].append(enterParamtersDict)
        else:
            self.selectedEvent = selectedEventList[0]
            self.initializeVariablesFromPhysicalEvent(self.selectedEvent)
            dialogDict["fields"] += [
                self.physicalEventLabelMegawidget("Create a Tsunami Observatory Message for "
                                                  f"{self.physicalEventType} {self.physicalEventID}\n")]

        # Default physical event type
        peType = "Seismic"
        if self.selectedEvent:
            peType = self.physicalEventType
        physicalEventTypeDict = self.createPhysicalEventTypeMegawidget(fieldEditable, peType)
        # Origin group, which includes origin time, lon, lat, location
        originGroupDict = self.createOriginGroupMegawidgets(fieldEditable)
        dialogDict["fields"] += [physicalEventTypeDict, originGroupDict]
        if peType == "Seismic":
            dialogDict["fields"].append(self.createSeismicGroupMegawidgets(fieldEditable))
        elif peType in ["Volcanic", "Landslide"]:
            dialogDict["fields"].append(self.createOtherInfoMegawidgets(fieldEditable,
                                                                        peType))

        '''
        Determine if one physical event was selected from the PEM.
        If selected, use it to populate physical event properties,
        otherwise ask user to enter this information manually.
        Need to re-initiate self.magnitude and self.depthInMi,
        otherwise it will get previous seismic information even
        this is landslide/volcanic.
        '''
        if self.selectedEvent:
            originTime = self.selectedEvent.getRefTime().getTime()
            peName = self.selectedEvent.getName()
            dialogDict["valueDict"] = {
                "physicalEventType": self.physicalEventType,
                "originTime": originTime,
                "originLongitude": self.longitude,
                "originLatitude": self.latitude,
                "magnitude": self.magnitude,
                "originDepth": self.depthInMi,
                "peName": peName,
                }

        return dialogDict

    def createPhysicalEventTypeMegawidget(self, isEditable, peType):
        '''
        @summary: Creates the 'Physical Event Type' ComboBox of megawidget
        @param isEditable: Boolean to determine if these megawidgets
        can be edited
        @param peType: The physical event type (e.g., Seismic)
        @return: Dictionary of megawidget properties
        '''
        choices = [singleType.getLabel() for singleType in self.pem.getPhysicalEventTypes()]
        return {
            "fieldType": "ComboBox",
            "fieldName": "physicalEventType",
            "label": "Physical Event Type:",
            "choices": choices,
            "values": peType,
            "editable": isEditable
            }

    def createOriginGroupMegawidgets(self, isEditable):
        '''
        @summary: Creates the 'Origin' group of megawidgets
        @param isEditable: Boolean to determine if these megawidgets
        can be edited
        @return: Dictionary of megawidget properties
        '''
        nowMillis = TimeUtil.simulatedTimeInMilliseconds()
        return {
            "fieldName": "originGroup",
            "fieldType":"Group",
            "label": "Origin",
            "spacing": 5,
            "leftMargin": 5,
            "rightMargin": 5,
            "topMargin": 5,
            "bottomMargin": 5,
            "numColumns": 3,
            "expandHorizontally": True,
            "expandVertically": False,
            "fields": [
                {
                    "fieldType": "Time",
                    "fieldName": "originTime",
                    "label": "Origin Time: ",
                    "values": nowMillis,
                    "editable": isEditable
                    },
                {
                    "fieldType": "FractionSpinner",
                    "fieldName": "originLongitude",
                    "label": "Longitude:",
                    "sendEveryChange": False,
                    "minValue":-180,
                    "maxValue": 180,
                    "values": 0,
                    "incrementDelta": 0.5,
                    "precision": 2,
                    "editable": isEditable
                    },
                {
                    "fieldType": "FractionSpinner",
                    "fieldName": "originLatitude",
                    "label": "Latitude:",
                    "sendEveryChange": False,
                    "minValue":-90,
                    "maxValue": 90,
                    "values": 0,
                    "incrementDelta": 0.5,
                    "precision": 2,
                    "editable": isEditable
                    },
                ]
            }

    def createSeismicGroupMegawidgets(self, isEditable):
        '''
        @summary: Creates the 'Seismic Information' group of megawidgets
        @param isEditable: Boolean to determine if these megawidgets
        can be edited
        @return: Dictionary of megawidget properties
        '''
        return {
            "fieldName": "seismicGroup",
            "fieldType":"Group",
            "label": "Seismic Information: ",
            "spacing": 5,
            "leftMargin": 5,
            "rightMargin": 5,
            "topMargin": 5,
            "bottomMargin": 5,
            "numColumns": 2,
            "expandHorizontally": True,
            "expandVertically": False,
            "fields": [
                {
                    "fieldType": "FractionSpinner",
                    "fieldName": "magnitude",
                    "label": "Magnitude:",
                    "sendEveryChange": False,
                    "minValue": 0,
                    "maxValue": 10,
                    "values": 0,
                    "incrementDelta": 0.1,
                    "precision": 1,
                    "editable": isEditable
                    },
                {
                    "fieldType":"ComboBox",
                    "fieldName": "magnitudeType",
                    "label": "Type:",
                    "values": "Moment_P",
                    "useNewValueOnRefresh": True,
                    "choices": self.agu.getMagnitudeTypeChoices(),
                    "editable": isEditable
                    },
                {
                    "fieldType": "IntegerSpinner",
                    "fieldName": "numStationAverage",
                    "label": "Number Station Average:",
                    "sendEveryChange": False,
                    "minValue": 0,
                    "maxValue": 99,
                    "values": 0,
                    "incrementDelta": 1,
                    "editable": True
                    },
                {
                    "fieldType": "FractionSpinner",
                    "fieldName": "originDepth",
                    "label": "Depth (mi):",
                    "sendEveryChange": False,
                    "minValue": 0,
                    "maxValue": 700,
                    "values": 0,
                    "incrementDelta": 1,
                    "editable": isEditable
                    },
                ]
            }

    def createOtherInfoMegawidgets(self, isEditable, peType):
        '''
        @summary: Creates the '{TYPE} Information' group of megawidgets
        @param isEditable: Boolean to determine if these megawidgets
        can be edited
        @param peType: The physical event type (e.g., Seismic)
        @return: Dictionary of megawidget properties
        '''
        return {
            "fieldName": "otherPhysicalEventTypeGroup",
            "fieldType":"Group",
            "label": f"{peType} Information: ",
            "spacing": 5,
            "leftMargin": 5,
            "rightMargin": 5,
            "topMargin": 5,
            "bottomMargin": 5,
            "numColumns": 3,
            "expandHorizontally": True,
            "expandVertically": False,
            "fields": [
                {
                    "fieldType": "Text",
                    "fieldName": "peName",
                    "label": f"{peType} Name:",
                    "values": "",
                    "visibleChars": 40,
                    "editable": isEditable
                    },
                ]
            }

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        Runs the ObservatoryMessageTool

        @param eventSet: A set of events which include session
                         attributes
        @param dialogInputMap: A map of information retrieved from
                               a user's interaction with a dialog;
                               not used by this tool.
        @param visualFeatures: Input gathering visual features; not
                               used by this tool.
        @return: Set of events that were changed.
        '''
        newEventSet = EventSetFactory.createEventSet()
        # Need populated information from dialog into eventDict, then it can be displayed in the formatter
        hazardEvent = EventFactory.createEvent(self.practice)
        hazardEvent.setPhenomenon("TS")
        hazardEvent.setSignificance("ObservatoryMessage")
        hazardEvent.setStatus("POTENTIAL")
        physicalEventType = dialogInputMap.get("physicalEventType")
        hazardEvent.set("physicalEventType", physicalEventType)
        numStationAverage = dialogInputMap.get("numStationAverage")
        hazardEvent.set("numStationAverage", numStationAverage)
        hazardEvent.set("customId", self.physicalEventID)
        hazardEvent.set("originTime", dialogInputMap.get("originTime"))
        peLat = dialogInputMap.get("originLatitude")
        peLon = dialogInputMap.get("originLongitude")
        hazardEvent.set("originLongitude", peLon)
        hazardEvent.set("originLatitude", peLat)
        hazardGeometry = self.geomUtils.bufferPoint(peLat, peLon, 5)
        advancedGeometry = self.geomUtils.convertFromShapelyToAdvancedGeometry(hazardGeometry, 0)
        hazardEvent.setGeometry(advancedGeometry)
        # The following field is related with physical event type
        if physicalEventType == "Seismic":
            hazardEvent.set("magnitude", dialogInputMap.get("magnitude"))
            hazardEvent.set("magnitudeType", dialogInputMap.get("magnitudeType"))
            hazardEvent.set("originDepth", dialogInputMap.get("originDepth"))
        elif physicalEventType in ["Volcanic", "Landslide"]:
            hazardEvent.set("peName", dialogInputMap.get("peName"))
        hazardEvent.set("createdByOMT", True)
        hazardEvent.set("national", True)
        newEventSet.add(hazardEvent)

        return newEventSet
