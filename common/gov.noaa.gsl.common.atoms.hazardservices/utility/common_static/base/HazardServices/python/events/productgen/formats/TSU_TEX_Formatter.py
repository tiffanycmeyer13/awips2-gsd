# *** Override behavior of TSU_TEX_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Create TEX (Tsunami Event XML) message
    @since: Jan 2023
    @author GSL Hazard Services Team
'''

import xml.etree.ElementTree as ET
import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMessageMethods
import GeneralConstants
import GeneralUtilities
import HazardConstants
import NWS_Machine_Formatter
import TimeUtil
import TIB_Public_Formatter
import TIB_Spanish_Formatter
import TIB_Verbal_Formatter
import TSU_Public_Formatter
import TSU_Segmented_Formatter
import TSU_Spanish_Formatter
import TSU_TM_Formatter
import TSU_Verbal_Formatter
from com.raytheon.uf.common.hazards.productgen import ProductUtils


class Format(NWS_Machine_Formatter.Format):

    def initialize(self, productDict):
        '''
        @summary: Create instance variables visible to all methods
        in this class
        @param productDict: The product-level dictionary
        @return: New instance variables (i.e., self.agu)
        '''
        super(Format, self).initialize(productDict)

        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()

        self.eventDict = self.agu.getAllEventDicts(productDict)[0]
        self.productCategory = productDict.get("productCategory")
        self.productRegion = productDict.get("productRegion")
        self.siteId = productDict.get("siteID")
        if self.productCategory == "TSU":
            self.fieldNameSuffix = f"_{productDict.get('productLabel')}"
        else:
            self.fieldNameSuffix = ""

    def execute(self, productDict):
        '''
        @summary: Creates the message text for this formatter
        based on the contents of the product dictionary created
        by the product generator
        @param productDict: The product-level dictionary
        @return: A list of strings, each containing a block of
        text for a single message
        '''
        self.initialize(productDict)
        messages = []
        # Create root element: tsunamiEvent
        xml = self.makeRootElement(productDict)
        self.createTEX_message(xml, productDict)
        xmlString = self.convertElementObjectToString(xml, "unicode")
        messages.append(ProductUtils.prettyXML(xmlString, True))
        return messages

    def recordGeneratedText(self, productDict, textProductList):
        '''
        @summary: Write the text product(s) from this formatter to a physical file
        @param productDict: The product-level dictionary
        @param textProductList: A list of text product(s) created by the formatter
        @return: None
        '''
        if self.issueFlag:
            AtomsDisseminationUtilities.AtomsDisseminationUtilities().writeAtomsFile(productDict,
                                                                                     textProductList,
                                                                                     self.__module__)

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary
        '''
        pass

    def createTEX_message(self, xml, productDict):
        '''
        2.1 tsunamiEvent - root element
            2.1.1 TWCEventID
            2.1.2 TWCBulletin
            2.1.3 earthquakeInformation
            2.1.4 tsunamiInformation
        '''
        # 2.1.1 TWCEventID
        self.createSubElement(xml, self.populateTagDict("TWCEventID", text=productDict.get("customId")))
        # 2.1.2 TWCBulletin
        bulletinElement = self.createSubElement(xml, self.populateTagDict("TWCBulletin"))
        self.createBulletinBlock(bulletinElement, productDict)
        # 2.1.3 physicalEvent
        peInfoElement = self.createSubElement(xml, self.populateTagDict("physicalEvent"))
        self.createPhysicalEventInfo(peInfoElement, productDict)
        # 2.1.4 tsunamiInformation
        tsuInfoElement = self.createSubElement(xml, self.populateTagDict("tsunamiInformation"))
        self.createTsunamiInfoBlock(tsuInfoElement, productDict)

    def createBulletinBlock(self, xml, productDict):
        '''
        Create TWCBulletin sub-elements
        2.1.2 TWCBulletin
            2.1.2.1 header
            2.1.2.2 preamble
            2.1.2.3 productSegment
            2.1.2.4 actions
            2.1.2.5 text
            2.1.2.6 flags
            2.1.2.7 graphicProducts
        '''
        headerElement = self.createSubElement(xml, self.populateTagDict("header"))
        self.createHeaderBlock(headerElement, productDict)
        preambleElement = self.createSubElement(xml, self.populateTagDict("preamble"))
        self.createPreambleBlock(preambleElement, productDict)
        # Create this for each segment, can be multiple use
        productSegmentsElement = self.createSubElement(xml, self.populateTagDict("productSegment"))
        self.createProductSegmentsBlock(productSegmentsElement, productDict)
        actionsElement = self.createSubElement(xml, self.populateTagDict("actions"))
        self.createActionsBlock(actionsElement, productDict)
        textElement = self.createSubElement(xml, self.populateTagDict("text"))
        self.createTextBlock(textElement, productDict)
        flagsElement = self.createSubElement(xml, self.populateTagDict("flags"))
        self.createFlagsBlock(flagsElement, productDict)
        graphicProductsElement = self.createSubElement(xml, self.populateTagDict("graphicProducts"))
        self.createGraphicProductsBlock(graphicProductsElement, productDict)

    def createPhysicalEventInfo(self, xml, productDict):
        '''
        2.1.3 earthquakeInformation
            2.1.3.1 physicalEvenType
            2.1.3.2 physicalEventData
                2.1.3.2.1 USGSEventID
                2.1.3.2.2 magnitude
                    <magnitude type="Mwp" source=“PTWC”>8.6</magnitude>
                2.1.3.2.3 origin
                    2.1.3.2.3.1 originTime
                    2.1.3.2.3.2 originTimeZone
                    2.1.3.2.3.3 lat
                    2.1.3.2.3.4 long
                    2.1.3.2.3.5 depth
                    2.1.3.2.3.6 locationName
            2.1.3.4 theta
            2.1.3.5 earthquakeSource
                2.1.3.5.1 focalMechanism
                    2.1.3.5.1.1 nodalPlane1
                        2.1.3.5.1.1.1 strike
                        2.1.3.5.1.1.2 dip
                        2.1.3.5.1.1.3 rake
                    2.1.3.5.1.2 nodalPlane2
                        2.1.3.5.1.2.1 strike
                        2.1.3.5.1.2.2 dip
                        2.1.3.5.1.2.3 rake
                2.1.3.5.2 moment
                2.1.3.5.3 centroidMomentTensor
                    2.1.3.5.3.1 mrr
                    2.1.3.5.3.2 mff
                    2.1.3.5.3.3 mrf
                    2.1.3.5.3.4 mtt
                    2.1.3.5.3.5 mrt
                    2.1.3.5.3.6 mtf
                2.1.3.5.4 centroidOrigin
                    2.1.3.5.4.1 centroidOriginTime
                    2.1.3.5.4.2 centroidOriginTimeZone
                    2.1.3.5.4.3 lat
                    2.1.3.5.4.4 long
                    2.1.3.5.4.5 centroidDepth
                2.1.3.6 faultRuptureModel
                    2.1.3.6.1 faultLength
                    2.1.3.6.2 faultWidth
                    2.1.3.6.3 rigidity
                    2.1.3.6.4 slipVelocity
                    2.1.3.6.5 ruptureVelocity
                    2.1.3.6.6 ruptureLocation
                        2.1.3.6.6.1 strikePercent
                        2.1.3.6.6.2 dipPercent
            2.1.1.15.1 magnitude
            2.1.1.15.2 originTime
            2.1.1.15.3 OriginTimeZone
            2.1.1.15.4 depth
            2.1.1.15.5 lat
            2.1.1.15.6 long
            2.1.1.15.7 locationName
            2.1.1.15.8 faultLength
            2.1.1.15.9 faultWidth
            2.1.1.15.10 strike
            2.1.1.15.11 dip
            2.1.1.15.12 slip
            2.1.1.15.13 rigidity
            2.1.1.15.14 seismicMoment
            2.1.1.15.15 centroidMomentTensor
            2.1.1.15.16 ruptureVelocity
            2.1.1.15.17 slipVelocity
            2.1.1.15.18 epicenterLocation
                2.1.1.15.18.1 strikePercent
                2.1.1.15.18.2 dipPercent
        '''
        # USGSEventID, optional, merged earthquake event ID from the USGS’s Product Distribution Layer (PDL) system
        # Add a child to "physicalEvent" named "type" allowing the well known types:
        # Seismic, volcano, landslide, meteorite, etc.
        # Physical event type element
        peType = self.eventDict.get("physicalEventType")
        self.createSubElement(xml, self.populateTagDict("physicalEventType", text=peType))
        peDataElement = self.createSubElement(xml, self.populateTagDict("physicalEventData"))
        if peType == "Seismic":
            # Magnitude with type and source info
            tagDict = self.populateTagDict("magnitude",
                                           text=str(self.eventDict.get(f"magnitude{self.fieldNameSuffix}")),
                                           attrs={"type": self.eventDict.get(f"magnitudeType{self.fieldNameSuffix}")},
                                           )
            self.createSubElement(peDataElement, tagDict)
        # Origin element
        originElement = self.createSubElement(peDataElement,
                                              self.populateTagDict("origin", attrs={"source": self.eventDict.get("siteID")}))
        originTimeMillis = self.eventDict.get(f"originTime{self.fieldNameSuffix}")
        originTimeDT = TimeUtil.epochTimeMillisToDatetime(originTimeMillis)
        dt = TimeUtil.changeTimezoneOfDatetimeObject(originTimeDT, "UTC")
        originTimeString = dt.strftime("%Y-%m-%dT%H:%M:%S %Z")
        self.createSubElement(originElement, self.populateTagDict("originTime", text=originTimeString))
        timezoneList = self.alu.getTimezonesByProductRegionAbbreviation(self.productRegion)
        addUTC = (len(timezoneList) == 1 and timezoneList[0] == "UTC")
        for singleTZ in timezoneList:
            dt = TimeUtil.changeTimezoneOfDatetimeObject(originTimeDT, singleTZ)
            timezoneString = dt.strftime("%Z")
            if timezoneString != "UTC" or addUTC:
                self.createSubElement(originElement, self.populateTagDict("originTimeZone", text=timezoneString))
        self.createSubElement(originElement, self.populateTagDict("geo:lat", text=str(self.eventDict.get(f"originLatitude{self.fieldNameSuffix}"))))
        self.createSubElement(originElement, self.populateTagDict("geo:long", text=str(self.eventDict.get(f"originLongitude{self.fieldNameSuffix}"))))
        if peType == "Seismic":
            depthInKm = self.eventDict.get(f"originDepth{self.fieldNameSuffix}") * GeneralConstants.KILOMETERS_PER_MILE
            self.createSubElement(originElement, self.populateTagDict("depth", text=f"{depthInKm}", attrs={"unit": "kilometers"}))
        if peType in ["Volcanic", "Landslide"]:
            self.createSubElement(originElement, self.populateTagDict("name", text=self.eventDict.get(f"peName{self.fieldNameSuffix}")))
        eventLocationString = self.amm.getPrimaryPhysicalEventLocation(self.eventDict, self.fieldNameSuffix)
        self.createSubElement(originElement, self.populateTagDict("location", text=eventLocationString))

    def createTsunamiInfoBlock(self, xml, productDict):
        '''
        2.1.4 tsunamiInformation
            2.1.4.1 site
                2.1.4.1.1 location
                    2.1.4.1.1.1 siteName
                    2.1.4.1.1.2 siteStateName
                    2.1.4.1.1.3 siteStateCode
                    2.1.4.1.1..4 siteCountry
                    2.1.4.1.1.5 siteISOCountryCode
                    2.1.4.1.1.6 siteAreaID
                    2.1.4.1.1.7 siteCode
                    2.1.4.1.1.8 lat
                    2.1.4.1.1.9 long
                    2.1.4.1.1.10 siteLocalTimeZone
                2.1.4.1.2 forecast
                    2.1.4.1.2.1 forecastModelType
                    ...
                    2.1.4.1.2.20 currentMap
                2.1.4.1.3 observation
                    2.1.4.1.3.1 observedArrivalTime
                    ....
                    2.1.4.1.3.17 observedTimeSeries
                2.1.4.1.4 seaLevelStation
                    2.1.4.1.4.1 seaLevelStationURL
                    2.1.4.1.4.2 platformID
        '''
        sites = self.eventDict.get(f"seaLevelObs{self.fieldNameSuffix}")
        if sites:
            siteId = 1
            for site in sites:
                self.createSiteBlock(xml, productDict, site, siteId)
                siteId += 1

    # TWCBulletin sub-element
    def createHeaderBlock(self, xml, productDict):
        '''
        Create header block with the following sub-elements:
        2.1.2.1 header
            2.1.2.1.1 WMOID
            2.1.2.1.2 WMOCenterID
            2.1.2.1.3 WMODateTime
            2.1.2.1.4 AWIPSID
            2.1.2.1.5 bulletinNumber
            2.1.2.1.6 bulletinName
            2.1.2.1.7 issuingCenter
            2.1.2.1.8 bulletinDateTime
            2.1.2.1.9 bulletinDateTimeString
            2.1.2.1.10 productDescription
        '''
        # 2.1.2.1.1 WMOID
        self.createSubElement(xml, self.populateTagDict("WMOID", text=productDict.get("wmoID"),
                                                        attrs={"source": productDict.get("officeId")}))
        # 2.1.2.1.2 WMOCenterID
        self.createSubElement(xml, self.populateTagDict("WMOCenterID", text=productDict.get("officeId")))
        # 2.1.2.1.3 WMODateTime
        ddhhmmTime = self.tpc.getFormattedTime(self.issueTime, "%d%H%M", stripLeading=False,
                                               changeNoonMidnight=False)
        self.createSubElement(xml, self.populateTagDict("WMODateTimeGroup", text=ddhhmmTime))
        # 2.1.2.1.4 AWIPSID
        self.createSubElement(xml, self.populateTagDict("AWIPSID", text=productDict.get("awipsId")))
        # 2.1.2.1.5 bulletinNumber
        self.createSubElement(xml, self.populateTagDict("bulletinNumber",
                                                        text=str(productDict.get("messageNumber"))))
        # 2.1.2.1.6 bulletinName
        bulletinName = self.getBulletinName(productDict)
        self.createSubElement(xml, self.populateTagDict("bulletinName", text=bulletinName))
        # 2.1.2.1.7 issuingCenter
        if self.siteId == "NTWC":
            officeLocation = self.amm.ntwcOfficeLocationEnglish()
        else:
            officeLocation = self.amm.ptwcOfficeLocationEnglish()
        self.createSubElement(xml, self.populateTagDict("issuingCenter", text=officeLocation))
        # 2.1.2.1.8 bulletinDateTime
        issueTimeDT = TimeUtil.epochTimeMillisToDatetime(self.issueTime)
        issueTimeDT = TimeUtil.changeTimezoneOfDatetimeObject(issueTimeDT, "UTC")
        bulletinIssueTime = issueTimeDT.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.createSubElement(xml, self.populateTagDict("bulletinIssueTime", text=bulletinIssueTime))
        # 2.1.2.1.9 bulletinDateTimeString
        if self.productCategory in ["TIB", "TSU_TM"]:
            bulletinTimeZone = self.alu.getPrimaryTimezoneByProductRegionAbbreviation(self.productRegion)
        else:
            bulletinTimeZone = self.amm.getProductLevelTimezone(productDict)
        issueTimeString = self.getIssuanceTimeDate([bulletinTimeZone])
        if issueTimeString[-1] == "\n":
            issueTimeString = issueTimeString[:-1]
        self.createSubElement(xml, self.populateTagDict("bulletinIssueTimeString", text=issueTimeString))
        # 2.1.2.1.10 productDescription
        productDesc = productDict.get("productDescr")
        self.createSubElement(xml, self.populateTagDict("productDescription", text=productDesc))

    def createPreambleBlock(self, xml, productDict):
        '''
        Create preamble block with the following sub-elements:
        2.1.2.2 preamble
            2.1.2.2.1 bulletinHeadline
            2.1.2.2.2 bulletinPurpose
            2.1.2.2.3 bulletinApplies
            2.1.2.2.4 bulletinUpdates
        '''
        updateText = productDict.get("updatesBullet")
        if updateText:
            updateText = self.truncateText(updateText, 512)
            self.createSubElement(xml, self.populateTagDict("bulletinUpdates", text=updateText))

    def createProductSegmentsBlock(self, xml, productDict):
        '''
        Create productSegment block with the following sub-elements:
        2.1.2.3 productSegment
            An area can be described three ways: as a coastline segment defined by two break
            points, as a polygon defined by many vertices, or by zone/region descriptions
            2.1.2.3.1 area
        '''
        segmentDicts = productDict.get("segments")
        if self.productCategory == "TSU_TM":
            # ThreatMessage is different from other products in this part, which is based
            # on max amplitude category and country in that category
            self.createThreatMesgAreaBlock(xml, segmentDicts[0])
        elif (self.productRegion in self.amm.productRegionsWithSegmented() or
              self.productCategory == "TIB"):
            segId = 1
            for segmentDict in segmentDicts:
                self.createAreaBlock(xml, segmentDict, segId)
                segId += 1
        elif self.productRegion in ["Hi", "As", "Gu"] and self.productCategory == "TSU":
            self.createAreaBlock(xml, productDict, 1)

    def createActionsBlock(self, xml, productDict):
        '''
        Container for bulletin evaluation, response action, potential impacts, and
        other additional information descriptions.
        2.1.2.4.1 evaluation
        2.1.2.4.2 potentialImpacts
        2.1.2.4.3 recommendedActions
        2.1.2.4.4 earthquakeCaveat
        2.1.2.4.5 forecastCaveat
        2.1.2.4.6 otherTWCActions
        2.1.2.4.7 additionalInformation
        2.1.2.4.8 nextBulletin
        2.1.2.4.9 validTime
        '''

    def createTextBlock(self, xml, productDict):
        '''
        Container for all versions of the bulletin in its text forms
        2.1.2.5.1 bulletinBodyFull
        2.1.2.5.2 bulletinBodyPublic
        2.1.2.5.3 bulletinBodySpanish
        2.1.2.5.4 bulletinBodyShort
        2.1.2.5.5 bulletinBodyEAS
        '''
        # Get a complete copy of segmented text (2.1.1.18)
        segmentedBody = self.getTsunamiBulletinBodySegmentedText(productDict)
        if segmentedBody:
            tagDict = self.populateTagDict("bulletinBodyFull",
                                           text=self.createCdataText(segmentedBody))
            bulletinBody = self.createSubElement(xml, tagDict)

        # Get a complete copy of public bulletin (2.1.1.19)
        publicBody = self.getTsunamiBulletinBodyPublicText(productDict)
        if publicBody:
            tagDict = self.populateTagDict("bulletinBodyPublic",
                                           text=self.createCdataText(publicBody))
            bulletinBody = self.createSubElement(xml, tagDict)

        # Get a complete copy of Spanish bulletin (2.1.1.20)
        spanishBody = self.getTsunamiBulletinBodySpanishText(productDict)
        if spanishBody:
            tagDict = self.populateTagDict("bulletinBodySpanish",
                                           text=self.createCdataText(spanishBody))
            bulletinBody = self.createSubElement(xml, tagDict)
        # Get a complete copy of short version of bulletin (2.1.1.20)
        shortText = self.getTsunamiBulletinBodyShortText(productDict)
        if shortText:
            tagDict = self.populateTagDict("bulletinBodyShort",
                                           text=self.createCdataText(shortText))
            bulletinBody = self.createSubElement(xml, tagDict)

    def createFlagsBlock(self, xml, productDict):
        '''
        Container for Boolean flags related to the bulletin
        2.1.2.6.1 testMessage
        2.1.2.6.2 tsunamiRecorded
        '''
        self.createSubElement(xml, self.populateTagDict("testMessage", text=self.getTestMessageFlag()))
        self.createSubElement(xml, self.populateTagDict("tsunamiRecorded", text=self.getTsunamiRecordedFlag()))

    def createGraphicProductsBlock(self, xml, productDict):
        '''
        Container for tags that identify supplemental products associated with
        this bulletin that will be available via the website
        2.1.2.7.1 offshoreForecastMap
        2.1.2.7.2 coastalForecastMap
        2.1.2.7.3 polygonMap
        2.1.2.7.4 travelTimeMap
        2.1.2.7.5 video
        '''
        imageryDescriptors = self.eventDict.get(f"imageryDescriptors{self.fieldNameSuffix}")
        if imageryDescriptors:
            energyMapName = ""
            polygonMapName = ""
            travelTimeMapName = ""
            imageryDescs = imageryDescriptors.split("\n")
            for imageryDesc in imageryDescs:
                if "EnergyMap" in imageryDesc:
                    energyMapName = imageryDesc
                elif "PolygonMap" in imageryDesc:
                    polygonMapName = imageryDesc
                elif "TravelTimesMap" in imageryDesc:
                    travelTimeMapName = imageryDesc
            if energyMapName:
                eneryMapElement = self.createSubElement(xml, self.populateTagDict("offshoreForecastMap"))
                self.createSubElement(eneryMapElement, self.populateTagDict("imageLink", text=energyMapName))
                self.createSubElement(eneryMapElement, self.populateTagDict("validTime", text="60", attrs={"unit": "minutes"}))
            if polygonMapName:
                polygonMapElement = self.createSubElement(xml, self.populateTagDict("polygonMap"))
                self.createSubElement(polygonMapElement, self.populateTagDict("imageLink", text=polygonMapName))
                self.createSubElement(polygonMapElement, self.populateTagDict("validTime", text="60", attrs={"unit": "minutes"}))
            if travelTimeMapName:
                travelTimeMapElement = self.createSubElement(xml, self.populateTagDict("travelTimeMap"))
                self.createSubElement(travelTimeMapElement, self.populateTagDict("imageLink", text=travelTimeMapName))
                self.createSubElement(travelTimeMapElement, self.populateTagDict("validTime", text="60", attrs={"unit": "minutes"}))

    def createThreatMesgAreaBlock(self, xml, segmentDict):
        '''
        Create Threat Message Area block
        '''
        # Determine the analysis type performed on the stations
        stationAnalysisType = self.eventDict.get("stationAnalysisType")
        # Get either a list of country names or a dictionary or categories
        countryInformation = self.eventDict.get("threatCountryInformation")
        if (stationAnalysisType == "amplitudes" and countryInformation):
            countryInformationDict = countryInformation[0]
            segmentNumber = 1
            for category in ["high", "medium", "low"]:
                countryList = countryInformationDict.get(category)
                if countryList:
                    self.createTMCategorySegment(xml, segmentDict, category,
                                                 countryList, segmentNumber)
                    segmentNumber += 1

    def createTMCategorySegment(self, xml, segmentDict, ampCate, names, segId):
        areaElement = self.createSubElement(xml, self.populateTagDict("area",
                                                                      attrs={"id": f"{segId}"}))
        hdlnText = self.slm.summaryHeadlines_text(segmentDict, False, False).strip("...")
        headline = self.createSubElement(areaElement, self.populateTagDict("headline",
                                                                           text=self.createCdataText(hdlnText)))
        if ampCate == "high":
            cateText = "greater than 3 meters"
        elif ampCate == "medium":
            cateText = "1-3 meters"
        elif ampCate == "low":
            cateText = "0.3-1 meters"
        self.createAreaStatusLevelElement(areaElement, cateText)
        self.createZoneBlock(areaElement, names)

    def createAreaBlock(self, xml, inputDict, segId):
        '''
        2.1.2.3.1 area
            2.1.2.3.1.1 UGCCode
            2.1.2.3.1.2 VTECCode
            2.1.2.3.1.3 areaHeadline
            2.1.2.3.1.4 areaName
            2.1.2.3.1.5 areaStatusLevel
                Must be one of the following alert or threat levels:
                5 Alert levels:
                Information
                Watch
                Advisory
                Warning
                Cancellation

                6 Threat levels:
                Undetermined
                Potential Threat
                0 – 0.3 meters
                0.3 – 1.0 meters
                1.0 – 3.0 meters
                >3.0 meters
            2.1.2.3.1.6 areaStatusDefinition
            2.1.2.3.1.7 areaPotentialImpacts
            2.1.2.3.1.8 areaRecommendedActions
            2.1.2.3.1.9 areaEASSummary
            2.1.2.3.1.10 breakPoint
                2.1.2.3.1.10.1 breakPointStart
                2.1.2.3.1.10.2 breakPointEnd
            2.1.2.3.1.11 polygon
            2.1.2.3.1.12 zone
        '''
        areaElement = self.createSubElement(xml, self.populateTagDict("area", attrs={"id": f"{segId}"}))
        if self.productCategory == "TSU":
            ugcCodeElement = self.createSubElement(areaElement, self.populateTagDict("UGCCode"))
            if self.productRegion in self.amm.productRegionsWithSegmented():
                ugcCodeElement.text = self.createCdataText(inputDict.get("segmentBeginDict").get("ugcHeader", ""))
                # VTECCode, optional, If used, used up to twice per segment, such as CAN/EXA, or CAN/NEW
                vtecStrings = inputDict.get("segmentBeginDict").get("vtecString")
                if vtecStrings is not None:
                    if len(vtecStrings) > 1:
                        vtecStrings = vtecStrings.split("\n")
                    for vtecString in vtecStrings:
                        self.createSubElement(areaElement, self.populateTagDict("VTECCode", text=vtecString))
            else:
                ugcCodeElement.text = self.createCdataText(inputDict.get("productBeginDict").get("ugcHeader_pub"))
                vtecString = inputDict.get("productBeginDict").get("vtecString_pub")
                self.createSubElement(areaElement, self.populateTagDict("VTECCode", text=vtecString))

        # Area headline:short descriptive summary of this segment
        if self.productRegion in self.amm.productRegionsWithSegmented() or self.productCategory == "TIB":
            hdlnText = self.slm.summaryHeadlines_text(inputDict, False, False).strip("...")
        else:
            hdlnText = inputDict.get("productBeginDict").get("summaryHeadlines_pub").strip("...")
        areaHeadline = self.createSubElement(areaElement, self.populateTagDict("areaHeadline",
                                                                               text=self.createCdataText(hdlnText)))

        # Area Name: Descriptive text of the region for this area
        if self.productCategory == "TSU" and self.productRegion in self.amm.productRegionsWithSegmented():
            areaText = self.createCdataText(inputDict.get("segmentBeginDict").get("areaList_Std"))
            areaName = self.createSubElement(areaElement, self.populateTagDict("areaName", text=areaText))

        # areaStatusLevel
        areaStatusLevel = self.amm.getSegmentCategory(inputDict)
        self.createAreaStatusLevelElement(areaElement, areaStatusLevel)

        # AreaStatusDefinition
        areaStatusDefinition = self.amm.getAreaStatusDefinition(inputDict)
        self.createSubElement(areaElement, self.populateTagDict("areaStatusDefinition",
                                                                text=areaStatusDefinition))

        # Now only NTWC has breakPoints
        if self.siteId == "NTWC":
            self.createBreakPointBlock(areaElement, inputDict)
        elif self.siteId == "PTWC":
            zoneList = self.getZoneList()
            self.createZoneBlock(areaElement, zoneList)

    def createBreakPointBlock(self, xml, segmentDict):
        bkptElement = self.createSubElement(xml, self.populateTagDict("breakPoint"))
        # Get breakpointStart/End for this segment
        startEndBreakPointDicts = self.getSegmentStartAndEndBreakPoint(segmentDict)
        eventDict = self.agu.getAllEventDicts(segmentDict)[0]
        breakPointsDict = eventDict.get("breakPointsDict")
        for startEnd in startEndBreakPointDicts:
            startBpDict = startEnd[0]
            endBpDict = startEnd[1]

            bkptStartElement = self.createSubElement(bkptElement,
                                                     self.populateTagDict("breakPointStart"))
            if not self.agu.isBreakPointSegmentSpecial(startBpDict):
                # Sub - Elements (location, lat, long), to do if have descriptor, add to the location.
                startBkptName = startBpDict.get(HazardConstants.LOWER_BP_ATTR_NAME)
                startBkptInfo = breakPointsDict.get(startBkptName)
                startDescriptor = startBkptInfo.get("descriptor")
                startState = startBpDict.get("state")
                startText = f"{startBkptName}, {startState}"
                if startDescriptor != "None":
                    startText += f" ({startDescriptor})"
                self.createSubElement(bkptStartElement, self.populateTagDict("breakpointLocation",
                                                                             text=startText))
                strLat = str(startBkptInfo.get("latitude"))
                strLon = str(startBkptInfo.get("longitude"))
                self.createSubElement(bkptStartElement, self.populateTagDict("geo:lat", text=strLat))
                self.createSubElement(bkptStartElement, self.populateTagDict("geo:long", text=strLon))

            bkptEndElement = self.createSubElement(bkptElement,
                                                   self.populateTagDict("breakPointEnd"))
            if not self.agu.isBreakPointSegmentSpecial(endBpDict):
                # Sub - Elements (location, lat, long)
                endBkptName = endBpDict.get(HazardConstants.UPPER_BP_ATTR_NAME)
                endBkptInfo = breakPointsDict.get(endBkptName)
                endDescriptor = endBkptInfo.get("descriptor")
                endState = endBpDict.get("state")
                endText = f"{endBkptName}, {endState}"
                if endDescriptor != "None":
                    endText += f" ({endDescriptor})"
                self.createSubElement(bkptEndElement, self.populateTagDict("breakpointLocation",
                                                                           text=endText))
                strLat = str(endBkptInfo.get("latitude"))
                strLon = str(endBkptInfo.get("longitude"))
                self.createSubElement(bkptEndElement, self.populateTagDict("geo:lat", text=strLat))
                self.createSubElement(bkptEndElement, self.populateTagDict("geo:long", text=strLon))

    def getSegmentStartAndEndBreakPoint(self, segmentDict):
        '''
        @summary: Get the break point segment start and end locations
        @param segmentDict: The segment-level dictionary
        @return: A list of tuples containing the break point start and end dictionaries
        of information
        '''
        startEndList = []
        eventDict = self.agu.getAllEventDicts(segmentDict)[0]
        brkptSegs = eventDict.get("breakPointSegmentDicts")
        if not brkptSegs:
            return startEndList
        consecutiveNumGroups = self.agu.getConsecutiveSegmentGroups(brkptSegs)
        for s, e in consecutiveNumGroups:
            for brkptSeg in brkptSegs:
                bpNum = self.agu.getBreakPointInteger(brkptSeg.get(HazardConstants.BP_NUM_ATTR_NAME))
                if s == bpNum:
                    breakPointStartDict = brkptSeg
                if e == bpNum:
                    breakPointEndDict = brkptSeg
            startEnd = (breakPointStartDict, breakPointEndDict)
            startEndList.append(startEnd)
        return startEndList

    def createAreaStatusLevelElement(self, xml, areaStatusLevel):
        self.createSubElement(xml, self.populateTagDict("areaStatusLevel", text=areaStatusLevel))

    def createZoneBlock(self, xml, zoneList):
        zoneId = 1
        zoneListStr = self.tpc.joinStringsWithOxfordComma(zoneList)
        self.createRegionNameElement(xml, zoneListStr)
        for zoneLoc in zoneList:
            zoneElement = self.createSubElement(xml, self.populateTagDict("zone",
                                                                          attrs={"id": f"{zoneId}"}))
            self.createSubElement(zoneElement, self.populateTagDict("zoneLocation", text=zoneLoc))
            zoneId += 1

    def createRegionNameElement(self, xml, names):
        self.createSubElement(xml, self.populateTagDict("regionName", text=self.createCdataText(names)))

    def createSiteBlock(self, xml, productDict, site, siteId):
        '''
        Container for observations and predictions related to the event for a particular site
            location
            forecast
            observation
            seaLevelStation
        '''
        siteElement = self.createSubElement(xml, self.populateTagDict("site", attrs={"id": f"{siteId}"}))
        self.createLocationBlock(siteElement, productDict, site)
        self.createForecastBlock(siteElement, productDict, site)
        self.createObservationBlock(siteElement, productDict, site)
        self.createSeaLevelStation(siteElement, productDict, site)

    def createLocationBlock(self, xml, productDict, site):
        '''
        Container for the location information for the specified site.
        for example (for full structure),
        <location>
         <siteName>Shemya, Alaska</siteName>
         <siteCountry>U.S./Canada</siteCountry>
         <siteISOCountryCode></siteISOCountryCode>
         <siteAreaID>0</siteAreaID>
         <geo:lat>52.730000</geo:lat>
         <geo:long>174.070007</geo:long>
         <siteLocalTimeZone>AKDT</siteLocalTimeZone>
        </location>
        '''
        locationElement = self.createSubElement(xml, self.populateTagDict("location"))
        self.createSubElement(locationElement, self.populateTagDict("siteName", text=site[1]))

    def createForecastBlock(self, xml, productDict, site):
        '''
        Container for elements pertaining to tsunami forecasts at the site
        '''
        forecastElement = self.createSubElement(xml, self.populateTagDict("forecast"))
        self.createSubElement(forecastElement, self.populateTagDict("forecastArrivalTime", text=site[2]))

    def createObservationBlock(self, xml, productDict, site):
        '''
        Container for elements pertaining to tsunami observations at the site
        '''
        observationElement = self.createSubElement(xml, self.populateTagDict("observation"))
        self.createSubElement(observationElement, self.populateTagDict("observedPosAmplitude", text=site[3]))

    def createSeaLevelStation(self, xml, productDict, site):
        '''
        Container for elements containing details of the specified sea level gauge if one exists at the site
        '''
        self.createSubElement(xml, self.populateTagDict("seaLevelStation"))

    def getBulletinName(self, productDict):
        text = ""
        if self.productCategory == "TSU":
            text += "TSUNAMI MESSAGE NUMBER "
        elif self.productCategory in ["TIB", "TSU_TM"]:
            text += "Tsunami Information Statement Number "
        msgNum = self.agu.getTsunamiMessageNumber(productDict)
        text += f"{msgNum}"
        return text

    def getZoneList(self):
        '''
        @summary: Get the state name for PTWC products
        @return: list of zones
        '''
        zoneList = []
        if self.productRegion == "Hi":
            zoneList = ["ALL COUNTIES IN THE STATE OF HAWAII"]
        elif self.productRegion == "As":
            zoneList = ["American Samoa"]
        elif self.productRegion == "Gu":
            zoneList = ["Guam", "CNMI"]
        elif self.productRegion == "Pr":
            zoneList = ["Puerto Rico", "the Virgin Islands"]
        return zoneList

    def getTsunamiBulletinBodySegmentedText(self, productDict):
        '''
        @param: productDict
        @return: Return the whole body of segmented formatter if having segmented formatter
        '''
        if self.productCategory == "TSU":
            legacyText = TSU_Segmented_Formatter.Format().execute(productDict)
            if legacyText:
                return legacyText[0]
            else:
                return ""

    def getTsunamiBulletinBodyPublicText(self, productDict):
        bodyText = ""
        if self.productCategory == "TSU":
            bodyText = TSU_Public_Formatter.Format().execute(productDict)[0]
        elif self.productCategory == "TIB":
            bodyText = TIB_Public_Formatter.Format().execute(productDict)[0]
        elif self.productCategory == "TSU_TM":
            bodyText = TSU_TM_Formatter.Format().execute(productDict)[0]
        return bodyText

    def getTsunamiBulletinBodySpanishText(self, productDict):
        bodyText = ""
        if self.productCategory == "TSU":
            bodyText = TSU_Spanish_Formatter.Format().execute(productDict)
        elif self.productCategory == "TIB":
            bodyText = TIB_Spanish_Formatter.Format().execute(productDict)
        if bodyText:
            return bodyText[0]
        else:
            return ""

    def getTsunamiBulletinBodyShortText(self, productDict):
        bodyText = ""
        if self.productCategory == "TSU":
            bodyText = TSU_Verbal_Formatter.Format().execute(productDict)[0]
        elif self.productCategory == "TIB":
            bodyText = TIB_Verbal_Formatter.Format().execute(productDict)[0]
        return bodyText

    def getTestMessageFlag(self):
        testMessage = GeneralUtilities.isPractice(self.runMode) or self.testMode
        return "true" if testMessage else "false"

    def getTsunamiRecordedFlag(self):
        tsunamiRecordedFlag = "false"
        return tsunamiRecordedFlag

    def createCdataText(self, text):
        return "<![CDATA[%s]]>" % text

    def truncateText(self, text, length):
        return text[:length] + "..." if len(text) > length else text

    def makeRootElement(self, productDict):
        '''
        Create root element and namespace for TEX
        '''
        xml = self.createElement("tsunamiEvent")
        xml.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        xml.attrib["xsi:noNamespaceSchemaLocation"] = "http://ntwc.arh.noaa.gov/schema/TEX2.0.xsd"
        xml.attrib["xmlns:geo"] = "http://www.w3.org/2003/01/geo/wgs84_pos#"
        return xml


# Override ElementTree _escape_cdata function
def _escape_cdata(text, encoding="unicode"):
    # escape character data
    try:
        # it's worth avoiding do-nothing calls for strings that are
        # shorter than 500 character, or so. Assume that's, by far,
        # the most common case in most applications.
        if "&" in text:
            text = text.replace("&", "&amp;")
        # if "<" in text:
        #     text = text.replace("<", "&lt;")
        # if ">" in text:
        #     text = text.replace(">", "&gt;")
        # return text.encode(encoding, "xmlcharrefreplace")
        return text
    except (TypeError, AttributeError): _raise_serialization_error(text)


ET._escape_cdata = _escape_cdata
