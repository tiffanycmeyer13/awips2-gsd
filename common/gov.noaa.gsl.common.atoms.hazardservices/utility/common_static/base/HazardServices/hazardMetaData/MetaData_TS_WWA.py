# *** Override behavior of MetaData_TS_WWA.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Hazard Information dialog (HID) Metadata megawidgets
    for Tsunami Warning/Advisory/Watch.
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
        self.siteID = metaDict.get("eventSite")
        self.mapName = metaDict.get("geometryCreationMapName")

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
        # Initialize all global variables
        self.initialize(hazardEvent, metaDict)
        # If no physical event selected, throw announcement banner
        if not self.cmdTsu.getDefaultPhysicalEventType(hazardEvent):
            announcementLabelDict = self.getCannedAnnouncementLabelDict("NoPhyEventSelected")
            metaData = [self.getAnnouncementsGroupWrapper(messageText=announcementLabelDict["text"],
                                                          messageType=announcementLabelDict["labelType"],
                                                          labelBold=announcementLabelDict["labelBold"],
                                                          labelColor=announcementLabelDict["color"])]
            return {"metadata": metaData}
        # Set creation, start, and end times to the hazard event
        self.cmdTsu.setEventStartEndTime(self.hazardStatus, hazardEvent)
        # Build megawidgets that go into the 'Details section of the HID
        details = self.buildDetailsGroup()
        # Build meta data list
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
        # Mandatory fields that will exist regardless of status
        details = [
            self.cmdTsu.getTsunamiMetadataRefreshCounter(),
            self.cmdTsu.getPhysicalEventType(self.hazardEvent),
            self.cmdTsu.getCustomId(self.hazardEvent),
            self.cmdTsu.getProductRegion(self.hazardEvent),
            self.getLocationCoverage(),
            self.getForceSegment(),
            ]
        if self.isStatusNoLongerIssued(self.hazardStatus):
            details.append(self.getEndingOption(self.isStatusEndingOrElapsing(self.hazardStatus)))
        else:
            details += self.getInclusionReferenceAreas()
            if self.hazardType in ["TS.Y", "TS.W"]:
                details.append(self.getImpacts(self.getDefaultImpacts()))
            details += [
                    self.getCTAs(self.getDefaultCTAs()),
                    self.getCAP_Fields(),
                    ]

        details += self.idsHidden
        return details

    def getLocationCoverage(self):
        '''
        @summary: RadioButtons megawidget to determine whether this hazard event only covers
        break point segments, special procedure areas, or both
        @return: Dictionary of megawidget properties
        '''
        widgetDict = {
            "fieldType": "HiddenField",
            "fieldName": "wwaLocationCoverage",
            }
        if self.siteID == "NTWC":
            currentCoverageChoice = self.hazardEvent.get("wwaLocationCoverage")
            if self.mapName and not currentCoverageChoice:
                if "Special Procedure" in self.mapName:
                    currentCoverageChoice = "specialAreas"
                else:
                    currentCoverageChoice = "segmentAreas"
            widgetDict["values"] = currentCoverageChoice
        else:
            widgetDict["values"] = "segmentAreas"
        return widgetDict

    def endingOptionChoices(self):
        '''
        @summary: Return choices for the Ending Option(s) megawidget
        @return: List of dictionaries containing megawidget choice properties
        '''
        return [
            self.noTsunamiDanger(),
            ]

    def noTsunamiDanger(self):
        '''
        @summary: Specify the megawidget choice properties for the
        "No tsunami danger" choice for the Ending Option(s):
        megawidget.
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "noTsunamiDanger",
            "displayString": "No tsunami danger",
            "productString": "No tsunami danger exists for this area.",
            }

    def getInclusionReferenceAreas(self):
        '''
        @summary: Builds three megawidgets based on the break point segments
        included in the hazard event and how AtomsProductLocationInfo.py is
        configured:

        #1 - An optional checkBoxes megawidget of geographical reference
        locations, defined using 'inclusionReferencePoints', for the
        affected break point segments. If no reference points exist then
        a HiddenField megawidget will be created.
        #2 - An optional checkBoxes megawidget of special procedure
        locations, defined using 'inclusionSpecialProcedures', for the
        affected break point segments. If no special procedures exist then
        a HiddenField megawidget will be created.
        #3 - An HiddenField megawidget containing a list of all possible
        special procedure choices available for this hazard event

        @return: A dictionary of megawidget information
        '''
        currentHazardLocations = self.hazardEvent.get("hazardLocations")
        inclusionReferenceDict = {
            "fieldType": "HiddenField",
            "fieldName": "inclusionReferences",
            "values": [],
            }
        specialProcedureSelectionDict = {
            "fieldType": "HiddenField",
            "fieldName": "specialProcedureSelections",
            "values": [],
            }
        specialProcedureChoicesDict = {
            "fieldType": "HiddenField",
            "fieldName": "specialProcedureOptions",
            "values": [],
            "useNewValueOnRefresh": True,
            }
        if currentHazardLocations:
            locInfoDict = self.bridge.getAtomsProductLocationInfo()
            inclusionChoices = [] ; inclusionValues = []
            specialChoices = [] ; specialValues = []
            for segment in currentHazardLocations:
                if segment in locInfoDict:
                    refDict = locInfoDict[segment]["inclusionReferencePoints"]
                    for location in refDict:
                        if location not in inclusionChoices:
                            inclusionChoices.append(location)
                        if refDict[location] and location not in inclusionValues:
                            inclusionValues.append(location)
                    specDict = locInfoDict[segment]["inclusionSpecialProcedures"]
                    for location in specDict:
                        if location not in specialChoices:
                            specialChoices.append(location)
                        if specDict[location] and location not in specialValues:
                            specialValues.append(location)
            if inclusionChoices:
                inclusionReferenceDict["fieldType"] = "CheckBoxes"
                inclusionReferenceDict["label"] = "Include Geographical Reference Points:"
                inclusionReferenceDict["choices"] = inclusionChoices
                inclusionReferenceDict["values"] = inclusionValues
            if specialChoices:
                specialProcedureSelectionDict["fieldType"] = "CheckBoxes"
                specialProcedureSelectionDict["label"] = "Include Special Procedure Areas:"
                specialProcedureSelectionDict["choices"] = specialChoices
                specialProcedureSelectionDict["values"] = specialValues
                specialProcedureSelectionDict["modifyTool"] = "ModifyTsunamiTool"
                specialProcedureChoicesDict["values"] = specialChoices
        return [inclusionReferenceDict, specialProcedureSelectionDict,
                specialProcedureChoicesDict]

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
    if not propertyChanges:
        propertyChanges = {}
    return propertyChanges
