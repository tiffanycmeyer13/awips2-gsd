# *** Override behavior of TSU_CAP_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Create CAP messages corresponding to a single product
    @since: Aug 2022
    @author GSL Hazard Services Team
'''

import copy, os
import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsMessageMethods
import CAP_Utilities
import GeneralConstants
import GeneralUtilities
import GenericRegistryObjectDataAccess as GRODA
import NWS_Machine_Formatter
import TimeUtil
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

        self.adu = AtomsDisseminationUtilities.AtomsDisseminationUtilities()
        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.capUtils = CAP_Utilities.CAP_Utilities()

        # Determine if CAVE is in practice more or not
        self.practice = GeneralUtilities.isPractice(self.runMode)
        # Build message identifier information
        self.prefix = ""
        self.segmentIdentifier = 0
        # Get the message status
        self.status = self.getStatus()
        self.productRegion = productDict.get("productRegion")
        self.siteId = productDict.get("siteID")
        self.productCategory = productDict.get("productCategory")
        if self.productCategory == "TSU":
            self.fieldNameSuffix = f"_{productDict.get('productLabel')}"
        else:
            self.fieldNameSuffix = ""
        self.issueFlag = productDict.get("issueFlag")

    def execute(self, productDict):
        '''
        @summary: Main method of execution to generate Common Alerting Protocol
        (CAP) messages. Loops through the segments of the product dictionary and
        produces a CAP message for every P-VTEC line.
        @param productDict: The product-level dictionary produced by a product
        generator
        @return: Returns the resulting CAP messages in XML format.
        '''
        self.initialize(productDict)

        messages = []
        if productDict:
            # For each VTEC line of the productDict, there will be a separate CAP message
            for segmentDict in productDict.get("segments"):
                self.segmentIdentifier += 1
                # Establish time zone to use for the segment
                self.setUp_segment(segmentDict)
                self.tz = self.segmentTimeZones[0]
                # Create one CAP message per VTEC line and which there is only one of per section
                sections = segmentDict.get("sections")
                self.pvtecIdentifier = 1
                for sectionDict in sections:
                    capSegDict = copy.deepcopy(segmentDict)
                    capSegDict["sections"] = [sectionDict]
                    '''
                    Create one CAP message per polygon. If there is more than one polygon in
                    the eventDict, add the polygon number to the end of <identifier> tag
                    It was decided that, if ATOMS were to include polygons in CAP messages,
                    they would be predefined for each UGC area, and stored in a database on
                    ATOMS to be accessed as needed. To stay under the 100 vertex limit, a
                    CAP message would be generated for every UGC-defined area under threat.
                    This could result in a large number of CAP messages for each WMO bulletin;
                    GSL suggested that the CAP identifier be extended with a suffix like “-a”,
                    “-b”, etc. The identifier is crucial to tracking a series of CAP messages
                    through the life cycle of an event.
                    '''
                    capMessageDict = self.createCAPMessageDict(sectionDict)
                    capMessageKeys = list(capMessageDict.keys())
                    if len(capMessageKeys) == 1:
                        self.polygonIdentifier = 0
                        self.polygon = capMessageDict.get(capMessageKeys[0])
                        self.createCAP_message(messages, productDict, capSegDict, sectionDict)
                    else:
                        for key in capMessageKeys:
                            self.polygon = capMessageDict[key]
                            self.polygonIdentifier = key
                            self.createCAP_message(messages, productDict, capSegDict, sectionDict)
                    self.pvtecIdentifier += 1
        return messages

    def recordGeneratedText(self, productDict, textProductList):
        '''
        @summary: Write the text product(s) from this formatter to a physical file
        @param productDict: The product-level dictionary
        @param textProductList: A list of text product(s) created by the formatter
        @return: None
        '''
        if self.issueFlag and productDict.get("siteID") in ["NTWC", "PTWC"]:
            self.adu.writeAtomsFile(productDict, textProductList, self.__module__)

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary or "pass" if a
        machine-readable formatter with no defined product parts
        '''
        pass

    def createCAPMessageDict(self, sectionDict):
        '''
        @summary: Create a dictionary that determines the number of CAP messages to be
        created based on the number of ugc associated with each hazard event accessible
        from the eventDict, this is to do
            key - a message number that will increment with each ugc (Default: 1)
            value - a shapely Polygon geometry
                    None if the product does not require a <polygon> tag
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @return: capMessageDict
        '''
        capMessageNum = 1
        capMessageDict = {}
        if self.productID in self.capUtils.PolygonExclusionCategories():
            capMessageDict[capMessageNum] = None
        else:
            # Determine how many polygons are in this sectionDict
            for eventDict in sectionDict.get("eventDicts"):
                geometryList = self.geomUtils.getValidGeometryList(eventDict.get("geometry"))
                for geom in geometryList:
                    capMessageDict[capMessageNum] = geom
                    capMessageNum += 1
        return capMessageDict

    # List of languages for supporting Wireless Emergency Alert (WEA) messages
    def getLanguageInfo(self):
        '''
        @summary: A configurable list of languages supported by this formatter
        that will be written if the message triggers the Wireless Emergency
        Alerting (WEA) system
        @return: A list of dictionaries
        '''
        return [
            {"languageType": "en-US", "shortText": ".EN.S", "longText": ".EN.L"},
            {"languageType": "es-US", "shortText": ".SP.S", "longText": ".SP.L"},
            ]

    def createCAP_message(self, messages, productDict, capSegDict, sectionDict):
        '''
        @summary: Create a single CAP message using the information from a single VTEC
        line within the product dictionary
        @param messages: A list of Element objects, each one corresponding to a single CAP message
        @param productDict: The product-level dictionary
        @param capSegDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @return: An updated messages list in memory
        '''
        xml = self.createElement("alert")
        xml.attrib["xmlns"] = self.capVersionId_text()
        self.createCAP_xml(xml, productDict, capSegDict, sectionDict)
        xmlString = self.convertElementObjectToString(xml, "unicode")
        if self.issueFlag:
            self.storeCapIdToTable(productDict, capSegDict, sectionDict)
        messages.append(ProductUtils.prettyXML(xmlString, True))

    def createCAP_xml(self, xml, productDict, segDict, sectionDict):
        '''
        @summary: Returns the CAP message in XML format for the given polygon.
        @param xml: XML data structure corresponding to a single CAP message
        @param productDict: dictionary values for an entire product
        @param segDict: dictionary of values for a segment of the product
        @param sectionDict: dictionary of values for a section of the product
        @return: Returns the resulting CAP message XML format.
        '''
        # Main Section
        self.createMainTags(xml, productDict, segDict, sectionDict)

        # Info Section
        infoDicts = self.createInfoDicts(productDict, segDict, sectionDict)
        for infoDict in infoDicts:
            # Always create English version info block
            self.createInfoBlock(xml, productDict, segDict, sectionDict, infoDict, "en-US")
            # If a WEA message needs be issued, create Spanish version info block
            if self.isMessageActivatingWEA_VTEC(productDict, segDict, sectionDict, infoDict):
                self.createInfoBlock(xml, productDict, segDict, sectionDict, infoDict, "es-US")

    def createMainTags(self, xml, productDict, segDict, sectionDict):
        '''
        @summary: Create all of the tags that appear in the CAP message prior to the <info> blocks
        @param xml: XML data structure corresponding to a single CAP message
        @param productDict: dictionary values for an entire product
        @param segDict: dictionary of values for a segment of the product
        @param sectionDict: dictionary of values for a section of the product
        @return: NoneType; the xml is updated in memory
        '''
        tagDict = {
            "identifier": self.createIdentifierTag(productDict, segDict, sectionDict),
            "sender": self.createSenderTag(),
            "sent": self.createSentTag(),
            "status": self.createStatusTag(),
            "msgType": self.createMsgTypeTag(sectionDict),
            "source": self.createSourceTag(),
            "scope": self.createScopeTag(),
            "code": self.createCodeTag(),
            "references": self.createReferencesTag(sectionDict),
            "incidents": self.createIncidentsTag(productDict, segDict, sectionDict)
            }
        # Create all tags
        for tagName in tagDict:
            tagValue = tagDict[tagName]
            if tagValue:
                self.createSubElement(xml, self.populateTagDict(tagName, text=tagValue))

    def createIdentifierTag(self, productDict, segmentDict, sectionDict, infoDict=None):
        '''
        @summary: Create the <identifier> tag within the main section of the CAP message
        Identifer is composed as follows:
        AAAA-NN-BBBBBB where:
        1) AAAA is the four character identification of the tsunami center:
        - PAAQ identifies the National Tsunami Warning Center
        - PHEB identifies the Pacific Tsunami Warning Center
        2) NN is the bulletin number
        3) BBBBBB is a unique identifier automatically generated by the
        tsunami warning computer system. This unique identifier is used
        internally, to identify a particular seismic/tsunami event.
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary; this could also be None if not defined
        @param infoDict: A dictionary of commonly accessible parameters; this could also be None if not defined
        @return: String
        '''
        bulletNum = str(productDict.get("messageNumber"))
        customID = productDict.get("customId")
        officeId = str(productDict.get("officeId"))
        identifier = f"{officeId}-{bulletNum}-{customID}"
        return identifier

    def createSenderTag(self):
        '''
        @summary: Create the <sender> tag within the main section of the CAP message
        @return: String
        '''
        return f"{self.siteId.lower()}@noaa.gov"

    def createSentTag(self):
        '''
        @summary: Create the <sent> tag within the main section of the CAP message
        @return: String
        '''
        return self.createTimeString(self.issueTime, self.tz)

    def createStatusTag(self):
        '''
        @summary: Create the <status> tag within the main section of the CAP message
        @return: String
        '''
        return self.status

    def createMsgTypeTag(self, sectionDict):
        '''
        @summary: Determine the message time based on the Valid Time Event Code (VTEC)
        or the event at the section-level
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @return: String
        '''
        vtecRecord = sectionDict.get("vtecRecord", {})
        action = self.tpc.getVtecAction(vtecRecord)
        self.msgType = "Alert"
        if action in ["EXA", "EXB", "NEW"]:
            self.msgType = "Alert"
        elif action in ["CON", "COR", "EXP", "EXT"]:
            self.msgType = "Update"
        elif action in ["CAN", "UPG"]:
            self.msgType = "Cancel"
        return self.msgType

    def createSourceTag(self):
        '''
        @summary: Create the <source> tag within the main section of the CAP message
        @return: String
        '''
        return self.siteId

    def createScopeTag(self):
        '''
        @summary: Create the <scope> tag within the main section of the CAP message
        @return: String
        '''
        return "Public"

    def createCodeTag(self):
        '''
        @summary: Create the <code> tag within the main section of the CAP message
        @return: String
        '''
        return "profile:CAP-TSU:1.1"

    def createReferencesTag(self, sectionDict):
        '''
        @summary: Create the optional <references> tag within the main section of the
        CAP message
        @return: String
        '''
        return self.getReferences(sectionDict)

    def createIncidentsTag(self, productDict, segDict, sectionDict):
        '''
        @summary: Create the <incidents> tag within the main section of the
        CAP message
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary; this could also be None if not defined
        @return: String
        '''
        return productDict.get("customId")

    def createInfoDicts(self, productDict, segDict, sectionDict):
        '''
        @summary: Create infoDict list based on product category. For threat message,
        it creates an infoDict per category, for others, it creates an infoDict per
        eventDict.
        @param productDict: The product-level dictionary
        @param segDict: The segment-level dictionary
        @param sectionDict: A single section of the segment-level dictionary
        @return: A list of dictionaries
        '''
        if self.productCategory == "TSU_TM":
            infoDicts = self.createInfoDictsForThreatMessage(productDict, segDict, sectionDict)
        else:
            infoDicts = self.createInfoDictsForSection(productDict, segDict, sectionDict)
        return infoDicts

    def createInfoDictsForThreatMessage(self, productDict, segDict, sectionDict):
        '''
        @summary: Parse the nested product dictionary to retrieve common
        attributes that will be used frequently in this formatter and put
        these in a flattened dictionary
        @param productDict: The product-level dictionary
        @param segDict: The segment-level dictionary
        @param sectionDict: A single section of the segment-level dictionary
        @return: A list of dictionaries
        '''
        infoDicts = []
        if "eventDicts" in sectionDict and sectionDict.get("eventDicts"):
            eventDicts = sectionDict.get("eventDicts")
            for eventDict in eventDicts:
                stationAnalysisType = eventDict.get("stationAnalysisType")
                countryInformation = eventDict.get("threatCountryInformation")
                eventTagValue = "Tsunami Potential Threat"
                countryList = []
                if countryInformation:
                    # Logic for a threat message with no amplitude information
                    if stationAnalysisType and stationAnalysisType != "amplitudes":
                        countryList = countryInformation
                        infoDict = self.createInfoDictTMCategory(sectionDict, eventDict,
                                                                 eventTagValue, countryList)
                        infoDicts.append(infoDict)
                    elif stationAnalysisType == "amplitudes":
                        countryInformationDict = countryInformation[0]
                        for category in ["high", "medium", "low"]:
                            countryList = countryInformationDict.get(category)
                            if countryList:
                                if category == "high":
                                    categoryValue = "greater than 3 meters"
                                elif category == "medium":
                                    categoryValue = "1-3 meters"
                                elif category == "low":
                                    categoryValue = "0.3-1 meters"
                                eventTagValue = f"Tsunami {categoryValue}"
                                infoDict = self.createInfoDictTMCategory(sectionDict, eventDict,
                                                                         eventTagValue, countryList)
                                infoDicts.append(infoDict)
                else:
                    infoDict = self.createInfoDictTMCategory(sectionDict, eventDict,
                                                             eventTagValue, countryList)
                    infoDicts.append(infoDict)
        return infoDicts

    def createInfoDictTMCategory(self, sectionDict, eventDict, eventTagValue, countryList):
        '''
        @summary: Create a infoDict for each Treat message category
        @param sectionDict: A single section of the segment-level dictionary
        @param eventDict: The event-level dictionary
        @param eventTagValue: The value for event tag
        @param countryList: A list of country for that category
        @return: A infoDict
        '''
        vtecRecord = sectionDict.get("vtecRecord", {})
        infoDict = {
                    "productLookupKey": self.getProductLookupKey(vtecRecord),
                    "action": self.tpc.getVtecAction(vtecRecord),
                    "phensig": vtecRecord.get("phensig"),
                    "category": self.category_text(),
                    "issueTimeMillis": vtecRecord.get("issueTime"),
                    "responseType": self.getResponseType(sectionDict, eventDict),
                    "urgency": self.getUrgency(sectionDict, eventDict),
                    "severity": self.getSeverity(sectionDict, eventDict),
                    "certainty": self.getCertainty(sectionDict, eventDict),
                    "startTime_datetime": eventDict.get("startTime"),
                    "eventEndingTime_datetime": eventDict.get("endTime"),
                    "isUntilFurtherNotice": eventDict.get("endTimeUntilFurtherNotice"),
                    "pil": eventDict.get("pil", ""),
                    "event": eventTagValue,
                    "geoType": eventDict.get("geoType", "polygon"),
                    "creationTime": eventDict.get("creationTime"),
                    "countries": countryList,
                    }
        return infoDict

    def createInfoDictsForSection(self, productDict, segDict, sectionDict):
        '''
        @summary: Parse the nested product dictionary to retrieve common
        attributes that will be used frequently in this formatter and put
        these in a flattened dictionary
        @param productDict: The product-level dictionary
        @param segDict: The segment-level dictionary
        @param sectionDict: A single section of the segment-level dictionary
        @return: A list of dictionaries
        '''
        infoDicts = []
        vtecRecord = sectionDict.get("vtecRecord", {})
        phensig = vtecRecord.get("phensig")
        issueTimeMillis = vtecRecord.get("issueTime")
        action = self.tpc.getVtecAction(vtecRecord)
        if "eventDicts" in sectionDict and sectionDict.get("eventDicts"):
            eventDicts = sectionDict.get("eventDicts")
            for eventDict in eventDicts:
                infoDict = {
                    "productLookupKey": self.getProductLookupKey(vtecRecord),
                    "action": action,
                    "phensig": phensig,
                    "category": self.category_text(),
                    "issueTimeMillis": issueTimeMillis,
                    "responseType": self.getResponseType(sectionDict, eventDict),
                    "urgency": self.getUrgency(sectionDict, eventDict),
                    "severity": self.getSeverity(sectionDict, eventDict),
                    "certainty": self.getCertainty(sectionDict, eventDict),
                    "startTime_datetime": eventDict.get("startTime"),
                    "eventEndingTime_datetime": eventDict.get("endTime"),
                    "isUntilFurtherNotice": eventDict.get("endTimeUntilFurtherNotice"),
                    "pil": eventDict.get("pil", ""),
                    "event": eventDict.get("headline").title(),
                    "geoType": eventDict.get("geoType", "polygon"),
                    "creationTime": eventDict.get("creationTime"),
                    }
                infoDicts.append(infoDict)
        return infoDicts

    def getProductLookupKey(self, vtecRecord):
        '''
        @summary: Build a key to look up the contents of certain tag elements
        within the CAP message (e.g., <eventCode>, <certainty>, etc.)
        @param vtecRecord: The VTEC record dictionary
        @param ibwType: The ibwType
        @return: String
        '''
        capPil = vtecRecord.get("pil")
        phensig = vtecRecord.get("phensig")
        lookupKey = f"{capPil}.{phensig}"
        return lookupKey

    def getResponseType(self, sectionDict, eventDict):
        '''
        @summary: Retrieve the "responseType" attribute from the eventDict unless
        the VTEC action is CAN or UPG then use "AllClear" and "Monitor" respectively
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary;
        @param eventDict: The event-level dictionary
        @return: String
        '''
        vtecRecord = sectionDict.get("vtecRecord", {})
        vtecAction = self.tpc.getVtecAction(vtecRecord)
        if vtecAction not in ["CAN", "UPG"]:
            responseType = eventDict.get("responseType", "")
        if vtecAction == "CAN":
            responseType = "AllClear"
        elif vtecAction == "UPG":
            responseType = "Monitor"
        return responseType

    def getUrgency(self, sectionDict, eventDict):
        '''
        @summary: Retrieve the "urgency" attribute from the eventDict unless
        the VTEC action is CAN or UPG then use "Past"
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary;
        @param eventDict: The event-level dictionary
        @return: String
        '''
        vtecRecord = sectionDict.get("vtecRecord", {})
        vtecAction = self.tpc.getVtecAction(vtecRecord)
        if vtecAction not in ["CAN", "UPG"]:
            urgency = eventDict.get("urgency", "")
        else:
            urgency = "Past"
        return urgency

    def getSeverity(self, sectionDict, eventDict):
        '''
        @summary: Retrieve the "severity" attribute from the eventDict unless
        the VTEC action is CAN then use "Minor"
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary;
        @param eventDict: The event-level dictionary
        @return: String
        '''
        vtecRecord = sectionDict.get("vtecRecord", {})
        vtecAction = self.tpc.getVtecAction(vtecRecord)
        if vtecAction != "CAN":
            severity = eventDict.get("severity", "")
        else:
            severity = "Minor"
        return severity

    def getCertainty(self, sectionDict, eventDict):
        '''
        @summary: Retrieve the "certainty" attribute from the eventDict unless
        the VTEC action is CAN then use "Observed"
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary;
        @param eventDict: The event-level dictionary
        @return: String
        '''
        vtecRecord = sectionDict.get("vtecRecord", {})
        vtecAction = self.tpc.getVtecAction(vtecRecord)
        if vtecAction not in ["CAN", "UPG"]:
            certainty = eventDict.get("certainty", "")
        else:
            certainty = "Observed"
        return certainty

    def createInfoBlock(self, xml, productDict, segDict, sectionDict, infoDict, langType):
        '''
        @param: Create an <info> block with sub-tags associated with the specified language type
        @param xml: XML data structure corresponding to a single CAP message
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @param infoDict: A dictionary of commonly accessible parameters
        @param langType: The language associated with this <info> block (either en-US or es-US)
        @return: A new <info> SubElement and associated sub-tags into the main XML message in memory
        '''
        infoBlockXML = self.createSubElement(xml, self.populateTagDict("info"))
        # Main tags
        self.createInfoBlockTags(infoBlockXML, productDict, segDict, sectionDict, infoDict, langType)
        # Parameters
        self.createParameterBlocks(infoBlockXML, productDict, segDict, sectionDict, infoDict, langType)
        # Area
        self.createAreas(infoBlockXML, productDict, segDict, sectionDict, infoDict)

    def createInfoBlockTags(self, infoBlockXML, productDict, segDict, sectionDict, infoDict, langType):
        '''
        @param: Populate the <info> with its primary tags
        @param infoBlockXML: XML data structure corresponding to a single CAP message
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @param infoDict: A dictionary of commonly accessible parameters
        @param langType: The language associated with this <info> block (either en-US or es-US)
        @return: NoneType; the infoBlockXML is updated in memory
        '''
        tagDict = {
            "language": self.createLanguageInfoTag(langType),
            "category": self.createCategoryInfoTag(),
            "event": self.createEventInfoTag(infoDict),
            "responseType": self.createResponseTypeInfoTag(infoDict),
            "urgency": self.createUrgencyInfoTag(infoDict),
            "severity": self.createSeverityInfoTag(infoDict),
            "certainty": self.createCertaintyInfoTag(infoDict),
            "eventCode": "",
            "effective": self.createEffectiveInfoTag(),
            "onset": self.createOnsetInfoTag(infoDict),
            "expires": self.createExpiresInfoTag(infoDict),
            "senderName": self.createSenderNameInfoTag(),
            "headline": self.createHeadlineInfoTag(productDict, segDict),
            "description": self.createDescriptionInfoTag(productDict, segDict, sectionDict, infoDict),
            "instruction": self.createInstructionInfoTag(segDict),
            "web": self.createWebInfoTag(productDict),
            }

        # Create all tags
        for tagName in tagDict:
            tagValue = tagDict[tagName]
            if tagValue:
                self.createSubElement(infoBlockXML, self.populateTagDict(tagName, text=tagValue))
            elif tagName == "eventCode":
                self.createEventCodeInfoTag(infoBlockXML, productDict, segDict, sectionDict, infoDict)

    def createLanguageInfoTag(self, languageType):
        '''
        @summary: Create the <languages> tag within the <info> section of the
        CAP message
        @param languageType: The language string (e.g., en-US)
        @return: String
        '''
        return languageType

    def createCategoryInfoTag(self):
        '''
        @summary: Create the <category> tag within the <info> section of the
        CAP message
        @return: String
        '''
        return "Geo"

    def createEventInfoTag(self, infoDict):
        '''
        @summary: Create the <event> tag within the <info> section of the
        CAP message
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        return infoDict.get("event")

    def createResponseTypeInfoTag(self, infoDict):
        '''
        @summary: Create the <responseType> tag within the <info> section of the
        CAP message
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        return infoDict.get("responseType")

    def createUrgencyInfoTag(self, infoDict):
        '''
        @summary: Create the <urgency> tag within the <info> section of the
        CAP message
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        return infoDict.get("urgency")

    def createSeverityInfoTag(self, infoDict):
        '''
        @summary: Create the <severity> tag within the <info> section of the
        CAP message
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        return infoDict.get("severity")

    def createCertaintyInfoTag(self, infoDict):
        '''
        @summary: Create the <severity> tag within the <info> section of the
        CAP message
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        return infoDict.get("certainty")

    def createEventCodeInfoTag(self, infoBlockXML, productDict, segDict, sectionDict, infoDict):
        '''
        @param: Create and populate the <eventCode> tag within the <info> block
        @param infoBlockXML: The SubElement containing the contents for the <info> block
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        if self.productCategory == "TSU":
            sameEventKey = infoDict.get("productLookupKey")
            phensig = infoDict.get("phensig")
            nwsValue = phensig.replace(".", "")
            # Search dictionary in CAP_Utilities to get the SAME event code
            self.sameEventValue = self.capUtils.getSAME_EventCodeDictionary().get(sameEventKey)
            # If no code exists, default to NWS
            if not self.sameEventValue:
                self.sameEventValue = self.defaultSAME_text()
            # Build <eventCode> tags
            self.createNewBlock(infoBlockXML, "eventCode",
                                self.createValueDict("SAME", self.sameEventValue))
            self.createNewBlock(infoBlockXML, "eventCode",
                                self.createValueDict("TsunamiSystemCategory", nwsValue))

    def createEffectiveInfoTag(self):
        '''
        @summary: Create the <effective> tag within the <info> section of the
        CAP message
        @return: String
        '''
        return self.createTimeString(self.issueTime, self.tz)

    def createOnsetInfoTag(self, infoDict):
        '''
        @summary: Create the <onset> tag within the <info> section of the
        CAP message
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        return self.getOnset(self.issueTime, infoDict.get("startTime_datetime"), self.tz)

    def createExpiresInfoTag(self, infoDict):
        '''
        @param: Create the <expires> tag within the <info> section of the
        CAP message
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        dt = 0
        expiresTimeString = ""
        action = infoDict.get("action")
        # For Tsunami Information and Cancellation add one hourto the current time
        if action == "CAN" or self.productCategory in ["TIB", "TSU_TM"]:
            dt = int(self.issueTime) + (60 * GeneralConstants.MILLIS_PER_MINUTE)
        # For Tsunami warning/watch/advisory add 2 hours to the current time
        elif self.productCategory == "TSU":
            dt = int(self.issueTime) + (120 * GeneralConstants.MILLIS_PER_MINUTE)
        if dt:
            expiresTimeString = self.createTimeString(dt, self.tz)
        return expiresTimeString

    def createSenderNameInfoTag(self):
        '''
        @summary: Create the <senderName> tag within the <info> section of the
        CAP message
        @return: String
        '''
        officeLocation = ""
        if self.siteId == "NTWC":
            officeLocation = self.amm.ntwcOfficeLocationEnglish()
        elif self.siteId == "PTWC":
            officeLocation = self.amm.ptwcOfficeLocationEnglish()
        return officeLocation

    def createHeadlineInfoTag(self, productDict, segDict):
        '''
        @summary: Create the <headline> tag within the <info> section of the
        CAP message
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @return: String
        '''
        headline = ""
        if self.productCategory == "TSU":
            '''
            If product region has segmented product, get headline from segmentDict,
            otherwise get form productDict
            '''
            if self.productRegion in self.amm.productRegionsWithSegmented():
                summaryHeadline = segDict.get("summaryHeadlines_Std")
            else:
                summaryHeadline = productDict.get("productBeginDict").get("summaryHeadlines_pub")
            headline = summaryHeadline.replace("\n", " ").lstrip("...").rstrip("... ")
        elif self.productCategory == "TIB":
            headline = "THIS IS A TSUNAMI INFORMATION STATEMENT"
        elif self.productCategory == "TSU_TM":
            headline = "TSUNAMI THREAT MESSAGE"
        return headline

    def createDescriptionInfoTag(self, productDict, segDict, sectionDict, infoDict):
        '''
        @summary: Create the <description> tag within the <info> section of the
        CAP message
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        description = ""
        vtecRecord = sectionDict.get("vtecRecord")
        if vtecRecord is not None:
            action = infoDict.get("action")
            hazName = self.tpc.hazardName(vtecRecord.get("hdln"), self.testMode, False).title()
            if action == "CAN":
                description = f"The {hazName} has been cancelled and is no longer in effect."
            else:
                hdln = self.createHeadlineInfoTag(productDict, segDict)
                eventDict = self.agu.getAllEventDicts(productDict)[0]
                descriptionString = self.amm.getPhysicalEventDescriptionString(eventDict, self.fieldNameSuffix)
                description += f"{hdln}. Event details: {descriptionString}"
        return description

    def createInstructionInfoTag(self, segDict):
        '''
        @summary: Create the <instruction> tag within the <info> section of the
        CAP message
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @return: String
        '''
        if self.productCategory == "TSU":
            ctas = self.getSegmentRecommendActions(segDict)
        else:
            ctas = ""
        return ctas

    def getSegmentRecommendActions(self, segmentDict):
        '''
        @summary: Create a single string of all Calls to Action (CTA) statements by
        combining all section-level CTAs together
        @param segmentDict: A single segment-level dictionary
        @return: A string of CTAs
        '''
        actionText = ""
        ctas = []
        activeSectionDicts = self.agu.getActiveSectionDicts(segmentDict)
        for sectionDict in activeSectionDicts:
            sectionActions = self.tpc.getVal(sectionDict, "callsToAction", "")
            if sectionActions:
                sectionActions = sectionActions.rstrip().split("\n")
                for sectionAction in sectionActions:
                    if sectionAction and sectionAction not in ctas:
                        ctas.append(sectionAction)
        if ctas:
            actionText = "\n\n".join(ctas)
        return actionText

    def createWebInfoTag(self, productDict):
        '''
        @summary: Create the <web> tag within the <info> section of the
        CAP message
        @return: String
        '''
        return self.getWebAddressString(productDict)

    def createParameterBlocks(self, infoBlockXML, productDict, segDict, sectionDict, infoDict, langType):
        '''
        @param: Create a series of <parameter> blocks within the <info> block
        @param infoBlockXML: The SubElement containing the contents for the <info> block
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @param infoDict: A dictionary of commonly accessible parameters
        @param langType: The language associated with this <info> block (either en-US or es-US)
        @return: String
        '''
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        isWeaActivated = self.isMessageActivatingWEA_VTEC(productDict, segDict, sectionDict, infoDict)
        if self.productCategory == "TSU":
            self.createVtecIdentifierParameter(infoBlockXML, sectionDict)
            self.createEasOrgIdentifierParameter(infoBlockXML)
            self.createNwsUgcIdentifierParameter(infoBlockXML, segDict)
            if isWeaActivated:
                self.createWEA_message(infoBlockXML, productDict, segDict, sectionDict,
                                       infoDict, langType)
            else:
                self.createBlockChannelIdentifierParameter(infoBlockXML)
        self.createLocationNameIdentifierParameter(infoBlockXML, eventDict)
        if self.agu.isPhysicalEventTypeSeismic(eventDict.get("physicalEventType")):
            self.createSeismicIdentifierParameters(infoBlockXML, eventDict)
        self.createEventOriginTimeIdentifierParameter(infoBlockXML, eventDict)
        self.createEventLatLonIdentifierParameter(infoBlockXML, eventDict)
        self.createImageryIdentifierParameters(infoBlockXML, productDict, eventDict)
        self.createTestingJsonIdentifierParameter(infoBlockXML, productDict)

    def createVtecIdentifierParameter(self, infoBlockXML, sectionDict):
        '''
        @summary: Get the information for the VTEC parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        vtecRecord = sectionDict.get("vtecRecord")
        vtecString = vtecRecord.get("vtecstr")
        if vtecString:
            vtecString = self.amm.replaceSiteIdWithOfficeId(vtecString, self.siteId)
            self.createNewBlock(infoBlockXML, "parameter",
                                self.createValueDict("VTEC", vtecString))

    def createEasOrgIdentifierParameter(self, infoBlockXML):
        '''
        @summary: Get the information for the EAS-ORG parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        self.createNewBlock(infoBlockXML, "parameter",
                            self.createValueDict("EAS-ORG", "WXR"))

    def createNwsUgcIdentifierParameter(self, infoBlockXML, segDict):
        '''
        @summary: Get the information for the NWSUGC parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        ugcString = self.tpc.makeUGCString(segDict.get("ugcs"))
        if ugcString:
            self.createNewBlock(infoBlockXML, "parameter",
                                self.createValueDict("NWSUGC", ugcString))

    def createWEA_message(self, infoBlockXML, productDict, segDict, sectionDict, infoDict, languageType):
        '''
        @param: Create a series of <parameter> blocks within the <info> block that correspond to a WEA
        activation
        @param infoBlockXML: The SubElement containing the contents for the <info> block
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @param infoDict: A dictionary of commonly accessible parameters
        @param langType: The language associated with this <info> block (either en-US or es-US)
        @return: String
        '''
        # Create WEAHandling parameter
        self.createNewBlock(infoBlockXML, "parameter", self.createValueDict("WEAHandling", "Imminent Threat"))
        # Create English/Spanish <CMAMtext> parameter for the 90 or 360 character WEA message
        for languageDict in self.getLanguageInfo():
            if languageDict["languageType"] == languageType:
                # CMAMtext holds the 90 character WEA message
                weaTextShort = self.getWeaTextString(infoDict, languageDict["shortText"])
                self.createNewBlock(infoBlockXML, "parameter", self.createValueDict("CMAMtext", weaTextShort))
                # CMAMlongtext holds the 360 character WEA message
                weaTextLong = self.getWeaTextString(infoDict, languageDict["longText"])
                self.createNewBlock(infoBlockXML, "parameter", self.createValueDict("CMAMlongtext", weaTextLong))

    def getWeaTextString(self, infoDict, textType):
        '''
        @summary: Get the text to populate the CMAMtext or CMAMlongtext strings
        @param infoDict: A dictionary of commonly accessible parameters
        @param textType: The short or long text type (e.g., EN.S, SP.L, etc.)
        @return: String
        '''
        weaDict = self.capUtils.getWEA_MessageDictionary()
        weaKey = infoDict.get("productLookupKey")
        # Pull language from dictionary
        weaText = weaDict.get(f"{weaKey}{textType}")
        return weaText

    def createBlockChannelIdentifierParameter(self, infoBlockXML):
        '''
        @summary: Get the information for the BLOCKCHANNEL parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        self.createNewBlock(infoBlockXML, "parameter",
                            self.createValueDict("BLOCKCHANNEL", "CMAS"))

    def createLocationNameIdentifierParameter(self, infoBlockXML, eventDict):
        '''
        @summary: Get the information for the EventLocationName parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param eventDict: The event-level dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        eventLocationString = self.amm.getPrimaryPhysicalEventLocation(eventDict, self.fieldNameSuffix)
        self.createNewBlock(infoBlockXML, "parameter",
                            self.createValueDict("EventLocationName", eventLocationString))

    def createSeismicIdentifierParameters(self, infoBlockXML, eventDict):
        '''
        @summary: Get the information for the EventPreliminaryMagnitude, EventPreliminaryMagnitudeType,
        and parameter block and, if it exists,
        add EventDepth parameter blocks and add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param eventDict: The event-level dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        magnitude = str(eventDict.get(f"magnitude{self.fieldNameSuffix}"))
        if magnitude:
            self.createNewBlock(infoBlockXML, "parameter",
                                self.createValueDict("EventPreliminaryMagnitude", magnitude))
        magnitudeType = eventDict.get(f"magnitudeType{self.fieldNameSuffix}")
        if magnitudeType:
            self.createNewBlock(infoBlockXML, "parameter",
                                self.createValueDict("EventPreliminaryMagnitudeType", magnitudeType))
        originDepth = str(eventDict.get(f"originDepth{self.fieldNameSuffix}"))
        if originDepth:
            self.createNewBlock(infoBlockXML, "parameter",
                                self.createValueDict("EventDepth", originDepth))

    def createEventOriginTimeIdentifierParameter(self, infoBlockXML, eventDict):
        '''
        @summary: Get the information for the EventOriginTime parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param eventDict: The event-level dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        originTime = eventDict.get(f"originTime{self.fieldNameSuffix}")
        if originTime:
            originTimeString = self.tpc.formatDatetime(originTime, "%H%M %p %Z %b %e %Y")
            self.createNewBlock(infoBlockXML, "parameter",
                                self.createValueDict("EventOriginTime", originTimeString))

    def createEventLatLonIdentifierParameter(self, infoBlockXML, eventDict):
        '''
        @summary: Get the information for the EventLatLon parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param eventDict: The event-level dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        originLatLon = self.amm.createLatLongText(eventDict, self.fieldNameSuffix)
        if originLatLon:
            self.createNewBlock(infoBlockXML, "parameter",
                                self.createValueDict("EventLatLon", originLatLon))

    def createImageryIdentifierParameters(self, infoBlockXML, productDict, eventDict):
        '''
        @summary: Get the information for the resource parameter blocks and, if any exist,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param productDict: The product-level dictionary
        @param eventDict: The event-level dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        imageryDescriptors = eventDict.get(f"imageryDescriptors{self.fieldNameSuffix}")
        if imageryDescriptors:
            energyMapDict = {}
            polygonMapDict = {}
            travelTimeMapDict = {}
            imageryDescs = imageryDescriptors.split("\n")
            mapUri = self.adu.getEventMapsJsonUri(productDict)
            for imageryDesc in imageryDescs:
                if "EnergyMap" in imageryDesc:
                    energyMapDict = {
                        "resourceDesc": "Energy Map",
                        "mimeType": "image/jpeg",
                        "uri": mapUri,
                        }
                elif "PolygonMap" in imageryDesc:
                    polygonMapDict = {
                        "resourceDesc": "Polygon Map",
                        "mimeType": "image/jpeg",
                        "uri": mapUri,
                        }
                elif "TravelTimesMap" in imageryDesc:
                    travelTimeMapDict = {
                        "resourceDesc": "Travel Time Map",
                        "mimeType": "image/jpeg",
                        "uri": mapUri,
                        }
            if energyMapDict:
                self.createNewBlock(infoBlockXML, "resource", energyMapDict)
            if polygonMapDict:
                self.createNewBlock(infoBlockXML, "resource", polygonMapDict)
            if travelTimeMapDict:
                self.createNewBlock(infoBlockXML, "resource", travelTimeMapDict)

    def createTestingJsonIdentifierParameter(self, infoBlockXML, productDict):
        '''
        @summary: Get the information for the resource parameter block and, if it exists,
        add it to the CAP message
        @param infoBlockXML: The XML SubElement representing the <info> block of the CAP message
        @param productDict: The product-level dictionary
        @return: NoneType; The infoBlockXML is updated in memory
        '''
        path = self.adu.getEventMapsJsonUri(productDict)
        jsonPath = os.path.join(path, f"{productDict.get('officeId')}.json")
        valueDict = {
            "resourceDesc": "Event Data as a JSON document",
            "mimeType": "application/json",
            "uri": jsonPath,
            }
        self.createNewBlock(infoBlockXML, "resource", valueDict)

    def createAreas(self, infoBlockXML, productDict, segmentDict, sectionDict, infoDict):
        '''
        @param: Create the <area> block and populate various tags within this block
        @param infoBlockXML: The SubElement containing the contents for the <info> block
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @param infoDict: A dictionary of commonly accessible parameters
        @return: String
        '''
        areaElement = self.createSubElement(infoBlockXML, self.populateTagDict("area"))
        # <areaDesc> tag creation
        areaDesc = ""
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        if self.productCategory == "TSU_TM":
            areaDesc = self.tpc.joinStringsWithOxfordComma(infoDict.get("countries", ""))
        elif self.productCategory == "TSU":
            if self.siteId == "NTWC":
                areaDesc = self.amm.getAreaListTextSegment(segmentDict, self.productRegion)
            elif self.siteId == "PTWC":
                locationList = segmentDict.get("subRegionLocations")
                areaDesc = self.amm.getPTWC_HeadlineLocations(self.productRegion, locationList)
        elif self.productCategory == "TIB":
            areaDesc = self.amm.getPrimaryPhysicalEventLocation(eventDict, self.fieldNameSuffix)
        self.createSubElement(areaElement, self.populateTagDict("areaDesc", text=areaDesc))
        # <geoCode> tag creation
        if self.productCategory == "TSU":
            ugcs = segmentDict.get("ugcs")
            for ugc in ugcs:
                self.createNewBlock(areaElement, "geocode", self.createValueDict("UGC", ugc))
        elif self.productCategory == "TIB":
            self.createSubElement(areaElement,
                                  self.populateTagDict("circle", text=self.getLatLon(productDict)))

    def getReferences(self, sectionDict, getExpiredReferences=False):
        '''
        @summary: This method creates either the <references> tag (getExpiredReferences = False) or
        the <expiredReferences> tag (getExpiredReferences = True) by searching in the registry for
        CAP GenericRegistryDataAccessObjects and only retaining/referencing those that are associated
        with this current and historical product issuance.
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary; this could also be None if not defined
        @param infoDict: A dictionary of commonly accessible parameters, can also be None if not defined yet
        @param getExpiredReferences: Optional boolean to determine whether to include (True) or exclude (False)
        CAP messages that are expired
        @return: String
        '''
        '''
        Tag structure:
            <references>sender,identifier,sent</references>
        Where sender, identifier, and sent are the sender, identifier, and sent elements from the earlier
        CAP message(s) that this one replaces. When multiple messages are referenced, they are separated
        by whitespace.

        Example:
        <references>w-nws.webmaster@noaa.gov,urn:oid:2.49.0.1.840.0.3dbcc6878e7610c0d9b0ae89fe855807c2409c29.001.001,2020-03-03T13:14:00-06:00 </references>

        Inclusion: Included whenever the NWS updates or cancels an alert for which a CAP message has been produced.
        '''
        reference = ""
        if self.msgType not in ["Update", "Cancel"]:
            return reference
        # Find all valid CAP messages
        capIdDictList = self.filterCAPMessages(sectionDict,
                                               getExpiredMessages=getExpiredReferences)
        # If no messages returned, return empty string
        if not capIdDictList:
            if not getExpiredReferences:
                self.msgType = "Alert"
            return reference
        # Build and return the reference string
        reference = self.createReferenceString(capIdDictList,
                                               sortByExpirationTime=getExpiredReferences)
        return reference

    def filterCAPMessages(self, sectionDict, getExpiredMessages):
        '''
        @summary: Loop over the CAP messages and return either valid, non-expired CAP messages
        (getExpiredMessages=False) or expired/nearly-expired CAP messages (getExpiredMessages=True).
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line
        within the segment-level dictionary; this could also be None if not defined
        @param getExpiredMessages: Boolean to determine whether to only return messages that have
        expiration times in the past or near the current time by some buffer (True) or only have
        expiration times in the future (False)
        @return: A list of dictionaries containing the contents of the GenericRegistryDataAccessObjects
        that match the eventID(s), etn, some UGCs, and the time constraints for this VTEC line
        '''
        # Query CAP messages from the registry
        capMessages = self.getCAPMessagesFromRegistry(sectionDict)
        # List to store the CAP messages
        capIdDictList = []
        # Grab the time from the CAVE clock
        validTime = TimeUtil.simulatedTimeAsDatetime()
        # Searching for (nearly) expired messages
        if getExpiredMessages:
            # Add configurable time buffer to grab messages that are close to expiration
            validTime += datetime.timedelta(minutes=self.capUtils.ExpirationReferenceDeltaTime())
            # Loop over the CAP message and add expired ones to the list
            for result in capMessages:
                if TimeUtil.epochTimeMillisToDatetime(result["expirationTime"]) <= validTime:
                    capIdDictList.append(result)
        # Searching for valid/non-expired messages
        else:
            # Loop through CAP messages and grab the non-expired CAP messages
            for result in capMessages:
                if TimeUtil.epochTimeMillisToDatetime(result["expirationTime"]) > validTime:
                    capIdDictList.append(result)
        # Return list of filtered CAP messages
        return capIdDictList

    def getCAPMessagesFromRegistry(self, sectionDict):
        '''
        @summary: Queries the registry to get the CAP messages with the
        same hazard event ID, same etn, and has UGCs that overlap.
        @param sectionDict: A single section-level dictionary corresponding to a
        single VTEC line within the segment-level dictionary; this could also be None
        if not defined
        @return: A list of dictionaries containing the contents of the GenericRegistryDataAccessObjects
        that match the eventID(s), etn, and some UGCs for this VTEC line
        '''
        # List to store the final results
        finalResults = []
        # Pull the VTEC record from the sectionDict and get its attributes
        vtecRecord = sectionDict.get("vtecRecord")
        etn = str(vtecRecord.get("etn"))
        eventIDs = vtecRecord.get("eventID")

        # Query the CAP messages in the registry
        rawResults = self.findCapIDWithEventIDAndETN(eventIDs, etn)

        # Loop over each CAP message the verify some of the UGCs overlap
        vtecUGCs = vtecRecord.get("id")
        for result in rawResults:
            # Get UGCs from the CAP object
            eventUGCs = result.get("eventUGCs")
            # If any UGC overlap, add to list
            if not vtecUGCs.isdisjoint(eventUGCs):
                finalResults.append(result)
        # Return list of valid messages
        return finalResults

    def findCapIDWithEventIDAndETN(self, eventIDs, etn):
        '''
        @summary: Perform a query on the registry to retrieve
        all GenericRegistryDataAccessObjects that match the provided
        eventIDs and etn
        @param eventIDs: A set of eventIDs pulled from the section-level
        VTECRecord dictionary
        @param etn: The single etn associated with this VTEC record
        @return: A list of dictionaries containing the contents of the
        GenericRegistryDataAccessObjects
        '''
        # Ensure that the event IDs are a list
        if not isinstance(eventIDs, (set, list, tuple)):
            eventIDs = [eventIDs]
        elif not isinstance(eventIDs, list):
            eventIDs = list(eventIDs)
        # Build and execute the query
        queryDict = [
            ("objectType", "CapIdentifier"),
            ("eventID", "in", eventIDs),
            ("etn", etn)
            ]
        results = GRODA.queryObjects(queryDict, self.practice)
        # Convert the eventUGCs result entry to a set and return the results
        for result in results:
            result["eventUGCs"] = set(result["eventUGCs"]) if result["eventUGCs"] else set()
        return results

    def createReferenceString(self, capIdDictList, sortByExpirationTime):
        '''
        @summary: Build string containing information from previous CAP messages
        stored in the registry
        @param capIdDictList: A list of dictionaries containing the contents of the
        GenericRegistryDataAccessObjects
        @param sortByExpirationTime: Create the strings sorted by issue time in reverse
        chronological order (False) or by expiration time in chronological order (True)
        @return: A string of references sorted either by expiration time in chronological order
        of by issue time in reverse chronological order
        '''
        # Build nested list of issue times and formatted reference strings
        referenceList = []
        # Loop over each CAP message in the list
        for queryResult in capIdDictList:
            # Remove second and microsecond from issue time, otherwise validation will fail
            latestIssueTime = TimeUtil.epochTimeMillisToDatetime(queryResult["issueTime"]).replace(second=0, microsecond=0)
            # Convert to formatted string
            sent = self.tpc.formatDatetime(latestIssueTime, timeZone=self.tz)
            # Assemble reference string
            referenceString = f"{self.sender_text()},{queryResult['uniqueID']},{sent}"
            '''
            Assemble nested list of [time, referenceString] where time is either
            the expiration time or issuance time.
            '''
            if sortByExpirationTime:
                expTime = time.mktime(TimeUtil.epochTimeMillisToDatetime(queryResult["expirationTime"]).timetuple())
                referenceList.append([expTime, referenceString])
            else:
                referenceList.append([latestIssueTime, referenceString])
        '''
        If expiration times are being used, sort in chronological order (oldest to most recent)
        Otherwise, sort in reverse chronological order (most recent to oldest)
        '''
        if sortByExpirationTime:
            reverseOrder = False
        else:
            reverseOrder = True
        # Build and return the reference string
        referenceStrings = [refTuple[1] for refTuple in sorted(referenceList, reverse=reverseOrder)]
        referenceString = " ".join(referenceStrings)
        return referenceString

    def getWeaTextString(self, infoDict, textType):
        '''
        @summary: Get the text to populate the CMAMtext or CMAMlongtext strings
        @param infoDict: A dictionary of commonly accessible parameters
        @param textType: The short or long text type (e.g., EN.S, SP.L, etc.)
        @return: String):
        '''
        weaDict = self.capUtils.getWEA_MessageDictionary()
        weaKey = infoDict.get("productLookupKey")
        weaText = weaDict.get(f"{weaKey}{textType}")
        return weaText

    def getWebAddressString(self, productDict):
        '''
        @summary: Get the web address where you can retrieve Tsunami Warning/Watch/Advisory
        public text message, Tsunami information statement text message, and Threat message
        text message, for example:
        <web>http://ntwc.arh.noaa.gov/events/PAAQ/2024/12/05/so0rg3/1/WEAK53/WEAK53.txt</web>
        need to discuss this
        @return: String
        '''
        basePath = self.adu.getEventMapsJsonUri(productDict)
        textFormatterPath = os.path.join(basePath, f"{productDict.get('wmoID')}.txt")
        return textFormatterPath

    def getLatLon(self, productDict):
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        originLat = eventDict.get(f"originLatitude{self.fieldNameSuffix}")
        originLon = eventDict.get(f"originLongitude{self.fieldNameSuffix}")
        return f"{originLat},{originLon} 0.0"

    def isMessageActivatingWEA_VTEC(self, productDict, segDict, sectionDict, infoDict):
        '''
        @summary: Method to determine if this CAP message is activating the Wireless
        Emergency Alerting (WEA) system
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary
        @param infoDict: The info dictionary
        @return: Boolean
        '''
        return infoDict.get("productLookupKey") in self.weaProductLookupKeys()

    def storeCapIdToTable(self, productDict, segDict, sectionDict):
        '''
        @summary: Store elements of the CAP message as a GRODA in the registry to access
        again later
        @param productDict: The product-level dictionary
        @param segDict: A single segment-level dictionary of information from the product dictionary
        @param sectionDict: A single section-level dictionary corresponding to a single VTEC line within
        the segment-level dictionary
        @return: NoneType
        '''
        vtecRecord = sectionDict.get("vtecRecord", {})
        vtecUGCs = vtecRecord.get("id")
        capIdDict = {
            "uniqueID": self.createIdentifierTag(productDict, segDict, sectionDict),
            "objectType": "CapIdentifier",
            "eventID": vtecRecord.get("eventID"),
            "etn": str(vtecRecord.get("etn", "")),
            "eventUGCs": list(vtecUGCs) if vtecUGCs else [],
            "issueTime": self.issueTime,
            "expirationTime": segDict.get("expirationTime")
            }
        GRODA.storeObject(capIdDict, self.practice)
