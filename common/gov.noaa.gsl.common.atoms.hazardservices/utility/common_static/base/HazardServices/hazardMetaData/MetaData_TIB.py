# *** Override behavior of MetaData_TIB.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Hazard Information dialog (HID) Metadata megawidgets
    for Tsunami Information Statement.
    * Metadata is found under the Type grouping in the HID.
    * For more information about the megawidget framework, see the Google Doc:
    "Megawidget Framework Reference for Focal Points (H.S. Integrated)"
    The link to the document is at the top of CommonMetaData.py.
'''

import CommonMetaData
import CommonMetaData_Tsunami


class MetaData(CommonMetaData.MetaData):

    def initializeOtherVariables(self, hazardEvent, metaDict):
        '''
        @summary: Initialize any other variables that may be
        needed more universally in this file
        @param hazardEvent: The hazard event
        @param metaDict: The metadata dictionary passed into
        the execute() method
        @return: None
        '''
        self.cmdTsu = CommonMetaData_Tsunami.CommonMetaData_Tsunami()

    def execute(self, hazardEvent=None, metaDict={}):
        '''
        @summary: Create all the combobox, radio button, text box, etc. megawidgets
        under the Time Range and Details grouping in the Hazard Information dialog.
        @param hazardEvent: Container holding all the space/time info and metadata
        needed to create watch/warning/advisory products
        @param metaDict: Dictionary containing initial metadata information, defaults to
        an empty dictionary
            example:
                {"lockersForLockedByOthersEventIds": {}, "workStation": "awips2devel",
                "readOnlyTimeRange": False, "site": "PTWC", "newlyAssignedType": False,
                "refreshMetadataKeys": set(), "userName": "awips",
                "correctionEventIds": set(), "eventSite": "PTWC"}
        @return: Dictionary holding a list of megawidgets
        '''
        self.initialize(hazardEvent, metaDict)
        if not self.cmdTsu.getDefaultPhysicalEventType(hazardEvent):
            announcementLabelDict = self.getCannedAnnouncementLabelDict("NoPhyEventSelected")
            metaData = [self.getAnnouncementsGroupWrapper(messageText=announcementLabelDict["text"],
                                                          messageType=announcementLabelDict["labelType"],
                                                          labelBold=announcementLabelDict["labelBold"],
                                                          labelColor=announcementLabelDict["color"])]
            return {"metadata": metaData}

        self.cmdTsu.setEventStartEndTime(self.hazardStatus, hazardEvent)
        details = self.buildDetailsGroup()
        metaData = [self.getDetailsGroupWrapper(details)]

        return {
            "metadata": metaData,
            "modifiedHazardEvent": hazardEvent,
            }

    def buildDetailsGroup(self):
        '''
        @summary: Defines what megawidgets will be visible in the "Details" section of the
        Hazard Information Dialog
        @return: List of dictionaries of megawidget properties
        '''
        fieldNameSuffix = ""
        details = [
            self.cmdTsu.getTsunamiMetadataRefreshCounter(),
            self.cmdTsu.getPhysicalEventType(self.hazardEvent),
            self.cmdTsu.getCustomId(self.hazardEvent),
            self.cmdTsu.getProductRegion(self.hazardEvent),
            self.getTIBEvaluationOptions(),
            self.getCAP_Fields(),
            ]
        details += self.cmdTsu.getPhyEventInfo(self.hazardEvent, fieldNameSuffix)
        details += self.idsHidden
        return details

    def getTIBEvaluationOptions(self):
        '''
        @summary: Create the radio buttons for the "Evaluation Options" megawidget
        @return: Dictionary of megawidget properties
        '''
        if self.hazardEvent and self.hazardEvent.get("tisType"):
            tisType = self.hazardEvent.get("tisType")
        else:
            tisType = self.tisEvaluationChoices()[0].get("identifier")
        return {
            "fieldType": "RadioButtons",
            "fieldName": "tisType",
            "label": "Evaluation Options:",
            "values": tisType,
            "choices": self.tisEvaluationChoices(),
            "useNewValueOnRefresh": True,
            }

    def tisEvaluationChoices(self):
        '''
        @summary: Return choices for the Evaluation Options
        @return: List of dictionaries containing megawidget choice properties
        '''
        return [
            self.tisLow(),
            self.tisHigh(),
            self.tisFinal(),
            ]

    def tisLow(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tisType" megawidget - TIS no threat
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "tisLow",
            "displayString": "TIS no danger",
            }

    def tisHigh(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tisType" megawidget - TIS potential threat
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "tisHigh",
            "displayString": "TIS potential danger",
            }

    def tisFinal(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tisType" megawidget - Final TIS
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "tisFinal",
            "displayString": "TIS final",
            }

    def validate(self, hazardEvent):
        '''
        @summary: Check the values from the selections in the Hazard Information dialog
        to make sure the values make sense.
        @param hazardEvent: Container holding all the space/time info and metadata
        needed to create watch/warning/advisory products
        @see: Overrides CommonMetaData.validate()
        @return: String of error messages found during validation check
        or None if validation was successful
        '''
        validationMethodList = [
            self.validatePhysicalEventID(hazardEvent),
            ]
        validationError = None
        validErrorList = [msg for msg in validationMethodList if msg]
        if validErrorList:
            validationError = "\n\n".join(validErrorList)
        return validationError

    def validatePhysicalEventID(self, hazardEvent):
        '''
        @summary: Validate that a physical event is associated with the hazard event
        @param hazardEvent: Container holding all the space/time info and metadata
        needed to create watch/warning/advisory products
        @return: String of error messages found during validation check
        or None if validation was successful
        '''
        message = None
        if not hazardEvent.get("customId"):
            message = (f"{hazardEvent.getEventID()}: make sure that PEM has at least one active physical event. "
                       "Optionally, close the HID, delete the event, return to the PEM Dialog and set the event "
                       "to ACTIVE, then recreate event.")
        return message


def applyInterdependencies(triggerIdentifiers, mutableProperties, invocationSource):
    '''
    @summary: Interdependency script entry point that will apply changes to the properties of another megawidget
    when a megawidget experiences state changes
    @param triggerIdentifiers: List of megawidgets that experienced a state change
    @param mutableProperties: Dictionary of properties that are able to be changed
    @param invocationSource: String indicating what caused the invocation of the script
    e.g. "user", "constraints", "programmatic"
    @return: Dictionary of properties that were changed
    @see: "Megawidget Framework Reference for Focal Points (H.S. Integrated)" for more details
    on megawidget interdependencies. The link to the document is at the top of CommonMetaData.py.
    '''
    propertyChanges = CommonMetaData.applyStartTimeCurrentTimeEndTimesWithDurationInterdependencies(
                                                                triggerIdentifiers, mutableProperties,
                                                                None, invocationSource)
    return propertyChanges
