# *** Override behavior of CommonMetaData_Tsunami.py ***
# -- Override ability: Class-based
# -- Levels: All

"""
    Description: Common Meta Data shared among Tsunami hazard types.
    Hazard Information dialog (HID) Metadata megawidgets
    for hazard types:
      TS.W - Tsunami Warning
      TS.Y - Tsunami Advisory
      TS.A - Tsunami Watch
      TS.S - Tsunami Information Statement
      TS.ThreatMessage - Tsunami Threat Message
      TS.ConferenceCall - Tsunami Conference Call
    * Metadata is found under the Type grouping in the HID.
    * For more information about the megawidget framework, see the Google Doc:
    "Megawidget Framework Reference for Focal Points (H.S. Integrated)"
    The link to the document is at the top of CommonMetaData.py.
"""

import logging
import AtomsFcstObsUtilities
import AtomsGeneralUtilities
import AtomsMapUtilities
import GeneralConstants
import GeometryUtilities
import JUtil
import TextProductCommon
import TimeUtil
import VTECConstants
import UFStatusHandler

from gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs import SLObsUtils
from gov.noaa.gsl.common.dataplugin.pem import PhysicalEventManager, PhysicalEventType, ActiveOption
from gov.noaa.gsl.viz.atomsForecast import TsunamiForecastDao, TsunamiForecastTable, TsunamiForecastUtils
from gov.noaa.gsl.viz.atomsSeaLevelObs import SeaLevelObsDao
from gov.noaa.gsl.viz.atomsImagery import TfsImageryDao
from org.locationtech.jts.geom import Coordinate


