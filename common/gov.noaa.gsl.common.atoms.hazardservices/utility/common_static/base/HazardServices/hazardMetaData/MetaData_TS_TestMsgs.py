# *** Override behavior of MetaData_TS_TestMsgs.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Hazard Information dialog (HID) Metadata megawidgets
    for Tsunami Test Messages.
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
            self.cmdTsu.getTsunamiMetadataRefreshCounter(),
            self.cmdTsu.getPhysicalEventType(self.hazardEvent),
            ]
        details += self.idsHidden
        return details
