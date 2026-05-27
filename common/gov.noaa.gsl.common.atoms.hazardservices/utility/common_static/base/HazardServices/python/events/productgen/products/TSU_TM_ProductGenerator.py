# *** Override behavior of TSU_TM_ProductGenerator.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Product Generator for the Tsunami Threat Message products.

    @author: GSL Hazard Services Team
    @version 1.0
    @since August 2022
'''

import AtomsFcstObsUtilities
import AtomsGeneralUtilities
import AtomsMapUtilities
import GeneralUtilities
import HazardDataAccess
import NWS_Base_Generator
import TimeUtil


class Product(NWS_Base_Generator.Product):

    def __init__(self):
        super(Product, self).__init__()

        self.afou = AtomsFcstObsUtilities.AtomsFcstObsUtilities()
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.amu = AtomsMapUtilities.AtomsMapUtilities()

        # Used by the VTECEngineWrapper to access the productGeneratorTable
        self.productGeneratorName = "TSU_TM_ProductGenerator"

    def initialize(self):
        super(Product, self).initialize()
        self.productID = "TSU"
        self.productCategory = "TSU_TM"
        self.productName = "Tsunami Threat Message"
        self.productLabel = "Tsunami Threat Message"

        # Polygon-based, so locations listed will be limited to within the polygon rather than county area
        self.polygonBased = False
        self.vtecProduct = False

    def getPurgeHours(self, hazardType):
        '''
        @summary: Get the purge hours to use for events with the given hazard type. This is the
        number of hours past issuance that the event's expiration time should be.
        @param hazardType: The hazard type (e.g., FA.W) to determine purge hours for
        @return: The purge hours, or -1.0 to indicate that the purge time should
        match the event's end time
        '''
        return -1.0

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the product generator, such as author,
        description, and script version.
        @return: A dictionary
        '''
        return {
            "author": "GSL",
            "description": "Product generator for the Tsunami Threat Message",
            "version": "1.0",
            }

    def defineDialog(self, eventSet):
        '''
        @return: dialog definition to solicit user input before running tool
        '''
        return {}

    def execute(self, eventSet, dialogInputMap):
        self.initialize()

        # Extract information for execution
        self.getVariables(eventSet, dialogInputMap)
        eventSetAttributes = eventSet.getAttributes()

        if not self.inputHazardEvents:
            return [], []

        productDicts, hazardEvents = self.makeNonVtecProducts_FromHazardEvents(self.inputHazardEvents,
                                                                               eventSetAttributes)
        return productDicts, hazardEvents

    def getMetadata(self):
        return self.metadata

    def createProductLevelProductDictionaryData(self, productDict, hazardEvents):
        '''
        @summary: Add additional attributes to the product-level of the product
        dictionary
        @param productDict: The product dictionary
        @param hazardEvents: A list of hazard events brought into product generation
        @return: An updated productDict in memory
        '''
        hazardEvent = hazardEvents[0]
        productDict["productRegion"] = hazardEvent.get("productRegion")
        productDict["customId"] = hazardEvent.get("customId")
        productDict["physicalEventType"] = hazardEvent.get("physicalEventType")

    def setHazardAttributesFromTheEventDict(self, hazardEvent, eventDict):
        '''
        @summary: Assign new hazard attributes to the hazard event based on the contents
        of the eventDict associated with this hazard event
        @param hazardEvent: The hazard event object
        @param eventDict: The event-level dictionary
        @return: The hazardEvent is updated in memory
        '''
        # Pass the computed binned country information back onto the hazard event
        hazardEvent.set("threatCountryInformation", eventDict.get("threatCountryInformation"))
        # Determine the user deselected forecast stations and pass it back to the hazard event
        forecastRunTableList = eventDict.get("forecastRunTable")
        deselectedStations = self.afou.getDeselectedStationFromForecastRunTable(forecastRunTableList)
        hazardEvent.set("deselectedForecastStations", deselectedStations)

    def postProcessProductDicts(self, productDicts):
        '''
        @summary: Write additional parameters to the product dictionary
        @param productDicts: A list of product dictionaries
        @return: The productDicts entry passed in is updated
        '''
        for productDict in productDicts:
            # Get the location description information for this product type
            locationInformation = self.agu.getLocationInformation(productDict, onlyFE=False)
            isPractice = GeneralUtilities.isPractice(productDict.get("runMode"))
            ##################################
            # Event-level dictionary updates
            ##################################
            eventDicts = self.agu.getAllEventDicts(productDict)
            for eventDict in eventDicts:
                # Add location description information
                eventDict[f"locationDescription"] = locationInformation
                # Categorize the countries affected by amplitude
                self.binCountriesByForecastInformation(eventDict)
                # Filter down the forecast run table to only warning points in alert areas
                self.filterDownForecastRunTable(eventDict)
                # Determine if forecast information has been updated since last issued
                self.checkForForecastUpdates(eventDict, isPractice)

    def binCountriesByForecastInformation(self, eventDict):
        '''
        @summary: Use the time of arrival and amplitude forecasts provided to produce
        a list of countries (e.g., time of arrival forecast only) or a dictionary of
        countries based on different amplitude thresholds (e.g., amplitude forecast)
        @param eventDict: The event-level dictionary
        @return: NoneType; the eventDict is updated in memory
        '''
        forecastRunTableList = eventDict.get("forecastRunTable")
        countryInformation = []
        if self.afou.isForecastSelected(eventDict.get("amplitudeForecast")):
            countryInformation = [self.afou.getCountriesByThreatMessageCategory(forecastRunTableList)]
        elif self.afou.isForecastSelected(eventDict.get("timeOfArrivalForecast")):
            countryInformation = self.afou.getAllCountriesFromRunTable(forecastRunTableList)
        eventDict["threatCountryInformation"] = countryInformation

    def filterDownForecastRunTable(self, eventDict):
        '''
        @summary: For Tsunami Threat Messages the forecast run / ETAs table should only contain
        records that:
        1) Are warning points, and only those that are in the appropriate domain
        2) If an amplitude forecast exists, then only records that occur within an alert region that have a 0.3 m amplitude
        3) Has an arrival time
        This method will update the event-level 'forecastRunTable' entry to only have
        stations that match these three criteria
        @param eventDict: The event-level dictionary
        @return: NoneType; the eventDict is updated in memory
        '''
        # Only perform this step if forecast amplitudes exist
        forecastRunTableList = eventDict.get("forecastRunTable")
        if eventDict.get("stationAnalysisType") == "amplitudes":
            # Get all stations that exceed some amplitude threshold
            significantAmplitudeStations = self.afou.getStationsExceedingSomeDefinedAmplitude(forecastRunTableList, 0.3)
            # Determine the alert regions that intersect with forecast points with an amplitude >= 0.3 m
            geometryList = self.afou.createBufferedGeometriesFromForecastRunTable(significantAmplitudeStations, 0.01)
            unionedGeometry = self.geomUtils.getUnionFromListOfGeometries(geometryList)
            alertRegionsResults = self.amu.getPtwcAlertRegionsByGeometry(unionedGeometry)
            alertRegionsGeom = self.amu.getUnionedGeometryFromQueryResults(alertRegionsResults)
            # Determine which stations overlap with these matching alert regions
            forecastRunTableList = self.afou.getStationsInsideGeometry(forecastRunTableList, alertRegionsGeom)

        # Restrict to only warning points, for BOTH cases (ie using TTT and/or Amplitudes)
        warningPointsDomain = self.afou.getWarningPointsDomain(eventDict.get("productRegion"))
        warningPointIds = self.amu.getPtwcWarningPointsByDomainName(warningPointsDomain)
        finalStationList = []
        for stationInfo in forecastRunTableList:
            if stationInfo[1] in warningPointIds:
                finalStationList.append(stationInfo)
        eventDict["forecastRunTable"] = finalStationList

    def checkForForecastUpdates(self, eventDict, isPractice):
        '''
        @summary: Check if either the time of arrival or amplitude forecast has been
        updated since the last issuance
        @param eventDict: The event-level dictionary
        @param isPractice: Boolean determining if CAVE is in practice mode (True)
        or not (False)
        @return: NoneType; the eventDict is updated in memory
        '''
        newForecastInfo = False
        eventID = eventDict.get("eventID")
        lastIssuedEvent = HazardDataAccess.getLastIssuedHazardEvent(eventID, isPractice)
        if lastIssuedEvent:
            currentThreatLocations = eventDict.get("threatCountryInformation")
            previousThreatLocations = lastIssuedEvent.get("threatCountryInformation")
            if currentThreatLocations != previousThreatLocations:
                newForecastInfo = True
        eventDict["newForecastInfo"] = newForecastInfo
