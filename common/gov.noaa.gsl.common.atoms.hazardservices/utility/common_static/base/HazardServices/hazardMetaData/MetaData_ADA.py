# *** Override behavior of MetaData_ADA.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Hazard Information dialog (HID) Metadata megawidgets
    for Forecast Information.
    * Metadata is found under the Type grouping in the HID.
    * For more information about the megawidget framework, see the Google Doc:
    "Megawidget Framework Reference for Focal Points (H.S. Integrated)"
    The link to the document is at the top of CommonMetaData.py.
'''

import CommonMetaData
import CommonMetaData_Tsunami
import TimeUtil


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
                {"workStation": "workstation1", "site": "OAX", "newlyAssignedType": True,
                "refreshMetadataKeys": set(), "userName": "awips", "correctionEventIds": set()}
        @return: Dictionary holding a list of megawidgets
        '''
        self.initialize(hazardEvent, metaDict)
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
        details = [
                self.getConferenceLocation(self.hazardEvent),
                self.getConferenceCallTime(),
                ]
        details += self.idsHidden
        return details

    def getConferenceLocation(self, hazardEvent):
        '''
        @summary: Creates the ComboBox for the "Conference Call Location" megawidget
        @return: Dictionary of megawidget properties
        '''
        choices = self.getLocationChoices()
        if hazardEvent and hazardEvent.get("productRegion"):
            callLocation = hazardEvent.get("productRegion")
        else:
            callLocation = choices[0].get("identifier")
        return {
            "fieldType": "ComboBox",
            "fieldName": "callLocation",
            "label": "Conference Call Location:",
            "choices": choices,
            "values": callLocation
            }

    def getLocationChoices(self):
        '''
        @summary: List of tsunami conference call location choices provided to the user
        @return: List of megawidget choices
        '''
        return [
            self.atlanticLocationChoice(),
            self.pacificLocationChoice(),
            ]

    def atlanticLocationChoice(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "callLocation" megawidget - Atlantic
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "Atlantic",
            "displayString": "Atlantic"
        }

    def pacificLocationChoice(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "callLocation" megawidget - Pacific
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "Pacific",
            "displayString": "Pacific"
        }

    def getConferenceCallTime(self):
        '''
        @summary: Creates the TimeScale for the "Conference Call Time" megawidget
        @return: Dictionary of megawidget properties
        '''
        currentTimeMills = TimeUtil.simulatedTimeInMilliseconds()
        return {
            "fieldName": "callTime",
            "fieldType": "TimeScale",
            "valueLabels": {
                "callTime": "Conference Call Time:"
                },
            "snapInterval": {
                "callTime": self.getDefaultSnapInterval()
                },
            "values": {
                "callTime": currentTimeMills
                }
            }

    def getDefaultSnapInterval(self):
        '''
        @summary: The default snap interval for the conference call time megawidget
        @return: Integer
        '''
        return 900


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
