# *** Override behavior of AtomsTestTool.py ***
# -- Override ability: class-based
# -- Levels: All
'''
    Description: Supports automated testing of physical events

    @since: October 2024
    @author: GSL Hazard Services Team
'''

import logging, UFStatusHandler
import AtomsMapUtilities
import EventSetFactory
import TsunamiRecommenderCommon
from TsunamiRecommender import Recommender as TRECS


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()

        self.logger = logging.getLogger("AtomsTestTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.recommenders.hydro", "AtomsTestTool",
            level=logging.INFO))
        self.logger.setLevel(logging.INFO)

        self.amu = AtomsMapUtilities.AtomsMapUtilities()

        self.siteID = None

    def getProductIdentifierPrefixesNTWC(self):
        '''
        @summary: A list of strings for NTWC, where each string consists of
        a startsWith pattern string to match on the physical event's custom ID
        @return: List of strings
        '''
        return [
            "Alaska.Cat", "Arctic.Cat", "Atlantic.Cat", "BcWc.Cat", "Bering.Cat",
            "Carib.Cat", "EcGc.Cat", "HumboldtDec2024", "Pacific.NTWC.Cat", "DBRegion",
            "Augustine_SP_NTWC_ThreatDB", "Barry_Arm_Landslide_SP_NTWC_ThreatDB",
            "Cook_Inlet_SP_NTWC_ThreatDB", "Juan_de_Fuca_SP_NTWC_ThreatDB",
            "Puget_Sound_SP_NTWC_ThreatDB", "SF_Bay_SP_NTWC_ThreatDB",
            "Strait_of_Georgia_SP_NTWC_ThreatDB", "DK_RW_20220910", "DK_RW_20220901",
            ]

    def getProductIdentifierPrefixesPTWC(self):
        '''
        @summary: A list of strings for PTWC, where each string consists of
        a startsWith pattern string to match on the physical event's custom ID
        @return: List of strings
        '''
        return [
            "AmSam.15", "AmSam.Cat", "Caribe.PTWC.Cat", "Guam.Cat", "Hawaii.Cat",
            "Pacific.PTWC.Cat", "PuertoRico.Cat",
            ]

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        return {
            "toolName": "AtomsTestTool",
            "author": "GSL",
            "version": "1.0",
            "description": "Tests the TRECS "
            }

    def defineDialog(self, eventSet):
        '''
        @return: MegaWidget dialog definition to solicit user input before running tool
        '''

        self.siteID = eventSet.getAttribute("siteID")
        self.initializeVariablesFromEventSetAttributes(eventSet)
        self.physicalEvents = None
        dialogDict = {
            "title": "Atoms Test Tool",
            "valueDict": {}
            }

        # Physical event ID prefixes
        choiceList = self.get_DFLT_PE_ID_PREFIXES()
        defaultList = self.get_DFLT_PE_ID_PREFIXES()
        valueList = list(set(choiceList) & set(defaultList))
        if not valueList:
            valueList = choiceList
        physicalEventIdsCheckList = {
            "fieldType": "CheckList",
            "fieldName": "physicalEventIdPrefixSelections",
            "label": "What physical events (ID prefixes) would you like to test?",
            "choices": choiceList,
            "values": valueList,
            }
        dialogDict["fields"] = [physicalEventIdsCheckList]
        return dialogDict

    def get_DFLT_PE_ID_PREFIXES(self):
        if self.siteID == "NTWC":
            return self.getProductIdentifierPrefixesNTWC()
        else:
            return self.getProductIdentifierPrefixesPTWC()

    def execute(self, eventSet, dialogInputMap, visualFeatures):
        '''
        @summary: Runs thru test physical events to see if TRECS produces the correct results.
        This is done with the following sequence of logic:
            1. Only testing physical events whose custom IDs start with one of the prefixes in self.DFLT_PE_ID_PREFIXES
            2. Checks if there is an expected threat DB hit (by checking if the id starts with DBRegion, or if the
               physical event isKnown == True apriori), and if so, checks if indeed there a successful threatDB usage.
        '''

        # NTWC Expected Warnings:
        #    Alaska.Cat6a.Too, Alaska.Cat6b, Alaska.Cat7.Offshore, AmSam.15*, BcWc.Cat2aOutsideBad, Pacific.NTWC.Cat6a.5hrs

        # Example PTWC TRECs received dialogInputMap =
        # {'bypassThreatDBCheckBox': False,
        #  'regionalSelections': ['Hawaii (Hi)', 'Guam/CNMI (Gu)', 'American Samoa (As)', 'Non U.S. Pacific (Pac)'],
        #  'amplitudeSelection': '',
        #  'physicalEvent': <jep.PyJObject object at 0x7f1b705cb180>,
        #  'hazardTypeSelections': ['Tsunami Watch/Warning/Advisory (TS.A/TS.W/TS.Y)', 'Tsunami Information Statement (TS.S)', 'Tsunami Threat Message (TS.ThreatMessage)',
        #                           'Tsunami Observatory Message (TS.ObservatoryMessage)'], 'timeOfArrivalSelection': ''}
        # Example NTWC TRECs received dialogInputMap =
        # {'bypassThreatDBCheckBox': False,
        # 'regionalSelections': ['Alaska/British Columbia/U.S. West Coast (AkBcWc)'],
        # 'amplitudeSelection': '',
        # 'physicalEvent': <jep.PyJObject object at 0x7f13111f21e0>,
        # 'hazardTypeSelections': ['Tsunami Watch/Warning/Advisory (TS.A/TS.W/TS.Y)', 'Tsunami Information Statement (TS.S)', 'Tsunami Conference Call (TS.ConferenceCall)',
        #                          'Tsunami Observatory Message (TS.ObservatoryMessage)'], 'timeOfArrivalSelection': ''}

        newEventSet = None
        # PhyEvent customIDs are the dict keys, and the list of failAndWarnMessages is the value
        failAndWarnMessagesDict = {}
        # For each physical event in the PEM
        physicalEventIdsList = self.pem.getPhysicalEventIdsList()
        physicalEventIdPrefixesToTest = dialogInputMap.get("physicalEventIdPrefixSelections")
        for phyEventId in physicalEventIdsList:
            phyEvent = self.pem.getPhysicalEvent(phyEventId)
            testThisPhyEvent = False
            for startsWith in physicalEventIdPrefixesToTest:
                if phyEventId.startswith(startsWith):
                    testThisPhyEvent = True
                    break
            if testThisPhyEvent:
                failAndWarnMessages = []
                self.pem.setSelected(phyEvent)
                print(f"AtomsTestTool ===== Testing {phyEventId} =====")
                '''
                Dump Brkpt Segments - To dump brkpt segments, add an empty [] entry to the
                ExpectedBrkptSegmentsDict for the appropriate physical event id
                '''
                # Here are the smart defaults and options we need to pass to the TRECS,
                # but let's get em from the trecs himself since the TRECS code
                # has the logic to figure out the smart defaults. THis changes for
                # every earthquake/physicalEvent!
                # The trecs gets the selected PE from the PEM in it's defineDialog method
                # So create a new TRECS, call its defineDialog, and then execute it
                aTrecs = TRECS()
                aTrecs.isAutoTest = True
                aTrecs.suppressTTTMissingErrors = True
                aTrecs.defineDialog(eventSet)
                choiceList = aTrecs.getHazardTypesToRecommend()
                defaultList = aTrecs.defaultHazardTypesToRecommend()
                valueList = list(set(choiceList) & set(defaultList))
                if not valueList:
                    valueList = choiceList

                tttForecastChoices = aTrecs.getForecastChoicesWithType(aTrecs.tsunamiForecastInfoDict, "timeOfArrival")
                tttDefaultChoice = ""
                if tttForecastChoices:
                    tttDefaultChoice = tttForecastChoices[0]

                possibleRegionAbbrevs = aTrecs.getProductRegionAbbreviations(False)
                # Select the ones based on the physical event location
                selectedRegionAbbrevs = []
                if aTrecs.isInCentralAmericaDualProcRegion() or aTrecs.isInSouthAmericaDualProcRegion():
                    selectedRegionAbbrevs = aTrecs.getProductRegionAbbreviations(False)
                else:
                    selectedRegionAbbrevs = aTrecs.getProductRegionAbbreviations(True)
                if not selectedRegionAbbrevs:
                    selectedRegionAbbrevs = possibleRegionAbbrevs

                dialogInputMap = {
                    "bypassThreatDBCheckBox": False,
                    "regionalSelections": selectedRegionAbbrevs,
                    "amplitudeSelection": "",
                    "physicalEvent": phyEvent,
                    "hazardTypeSelections": valueList,
                    "timeOfArrivalSelection": tttDefaultChoice,
                    "performSurgery": False
                    }
                for regionAbbrev in selectedRegionAbbrevs:
                    dialogInputMap[f"{regionAbbrev}_MessageType"] = "initialMessage"

                newEventSet = aTrecs.execute(eventSet, dialogInputMap, visualFeatures)

                # Check if threat DB hits are expected and if so, assert they happened
                expectedThreatDBHitProductRegions = self.getExpectedThreatDBHitProductRegions(phyEvent)
                if expectedThreatDBHitProductRegions:
                    for expectedThreatDBHitProdRegion in expectedThreatDBHitProductRegions:
                        if aTrecs.trecsExecInfo.wasThreatDBHit(expectedThreatDBHitProdRegion) and len(newEventSet.events) > 0:
                            self.printSuccess(f"ThreatDB hit for productRegion = {expectedThreatDBHitProdRegion} and # HazardEvents = {len(newEventSet.events)}")
                        else:
                            failMsg = (f"Expected ThreatDB hit for productRegion = {expectedThreatDBHitProdRegion} and # HazardEvents = {len(newEventSet.events)}\n"
                                       f"  because wasThreatDBHit({expectedThreatDBHitProdRegion}) = {aTrecs.trecsExecInfo.wasThreatDBHit(expectedThreatDBHitProdRegion)}\n"
                                       f"      and len(newEventSet.events) = {len(newEventSet.events)}")
                            failAndWarnMessages.append(self.getFail(failMsg))
                            print(self.getFail(failMsg))

                # Now go thru the executed procedural categories, and ask them if they were successful
                execedCategories = aTrecs.executedProcCategories
                if execedCategories is not None:
                    for category in execedCategories:
                        actionsAsserted = category.assertActions(aTrecs, newEventSet)
                        if actionsAsserted:
                            self.printSuccess(f"{category.__class__.__name__} actionsAsserted succeeded.")
                        else:
                            # Just because a Category fails to assert, doesnt mean it was a failure.
                            # For example, an EQ > 500 km from any break point will fail Categ 6 if
                            # Categ 6 says to light up within 250 km.
                            warnMsg = f"{category.__class__.__name__} actionsAsserted failed."
                            failAndWarnMessages.append(self.getWarning(warnMsg))
                            print(self.getWarning(warnMsg))

                expectedBrkptSegmentsByPhensigList = self.getExpectedBrkptSegmentsDict().get(phyEventId)
                # If we have no entry, then warn. But if the result is empty, then that is the expected results.
                if expectedBrkptSegmentsByPhensigList is None:
                    warnMsg = ("There is no break point segment name configuration for that physical event. \n"
                               "Hence nothing to compare the hazard area(s) to.")
                    failAndWarnMessages.append(self.getWarning(warnMsg))
                    print(self.getWarning(warnMsg))
                elif newEventSet is not None:
                    for event in newEventSet.events:
                        eventPhensig = event.getPhensig()
                        # Only check break point segment names for TS.WYAs
                        if eventPhensig in ["TS.W", "TS.Y", "TS.A"]:
                            hzdBrkptSegList = event.get("hazardLocations")
                            if not hzdBrkptSegList:
                                failMsg = "The hazardEvent has None or Empty hazardLocations attribute!"
                                failAndWarnMessages.append(self.getFail(failMsg))
                                print(self.getFail(failMsg))
                            elif expectedBrkptSegmentsByPhensigList is None:
                                failMsg = ("The physical event has not been configured in AtomsTestTool.py \n"
                                           "with any expected/predefined brkpt segment names!")
                                failAndWarnMessages.append(self.getFail(failMsg))
                                print(self.getFail(failMsg))
                            else:
                                foundAtLeastOneExpectedPhensig = False
                                brkptSegNamesMatch = False
                                for phensigToBrkptSegNamesDict in expectedBrkptSegmentsByPhensigList:
                                    matchedPhensigKeys = []
                                    for expectedPhensigKey in phensigToBrkptSegNamesDict:
                                        if expectedPhensigKey == eventPhensig:
                                            foundAtLeastOneExpectedPhensig = True
                                            expectedBrkptSegNamesList = phensigToBrkptSegNamesDict.get(expectedPhensigKey)
                                            setOfExpectedBrkptSegNames = set(expectedBrkptSegNamesList)
                                            unionList = [name for name in hzdBrkptSegList if name in setOfExpectedBrkptSegNames]
                                            if len(unionList) == len(setOfExpectedBrkptSegNames) and len(unionList) == len(hzdBrkptSegList):
                                                matchedPhensigKeys.append(expectedPhensigKey)
                                                brkptSegNamesMatch = True
                                                break
                                    for matchedKey in matchedPhensigKeys:
                                        phensigToBrkptSegNamesDict.pop(matchedKey, None)
                                    if brkptSegNamesMatch:
                                        break

                                if not foundAtLeastOneExpectedPhensig:
                                    failMsg = (f"A Hazard Type of {eventPhensig} was created but NOT expected \n"
                                                   "(no brkpt segments predefined for that phensig)!")
                                    failAndWarnMessages.append(self.getFail(failMsg))
                                    print(self.getFail(failMsg))
                                if brkptSegNamesMatch:
                                    self.printSuccess(f"Validated expected break point segment names for {eventPhensig}")
                                else:
                                    failMsg = (f"For {eventPhensig}, that hazard event has brkpt segments:\n"
                                               f"{hzdBrkptSegList}\n"
                                               f"But expected the following configured brkpt segments:")
                                    failAndWarnMessages.append(self.getFail(failMsg))
                                    print(self.getFail(failMsg))
                                    oneMatchingPhensigFoundAlready = False
                                    for phensigToBrkptSegNamesDict in expectedBrkptSegmentsByPhensigList:
                                        for expectedPhensigKey in phensigToBrkptSegNamesDict:
                                            if expectedPhensigKey == eventPhensig:
                                                if oneMatchingPhensigFoundAlready:
                                                    print(self.getFail("OR"))
                                                    failAndWarnMessages.append(self.getFail("OR"))
                                                failMsg = f"{phensigToBrkptSegNamesDict.get(expectedPhensigKey)}"
                                                failAndWarnMessages.append(self.getFail(failMsg))
                                                print(self.getFail(failMsg))
                                                set1 = set(phensigToBrkptSegNamesDict.get(expectedPhensigKey))
                                                set2 = set(hzdBrkptSegList)
                                                difference1 = set1 - set2
                                                list1 = list(difference1)
                                                difference2 = set2 - set1
                                                list2 = list(difference2)
                                                list1.extend(list2)
                                                failMsg = f"DIFFERENCE = {list1}"
                                                failAndWarnMessages.append(self.getFail(failMsg))
                                                print(self.getFail(failMsg))
                                                oneMatchingPhensigFoundAlready = True

                    for phensigToBrkptSegNamesDict in expectedBrkptSegmentsByPhensigList:
                        for key in phensigToBrkptSegNamesDict:
                            failMsg = (f"Expecting, but did not find, a {key} hazard event with brkpt segments: {phensigToBrkptSegNamesDict}")
                            failAndWarnMessages.append(self.getFail(failMsg))
                            print(self.getFail(failMsg))

                if not expectedThreatDBHitProductRegions and not execedCategories and len(expectedBrkptSegmentsByPhensigList) != 0:
                    failMsg = "No ThreatDB hits expected, and no procedural categories matched! ie Nothing to test!?"
                    failAndWarnMessages.append(self.getFail(failMsg))
                    print(self.getFail(failMsg))

                failAndWarnMessagesDict[phyEventId] = failAndWarnMessages

        print("AtomsTestTool Done.")
        # We actually do not want to return any new HazardEvents from the test tool
        emptyEventSet = EventSetFactory.createEventSet()
        # Build up user messages, either a bunch of fail/warns, or a single Success
        failOrWarn = False
        totalUserMessage = ""
        for phyEventId in failAndWarnMessagesDict:
            failAndWarnMessages = failAndWarnMessagesDict[phyEventId]
            if failAndWarnMessages:
                totalUserMessage += f"=== Testing {phyEventId} ===\n"
            for failOrWarnMsg in failAndWarnMessagesDict[phyEventId]:
                # If it is not None, then we have a fail or warning message
                failOrWarn = True
                totalUserMessage += f"{failOrWarnMsg}\n"
        if not failOrWarn:
            totalUserMessage = "Success, all physical events passed."
        emptyEventSet.addAttribute("resultsMessage", totalUserMessage)

        return emptyEventSet

    def printSuccess(self, message):
        print(f"    AtomsTestTool SUCCESS: {message}")

    def getWarning(self, message):
        return f"    AtomsTestTool ------> WARNING (Possible FAILURE): {message}"

    def getFail(self, message):
        return f"    AtomsTestTool ------> FAILURE: {message}"

    def summarizeUserMessages(self, userMessages, newEventSet):
        '''
        @summary: Concatenate all user messages and attach it to the result eventSet as the
        "resultsMessage" attribute
        @param userMessages: The list of strings
        @param newEventSet: The eventSet to be returned
        @return: An updated newEventSet
        '''
        messageList = [f"{userMsg}\n" for userMsg in userMessages]
        totalUserMsg = "".join(messageList)
        newEventSet.addAttribute("resultsMessage", totalUserMsg)
        return newEventSet

    def removeSameBrkptSegNames(self, hzdBrkptSegNamesDict, expectedBrkptSegNamesDict):
        # Leftovers in each dict should be only those not in both dicts
        keysInBoth = []
        for segName in hzdBrkptSegNamesDict:
            if segName in expectedBrkptSegNamesDict:
                keysInBoth.append(segName)

        for segName in keysInBoth:
            hzdBrkptSegNamesDict.pop(segName, None)
            expectedBrkptSegNamesDict.pop(segName, None)

    def getExpectedThreatDBHitProductRegions(self, phyEvent):
        if self.siteID == "NTWC":
            return self.getExpectedThreatDBHitProductRegionsNTWC(phyEvent)
        else:
            return self.getExpectedThreatDBHitProductRegionsPTWC(phyEvent)

    def getExpectedThreatDBHitProductRegionsNTWC(self, phyEvent):
        '''
        @summary: NTWC. If the phyEvent should have one or more threat DB hits, then this should
        return a List of productRegions (eg AkBcWc, EcGc) for which a threat DB hit is expected.
        @return: A List or None
        '''
        if phyEvent.getCustomId().startswith("DBRegion057"):
            return ["EcGc"]
        elif phyEvent.getCustomId().startswith("DBRegion"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("DK_RW_"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("HumboldtDec2024.Region22"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("Barry_Arm_Landslide_SP_NTWC_ThreatDB.2"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("Cook_Inlet_SP_NTWC_ThreatDB"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("Juan_de_Fuca_SP_NTWC_ThreatDB"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("Puget_Sound_SP_NTWC_ThreatDB"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("SF_Bay_SP_NTWC_ThreatDB"):
            return ["AkBcWc"]
        elif phyEvent.getCustomId().startswith("Strait_of_Georgia_SP_NTWC_ThreatDB"):
            return ["AkBcWc"]
        elif phyEvent.getIsKnownEvent() == True:
            return ["AkBcWc"]
        else:
            return None

    def getExpectedThreatDBHitProductRegionsPTWC(self, phyEvent):
        '''
        @summary: PTWC. If the phyEvent should have one or more threat DB hits, then this should
        return a List of productRegions (eg Hawaii, Guam) for which a threat DB hit is expected.
        @return: A List or None
        '''
        # For PTWC, it's not clear which product region(s) are applicable for a known event.
        # Matter of fact, multiple product regions could be applicable. So instead, we
        # should determine if there should be a ThreatDB hit by Physical Event ID instead.
        # if phyEvent.getIsKnownEvent() == True:
        #     return ["Hi"]
        if phyEvent.getCustomId().startswith("AmSam.15"):
            return ["As"]
        else:
            return None

    def getExpectedBrkptSegmentsDict(self):
        if self.siteID == "NTWC":
            return self.getExpectedBrkptSegmentsDictNTWC()
        else:
            return self.getExpectedBrkptSegmentsDictPTWC()

    def getExpectedBrkptSegmentsDictNTWC(self):
        return {
            "Alaska.Cat1": [],
            "Alaska.Cat2a": [],
            "Alaska.Cat2b": [],
            "Alaska.Cat3a": [],
            "Alaska.Cat3b": [],
            "Alaska.Cat4a": [],
            "Alaska.Cat4b": [],
            "Alaska.Cat5.Deep": [],
            "Alaska.Cat5.Inland": [],
            "Alaska.Cat5.Shallow": [],
            "Alaska.Cat6a": [{"TS.W": ["Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]}],
            "Alaska.Cat6a.Too": [],
            "Alaska.Cat6b": [{"TS.Y": ["Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]}],
            "Alaska.Cat6b.Too": [{"TS.Y": ["Hinchinbrook Entrance to Kennedy Entrance", "Cape Suckling to Hinchinbrook Entrance"]}],
            "Alaska.Cat7.Offshore": [{"TS.Y": ["Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]}],
            "Alaska.Cat7.Too": [
                {"TS.W": ["Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                {"TS.Y": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass"]},
                ],
            "Alaska.Cat8.Offshore": [
                {"TS.W": ["The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border"]},
                ],
            "Arctic.Cat1a": [],
            "Arctic.Cat1b": [],
            "Arctic.Cat2a": [],
            "Arctic.Cat2b": [],
            "Arctic.Cat2c": [],
            "Arctic.Cat3a": [],
            "Arctic.Cat3b": [],
            "Arctic.Cat3c": [],
            "Arctic.Cat4": [],
            "Arctic.Cat4.50km": [],
            "Arctic.Cat4.80km": [],
            "Arctic.Cat4.Deep": [],
            "Arctic.Cat5a.1000miDeep80km": [{"TS.Y": ["Western AK from Cape Prince of Wales to Wainwright", "Northern AK Border from Wainwright to the Canadian Border"]}],
            "Arctic.Cat5a.Too": [{"TS.Y": ["Western AK from Cape Prince of Wales to Wainwright", "Northern AK Border from Wainwright to the Canadian Border"]}],
            "Arctic.Cat5b": [],
            "Arctic.Cat5b.80km": [],
            "Arctic.Cat6": [],
            "Atlantic.Cat1a": [],
            "Atlantic.Cat1b": [],
            "Atlantic.Cat2": [],
            "Atlantic.Cat3": [],
            "Atlantic.Cat3.Too": [],
            "Augustine_SP_NTWC_ThreatDB": [{"TS.W": ["Lower Cook Inlet Region south of Kalgin Island"]}],
            "Barry_Arm_Landslide_SP_NTWC_ThreatDB": [{"TS.W": ["Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance"]}],
            "Barry_Arm_Landslide_SP_NTWC_ThreatDB.2": [{"TS.W": ["Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance"]}],
            "BcWc.Cat1a": [],
            "BcWc.Cat1b": [],
            "BcWc.Cat2a": [],
            "BcWc.Cat2aOutsideBad": [],
            "BcWc.Cat2b": [],
            "BcWc.Cat3": [],
            "BcWc.Cat3.Deep": [],
            "BcWc.Cat3.Inland": [],
            "BcWc.Cat4a": [{"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport"]}],
            "BcWc.Cat4b": [{"TS.Y": ["Rincon Point to Point Conception", "Point Conception to Ragged Point"]}],
            "BcWc.Cat5.Offshore": [
                {"TS.W": ["The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border"]},
                {"TS.Y": ["Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border"]},
                {"TS.Y": ["The BC/Alaska Border to Cape Decision"]},
                ],
            "BcWc.Cat5.Onshore": [
                {"TS.W": ["The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border"]},
                {"TS.Y": ["Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border"]},
                {"TS.Y": ["The BC/Alaska Border to Cape Decision"]},
                ],
            "BcWc.Cat6.Offshore": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border"]},
                {"TS.A": ["The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "Bering.Cat1": [],
            "Bering.Cat2a": [],
            "Bering.Cat2a.Too": [],
            "Bering.Cat2b": [],
            "Bering.Cat3a": [],
            "Bering.Cat3b": [],
            "Bering.Cat3c": [],
            "Bering.Cat4a": [],
            "Bering.Cat4b": [],
            "Bering.Cat4c": [],
            "Bering.Cat5": [],
            "Bering.Cat5.1000miDeep50km": [],
            "Bering.Cat5.1000miDeep80km": [],
            "Bering.Cat5.Deep": [],
            "Bering.Cat6.1000miDeep": [{"TS.W": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "Bering.Cat7.1000miDeep": [{"TS.W": ["Bristol Bay and the Pribilof Islands"]}],
            "Bering.Cat7.Shallow": [{"TS.W": ["Bristol Bay and the Pribilof Islands"]}],
            "Bering.Nothing": [],
            "Carib.Cat1": [],
            "Carib.Cat2": [],
            "Carib.Cat3": [],
            "Cook_Inlet_SP_NTWC_ThreatDB": [{"TS.W": ["Northwest Kenai Peninsula", "Lower Cook Inlet Region south of Kalgin Island", "Upper Cook Inlet"]}],
            "DBRegion007aE_NTWC_ThreatDB": [{"TS.W": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion007aW_NTWC_ThreatDB": [{"TS.W": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion007bE_NTWC_ThreatDB": [{"TS.W": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion007bW_NTWC_ThreatDB": [{"TS.W": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion008_NTWC_ThreatDB": [{"TS.Y": ["Bristol Bay and the Pribilof Islands"]}],
            "DBRegion008_NTWC_ThreatDB.2": [{"TS.Y": ["Bristol Bay and the Pribilof Islands"]}],
            "DBRegion009_NTWC_ThreatDB": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "Strait of Georgia", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "Puget Sound"]},
                {"TS.Y": ["The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]},
                ],
            "DBRegion010_NTWC_ThreatDB": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "Strait of Georgia", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "Puget Sound"]},
                {"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception"]},
                {"TS.Y": ["The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion011_NTWC_ThreatDB": [{"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport"]}],
            "DBRegion012_NTWC_ThreatDB": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point"]},
                {"TS.Y": ["Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River"]},
                {"TS.A": ["Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion013_NTWC_ThreatDB": [{"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point"]}],
            "DBRegion014_NTWC_ThreatDB": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point"]},
                {"TS.Y": ["Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                ],
            "DBRegion015_NTWC_ThreatDB": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point"]},
                {"TS.Y": ["Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                {"TS.A": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion016_NTWC_ThreatDB": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River"]},
                {"TS.Y": ["Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino"]},
                ],
            "DBRegion017_NTWC_ThreatDB": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River"]},
                {"TS.Y": ["Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino"]},
                {"TS.A": ["Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion018_NTWC_ThreatDB": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                {"TS.Y": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line"]},
                ],
            "DBRegion019_NTWC_ThreatDB": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                {"TS.Y": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line"]},
                {"TS.A": ["Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion020_NTWC_ThreatDB": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                {"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception"]},
                {"TS.Y": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head"]},
                ],
            "DBRegion021_NTWC_ThreatDB": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                {"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception"]},
                {"TS.Y": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head"]},
                {"TS.A": ["Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion022_NTWC_ThreatDB": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head"]},
                {"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception"]},
                {"TS.Y": ["Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border"]},
                ],
            "DBRegion023_NTWC_ThreatDB": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head"]},
                {"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception"]},
                {"TS.Y": ["Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border"]},
                {"TS.A": ["The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion024_NTWC_ThreatDB": [
                {"TS.W": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather"]},
                {"TS.Y": ["Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island"]},
                {"TS.Y": ["Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line"]},
                {"TS.A": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion025_NTWC_ThreatDB": [
                {"TS.W": ["The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather"]},
                {"TS.Y": ["Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border"]},
                {"TS.Y": ["Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line"]},
                {"TS.A": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion026_NTWC_ThreatDB": [
                {"TS.W": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling"]},
                {"TS.Y": ["The Wash./BC Border to North Vancouver Island"]},
                {"TS.Y": ["Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                ],
            "DBRegion027_NTWC_ThreatDB": [
                {"TS.W": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                {"TS.Y": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass"]},
                ],
            "DBRegion028_NTWC_ThreatDB": [
                {"TS.W": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                {"TS.Y": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                {"TS.A": ["Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion029_NTWC_ThreatDB": [
                {"TS.W": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                {"TS.Y": ["The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border"]},
                {"TS.A": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DBRegion030_NTWC_ThreatDB": [{"TS.Y": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion031_NTWC_ThreatDB": [
                {"TS.W": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                ],
            "DBRegion032_NTWC_ThreatDB": [{"TS.Y": ["Amchitka Pass to Attu"]}],
            "DBRegion034_NTWC_ThreatDB": [
                {"TS.Y": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]},
                ],
            "DBRegion036_NTWC_ThreatDB": [
                {"TS.W": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]},
                ],
            "DBRegion038_NTWC_ThreatDB": [{"TS.Y": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion039_NTWC_ThreatDB": [
                {"TS.W": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]},
                ],
            "DBRegion040_NTWC_ThreatDB": [
                {"TS.W": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                ],
            "DBRegion041_NTWC_ThreatDB": [{"TS.Y": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion042_NTWC_ThreatDB": [
                {"TS.W": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                ],
            "DBRegion043_NTWC_ThreatDB": [
                {"TS.W": ["Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                ],
            "DBRegion044_NTWC_ThreatDB": [
                {"TS.W": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Unimak Pass to Samalga Pass"]},
                ],
            "DBRegion045_NTWC_ThreatDB": [
                {"TS.W": ["Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance"]},
                ],
            "DBRegion046_NTWC_ThreatDB": [
                {"TS.W": ["Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance"]},
                ],
            "DBRegion048_NTWC_ThreatDB": [
                {"TS.W": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                {"TS.Y": ["Kennedy Entrance to Chignik Bay"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance"]},
                ],
            "DBRegion049_NTWC_ThreatDB": [
                {"TS.W": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass"]},
                {"TS.Y": ["Kennedy Entrance to Chignik Bay"]},
                {"TS.Y": ["Amchitka Pass to Attu"]},
                ],
            "DBRegion050_NTWC_ThreatDB": [
                {"TS.W": ["Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass"]},
                {"TS.Y": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance"]},
                {"TS.Y": ["Amchitka Pass to Attu"]},
                {"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island"]},
                ],
            "DBRegion051_NTWC_ThreatDB": [
                {"TS.W": ["Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]},
                {"TS.Y": ["Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance"]},
                {"TS.Y": ["Samalga Pass to Amchitka Pass"]},
                ],
            "DBRegion052_NTWC_ThreatDB": [
                {"TS.W": ["Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]},
                {"TS.Y": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision"]},
                {"TS.Y": ["Unimak Pass to Samalga Pass"]},
                ],
            "DBRegion053_NTWC_ThreatDB": [
                {"TS.W": ["Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]},
                {"TS.Y": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision"]},
                {"TS.Y": ["Chignik Bay to Unimak Pass"]},
                ],
            "DBRegion054E_NTWC_ThreatDB": [{"TS.Y": ["Norton Sound/Saint Lawrence Island/Western AK Coast"]}],
            "DBRegion054W_NTWC_ThreatDB": [{"TS.Y": ["Norton Sound/Saint Lawrence Island/Western AK Coast"]}],
            "DBRegion055_NTWC_ThreatDB": [{"TS.Y": ["Western AK from Cape Prince of Wales to Wainwright"]}],
            "DBRegion056_NTWC_ThreatDB": [{"TS.Y": ["Northern AK Border from Wainwright to the Canadian Border"]}],
            "DBRegion057_NTWC_ThreatDB": [{"TS.W": ["Gulf of Saint Lawrence"]}],
            "DBRegion058_NTWC_ThreatDB": [{"TS.A": ["North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling"]}],
            "DBRegion059_NTWC_ThreatDB": [{"TS.A": ["The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance"]}],
            "DBRegion060_NTWC_ThreatDB": [{"TS.A": ["Amchitka Pass to Attu"]}],
            "DBRegion061_NTWC_ThreatDB": [{"TS.A": ["Amchitka Pass to Attu"]}],
            "DBRegion062_NTWC_ThreatDB": [{"TS.A": ["Amchitka Pass to Attu"]}],
            "DBRegion063_NTWC_ThreatDB": [{"TS.A": ["Amchitka Pass to Attu"]}],
            "DBRegion064_NTWC_ThreatDB": [{"TS.A": ["Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion065_NTWC_ThreatDB": [{"TS.A": ["Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "DBRegion066_NTWC_ThreatDB": [{"TS.A": ["Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass"]}],
            "DBRegion067_NTWC_ThreatDB": [{"TS.A": ["Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass"]}],
            "DBRegion069_NTWC_ThreatDB": [{"TS.A": ["Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass"]}],
            "DBRegion070_NTWC_ThreatDB": [{"TS.A": ["Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay"]}],
            "DK_RW_20220901": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "Strait of Georgia", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "Puget Sound"]},
                {"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception"]},
                {"TS.Y": ["The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "DK_RW_20220910": [
                {"TS.W": ["Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line"]},
                {"TS.Y": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception"]},
                {"TS.Y": ["Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head"]},
                {"TS.A": ["Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "EcGc.Nothing": [],
            "EcGc.Cat1": [],
            "EcGc.Cat2a": [],
            "EcGc.Cat2b": [],
            "EcGc.Cat3a": [],
            "EcGc.Cat3b": [],
            "EcGc.Cat4.30km": [],
            "EcGc.Cat4.50km": [],
            "EcGc.Cat4.80km": [],
            "EcGc.Cat5.30km": [{"TS.W": self.getGulfOfAmericaBreakPointSegmentNames()}],
            "EcGc.Cat5.50km": [{"TS.W": self.getGulfOfAmericaBreakPointSegmentNames()}],
            "EcGc.Cat5.80km": [{"TS.W": self.getGulfOfAmericaBreakPointSegmentNames()}],
            "EcGc.Cat5.Offshore": [{"TS.W": self.getGulfOfAmericaBreakPointSegmentNames()}],
            "EcGc.Cat6.80km": [{"TS.W": ["Gulf of Saint Lawrence"]}],
            "EcGc.Cat7.can": [{"TS.W": ["Charlesville to Chezzetcook Inlet", "Chezzetcook Inlet to Meat Cove"]}],
            "EcGc.Cat7.us": [{"TS.W": ["Altamaha Sound to South Santee River", "South Santee River to Surf City", "Surf City to Duck"]}],
            "EcGc.Cat8.us": [
                {"TS.W": ["Surf City to Duck", "Duck to New Point Comfort", "New Point Comfort to Cape Henlopen", "Cape Henlopen to Sandy Hook", "Sandy Hook to Watch Hill", "Watch Hill to Merrimack River", "Merrimack River to Stonington"]},
                {"TS.Y": ["Altamaha Sound to South Santee River", "South Santee River to Surf City"]},
                {"TS.Y": ["Stonington to The US/Canada Border", "The US/Canada Border to Charlesville", "Charlesville to Chezzetcook Inlet"]},
                ],
            "EcGc.Cat8.us2": [
                {"TS.W": ["Cape Henlopen to Sandy Hook", "Sandy Hook to Watch Hill", "Watch Hill to Merrimack River", "Merrimack River to Stonington", "Stonington to The US/Canada Border", "The US/Canada Border to Charlesville", "Charlesville to Chezzetcook Inlet"]},
                {"TS.Y": ["Surf City to Duck", "Duck to New Point Comfort", "New Point Comfort to Cape Henlopen"]},
                {"TS.Y": ["Chezzetcook Inlet to Meat Cove", "Meat Cove to Cape Ray"]},
                ],
            "EcGc.Cat9.can": [
                {"TS.W": ["Charlesville to Chezzetcook Inlet", "Chezzetcook Inlet to Meat Cove", "Meat Cove to Cape Ray", "Cape Ray to La Manche", "La Manche to Strait of Belle Isle", "Strait of Belle Isle to Cape Chidley"]},
                {"TS.A": ["Brownsville to Baffin Bay", "Baffin Bay to Port OConnor", "Port OConnor to High Island", "High Island to Morgan City", "Morgan City to The Miss./Alabama Border", "The Miss./Alabama Border to Destin", "Destin to Suwannee River", "Suwannee River to Bonita Beach", "Bonita Beach to Flamingo", "Flamingo to Ocean Reef", "Ocean Reef to Jupiter Inlet", "Jupiter Inlet to Flagler Beach", "Flagler Beach to Altamaha Sound", "Altamaha Sound to South Santee River", "South Santee River to Surf City", "Surf City to Duck", "Duck to New Point Comfort", "New Point Comfort to Cape Henlopen", "Cape Henlopen to Sandy Hook", "Sandy Hook to Watch Hill", "Watch Hill to Merrimack River", "Merrimack River to Stonington", "Stonington to The US/Canada Border", "The US/Canada Border to Charlesville"]},
                ],
            "EcGc.Cat9.Too": [
                {"TS.W": ["Jupiter Inlet to Flagler Beach", "Flagler Beach to Altamaha Sound", "Altamaha Sound to South Santee River", "South Santee River to Surf City", "Surf City to Duck", "Duck to New Point Comfort", "New Point Comfort to Cape Henlopen", "Cape Henlopen to Sandy Hook", "Sandy Hook to Watch Hill", "Watch Hill to Merrimack River"]},
                {"TS.A": ["Brownsville to Baffin Bay", "Baffin Bay to Port OConnor", "Port OConnor to High Island", "High Island to Morgan City", "Morgan City to The Miss./Alabama Border", "The Miss./Alabama Border to Destin", "Destin to Suwannee River", "Suwannee River to Bonita Beach", "Bonita Beach to Flamingo", "Flamingo to Ocean Reef", "Ocean Reef to Jupiter Inlet"]},
                {"TS.A": ["Merrimack River to Stonington", "Stonington to The US/Canada Border", "The US/Canada Border to Charlesville", "Charlesville to Chezzetcook Inlet", "Chezzetcook Inlet to Meat Cove", "Meat Cove to Cape Ray", "Cape Ray to La Manche", "La Manche to Strait of Belle Isle", "Strait of Belle Isle to Cape Chidley"]},
                ],
            "HumboldtDec2024": [
                {"TS.W": ['Davenport to Gualala River', 'Gualala River to Mendo/Hum County Line', 'Mendo/Hum County Line to Cape Mendocino', 'Cape Mendocino to Humboldt/Del Norte Line', 'Humboldt/Del Norte Line to The Oregon/Cal. Border', 'The Oregon/Cal. Border to Douglas/Lane Line']}
                ],
            "HumboldtDec2024.Region09": [
                {"TS.W": ['Davenport to Gualala River', 'Gualala River to Mendo/Hum County Line', 'Mendo/Hum County Line to Cape Mendocino', 'Cape Mendocino to Humboldt/Del Norte Line', 'Humboldt/Del Norte Line to The Oregon/Cal. Border', 'The Oregon/Cal. Border to Douglas/Lane Line']}
                ],
            "HumboldtDec2024.Region22": [
                {"TS.Y": ['The Cal./Mexico Border to Orange/San Diego Line', 'Orange/San Diego Line to Rincon Point', 'Rincon Point to Point Conception']},
                {"TS.Y": ['Cascade Head to The Oregon/Wash. Border', 'The Oregon/Wash. Border to The Wash./BC Border']},
                {"TS.W": ['Point Conception to Ragged Point', 'Ragged Point to Davenport', 'Davenport to Gualala River', 'Gualala River to Mendo/Hum County Line', 'Mendo/Hum County Line to Cape Mendocino', 'Cape Mendocino to Humboldt/Del Norte Line', 'Humboldt/Del Norte Line to The Oregon/Cal. Border', 'The Oregon/Cal. Border to Douglas/Lane Line', 'Douglas/Lane Line to Cascade Head']},
                ],
            "Juan_de_Fuca_SP_NTWC_ThreatDB": [{"TS.W": ["Southern Strait of Juan de Fuca", "Northern Strait of Juan de Fuca", "Island County", "Possession Sound", "Western Skagit and Northwestern Snohomish Counties", "San Juan Islands", "Western Whatcom County"]}],
            "Pacific.NTWC.Cat1a": [],
            "Pacific.NTWC.Cat1b": [],
            "Pacific.NTWC.Cat2a": [],
            "Pacific.NTWC.Cat2b": [],
            "Pacific.NTWC.Cat3": [],
            "Pacific.NTWC.Cat4": [{"TS.Y": ["Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line"]}],
            "Pacific.NTWC.Cat4.Too": [
                {"TS.Y": ["The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border"]},
                ],
            "Pacific.NTWC.Cat4.Also": [{"TS.Y": ["Amchitka Pass to Attu"]}],
            "Pacific.NTWC.Cat4.Far": [],
            "Pacific.NTWC.Cat4.Far.Too": [],
            "Pacific.NTWC.Cat5a": [],
            "Pacific.NTWC.Cat5b": [],
            "Pacific.NTWC.Cat6a": [
                {"TS.W": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border"]},
                {"TS.A": ["The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]},
                ],
            "Pacific.NTWC.Cat6a.5hrs": [{"TS.A": ["The Cal./Mexico Border to Orange/San Diego Line", "Orange/San Diego Line to Rincon Point", "Rincon Point to Point Conception", "Point Conception to Ragged Point", "Ragged Point to Davenport", "Davenport to Gualala River", "Gualala River to Mendo/Hum County Line", "Mendo/Hum County Line to Cape Mendocino", "Cape Mendocino to Humboldt/Del Norte Line", "Humboldt/Del Norte Line to The Oregon/Cal. Border", "The Oregon/Cal. Border to Douglas/Lane Line", "Douglas/Lane Line to Cascade Head", "Cascade Head to The Oregon/Wash. Border", "The Oregon/Wash. Border to The Wash./BC Border", "The Wash./BC Border to North Vancouver Island", "North Vancouver Island to The BC/Alaska Border", "The BC/Alaska Border to Cape Decision", "Cape Decision to Salisbury Sound", "Salisbury Sound to Cape Fairweather", "Cape Fairweather to Cape Suckling", "Cape Suckling to Hinchinbrook Entrance", "Hinchinbrook Entrance to Kennedy Entrance", "Kennedy Entrance to Chignik Bay", "Chignik Bay to Unimak Pass", "Unimak Pass to Samalga Pass", "Samalga Pass to Amchitka Pass", "Amchitka Pass to Attu"]}],
            "Pacific.NTWC.Cat6a.7hrs": [],
            "Puget_Sound_SP_NTWC_ThreatDB": [{"TS.W": ["Puget Sound", "Island County", "Possession Sound", "Western Skagit and Northwestern Snohomish Counties"]}],
            "SF_Bay_SP_NTWC_ThreatDB": [{"TS.W": ["San Francisco Bay", "Suisun Bay"]}],
            "Strait_of_Georgia_SP_NTWC_ThreatDB": [{"TS.W": ["Strait of Georgia", "San Juan Islands", "Western Skagit and Northwestern Snohomish Counties", "Western Whatcom County"]}],
    }

    def getExpectedBrkptSegmentsDictPTWC(self):
        return {
            "AmSam.15.0S.172.0W": [
                {"TS.W": ["American Samoa"]},
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                ],
            "AmSam.15.5S.175.5W": [{"TS.W": ["American Samoa"]}],
            "AmSam.Cat1a": [],
            "AmSam.Cat1b": [{"TS.Y": ["American Samoa"]}],
            "AmSam.Cat1c": [
                {"TS.W": ["American Samoa"]},
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                ],
            "AmSam.Cat2a": [{"TS.Y": ["American Samoa"]}],
            "AmSam.Cat2b": [
                {"TS.W": ["American Samoa"]},
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                ],
            "AmSam.Cat3a": [{"TS.Y": ["American Samoa"]}],
            "AmSam.Cat3b": [
                {"TS.W": ["American Samoa"]},
                {"TS.A": ["Guam"]},
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                ],
            "AmSam.Cat4": [
                {"TS.A": ["American Samoa"]},
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                ],
            "AmSam.Cat5": [],
            "AmSam.Cat6.Deep": [],
            "AmSam.Cat6.Inland": [],
            "AmSam.Cat6.Shallow": [],
            "Caribe.PTWC.Cat1a": [],
            "Caribe.PTWC.Cat1b": [],
            "Caribe.PTWC.Cat1c": [],
            "Caribe.PTWC.Cat2a": [],
            "Caribe.PTWC.Cat2b": [],
            "Caribe.PTWC.Cat2c": [],
            "Caribe.PTWC.Cat3a.NoFcst": [],
            "Caribe.PTWC.Cat3a.RIFT": [],
            "Caribe.PTWC.Cat3a.TTT": [],
            "Caribe.PTWC.Cat4a.NoFcst": [{"TS.Y": ["Puerto Rico"]}],
            "Caribe.PTWC.Cat4a.RIFT": [{"TS.Y": ["Puerto Rico"]}],
            "Caribe.PTWC.Cat4a.TTT": [],
            "Caribe.PTWC.Cat5a.RIFT": [{"TS.W": ["Puerto Rico"]}],
            "Caribe.PTWC.Cat5a.TTT": [{"TS.W": ["Puerto Rico"]}],
            "Caribe.PTWC.Cat5b.NoFcst": [{"TS.W": ["Puerto Rico"]}],
            "Caribe.PTWC.Cat5b.NoThreat": [{"TS.W": ["Puerto Rico"]}],
            "Guam.Cat1a": [],
            "Guam.Cat1b": [{"TS.Y": ["Guam"]}],
            "Guam.Cat1c": [{"TS.W": ["Guam"]}],
            "Guam.Cat2a": [{"TS.Y": ["Guam"]}],
            "Guam.Cat2b": [{"TS.W": ["Guam"]}],
            "Guam.Cat3a": [{"TS.Y": ["Guam"]}],
            "Guam.Cat3b": [
                {"TS.W": ["Guam"]},
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.A": ["American Samoa"]},
                ],
            "Guam.Cat4": [
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.A": ["Guam"]},
                {"TS.A": ["American Samoa"]},
                ],
            "Guam.Cat5": [],
            "Guam.Cat6.Deep": [],
            "Guam.Cat6.Inland": [],
            "Guam.Cat6.Shallow": [],
            "Hawaii.Cat.Dunno.Chip": [
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.A": ["American Samoa"]},
                {"TS.A": ["Guam"]},
                ],
            "Hawaii.Cat1a": [{"TS.W": ["Hawaii"]}],
            "Hawaii.Cat1b": [{"TS.W": ["Hawaii", "Maui"]}],
            "Hawaii.Cat1b.Onshore": [{"TS.W": ["Hawaii", "Maui"]}],
            "Hawaii.Cat2a": [{"TS.W": ["Hawaii", "Maui"]}],
            "Hawaii.Cat2a.Onshore": [{"TS.W": ["Hawaii", "Maui"]}],
            "Hawaii.Cat2b": [
                {"TS.W": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.A": ["American Samoa"]},
                ],
            "Hawaii.Cat2b.Onshore": [{"TS.W": ["Hawaii", "Maui", "Honolulu", "Kauai"]}],
            "Hawaii.Cat3a": [{"TS.W": ["Hawaii", "Maui"]}],
            "Hawaii.Cat3b": [{"TS.W": ["Hawaii", "Maui", "Honolulu"]}],
            "Hawaii.Cat3c": [{"TS.W": ["Maui", "Honolulu", "Kauai"]}],
            "Hawaii.Cat3d": [{"TS.W": ["Honolulu", "Kauai"]}],
            "Hawaii.Cat4": [
                {"TS.W": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.A": ["American Samoa"]},
                ],
            "Hawaii.Cat4.Too": [
                {"TS.W": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.A": ["American Samoa"]},
                ],
            "Hawaii.Cat5a": [],
            "Hawaii.Cat5b": [],
            "Hawaii.Cat6": [
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.W": ["American Samoa"]},
                ],
            "Hawaii.Cat7": [{"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]}],
            "Hawaii.Cat7.Too": [
                {"TS.A": ["Hawaii", "Maui", "Honolulu", "Kauai"]},
                {"TS.W": ["Guam"]},
                ],
            "Hawaii.Cat8": [],
            "Hawaii.Cat9a": [],
            "Hawaii.Cat9b": [],
            "Hawaii.Cat9c": [],
            "Pacific.PTWC.Cat1a": [],
            "Pacific.PTWC.Cat1b": [],
            "Pacific.PTWC.Cat1c": [],
            "Pacific.PTWC.Cat2a.NoFcst": [],
            "Pacific.PTWC.Cat2a.RIFT": [],
            "Pacific.PTWC.Cat2a.TTT": [],
            "Pacific.PTWC.Cat2b": [],
            "Pacific.PTWC.Cat3a.NoFcst": [],
            "Pacific.PTWC.Cat3a.RIFT": [],
            "Pacific.PTWC.Cat3a.TTT": [],
            "Pacific.PTWC.Cat3b": [],
            "Pacific.PTWC.Cat4a.RIFT": [],
            "Pacific.PTWC.Cat4a.TTT": [{"TS.A": ["American Samoa"]}],
            "Pacific.PTWC.Cat4b.NoFcst": [{"TS.W": ["American Samoa"]}],
            "Pacific.PTWC.Cat4b.NoThreat": [{"TS.A": ["American Samoa"]}],
            "PuertoRico.Cat1a": [],
            "PuertoRico.Cat1b": [{"TS.Y": ["Puerto Rico"]}],
            "PuertoRico.Cat1c": [{"TS.W": ["Puerto Rico"]}],
            "PuertoRico.Cat2a": [{"TS.Y": ["Puerto Rico"]}],
            "PuertoRico.Cat2b": [{"TS.W": ["Puerto Rico"]}],
            "PuertoRico.Cat3a": [{"TS.Y": ["Puerto Rico"]}],
            "PuertoRico.Cat3b": [{"TS.W": ["Puerto Rico"]}],
            "PuertoRico.Cat4": [{"TS.A": ["Puerto Rico"]}],
            "PuertoRico.Cat5": [],
            "PuertoRico.Cat6": [],
            "PuertoRico.Cat7": [],
    }

    def getGulfOfAmericaBreakPointSegmentNames(self):
        '''
        @summary: Returns the break point segment names associated with the Gulf of America
        @return: List of Strings
        '''
        return ["Brownsville to Baffin Bay", "Baffin Bay to Port OConnor",
                "Port OConnor to High Island", "High Island to Morgan City",
                "Morgan City to The Miss./Alabama Border", "The Miss./Alabama Border to Destin",
                "Destin to Suwannee River", "Suwannee River to Bonita Beach",
                "Bonita Beach to Flamingo", "Flamingo to Ocean Reef"]
