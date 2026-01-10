# *** Override behavior of MetaData_TSU.py ***
# -- Override ability: Class-based
# -- Levels: All

'''
    Description: Product staging dialog metadata for TSU products.
'''

import CommonMetaData
import CommonMetaData_Tsunami


class MetaData(CommonMetaData.MetaData):

    def __init__(self):
        super().__init__()
        self.cmdTsu = CommonMetaData_Tsunami.CommonMetaData_Tsunami()

    def execute(self, hazardEvents=None, metaDict={}):
        '''
        @summary: Create all the combobox, radio button, text box, etc. megawidgets
        within the 'Product Staging' window
        @param hazardEvents: A list of all hazard events passed into product generation
        @param metaDict: Dictionary containing initial metadata information, defaults to
        an empty dictionary
        Example:
        {'productSegmentGroup': {'productID': 'TSU', 'productName': 'Tsunami Watch/Warning/Advisory',
        'geoType': 'polygon', 'productLabel': 'TSU_HumboldtDec2024_AkBcWc', 'actions': ['NEW'],
        'eventIDs': ['HZ-2025-NTWC-NTWC-403']}, 'productCategory': 'TSU', 'stagingDialogValues': None}
        @return: Dictionary holding a list of megawidgets
        '''
        executeDict = {
            "metadata": []
            }
        if not hazardEvents:
            return executeDict
        productSegmentGroup = metaDict.get("productSegmentGroup")
        productLabel = productSegmentGroup.get("productLabel")
        fieldNameSuffix = f"_{productLabel}"
        details = self.buildProductStagingDetailsGroup(hazardEvents, fieldNameSuffix)
        executeDict["metadata"] = details
        return executeDict

    def buildProductStagingDetailsGroup(self, hazardEvents, fieldNameSuffix):
        '''
        @summary: Defines what megawidgets will be visible in the "Details" section of the
        Hazard Information Dialog or populate the product staging dialog
        @param hazardEvents: Container holding all the space/time info and metadata
        needed to create watch/warning/advisory products
        @param fieldNameSuffix: Suffix added to all identifier megawidget descriptions
        (e.g., _TSU_HumboldtDec2024_AkBcWc)
        @return: List of dictionaries of megawidget properties
        '''
        customId = hazardEvents[0].get("customId")
        siteID = hazardEvents[0].getSiteID()
        peDetails = []
        if self.areAllHazardsAreEndingOrElapsing(hazardEvents):
            peDetails.append(self.getCancellationOption(siteID, fieldNameSuffix))
        else:
            if self.areAnyHazardEventsIssued(hazardEvents):
                peDetails.append(self.getUpdates(fieldNameSuffix))
            if siteID == "NTWC":
                peDetails.append(self.getStillEvaluatingSelector(hazardEvents[0], fieldNameSuffix))
            peDetails += self.cmdTsu.getPhysicalEventInfoAndForecastSeaLevelTables(hazardEvents, fieldNameSuffix)
            peDetails.append(self.cmdTsu.getEventForecastStations(hazardEvents, customId, fieldNameSuffix))
        return peDetails

    def areAllHazardsAreEndingOrElapsing(self, hazardEvents):
        '''
        @summary: Check if all hazard events have a status of ending, ended,
        elapsing, or elapsed
        @param hazardEvents: A list of hazard events brought into product generation
        @return: Boolean
        '''
        return all([self.isStatusNoLongerIssued(hazardEvent.getStatus())
                    for hazardEvent in hazardEvents])

    def areAnyHazardEventsIssued(self, hazardEvents):
        '''
        @summary: Check if any hazard events have a status of issued
        @param hazardEvents: A list of hazard events brought into product generation
        @return: Boolean
        '''
        return any([True for hazardEvent in hazardEvents
                    if hazardEvent.getStatus().upper() == "ISSUED"])

    def getStillEvaluatingSelector(self, hazardEvent, fieldNameSuffix):
        '''
        @summary: RadioButtons megawidget to specify whether locations outside of the
        watch/warning/advisory are still being evaluated and could be included in
        another message
        @param hazardEvent: Container holding all the space/time info and metadata
        needed to create watch/warning/advisory products
        @param fieldNameSuffix: The suffix added to all of the field names
        @return: Dictionary of megawidget identifiers
        '''
        evaluationChoice = hazardEvent.get(f"stillEvaluatingDanger{fieldNameSuffix}")
        if not evaluationChoice:
            evaluationChoice = self.getEvaluationChoices()[0]["identifier"]
        return {
            "fieldType": "RadioButtons",
            "fieldName": f"stillEvaluatingDanger{fieldNameSuffix}",
            "label": "Still Evaluating Other Locations:",
            "choices": self.getEvaluationChoices(),
            "values": evaluationChoice,
            }

    def getEvaluationChoices(self):
        '''
        @summary: Choices for the "stillEvaluatingDanger" megawidget
        @return: List of megawidget choices
        '''
        return [
            self.dangerStillBeingEvaluated(),
            self.noDangerExpected()
            ]

    def dangerStillBeingEvaluated(self):
        '''
        @summary: stillEvaluatingDanger megawidget choice that other locations are still
        being evaluated for a tsunami threat
        @return: A dictionary of choice properties
        '''
        return {
            "identifier": "dangerStillBeingEvaluated",
            "displayString": "Other locations still being evaluated for tsunami threat",
            }

    def noDangerExpected(self):
        '''
        @summary: stillEvaluatingDanger megawidget choice that no other locations are
        under threat of tsunami danger
        @return: A dictionary of choice properties
        '''
        return {
            "identifier": "noOtherDangerExpected",
            "displayString": "No tsunami threat at other locations",
            }

    def getUpdates(self, fieldNameSuffix):
        '''
        @summary: Builds the 'User Input Updates' group to be shown to the user
        when the product staging dialog window is thrown
        @param fieldNameSuffix: The suffix added to all of the field names
        @return: A dictionary of megawidget properties
        '''
        return {
            "fieldName": f"updatesGroup{fieldNameSuffix}",
            "fieldType":"Group",
            "label": "Updates",
            "spacing": 5,
            "leftMargin": 5,
            "rightMargin": 5,
            "topMargin": 5,
            "bottomMargin": 5,
            "expandHorizontally": True,
            "expandVertically": False,
            "fields": [
                {
                    "fieldName": f"userInputUpdates{fieldNameSuffix}",
                    "fieldType": "Text",
                    "label": "User Input Updates:",
                    "visibleChars": 60,
                    "lines": 4,
                    "values": "",
                    "expandHorizontally": True
                    },
                {
                    "fieldType": "CheckBoxes",
                    "fieldName": f"predefinedUpdates{fieldNameSuffix}",
                    "label": "Predefined Updates:",
                    "choices": self.getPredefinedUpdatesChoices(),
                    "values": [],
                    }
                ]
            }

    def getPredefinedUpdatesChoices(self):
        '''
        @summary: List of tsunami predefined update choices provided to the user
        @return: List of megawidget choices
        '''
        return [
            self.tsunamiConfirmedImpactsExpected(),
            self.updatedObservations(),
            self.revisedAlertArea(),
            self.revisedMagnitude(),
            self.revisedForecastInformation()
            ]

    def tsunamiConfirmedImpactsExpected(self):
        '''
        @summary: Specify the megawidget choice properties for the
        "tsunamiConfirmedImpactsExpected" choice for the "updates" megawidget
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "tsunamiConfirmedImpactsExpected",
            "displayString": "A Tsunami has been confirmed and some impacts are expected",
            "productString": "A Tsunami has been confirmed and some impacts are expected",
            "spanishProductString": "Se ha confirmado un Tsunami y se esperan algunos impactos",
            }

    def updatedObservations(self):
        '''
        @summary: Specify the megawidget choice properties for the
        "updatedObservations" choice for the "updates" megawidget
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "updatedObservations",
            "displayString": "Updated observations",
            "productString": "Updated observations",
            "spanishProductString": "Observaciones actualizadas",
            }

    def revisedAlertArea(self):
        '''
        @summary: Specify the megawidget choice properties for the
        "revisedAlertArea" choice for the "updates" megawidget
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "revisedAlertArea",
            "displayString": "Revised alert area",
            "productString": "Revised alert area",
            "spanishProductString": "Área de alerta revisada",
            }

    def revisedMagnitude(self):
        '''
        @summary: Specify the megawidget choice properties for the
        "revisedMagnitude" choice for the "updates" megawidget
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "revisedMagnitude",
            "displayString": "Revised magnitude",
            "productString": "Revised magnitude",
            "spanishProductString": "Magnitud revisada",
            }

    def revisedForecastInformation(self):
        '''
        @summary: Specify the megawidget choice properties for the
        "revisedForecastInformation" choice for the "updates" megawidget
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "revisedForecastInformation",
            "displayString": "Revised forecast information",
            "productString": "Revised forecast information",
            "spanishProductString": "Información de pronóstico revisada",
            }

    def getCancellationOption(self, siteID, fieldNameSuffix):
        '''
        @summary: Get the cancellation choices
        @param siteID: Site identifier, either PTWC or NTWC
        @param fieldNameSuffix: The suffix added to all of the field names
        @return: List of dictionaries containing megawidget choice properties
        '''
        return {
            "fieldType": "RadioButtons",
            "fieldName": f"tsunamiCancel_{fieldNameSuffix}",
            "label": "Tsunami cancellation reasons:",
            "choices": self.getCancellationChoices(siteID),
            }

    def getCancellationChoices(self, siteID):
        '''
        @summary: List of tsunami cancellation choices provided to the user
        @param siteID: Site identifier, either PTWC or NTWC
        @return: List of megawidget choices
        '''
        choices = []
        if siteID == "NTWC":
            choices = [
                self.noTsunamiOccurred(),
                self.noDamagingTsunamiOccurredInOAR(),
                self.damagingTsunamiOccurredInOAR(),
                ]
        elif siteID == "PTWC":
            choices = [
                self.noTsunamiGeneratedAtSource(),
                self.tsunamiGeneratedNoThreat(),
                self.forecastIndicatedNoThreat(),
                self.tsunamiNotGeneratedOrBelowWarningAdvisory(),
                self.destructiveTsunamiGeneratedFallBelowNow(),
                ]
        return choices

    # NTWC cancellation choices
    def noTsunamiOccurred(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - No tsunami occurred
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "noTsunami",
            "displayString": "No tsunami occurred",
            }

    def noDamagingTsunamiOccurredInOAR(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - No damaging tsunami occurred in the OAR
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "noDamagingTsunamiInOAR",
            "displayString": "No damaging tsunami occurred in the AOR",
            }

    def damagingTsunamiOccurredInOAR(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - A damaging tsunami occurred in the OAR
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "damagingTsunamiInOAR",
            "displayString": "A damaging tsunami occurred in the AOR",
            }

    # PTWC cancellation choices
    def noTsunamiGeneratedAtSource(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - A tsunami not generated at the source
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "noTsunamiAtSource",
            "displayString": "A tsunami not generated at the source",
            }

    def tsunamiGeneratedNoThreat(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - A tsunami generated, but small no threat
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "tsunamiGeneratedNoThreat",
            "displayString": "A tsunami generated, but small no threat",
            }

    def forecastIndicatedNoThreat(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - the model forecast indicated no threat
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "forecastIndicatedNoThreat",
            "displayString": "The model forecast indicated no threat",
            }

    def tsunamiNotGeneratedOrBelowWarningAdvisory(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - Tsunami not generated or below warning/advisory
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "tsunamiNotGeneratedOrBelow",
            "displayString": "Tsunami not generated or below warning/advisory",
            }

    def destructiveTsunamiGeneratedFallBelowNow(self):
        '''
        @summary: Specify a set of megawidget choice properties for the
        "tsunamiCancel" megawidget - Destructive tsunami generated, now falls below
        @see: CommonMetaData.py for descriptions on properties
        @return: Dictionary of properties
        '''
        return {
            "identifier": "destructiveTsunamiGeneratedFallBelow",
            "displayString": "Destructive tsunami generated, now falls below",
            }