class CommonMetaData_Tsunami(object):

    def __init__(self):
        self.afou = AtomsFcstObsUtilities.AtomsFcstObsUtilities()
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.amu = AtomsMapUtilities.AtomsMapUtilities()
        self.geomUtils = GeometryUtilities.GeometryUtilities()
        self.img = TfsImageryDao.getInstance()
        self.pem = PhysicalEventManager.getInstance()
        self.slo = SeaLevelObsDao.getInstance()
        self.tfd = TsunamiForecastDao.getInstance()
        self.tpc = TextProductCommon.TextProductCommon()
        self.selectedPE = self.checkPhysicalEventSelected()

        # Logger info
        self.logger = logging.getLogger("CommonMetaData_Tsunami")
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.dataplugin.hazards.hazardservices",
            "CommonMetaData_Tsunami", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def checkPhysicalEventSelected(self):
        '''
        @summary: Check if one and only one physical event is selected. If
        so, return it
        @return: Selected physical event from PEM (Physical Event Manager)
                 dialog, or NoneType
        '''
        selectedPE = None
        selectedEvents = list(self.pem.getSelectedPhysicalEvents())
        if len(selectedEvents) == 1:
            selectedPE = selectedEvents[0]
        return selectedPE

    '''
    For all Tsunami hazard events, set time as the following:
    start time: current time,
    end time  : UFN (Until further notice)
    '''

    def setEventStartEndTime(self, status, hazardEvent):
        '''
        @summary: Set current time as start time, "until further notice"
        @param status: The hazard event status (i.e., "potential", "pending")
        @param hazardEvent: Container holding all the space/time info and metadata needed to
        create watch/warning/advisory products
        @return: An updated hazardEvent object
        '''
        if status.lower() in ["pending", "potential"]:
            currentTimeSecs = TimeUtil.simulatedTimeInSeconds()
            currentTime = TimeUtil.epochTimeSecondsToDatetime(currentTimeSecs)
            hazardEvent.setStartTime(currentTime)
            hazardEvent.setCreationTime(currentTime)
            ufnTime = TimeUtil.epochTimeSecondsToDatetime(VTECConstants.UFN_TIME_VALUE_SECS)
            hazardEvent.setEndTime(ufnTime)

    def getPhysicalEventFromHazardEvent(self, hazardEvent):
        '''
        @summary: Given information from inside a hazard event, get the
        Physical Event object that supported the creation of this event
        @param hazardEvent: Container holding all the space/time info and metadata needed to
        create watch/warning/advisory products
        @return: A PhysicalEvent object
        '''
        customId = hazardEvent.get("customId")
        peTypeStr = self.getDefaultPhysicalEventType(hazardEvent)
        peType = PhysicalEventType.fromString(peTypeStr)
        peEvent = self.pem.retrievePhysicalEvent(customId, peType)
        return peEvent

    '''
    Shared hazard definition methods that are used in the hazard
    dropdown menus across multiple hazard types
    '''

    def getTsunamiMetadataRefreshCounter(self):
        '''
        @summary: A HiddenField that will trigger a metadata refresh for the
        hazard event it is attached to
        @return: Dictionary of megawidget properties
        '''
        return {
            "fieldType": "HiddenField",
            "fieldName": "tsunamiMetadataRefreshCounter",
            "values": 1,
            "refreshMetadata": True,
            }

    def getPhysicalEventType(self, hazardEvent, editable=False):
        '''
        @summary: Creates the ComboBox for the "Physical Event Type" megawidget
        @param hazardEvent: The hazard event being edited
        @param editable: Boolean determining whether this megawidget is editable
        @return: Dictionary of megawidget properties
        '''
        defaultValue = self.getDefaultPhysicalEventType(hazardEvent)
        choices = [peType.getLabel() for peType in self.pem.getPhysicalEventTypes()]
        return {
            "fieldType": "ComboBox",
            "fieldName": "physicalEventType",
            "label": "Physical Event Type:",
            "choices": choices,
            "values": defaultValue,
            "refreshMetadata": True,
            "editable": editable,
            }

    def getCustomId(self, hazardEvent):
        '''
        @summary: Creates the ComboBox for the "Physical Event CustomID" megawidget
        @param hazardEvent: The hazard event being edited
        @return: Dictionary of megawidget properties
        '''
        defaultValue = self.getDefaultCustomId(hazardEvent)
        peTypeStr = self.getDefaultPhysicalEventType(hazardEvent)
        peTypeValue = PhysicalEventType.fromString(peTypeStr)
        peDao = self.pem.getPhysicalEventDao(peTypeValue)
        if self.isFieldEditable(hazardEvent):
            eventIds = list(peDao.getPhysicalEventIds(ActiveOption.ACTIVE_ONLY))
        else:
            eventIds = [defaultValue]
        if not defaultValue:
            if eventIds:
                defaultValue = eventIds[0]
            else:
                # No active physical event in PEM will invoke popping up a validation error
                defaultValue = ""
                eventIds = [""]

        return {
            "fieldType": "ComboBox",
            "fieldName": "customId",
            "label": "Physical event",
            "choices": eventIds,
            "values": defaultValue,
            "editable": False,
            "refreshMetadata": True,
        }

    def getProductRegion(self, hazardEvent):
        '''
        @summary: Creates the ComboBox for the "Product Region" megawidget
        @param hazardEvent: The hazard event being edited
        @return: Dictionary of megawidget properties
        '''
        if hazardEvent and hazardEvent.get("productRegion"):
            productRegion = hazardEvent.get("productRegion")
        else:
            productRegion = self.getRegionChoices(hazardEvent)[0].get("identifier")
        choices = self.getRegionChoices(hazardEvent)
        return {
            "fieldType": "ComboBox",
            "fieldName": "productRegion",
            "label": "Product Region:",
            "choices": choices,
            "values": productRegion,
            "refreshMetadata": True,
            "editable": False,
            }

    def getPhyEventInfo(self, hazardEvent, fieldNameSuffix):
        '''
        @summary: Create the physical event info megawidget, which includes:
        - Origin time, longitude, latitude, and location
        If the physical event is a seismic event, add a group with the:
        - Magnitude, type, and depth
        If the physical event is a volcano or landslide, as a group with the:
        - Text descriptor
        @param hazardEvent: Container holding all the space/time info and metadata
        @param fieldNameSuffix: Suffix added to all identifier megawidget descriptions
        @return: Dictionary of physical event data related megawidget properties
        '''
        peTypeStr = hazardEvent.get("physicalEventType")
        peEvent = self.getPhysicalEventFromHazardEvent(hazardEvent)
        details = [
            self.getOriginTime(hazardEvent, peEvent, fieldNameSuffix),
            self.getOriginGroupInfo(hazardEvent, peEvent, fieldNameSuffix),
            self.getDistanceToCoastKm(peEvent, fieldNameSuffix),
            ]
        if peTypeStr == "Seismic":
            details += [self.getSeismicGroupInfo(hazardEvent, peEvent, fieldNameSuffix)]
        # Other physical event type information such as volume and name for volcanic and landslide
        elif peTypeStr in ["Volcanic", "Landslide"]:
            details += [self.getVolcanicLandslideGroupInfo(hazardEvent, peEvent, fieldNameSuffix)]

        return details

    def getOriginTime(self, hazardEvent, peEvent, fieldNameSuffix):
        '''
        @summary: Creates the time for the physical event "origin time" megawidget
        @param hazardEvent: The hazard event being edited
        @param peEvent: Physical event such as earthquake, volcano
        @param fieldNameSuffix: Suffix
        @return: Dictionary of megawidget properties
        '''
        fieldName = f"originTime{fieldNameSuffix}"
        return {
                "fieldName": f"originTimeGroup{fieldNameSuffix}",
                "fieldType": "Group",
                "label": "Origin Time",
                "spacing": 5,
                "leftMargin": 5,
                "rightMargin": 5,
                "topMargin": 5,
                "bottomMargin": 5,
                "expandHorizontally": True,
                "expandVertically": False,
                "fields": [
                    {
                        "fieldType": "Time",
                        "fieldName": fieldName,
                        "values": self.getPrevValueToUse(fieldName, hazardEvent, peEvent).getTime(),
                        "useNewValueOnRefresh": True,
                    }
                    ]
                }

    def getDistanceToCoastKm(self, peEvent, fieldNameSuffix):
        '''
        @summary: Creates the distance to coast line megawidget
        @param peEvent: Physical event such as earthquake, volcano
        @param fieldNameSuffix: Suffix
        @return: Dictionary of megawidget properties
        '''
        fieldName = f"distanceToCoastKm{fieldNameSuffix}"
        distanceToCoastKm = peEvent.getDistanceToCoastKm()
        return {
                "fieldType": "HiddenField",
                "fieldName": fieldName,
                "values": distanceToCoastKm,
                "useNewValueOnRefresh": True,
            }

    def getOriginGroupInfo(self, hazardEvent, peEvent, fieldNameSuffix):
        '''
        @summary: Creates physical event's longitude, latitude and location name group megawidget
        @param hazardEvent: The hazard event being edited
        @param peEvent: Physical event such as earthquake, volcano
        @param fieldNameSuffix: Suffix
        @return: Dictionary of megawidget properties
        '''
        originLonFieldName = f"originLongitude{fieldNameSuffix}"
        originLatFieldName = f"originLatitude{fieldNameSuffix}"
        locationNameFieldName = f"locationName{fieldNameSuffix}"
        return {
            "fieldName": f"originGroup{fieldNameSuffix}",
            "fieldType": "Group",
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
                    "fieldType": "FractionSpinner",
                    "fieldName": originLonFieldName,
                    "label": "Longitude:",
                    "sendEveryChange": False,
                    "minValue":-180,
                    "maxValue": 180,
                    "values": self.getPrevValueToUse(originLonFieldName, hazardEvent, peEvent),
                    "incrementDelta": 0.5,
                    "precision": 2,
                    "useNewValueOnRefresh": True,
                    },
                {
                    "fieldType": "FractionSpinner",
                    "fieldName": originLatFieldName,
                    "label": "Latitude:",
                    "sendEveryChange": False,
                    "minValue":-90,
                    "maxValue": 90,
                    "values": self.getPrevValueToUse(originLatFieldName, hazardEvent, peEvent),
                    "incrementDelta": 0.5,
                    "precision": 2,
                    "useNewValueOnRefresh": True,
                    },
                {
                    "fieldType": "Text",
                    "fieldName": locationNameFieldName,
                    "label": "Location:",
                    "editable": True,
                    "visibleChars": 28,
                    "spacing": 2,
                    "values": self.getPrevValueToUse(locationNameFieldName, hazardEvent, peEvent),
                    "useNewValueOnRefresh": True,
                    }
                ]
            }

    def getSeismicGroupInfo(self, hazardEvent, peEvent, fieldNameSuffix):
        '''
        @summary: Create the Seismic specific info megawidget, which includes
        depth, magnitude and type
        @param hazardEvent: Container holding all the space/time info and metadata
        @param peEvent: Physical event such as earthquake, landslide
        @param fieldNameSuffix: Suffix
        @return: Dictionary of Seismic data related megawidget properties
        '''
        magnitudeFieldName = f"magnitude{fieldNameSuffix}"
        magnitudeTypeFieldName = f"magnitudeType{fieldNameSuffix}"
        magnitudeTypeChoices = self.agu.getMagnitudeTypeChoices()
        originDepthFieldName = f"originDepth{fieldNameSuffix}"
        return {
            "fieldName": f"magnitudeGroup{fieldNameSuffix}",
            "fieldType": "Group",
            "label": "Magnitude",
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
                    "fieldType": "FractionSpinner",
                    "fieldName": magnitudeFieldName,
                    "label": " Magnitude:",
                    "sendEveryChange": False,
                    "minValue": 0,
                    "maxValue": 10,
                    "values": self.getPrevValueToUse(magnitudeFieldName, hazardEvent, peEvent),
                    "incrementDelta": 0.1,
                    "precision": 1,
                    "useNewValueOnRefresh": True,
                    },
                {
                    "fieldType": "ComboBox",
                    "fieldName": magnitudeTypeFieldName,
                    "label": "Type:",
                    "editable": True,
                    "values": "Moment_P",
                    "useNewValueOnRefresh": True,
                    "choices": magnitudeTypeChoices,
                    },
                {
                    "fieldType": "FractionSpinner",
                    "fieldName": originDepthFieldName,
                    "label": "Depth (mi):",
                    "sendEveryChange": False,
                    "minValue": 0,
                    "maxValue": 700,
                    "values": self.getPrevValueToUse(originDepthFieldName, hazardEvent, peEvent),
                    "incrementDelta": 1,
                    "useNewValueOnRefresh": True,
                    },
                ]
            }

    def getVolcanicLandslideGroupInfo(self, hazardEvent, peEvent, fieldNameSuffix):
        '''
        @summary: Create the Volcanic and Landslide specific info megawidget, which includes
        name, displaced volume
        @param hazardEvent: Container holding all the space/time info and metadata
        @param peEvent: Physical event such as earthquake, landslide
        @param fieldNameSuffix: Suffix
        @return: Dictionary of volcanic and landslide data related megawidget properties
        '''
        peNameFieldName = f"peName{fieldNameSuffix}"
        peTypeStr = hazardEvent.get("physicalEventType")
        return {
            "fieldName": f"otherPhysicalEventTypeGroup{fieldNameSuffix}",
            "fieldType": "Group",
            "label": f"{peTypeStr} information: ",
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
                    "fieldName": peNameFieldName,
                    "label": f"{peTypeStr} name:",
                    "values": self.getPrevValueToUse(peNameFieldName, hazardEvent, peEvent),
                    "visibleChars": 40,
                    },
                ]
            }

    def getPhysicalEventInfoAndForecastSeaLevelTables(self, hazardEvents, fieldNameSuffix, isThreatMsg=False):
        '''
        @summary: Create tabbed megawidget which includes "Seismic Data", "Tsunami Forecasts" and "Sea Level
        Station Observations"
        @param hazardEvents: Container holding all the space/time info and metadata
        @param fieldNameSuffix: Suffix
        @param isThreatMsg: Is this table being created for a TS.ThreatMessage?
        @return: Specifier (in dictionary form) for a Group megawidget wrapping the provided detail megawidgets.
        '''
        hazardEvent = hazardEvents[0]
        peData = self.getPhyEventInfo(hazardEvent, fieldNameSuffix)
        customId = hazardEvent.get("customId")
        peType = hazardEvent.get("physicalEventType")
        tsunamiForecasts = [self.getForecastTypeInfo(hazardEvent, customId, fieldNameSuffix)]
        tsunamiForecasts += [self.getForecastRunsTable(hazardEvents, customId, fieldNameSuffix, isThreatMsg)]
        seaLevelStationObservations = [
            self.getSeaLevelStationObservationsTable(hazardEvent, customId, fieldNameSuffix)
            ]
        imageryDescriptors = [self.getImageryDescriptors(hazardEvent, customId, fieldNameSuffix)]
        fieldName = f"TSUTabbedComposite{fieldNameSuffix}"
        peDetails = [
            {
                "fieldType": "TabbedComposite",
                "fieldName": fieldName,
                "leftMargin": 10,
                "rightMargin": 10,
                "topMargin": 10,
                "bottomMargin": 10,
                "expandHorizontally": True,
                "expandVertically": True,
                "refreshMetadata": True,
                "pages": [
                    {
                        "pageName": f"{peType} Data",
                        "pageFields": peData
                    },
                    {
                        "pageName": "Tsunami Forecasts",
                        "pageFields": tsunamiForecasts
                    },
                    {
                        "pageName": "Sea Level Station Observations",
                        "pageFields": seaLevelStationObservations
                    },
                    {
                        "pageName": "Imagery Descriptors",
                        "pageFields": imageryDescriptors
                    },
                ]
            }
        ]
        return peDetails

    def getForecastTypeInfo(self, hazardEvent, customId, fieldNameSuffix):
        '''
        @summary: Wrap the specified details megawidget list in a Group megawidget.
        @param hazardEvents: Container holding all the space/time info and metadata
        @param customId: Physical event identifier
        @param fieldNameSuffix: Suffix
        @return: Specifier (in dictionary form) for a Group megawidget wrapping the provided detail megawidgets.
        '''
        tsunamiForecastInfos = self.tfd.getTsunamiForecastInfos(customId)
        tttChoices = self.getTsunamiForecastRunChoices(tsunamiForecastInfos, "timeOfArrival")
        amplitudeChoices = self.getTsunamiForecastRunChoices(tsunamiForecastInfos, "amplitude")
        timeOfArrivalDefault = self.getDefaultForecastSelection(hazardEvent, "timeOfArrival",
                                                                tttChoices, fieldNameSuffix)
        amplitudeDefault = self.getDefaultForecastSelection(hazardEvent, "amplitude",
                                                            amplitudeChoices, fieldNameSuffix)

        return {
            "fieldName": f"forecastGroup{fieldNameSuffix}",
            "fieldType": "Group",
            "label": ("Select the forecast runs to use for 'Time of Arrival' "
                      "and 'Amplitude' calculations:"),
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
                    "fieldType": "ComboBox",
                    "fieldName": f"timeOfArrivalForecast{fieldNameSuffix}",
                    "label": "Time of Arrival: ",
                    "values": timeOfArrivalDefault,
                    "choices":tttChoices,
                    "refreshMetadata": True
                    },
                {
                    "fieldType": "ComboBox",
                    "label": "Amplitude: ",
                    "fieldName": f"amplitudeForecast{fieldNameSuffix}",
                    "choices": amplitudeChoices,
                    "values": amplitudeDefault,
                    "refreshMetadata": True
                    },
            ]
        }

    def getForecastRunsTable(self, hazardEvents, customId, fieldNameSuffix, isThreatMsg):
        '''
        @summary: Create a forecast run stations table
        @param hazardEvents: Container holding all the space/time info and metadata
        @param customId: Physical event identifier
        @param fieldNameSuffix: Suffix
        @param isThreatMsg: Is this table being created for a TS.ThreatMessage?
        @return: A table with forecast run stations information
        '''
        values = []
        firstHazardEvent = hazardEvents[0]
        tsunamiForecastInfos = self.tfd.getTsunamiForecastInfos(customId)
        arrivalTimeFcst = self.getForecastRun(firstHazardEvent, tsunamiForecastInfos,
                                              "timeOfArrival", fieldNameSuffix)
        ampFcst = self.getForecastRun(firstHazardEvent, tsunamiForecastInfos,
                                      "amplitude", fieldNameSuffix)
        if isThreatMsg:
            matchingHazardEvent = None
            for hazardEvent in hazardEvents:
                if hazardEvent.getHazardType() == "TS.ThreatMessage":
                    matchingHazardEvent = hazardEvent
                    break
            if matchingHazardEvent:
                tfTable = self.getForecastTableForThreatMessage(matchingHazardEvent, arrivalTimeFcst, ampFcst)
            else:
                tfTable = TsunamiForecastUtils.createForecastTable(arrivalTimeFcst, ampFcst)
        else:
            tfTable = TsunamiForecastUtils.getStationFcstsWithinHazardAreas(
                                            JUtil.pyValToJavaObj(hazardEvents),
                                            arrivalTimeFcst, ampFcst,
                                            TsunamiForecastTable.ARRIVE_TIME_COMPARATOR)
        stnRowsList = tfTable.getRows()
        lengthTable = (len(stnRowsList) if stnRowsList else 1)
        siteID = firstHazardEvent.getSiteID()
        deselectedStations = firstHazardEvent.get("deselectedForecastStations", [])
        for stnRow in stnRowsList:
            # For TTT there's arrival time and no amplitudes
            # For RIFT there's no arrival time but there are amplitudes
            arrivalTime = stnRow.getArrivalTime()
            amp = stnRow.getAmplitude()
            if arrivalTime is not None:
                arrivalTime = arrivalTime.getTime()
                currentTime = self.getCurrentCAVETime(hazardEvents[0])
                # Forecast ETAs are listed in products only if >= 1 hour stale (for PTWC) and >= NOW (for NTWC)
                # Only skip stale ETAs if no amplitudes exist, otherwise you're skipping amplitudes accidentally
                if amp is None and not self.afou.areETAsDisplayedInProduct(arrivalTime, currentTime, siteID):
                    continue
                arrivalTime = TimeUtil.epochTimeMillisToDatetime(arrivalTime).strftime("%H%M %m/%d/%y")
            else:
                arrivalTime = "NA"

            station = stnRow.getStation()
            stationId = station.getCustomId()
            # For NTWC, only include short list stations; For PTWC, include all stations
            if not self.afou.isStationOnShortList(stationId, siteID):
                continue
            name = station.getName()
            stateOrCountry = self.afou.getStateOrCountryFromStation(station)
            lat, lon = self.getLatLonValue(station)
            if amp or amp == 0.0:
                amp = f"{amp:.1f}"
            else:
                amp = "NA"
            checkedOn = True
            if stationId in deselectedStations:
                checkedOn = False
            value = [checkedOn, stationId, name, stateOrCountry, f"{lat} {lon}", arrivalTime, amp]
            if value not in values:
                values.append(value)
        return {
            "fieldType": "Table",
            "fieldName": f"forecastRunTable{fieldNameSuffix}",
            "label": "Forecast Run Stations",
            "lines": lengthTable,
            "selectionStyle": "multi",
            "columnHeaders": ["Station", "Name", "State/Country", "Coordinates", "Arrival Time", "Amplitude"],
            "values": values,
            "showCheckBoxes": True,
            "useNewValueOnRefresh": True,
            }

    def getForecastTableForThreatMessage(self, hazardEvent, arrivalTimeFcst, ampFcst):
        '''
        @summary: Build the forecast table for a TS.ThreatMessage
        @param hazardEvent: The TS.ThreatMessage hazard event
        @param arrivalTimeFcst: The arrival time forecast
        @param ampFcst: The amplitude forecast
        @return: A python TsunamiForecastRunsTable object
        '''
        # Initialize an empty table
        tfTable = TsunamiForecastTable()

        # Get the physical event associated with this hazard event
        physicalEvent = self.getPhysicalEventFromHazardEvent(hazardEvent)

        # if no time of arrival exists, return empty table
        if not arrivalTimeFcst or physicalEvent is None:
            return tfTable

        # Only a time of arrival forecast exists
        analysisType = ""
        if arrivalTimeFcst is not None and not ampFcst:
            # Time of arrival analyses require a magnitude
            if (physicalEvent.getEventType() != PhysicalEventType.SEISMIC or
                physicalEvent.getData().getPrefMagnitude() < 7.1):
                return tfTable
            # Get the seismic event magnitude
            magnitude = physicalEvent.getData().getPrefMagnitude()
            # Get the event location
            if magnitude >= 7.1 and magnitude <= 7.8:
                lonLatOrigin = Coordinate(physicalEvent.getLongitude(), physicalEvent.getLatitude())
                if magnitude <= 7.5:
                    distanceKm = 300.0
                    analysisType = "300km"
                else:
                    distanceKm = 1000.0
                    analysisType = "1000km"
                tfTable = TsunamiForecastUtils.getStationFcstsWithinDistance(arrivalTimeFcst, ampFcst,
                                                                             TsunamiForecastTable.ARRIVE_TIME_COMPARATOR,
                                                                             lonLatOrigin, distanceKm)
            else:
                analysisType = "3hr"
                tfTable = TsunamiForecastUtils.getStationFcstsWithinTravelTime(physicalEvent.getRefTime(),
                                                                               3 * GeneralConstants.MILLIS_PER_HOUR,
                                                                               arrivalTimeFcst, ampFcst,
                                                                               TsunamiForecastTable.ARRIVE_TIME_COMPARATOR)
        # Both a time of arrival and amplitude forecast exists
        elif arrivalTimeFcst is not None and ampFcst is not None:
            analysisType = "amplitudes"
            tfTable = TsunamiForecastUtils.createForecastTable(arrivalTimeFcst, ampFcst)
            for stnRow in tfTable.getRows():
                keepStation = False
                amplitude = stnRow.getAmplitude()
                if ((amplitude and amplitude > 0) or amplitude is None):
                    keepStation = True
                if not keepStation:
                    tfTable.removeRow(stnRow.getStation())

        # Remove all points that are not international
        for stnRow in tfTable.getRows():
            if not self.afou.isStationInternational(stnRow.getStation()):
                tfTable.removeRow(stnRow.getStation())

        if analysisType:
            hazardEvent.set("stationAnalysisType", analysisType)
        return tfTable

    def getEventForecastStations(self, hazardEvents, customId, fieldNameSuffix):
        '''
        @summary: Create a hidden field to store a dictionary with eventID and associated
                  forecast run table.
        @param hazardEvents: Container holding all the space/time info and metadata
        @param customId: Physical event identifier
        @param fieldNameSuffix: Suffix
        @return: Dictionary of event forecast run table related megawidget properties
        '''
        eventForecastStations = f"eventForecastStations{fieldNameSuffix}"
        tsunamiForecastInfos = self.tfd.getTsunamiForecastInfos(customId)
        arrivalTimeFcst = self.getForecastRun(hazardEvents[0], tsunamiForecastInfos,
                                              "timeOfArrival", fieldNameSuffix)
        ampFcst = self.getForecastRun(hazardEvents[0], tsunamiForecastInfos,
                                      "amplitude", fieldNameSuffix)
        eventIdAndForecastStations = []
        for hazardEvent in hazardEvents:
            eventStations = []
            tfTable = TsunamiForecastUtils.getStationFcstsWithinHazardArea(
                                                hazardEvent.toJavaObj(),
                                                arrivalTimeFcst, ampFcst,
                                                TsunamiForecastTable.ARRIVE_TIME_COMPARATOR)
            for stnRow in tfTable.getRows():
                stationID = stnRow.getStation().getCustomId()
                if stationID not in eventStations:
                    eventStations.append(stationID)
            eventIdAndForecastStations.append((hazardEvent.getEventID(), eventStations))
        return {
            "fieldType": "HiddenField",
            "fieldName": eventForecastStations,
            "values": eventIdAndForecastStations
            }

    def getSeaLevelStationObservationsTable(self, hazardEvent, customId, fieldNameSuffix):
        '''
        @summary: Create sea level station observations table
        @param hazardEvent: Container holding all the space/time info and metadata
        @param customId: Physical event identifier
        @param fieldNameSuffix: Suffix
        @return: Dictionary of sea level observations stations table related megawidget properties
        '''
        seaLevelObsFieldName = f"seaLevelObs{fieldNameSuffix}"
        slobs = self.slo.getSeaLevelObservations(customId, None)
        mostRecentSlobs = SLObsUtils.getMostRecentSLObsSet(slobs)
        values = []
        lengthTable = (len(mostRecentSlobs) if mostRecentSlobs else 1)
        for ob in mostRecentSlobs:
            startTime = ob.getStartTime().getTime()
            if not startTime:
                continue
            startTime = TimeUtil.epochTimeMillisToDatetime(startTime).strftime("%H%M %m/%d")
            obsAmp = ob.getAmplitude()
            if obsAmp or obsAmp == 0.0:
                # Convert to feet
                obsAmpFeet = f"{(obsAmp / GeneralConstants.METERS_PER_FOOT):.1f}"
                obsAmpMeters = f"{obsAmp:.2f}"
                # Display amplitude both in meters and feet
                obsAmp = f"{obsAmpMeters}M/{obsAmpFeet}FT"
            else:
               obsAmp = "NA"
            station = ob.getStation()
            name = station.getName()
            lat, lon = self.getLatLonValue(station)
            # state = station.getState()
            # country = station.getCountry()
            # if state:
            #     site = f"{name} {state}"
            # else:
            #     site = f"{name} {country}"
            period = ob.getPeriod()
            if period:
                period = f"{period:.2f}"
            else:
                period = "NA"
            value = [True, name, f"{lat} {lon}", startTime, obsAmp, period]
            if value not in values:
                values.append(value)
        return {
            "fieldType": "Table",
            "fieldName": seaLevelObsFieldName,
            "label": "Sea Level Observations:",
            "lines": lengthTable,
            "selectionStyle": "multi",
            "columnHeaders": ["site", "Coordinates", "Start Time", "Max Height", "Period"],
            "values": values,
            "showCheckBoxes": True
            }

    def getImageryDescriptors(self, hazardEvent, customId, fieldNameSuffix):
        '''
        @summary: Create imagery descriptors
        @param hazardEvent: Container holding all the space/time info and metadata
        @param customId: Physical event identifier
        @param fieldNameSuffix: Suffix
        @return: Dictionary of imagery descriptors related megawidget properties
        '''
        imageryDescriptorsFieldName = f"imageryDescriptors{fieldNameSuffix}"
        imageryDescs = self.img.getImageryDescriptors(customId)
        imageryDescriptors = ""
        for imageryDesc in imageryDescs:
            imageName = imageryDesc.getFilename()
            # imageFile = imageryDesc.getFile()
            # imageryDescriptors.append((imageName, imageFile))
            imageryDescriptors += f"{imageName}\n"
        return {
            "fieldType": "Text",
            "fieldName": imageryDescriptorsFieldName,
            "values": imageryDescriptors,
            "visibleChars": 40,
            "lines": 6,
            "expandHorizontally": True
            }

    def getDefaultCustomId(self, hazardEvent):
        '''
        @summary: Get the default physical event id
        @param hazardEvent: The input hazard event
        @return: Default physical event id
        '''
        defaultID = ""
        if hazardEvent and hazardEvent.get("customId"):
            defaultID = hazardEvent.get("customId")
        elif self.selectedPE:
            defaultID = self.selectedPE.getCustomId()
        return defaultID

    def getDefaultPhysicalEventType(self, hazardEvent):
        '''
        @summary: Get the default physical event type
        @param hazardEvent: The input hazard event
        @return: Default physical event type
        '''
        physicalEventType = ""
        if hazardEvent and hazardEvent.get("physicalEventType"):
            physicalEventType = hazardEvent.get("physicalEventType")
        elif self.selectedPE:
            physicalEventType = self.selectedPE.getEventType().getLabel()
        return physicalEventType

    def getDefaultRegion(self, hazardEvent):
        '''
        @summary: Get the default product region
        @param hazardEvent: The input hazard event
        @return: Default product region
        '''
        region = ""
        if hazardEvent and hazardEvent.get("productRegion"):
            region = hazardEvent.get("productRegion")
        return region

    def getTsunamiForecastRunChoices(self, tsunamiForecastInfos, inputType):
        '''
        @summary: Get Tsunami forecast run choices
        @param tsunamiForecastInfos: A container including all Tsunami forecast information related with a specific
        physical event id
        @return: A list of forecast choices with forecast type and run time
        '''
        forecastChoiceTuple = []
        forecastList = []
        for tfi in tsunamiForecastInfos:
            forecastType = tfi.getForecastType().getLabel()
            forecastTypeFormat = forecastType.ljust(7)
            runTimeStr = str(tfi.getRunTime())
            choiceLabel = f"{forecastTypeFormat} - {runTimeStr}"
            if ((inputType == "timeOfArrival" and forecastType in ["TTT", "Hybrid", "Derived"]) or
                (inputType == "amplitude" and forecastType != "TTT")):
                forecastChoiceTuple.append((choiceLabel, runTimeStr))
        if forecastChoiceTuple:
            forecastChoiceTuple = sorted(forecastChoiceTuple, key=lambda t: t[1], reverse=True)
            forecastList += [fc[0] for fc in forecastChoiceTuple]
        # Add empty selection
        forecastList += ["No Selection"]
        return forecastList

    def getDefaultForecastSelection(self, hazardEvent, fcstType, choices, fieldNameSuffix):
        '''
        @summary: Get the default choice either the amplitudeForecast or timeOfArrivalForecast
        @param hazardEvent: The input hazard event
        @param fcstType: The forecast type (either "amplitude" or "timeOfArrival")
        @param choices: List of possible forecast choice labels
        @param fieldNameSuffix: Suffix
        @return: The default choice of amplitudeForecast or timeOfArrivalForecast
        '''
        default = "No Selection"
        if hazardEvent and hazardEvent.get(f"{fcstType}Forecast{fieldNameSuffix}"):
            default = hazardEvent.get(f"{fcstType}Forecast{fieldNameSuffix}")
        elif choices:
            default = choices[0]
        return default

    def getForecastRun(self, hazardEvent, tsunamiForecastInfos, fcstType, fieldNameSuffix):
        '''
        @summary: Get the default choice for amplitudeForecast
        @param hazardEvent: The input hazard event
        @param tsunamiForecastInfos: A list of TsunamiForecastInfo objects
        @param fcstType: The forecast type (either "amplitude" or "timeOfArrival")
        @param fieldNameSuffix: Suffix
        @return: A TsunamiForecast object
        '''
        fcstRun = None
        fcstChoice = "No Selection"
        if fcstType in ["timeOfArrival", "amplitude"]:
            forecastChoices = self.getTsunamiForecastRunChoices(tsunamiForecastInfos, fcstType)
            fcstChoice = self.getDefaultForecastSelection(hazardEvent, fcstType, forecastChoices, fieldNameSuffix)
        if fcstChoice == "No Selection":
            return fcstRun
        # Parse the text string to get the forecast and time (e.g., "TTT     - 2024-02-21 21:50:46.0")
        fcstType, fcstRunTime = [xx.strip() for xx in fcstChoice.split(" - ")]
        for tfi in tsunamiForecastInfos:
            tfiType = tfi.getForecastType().getLabel()
            tfiRunTime = str(tfi.getRunTime())
            if tfiType == fcstType and tfiRunTime == fcstRunTime:
                fcstRun = self.tfd.getTsunamiForecast(tfi)
                break
        return fcstRun

    def getRegionChoices(self, hazardEvent):
        '''
        @summary: Determine the list of possible product regions based on
        the tsunami warning center site
        @param hazardEvent: The selected hazard event
        @return: A list of megawidget choice dictionaries
        '''
        siteSource = hazardEvent.getSiteID()
        if siteSource == "NTWC":
            choices = [
                        {"identifier": "AkBcWc", "displayString": "Alaska/British Columbia/U.S. West Coast"},
                        {"identifier": "EcGc", "displayString": "U.S. East Coast/Gulf of America/Canada"},
                      ]
        elif siteSource == "PTWC":
            choices = [
                        {"identifier": "Hi", "displayString": "Hawaii"},
                        {"identifier": "As", "displayString": "American Samoa"},
                        {"identifier": "Gu", "displayString": "Guam/CNMI"},
                        {"identifier": "Pr", "displayString": "Puerto Rico/Virgin Islands"},
                        {"identifier": "Pac", "displayString": "Non U.S. Pacific"},
                        {"identifier": "Car", "displayString": "Non U.S. Caribbean"},
                      ]
        return choices

    def getPrevValueToUse(self, fieldName, hazardEvent, peEvent):
        peData = peEvent.getData()
        if "originLongitude" in fieldName:
            prevValueToUse = peEvent.getLongitude()
        elif "originLatitude" in fieldName:
            prevValueToUse = peEvent.getLatitude()
        elif "originTime" in fieldName:
            prevValueToUse = peEvent.getRefTime()
        elif "magnitude" in fieldName:
            prevValueToUse = peData.getPrefMagnitude()
        elif "magnitudeType"in fieldName:
            prevValueToUse = peData.getPrefMagnitudeType()
        elif "originDepth" in fieldName:
            prevValueToUse = peData.getDepth()
        elif "locationName" in fieldName:
            name = hazardEvent.get("locationName")
            if name:
                prevValueToUse = name
            else:
                prevValueToUse = ""
        elif "peName" in fieldName:
            prevValueToUse = peEvent.getName()
        return prevValueToUse

    def getLatLonValue(self, station):
        '''
        @summary: Convert the station latitude and longitude into strings
        with the N-S and E-W designators
        @param station: The ForecastStation object
        @return: A list with a string representation of the latitude and longitude
        '''
        lat = station.getLatitude()
        lon = station.getLongitude()
        if lat >= 0.0:
            latLabel = "N"
        else:
            latLabel = "S"
        if lon >= 0.0:
            lonLabel = "E"
        else:
            lonLabel = "W"
        latValue = f"{abs(lat):.1f}{latLabel}"
        lonValue = f"{abs(lon):.1f}{lonLabel}"
        return latValue, lonValue

    def isFieldEditable(self, hazardEvent):
        '''
        @summary: Checks if the hazard event has at least been issued in its lifecycle.
        If so, then the field should not be editable.
        @param hazardEvent: The hazard event being analyzed
        @return: Boolean
        '''
        return hazardEvent.getStatus().lower() not in ["issued", "ending", "ended"]

    def getCurrentCAVETime(self, hazardEvent):
        '''
        @summary: Returns the CAVE system time that is shown in the clock on the bottom of CAVE
        @param hazardEvent: Container holding all the space/time info and metadata needed to
        create watch/warning/advisory products
        @return: milliseconds of current time
        '''
        physicalEvent = self.getPhysicalEventFromHazardEvent(hazardEvent)
        currentTime = physicalEvent.getRefTime().getTime()
        # TO USE THE CAVE CLOCK instead
        # currentTime = TimeUtil.simulatedTimeInMilliseconds()
        return currentTime
