# *** Override behavior of TsunamiRecommender.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
Tsunami Recommender (T-RECS) (PTWC)

@since: June 2022
@author: GSL Hazard Services Team
"""
import logging, UFStatusHandler
import EventSetFactory
import TsunamiRecommenderCommon
from com.raytheon.viz.gfe.ui.runtimeui import DisplayMessageDialog
from gov.noaa.gsl.viz.atoms.trecs import TrecsExecDialog


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()
        self.logger = logging.getLogger("TsunamiRecommender")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsl.common.atoms.hazardservices", "TsunamiRecommender",
            level=logging.INFO))
        self.logger.setLevel(logging.INFO)

        self.AMSAM_PRODUCT_REGION = "As"
        self.HAWAII_PRODUCT_REGION = "Hi"
        self.GUAM_PRODUCT_REGION = "Gu"
        self.PACIFIC_PRODUCT_REGION = "Pac"
        self.PRVI_PRODUCT_REGION = "Pr"
        self.CARIB_PRODUCT_REGION = "Car"

        self.PROC_HAWAII = "Hawaii Procedure"
        self.PROC_AMSAM = "AmSam Procedure"
        self.PROC_GUAM = "Guam/CNMI Procedure"
        self.PROC_PRVI = "PR/VI Procedure"
        self.PROC_NONUS_PAC = "NonUS Pacific Procedure"
        self.PROC_NONUS_CARIB = "NonUS Caribbean Procedure"

        self.procsListDict = self.buildTrecsProceduresDict()

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the recommender, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiRecommender (PTWC)",
            "author": "GSL",
            "version": 1.0,
            "description": ("Creates Tsunami hazard events based on criteria from an input "
                            "physical event and tsunami forecast information")
            }
        return metaDict

    def getHazardTypesToRecommend(self):
        '''
        @summary: The possible hazard type groups that the recommender will create
        hazard events for if selected by the user
        @return: A list of strings
        '''
        return [
            "Tsunami Watch/Warning/Advisory (TS.A/TS.W/TS.Y)",
            "Tsunami Information Statement (TS.S)",
            "Tsunami Threat Message (TS.ThreatMessage)",
            "Tsunami Observatory Message (TS.ObservatoryMessage)"
            ]

    def setSelectedTrecsExecProcsAndCategs(self, productRegions):
        self.trecsExecInfo.deselectAllProcedures()

        # Since we might execute more than one procedure (e.g., Hawaii, and Guam), select
        # all that are appropriate, though only the last one selected (or even better,
        # one that has a satisfied category - the bestSelectedProductRegion) will be the
        # "current" one in the TrecsExecDialog
        basinProcs = []
        if self.isPacificBasin() or self.isIndianOceanProcRegion() or self.isInSouthAmericaDualProcRegion() or self.isInCentralAmericaDualProcRegion():
            basinProcs.extend([self.PROC_HAWAII, self.PROC_AMSAM, self.PROC_GUAM, self.PROC_NONUS_PAC])
        if self.isAtlanticBasin() or self.isInSouthAmericaDualProcRegion() or self.isInCentralAmericaDualProcRegion():
            basinProcs.extend([self.PROC_PRVI, self.PROC_NONUS_CARIB])

        bestSelectedProductRegion = None
        for productRegion in productRegions:
            availProcs = self.trecsExecInfo.getProcedures(productRegion)
            for proc in availProcs:
                if proc.getName() in basinProcs:
                    self.trecsExecInfo.selectProcedureByName(proc.getName())
                    categories = proc.getCategories()
                    for category in categories:
                        if category.getPythonExecClassname() is not None:
                            try:
                                thePythonClassName = category.getPythonExecClassname()
                                klass = self.getTrecsExecClass(thePythonClassName)
                                pyExector = klass(category.getConditions(), category.getActions())
                                if pyExector.conditionsSatisfied(self):
                                    proc.setSelectedCategory(category)
                                    proc.setDefaultCategory(category)
                                    proc.setDefault(True)
                                    bestSelectedProductRegion = productRegion
                                    break
                            except Exception as e:
                                DisplayMessageDialog.openWarning(f"T_RECS Dialog - {self.physicalEventID}", e)
                                self.trecsExecInfo.appendToTrace(e.args)
        if bestSelectedProductRegion is not None:
            self.trecsExecInfo.setSelectedProductRegion(bestSelectedProductRegion)

    def buildTrecsProceduresDict(self):
        """
        @return: The Procedures List Dict - a dictionary by product region to a list of procedures
        """
        procsListDict = {
            "Hi": [
                {
                    "procName": self.PROC_HAWAII,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "ProcHawaiiCateg1a",
                                "conditions": ["Near SE Coast of Hawaii AND ", "h < 100km AND ",
                                               "6.9 <= M <= 7.5"],
                                "actions": ["Create a Tsunami Warning (TS.W) for the island of Hawaii"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "ProcHawaiiCateg1b",
                                "conditions": ["Near SE Coast of Hawaii AND ", "h < 100km AND ",
                                               "7.6 <= M <= 9.9"],
                                "actions": ["Create a Tsunami Warning (TS.W) for the following islands:",
                                            "Hawaii, Kahoolawe, Lanai, Maui, and Molokai"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "ProcHawaiiCateg2a",
                                "conditions": ["Near SW Coast of Hawaii AND ", "h < 100km AND ", "6.9 <= M <= 7.5"],
                                "actions": ["Create a Tsunami Warning (TS.W) for the following islands:"
                                            "Hawaii, Kahoolawe, Lanai, Maui, and Molokai"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "ProcHawaiiCateg2b",
                                "conditions": ["Near SW Coast of Hawaii AND ", "h < 100km AND", "7.6 <= M <= 9.9"],
                                "actions": ["Create a Tsunami Warning (TS.W) for all Hawaiian islands"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "ProcHawaiiCateg3a",
                                "conditions": ["Within 300 km of Hawaii AND ", "h < 100km AND ",
                                               "6.9 <= M <= 7.5 AND ", "Closest to Hawaii"],
                                "actions": ["Create a Tsunami Warning (TS.W) for the following islands:"
                                            "Hawaii, Kahoolawe, Lanai, Maui, and Molokai"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "ProcHawaiiCateg3b",
                                "conditions": ["Within 300 km of Hawaii AND ", "h < 100km AND ",
                                               "6.9 <= M <= 7.5 AND ", "Closest to Kahoolawe/Lanai/Maui/Molokai"],
                                "actions": ["Create a Tsunami Warning (TS.W) for the following islands:"
                                            "Hawaii, Kahoolawe, Lanai, Maui, Molokai, and Oahu"]
                            },
                            {
                                "name": "Category 3c",
                                "pythonExecClassName": "ProcHawaiiCateg3c",
                                "conditions": ["Within 300 km of Hawaii AND ", "h < 100km AND ",
                                               "6.9 <= M <= 7.5 AND ", "Closest to Oahu"],
                                "actions": ["Create a Tsunami Warning (TS.W) for the following islands:"
                                            "Kahoolawe, Kauai, Lanai, Maui, Molokai, Niihau, and Oahu"]
                            },
                            {
                                "name": "Category 3d",
                                "pythonExecClassName": "ProcHawaiiCateg3d",
                                "conditions": ["Within 300 km of Hawaii AND ", "h < 100km AND ",
                                               "6.9 <= M <= 7.5 AND ", "Closest to Kauai/Niihau"],
                                "actions": ["Create a Tsunami Warning (TS.W) for the following islands:"
                                            "Kauai, Niihau, and Oahu"]
                            },
                            {
                                "name": "Category 4",
                                "pythonExecClassName": "ProcHawaiiCateg4",
                                "conditions": ["Within 300 km of Hawaii AND ", "h < 100km AND ",
                                               "7.6 <= M <= 9.9"],
                                "actions": ["Create a Tsunami Warning (TS.W) for all islands"]
                            },
                            {
                                "name": "Category 5a",
                                "pythonExecClassName": "ProcHawaiiCateg5a",
                                "conditions": ["Within 300 km of Hawaii AND ", "4.0 <= M <= 6.8 AND ",
                                               "h < 100km"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No Threat"]
                            },
                            {
                                "name": "Category 5b",
                                "pythonExecClassName": "ProcHawaiiCateg5b",
                                "conditions": ["Within 300 km of Hawaii AND ", "h >= 100km AND ",
                                               "4.0 <= M <= 9.9"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No Threat"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "ProcHawaiiCateg6",
                                "conditions": ["Inside Pacific EQ Source Zone AND ", "h < 100km AND ",
                                               "7.9 <= M <= 9.9 AND ", "offshore AND ",
                                               "ArrivalTime within 3-6 hrs of NOW"],
                                "actions": ["Create a Tsunami Watch (TS.A) for all islands"]
                            },
                            {
                                "name": "Category 7",
                                "pythonExecClassName": "ProcHawaiiCateg7",
                                "conditions": ["Inside North Pacific EQ Source Zone AND ", "h < 100km AND ",
                                               "7.9 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Watch (TS.A) for all islands"]
                            },
                            {
                                "name": "Category 8",
                                "pythonExecClassName": "ProcHawaiiCateg8",
                                "conditions": ["Inside Pacific EQ Source Zone AND ", "h < 100km AND ",
                                                "7.9 <= M <= 9.9 AND ", "offshore AND ", "ArrivalTime > 6 hrs of NOW"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - Still Evaluating"]
                            },
                            {
                                "name": "Category 9a",
                                "pythonExecClassName": "ProcHawaiiCateg9a",
                                "conditions": ["Inside Pacific EQ Source Zone AND ", "h < 100km AND ",
                                               "6.5 <= M <= 7.8"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No Threat"]
                            },
                            {
                                "name": "Category 9b",
                                "pythonExecClassName": "ProcHawaiiCateg9b",
                                "conditions": ["Inside Pacific EQ Source Zone AND ", "h >= 100km AND ",
                                               "6.5 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No Threat"]
                            },
                            {
                                "name": "Category 9c",
                                "pythonExecClassName": "ProcHawaiiCateg9c",
                                "conditions": ["Inside Pacific EQ Source Zone AND ", "6.5 <= M <= 9.9 AND ",
                                               "onshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No Threat"]
                            },
                        ],
                },
            ],
            "As": [
                {
                    "procName": self.PROC_AMSAM,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "ProcAmSamCateg1a",
                                "conditions": ["Within 300km of AmSam AND ", "5.5 <= M <= 6.6"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "ProcAmSamCateg1b",
                                "conditions": ["Within 300km of AmSam AND ", "h < 100km AND ",
                                               "6.7 <= M <= 7.0 AND ", "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 1c",
                                "pythonExecClassName": "ProcAmSamCateg1c",
                                "conditions": ["Within 300km of AmSam AND ", "h < 100km AND ",
                                               "7.1 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "ProcAmSamCateg2a",
                                "conditions": ["Between 300-1000km from AmSam AND ", "h < 100km AND ",
                                               "7.1 <= M <= 7.5 AND ", "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "ProcAmSamCateg2b",
                                "conditions": ["Between 300-1000km from AmSam AND ", "h < 100km AND ",
                                               "7.6 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "ProcAmSamCateg3a",
                                "conditions": ["> 1000km from AmSam AND ", "ArrivalTime within 3 hrs of NOW AND ",
                                               "h < 100km AND ", "7.6 <= M <= 7.8 AND ", "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "ProcAmSamCateg3b",
                                "conditions": ["> 1000km from AmSam AND ", "ArrivalTime within 3 hrs of NOW AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 4",
                                "pythonExecClassName": "ProcAmSamCateg4",
                                "conditions": ["ArrivalTime between 3 - 6 hrs of NOW AND ", "h < 100km AND ",
                                               "7.9 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Watch (TS.A)"]
                            },
                            {
                                "name": "Category 5",
                                "pythonExecClassName": "ProcAmSamCateg5",
                                "conditions": ["Pacific EQ Source Zone AND ", "ArrivalTime > 6 hrs of NOW AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - Still Evaluating"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "ProcAmSamCateg6",
                                "conditions": ["Pacific EQ Source Zone AND ",
                                                 "((h < 100km AND 6.5 <= M <= 7.8) OR",
                                                 " (h >=100km AND 6.5 <= M <= 9.9 AND offshore) OR",
                                                 " (6.5 <= M <= 9.9 AND ONshore))"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                        ],
                },
            ],
            "Gu": [
                {
                    "procName": self.PROC_GUAM,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "ProcGuamCateg1a",
                                "conditions": ["Within 300km of Guam/CNMI AND ", "5.5 <= M <= 6.6"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "ProcGuamCateg1b",
                                "conditions": ["Within 300km of Guam/CNMI AND ", "h < 100km AND ",
                                               "6.7 <= M <= 7.0 AND ", "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 1c",
                                "pythonExecClassName": "ProcGuamCateg1c",
                                "conditions": ["Within 300km of Guam/CNMI AND ", "h < 100km AND ",
                                               "7.1 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "ProcGuamCateg2a",
                                "conditions": ["Between 300-1000km from Guam/CNMI AND ", "h < 100km AND ",
                                               "7.1 <= M <= 7.5 AND ", "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "ProcGuamCateg2b",
                                "conditions": ["Between 300-1000km from Guam/CNMI AND ", "h < 100km AND ",
                                               "7.6 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "ProcGuamCateg3a",
                                "conditions": ["> 1000km from Guam/CNMI AND ", "ArrivalTime within 3 hrs of NOW AND ",
                                               "h < 100km AND ", "7.6 <= M <= 7.8 AND ", "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "ProcGuamCateg3b",
                                "conditions": ["> 1000km from Guam/CNMI AND ", "ArrivalTime within 3 hrs of NOW AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 4",
                                "pythonExecClassName": "ProcGuamCateg4",
                                "conditions": ["ArrivalTime between 3 - 6 hrs of NOW AND ", "h < 100km AND ",
                                               "7.9 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Watch (TS.A)"]
                            },
                            {
                                "name": "Category 5",
                                "pythonExecClassName": "ProcGuamCateg5",
                                "conditions": ["Pacific EQ Source Zone AND ", "ArrivalTime > 6 hrs of NOW AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ", "offshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - Still Evaluating"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "ProcGuamCateg6",
                                "conditions": ["Pacific EQ Source Zone AND ",
                                                 "((h < 100km AND 6.5 <= M <= 7.8) OR",
                                                 " (h >=100km AND 6.5 <= M <= 9.9 AND offshore) OR",
                                                 " (6.5 <= M <= 9.9 AND ONshore))"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                        ],
                },
            ],
            "Pr": [
                {
                    "procName": self.PROC_PRVI,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "ProcPRVICateg1a",
                                "conditions": ["Within 300km of PRVI AND ",
                                               "4.5 <= M <= 6.4"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "ProcPRVICateg1b",
                                "conditions": ["Within 300km of PRVI AND ",
                                               "h < 100km AND ", "6.5 <= M <= 7.0 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 1c",
                                "pythonExecClassName": "ProcPRVICateg1c",
                                "conditions": ["Within 300km of PRVI AND ",
                                               "h < 100km AND ", "7.1 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "ProcPRVICateg2a",
                                "conditions": ["Between 300-1000km from PRVI AND ",
                                               "h < 100km AND ", "7.1 <= M <= 7.5 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "ProcPRVICateg2b",
                                "conditions": ["Between 300-1000km from PRVI AND ",
                                               "h < 100km AND ", "7.6 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "ProcPRVICateg3a",
                                "conditions": ["Greater than 1000km from PRVI AND ",
                                               "arrival time within 3 hrs AND ",
                                               "h < 100km AND ", "7.6 <= M <= 7.8 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Advisory (TS.Y)"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "ProcPRVICateg3b",
                                "conditions": ["Greater than 1000km from PRVI AND ",
                                               "arrival time within 3 hrs AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Warning (TS.W)"]
                            },
                            {
                                "name": "Category 4",
                                "pythonExecClassName": "ProcPRVICateg4",
                                "conditions": ["Arrival time between 3 - 6 hrs AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Watch (TS.A)"]
                            },
                            {
                                "name": "Category 5",
                                "pythonExecClassName": "ProcPRVICateg5",
                                "conditions": ["(Inside Caribbean EQ Source Zone OR ",
                                               " Inside Atlantic EQ Source Zone) AND ",
                                               "Arrival time greater than 6 hours AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - Still Evaluating"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "ProcPRVICateg6",
                                "conditions": ["Inside Caribbean EQ Source Zone AND ",
                                               "(6.0 <= M <= 7.8 OR",
                                               "(M >= 7.9 AND ONshore))"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 7",
                                "pythonExecClassName": "ProcPRVICateg7",
                                "conditions": ["Inside Atlantic EQ Source Zone AND ",
                                               "(6.5 <= M <= 7.8 OR",
                                               "(M >= 7.9 AND ONshore))"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                        ],
                },
            ],
            "Pac": [
                {
                    "procName": self.PROC_NONUS_PAC,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "ProcPacCateg1a",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h < 100km AND ", "6.5 <= M <= 7.0"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "ProcPacCateg1b",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h >= 100km AND ", "6.5 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 1c",
                                "pythonExecClassName": "ProcPacCateg1c",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "6.5 <= M <= 9.9 AND ",
                                               "onshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "ProcPacCateg2a",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h < 100km AND ", "7.1 <= M <= 7.5 AND ",
                                               "offshore AND ",
                                               "PTWS warning points within 300 km"],
                                "actions": ["Create a Tsunami Threat Message (TS.ThreatMessage)"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "ProcPacCateg2b",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h < 100km AND ", "7.1 <= M <= 7.5 AND ",
                                               "offshore AND ",
                                               "no PTWS warning points within 300 km"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat or still evaluating"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "ProcPacCateg3a",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h < 100km AND ", "7.6 <= M <= 7.8 AND ",
                                               "offshore AND ",
                                               "PTWS warning points within 1000 km"],
                                "actions": ["Create a Tsunami Threat Message (TS.ThreatMessage)"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "ProcPacCateg3b",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h < 100km AND ", "7.6 <= M <= 7.8 AND ",
                                               "offshore AND ",
                                               "no PTWS warning points within 1000 km"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat or still evaluating"]
                            },
                            {
                                "name": "Category 4a",
                                "pythonExecClassName": "ProcPacCateg4a",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ",
                                               "offshore AND ",
                                               "PTWS warning points within 3 hours"],
                                "actions": ["Create a Tsunami Threat Message (TS.ThreatMessage)"]
                            },
                            {
                                "name": "Category 4b",
                                "pythonExecClassName": "ProcPacCateg4b",
                                "conditions": ["Inside Pacific EQ Source Zone AND ",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ",
                                               "offshore AND ",
                                               "no PTWS warning points within 3 hours"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat or still evaluating"]
                            },
                        ],
                },
            ],
            "Car": [
                {
                    "procName": self.PROC_NONUS_CARIB,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "ProcCarCateg1a",
                                "conditions": ["Inside Caribbean EQ Source Zone AND ",
                                               "h < 100km AND ", "6.0 <= M <= 7.0"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "ProcCarCateg1b",
                                "conditions": ["Inside Caribbean EQ Source Zone AND ",
                                               "h >= 100km AND ", "6.0 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 1c",
                                "pythonExecClassName": "ProcCarCateg1c",
                                "conditions": ["Inside Caribbean EQ Source Zone AND ",
                                               "6.0 <= M <= 9.9 AND ",
                                               "inland"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "ProcCarCateg2a",
                                "conditions": ["Inside Atlantic EQ Source Zone AND ",
                                               "h < 100km ", "AND 6.5 <= M <= 7.0"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "ProcCarCateg2b",
                                "conditions": ["Inside Atlantic EQ Source Zone AND ",
                                               "h >= 100km AND ", "6.5 <= M <= 9.9 AND ",
                                               "offshore"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 2c",
                                "pythonExecClassName": "ProcCarCateg2c",
                                "conditions": ["Inside Atlantic EQ Source Zone AND ",
                                               "6.5 <= M <= 9.9 AND ",
                                               "inland"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "ProcCarCateg3a",
                                "conditions": ["(Inside Caribbean EQ Source Zone OR ",
                                               " Inside Atlantic EQ Source Zone) AND",
                                               "h < 100km AND ", "7.1 <= M <= 7.5 AND ",
                                               "offshore AND ", "CARIBE warning points within 300 km"],
                                "actions": ["Create a Tsunami Threat Message (TS.ThreatMessage)"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "ProcCarCateg3b",
                                "conditions": ["(Inside Caribbean EQ Source Zone OR ",
                                               " Inside Atlantic EQ Source Zone) AND",
                                               "h < 100km AND ", "7.1 <= M <= 7.5 AND ",
                                               "offshore AND ", "no CARIBE warning points within 300 km"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat or still evaluating"]
                            },
                            {
                                "name": "Category 4a",
                                "pythonExecClassName": "ProcCarCateg4a",
                                "conditions": ["(Inside Caribbean EQ Source Zone OR ",
                                               " Inside Atlantic EQ Source Zone) AND",
                                               "h < 100km AND ", "7.6 <= M <= 7.8 AND ",
                                               "offshore AND ", "CARIBE warning points within 1000 km"],
                                "actions": ["Create a Tsunami Threat Message (TS.ThreatMessage)"]
                            },
                            {
                                "name": "Category 4b",
                                "pythonExecClassName": "ProcCarCateg4b",
                                "conditions": ["(Inside Caribbean EQ Source Zone OR ",
                                               " Inside Atlantic EQ Source Zone) AND",
                                               "h < 100km AND ", "7.6 <= M <= 7.8 AND ",
                                               "offshore AND ", "no CARIBE warning points within 1000 km"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat or still evaluating"]
                            },
                            {
                                "name": "Category 5a",
                                "pythonExecClassName": "ProcCarCateg5a",
                                "conditions": ["(Inside Caribbean EQ Source Zone OR ",
                                               " Inside Atlantic EQ Source Zone) AND",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ",
                                               "offshore AND ", "CARIBE warning points within 3 hours"],
                                "actions": ["Create a Tsunami Threat Message (TS.ThreatMessage)"]
                            },
                            {
                                "name": "Category 5b",
                                "pythonExecClassName": "ProcCarCateg5b",
                                "conditions": ["(Inside Caribbean EQ Source Zone OR ",
                                               "Inside Atlantic EQ Source Zone) AND",
                                               "h < 100km AND ", "7.9 <= M <= 9.9 AND ",
                                               "offshore AND ", "no CARIBE warning points within 3 hours"],
                                "actions": ["Create a Tsunami Information Statement (TS.S) - No threat or still evaluating"]
                            },
                        ],
                },
            ],
         }

        return procsListDict

    def getTrecsExecClass(self, thePythonClassName):
        return globals()[thePythonClassName]

'''
PROCEDURES Hawaii
'''


class ProcHawaiiCateg1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInSoutheastHawaiiSourceZone() and
                theTRECSTool.isInMagnitudeRange(6.9, 7.5) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        matchingIslands = ["Hawaii"]
        breakPointSegmentResults = theTRECSTool.getBreakPointSegmentsByIslandNames(matchingIslands)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInSoutheastHawaiiSourceZone() and
                theTRECSTool.isInMagnitudeRange(7.6, 9.9) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        matchingIslands = ["Hawaii", "Maui", "Kahoolawe", "Molokai", "Lanai"]
        breakPointSegmentResults = theTRECSTool.getBreakPointSegmentsByIslandNames(matchingIslands)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInSouthwestHawaiiSourceZone() and
                theTRECSTool.isInMagnitudeRange(6.9, 7.5) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        matchingIslands = ["Hawaii", "Maui", "Kahoolawe", "Molokai", "Lanai"]
        breakPointSegmentResults = theTRECSTool.getBreakPointSegmentsByIslandNames(matchingIslands)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInSouthwestHawaiiSourceZone() and
                theTRECSTool.isInMagnitudeRange(7.6, 9.9) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.HAWAII_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        matchingIslands = ["Hawaii"]
        return (theTRECSTool.isWithinDistanceKmOfHawaii(0, 300) and
                theTRECSTool.isInMagnitudeRange(6.9, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isClosestHawaiianIslandGroup(matchingIslands))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        matchingIslands = ["Hawaii", "Maui", "Kahoolawe", "Molokai", "Lanai"]
        breakPointSegmentResults = theTRECSTool.getBreakPointSegmentsByIslandNames(matchingIslands)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        matchingIslands = ["Kahoolawe", "Lanai", "Maui", "Molokai"]
        return (theTRECSTool.isWithinDistanceKmOfHawaii(0, 300) and
                theTRECSTool.isInMagnitudeRange(6.9, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isClosestHawaiianIslandGroup(matchingIslands))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        matchingIslands = ["Hawaii", "Maui", "Kahoolawe", "Molokai", "Lanai", "Oahu"]
        breakPointSegmentResults = theTRECSTool.getBreakPointSegmentsByIslandNames(matchingIslands)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg3c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        matchingIslands = ["Oahu"]
        return (theTRECSTool.isWithinDistanceKmOfHawaii(0, 300) and
                theTRECSTool.isInMagnitudeRange(6.9, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isClosestHawaiianIslandGroup(matchingIslands))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        matchingIslands = ["Maui", "Kahoolawe", "Molokai", "Lanai", "Oahu", "Kauai", "Niihau"]
        breakPointSegmentResults = theTRECSTool.getBreakPointSegmentsByIslandNames(matchingIslands)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg3d(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        matchingIslands = ["Kauai", "Niihau"]
        return (theTRECSTool.isWithinDistanceKmOfHawaii(0, 300) and
                theTRECSTool.isInMagnitudeRange(6.9, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isClosestHawaiianIslandGroup(matchingIslands))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        matchingIslands = ["Oahu", "Kauai", "Niihau"]
        breakPointSegmentResults = theTRECSTool.getBreakPointSegmentsByIslandNames(matchingIslands)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg4(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfHawaii(0, 300) and
                theTRECSTool.isInMagnitudeRange(7.6, 9.9) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.HAWAII_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.W")


class ProcHawaiiCateg5a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfHawaii(0, 300) and
                theTRECSTool.isInMagnitudeRange(4.0, 6.8) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")


class ProcHawaiiCateg5b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfHawaii(0, 300) and
                theTRECSTool.isInMagnitudeRange(4.0, 9.9) and
                theTRECSTool.isDeepKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")


class ProcHawaiiCateg6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isWithinTimeRangeFromHawaii(3, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.HAWAII_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.A", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.A")


class ProcHawaiiCateg7(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInNorthPacificEarthquakeSourceZone() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.HAWAII_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.A", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.A")


class ProcHawaiiCateg8(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                not theTRECSTool.isWithinTimeRangeFromHawaii(0, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S", hazardAttributes={"tisType": "tisHigh"})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")


class ProcHawaiiCateg9a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 7.8) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")


class ProcHawaiiCateg9b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 9.9) and
                theTRECSTool.isDeepKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")


class ProcHawaiiCateg9c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 9.9) and
                theTRECSTool.isOnshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.HAWAII_PRODUCT_REGION, "TS.S")

'''
PROCEDURES AmSam
'''


class ProcAmSamCateg1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfAmSam(0, 300) and
                theTRECSTool.isInMagnitudeRange(5.5, 6.6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.S")


class ProcAmSamCateg1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfAmSam(0, 300) and
                theTRECSTool.isInMagnitudeRange(6.7, 7.0) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.AMSAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.Y")


class ProcAmSamCateg1c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfAmSam(0, 300) and
                theTRECSTool.isInMagnitudeRange(7.1, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.AMSAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.W")


class ProcAmSamCateg2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfAmSam(300, 1000) and
                theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.AMSAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.Y")


class ProcAmSamCateg2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfAmSam(300, 1000) and
                theTRECSTool.isInMagnitudeRange(7.6, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.AMSAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.W")


class ProcAmSamCateg3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (not theTRECSTool.isWithinDistanceKmOfAmSam(0, 1000) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromAmSam(0, 3))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.AMSAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.Y")


class ProcAmSamCateg3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (not theTRECSTool.isWithinDistanceKmOfAmSam(0, 1000) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromAmSam(0, 3))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.AMSAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.W")


class ProcAmSamCateg4(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromAmSam(3, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.AMSAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.A", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.A")


class ProcAmSamCateg5(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                not theTRECSTool.isWithinTimeRangeFromAmSam(0, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # TODO Somehow this should be a "Still Evaluating" TS.S
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.S", hazardAttributes={"tisType": "tisHigh"})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.S")


class ProcAmSamCateg6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                ((theTRECSTool.isInMagnitudeRange(6.5, 7.8) and theTRECSTool.isShallowKm(100)) or
                 (theTRECSTool.isInMagnitudeRange(6.5, 9.9) and theTRECSTool.isDeepKm(100) and theTRECSTool.isOffshore()) or
                 (theTRECSTool.isInMagnitudeRange(6.5, 9.9) and theTRECSTool.isOnshore())))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.AMSAM_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.AMSAM_PRODUCT_REGION, "TS.S")

'''
PROCEDURES Guam/CNMI
'''


class ProcGuamCateg1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfGuam(0, 300) and
                theTRECSTool.isInMagnitudeRange(5.5, 6.6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.S")


class ProcGuamCateg1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfGuam(0, 300) and
                theTRECSTool.isInMagnitudeRange(6.7, 7.0) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.GUAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.Y")


class ProcGuamCateg1c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfGuam(0, 300) and
                theTRECSTool.isInMagnitudeRange(7.1, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.GUAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.W")


class ProcGuamCateg2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfGuam(300, 1000) and
                theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.GUAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.Y")


class ProcGuamCateg2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfGuam(300, 1000) and
                theTRECSTool.isInMagnitudeRange(7.6, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.GUAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.W")


class ProcGuamCateg3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (not theTRECSTool.isWithinDistanceKmOfGuam(0, 1000) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromGuam(0, 3))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.GUAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.Y")


class ProcGuamCateg3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (not theTRECSTool.isWithinDistanceKmOfGuam(0, 1000) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromGuam(0, 3))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.GUAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.W")


class ProcGuamCateg4(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromGuam(3, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.GUAM_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.A", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.A")


class ProcGuamCateg5(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                not theTRECSTool.isWithinTimeRangeFromGuam(0, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.S", hazardAttributes={"tisType": "tisHigh"})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.S")


class ProcGuamCateg6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                ((theTRECSTool.isInMagnitudeRange(6.5, 7.8) and theTRECSTool.isShallowKm(100)) or
                 (theTRECSTool.isInMagnitudeRange(6.5, 9.9) and theTRECSTool.isDeepKm(100) and theTRECSTool.isOffshore()) or
                 (theTRECSTool.isInMagnitudeRange(6.5, 9.9) and theTRECSTool.isOnshore())))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.GUAM_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.GUAM_PRODUCT_REGION, "TS.S")

'''
PROCEDURES PRVI
'''


class ProcPRVICateg1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfPRVI(0, 300) and
                theTRECSTool.isInMagnitudeRange(4.5, 6.4))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.S")


class ProcPRVICateg1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfPRVI(0, 300) and
                theTRECSTool.isInMagnitudeRange(6.5, 7.0) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.PRVI_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.Y")


class ProcPRVICateg1c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfPRVI(0, 300) and
                theTRECSTool.isInMagnitudeRange(7.1, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.PRVI_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.W")


class ProcPRVICateg2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfPRVI(300, 1000) and
                theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.PRVI_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.Y")


class ProcPRVICateg2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isWithinDistanceKmOfPRVI(300, 1000) and
                theTRECSTool.isInMagnitudeRange(7.6, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.PRVI_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.W")


class ProcPRVICateg3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (not theTRECSTool.isWithinDistanceKmOfPRVI(0, 1000) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromPRVI(0, 3))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.PRVI_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.Y", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.Y")


class ProcPRVICateg3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (not theTRECSTool.isWithinDistanceKmOfPRVI(0, 1000) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromPRVI(0, 3))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.PRVI_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.W", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.W")


class ProcPRVICateg4(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isWithinTimeRangeFromPRVI(3, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        breakPointSegmentResults = theTRECSTool.amu.getBreakPointSegmentsByProductRegionName(theTRECSTool.PRVI_PRODUCT_REGION)
        eventGeometry = theTRECSTool.amu.getUnionedGeometryFromQueryResults(breakPointSegmentResults)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.A", eventGeometry, {})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.A")


class ProcPRVICateg5(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion() or
                 theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion()) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                not theTRECSTool.isWithinTimeRangeFromPRVI(0, 6))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.S", hazardAttributes={"tisType": "tisHigh"})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.S")


class ProcPRVICateg6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                (theTRECSTool.isInMagnitudeRange(6.0, 7.8) or (theTRECSTool.isInMagnitudeRange(7.9, 9.9) and theTRECSTool.isOnshore())))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.S")


class ProcPRVICateg7(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion()) and
                (theTRECSTool.isInMagnitudeRange(6.5, 7.8) or (theTRECSTool.isInMagnitudeRange(7.9, 9.9) and theTRECSTool.isOnshore())))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PRVI_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PRVI_PRODUCT_REGION, "TS.S")

'''
PROCEDURES Non-US Pacific (PTWS)
'''


class ProcPacCateg1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 7.0) and
                theTRECSTool.isShallowKm(100)
                )

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")


class ProcPacCateg1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 9.9) and
                theTRECSTool.isDeepKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")


class ProcPacCateg1c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 9.9) and
                theTRECSTool.isOnshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")


class ProcPacCateg2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 300, "PTWS"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.ThreatMessage")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.ThreatMessage")


class ProcPacCateg2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                not theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 300, "PTWS"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")


class ProcPacCateg3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 1000, "PTWS"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.ThreatMessage")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.ThreatMessage")


class ProcPacCateg3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                not theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 1000, "PTWS"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")


class ProcPacCateg4a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        # No forecast either means return False (when autotesting) or Exception
        if theTRECSTool.timeOfArrivalForecast is None:
            if theTRECSTool.suppressTTTMissingErrors:
                return False
            else:
                raise Exception(f"{type(self).__name__} " + theTRECSTool.NO_TTT_AVAILABLE_ERROR)

        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isWithinTimeOfArrivalOfWarningPoints(3, "PTWS"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.ThreatMessage")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.ThreatMessage")


class ProcPacCateg4b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        # No forecast either means return False (when autotesting) or Exception
        if theTRECSTool.timeOfArrivalForecast is None:
            if theTRECSTool.suppressTTTMissingErrors:
                return False
            else:
                raise Exception(f"{type(self).__name__} " + theTRECSTool.NO_TTT_AVAILABLE_ERROR)

        return ((theTRECSTool.isInPacificEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                not theTRECSTool.isWithinTimeOfArrivalOfWarningPoints(3, "PTWS"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S", hazardAttributes={"tisType": "tisHigh"})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.PACIFIC_PRODUCT_REGION, "TS.S")

'''
PROCEDURES Non-US Caribbean (CARIBE-EWS)
'''


class ProcCarCateg1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.0, 7.0) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.0, 9.9) and
                theTRECSTool.isDeepKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg1c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.0, 9.9) and
                theTRECSTool.isOnshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 7.0) and
                theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 9.9) and
                theTRECSTool.isDeepKm(100) and
                theTRECSTool.isOffshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg2c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(6.5, 9.9) and
                theTRECSTool.isOnshore())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or
                 theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 300, "CARIBE"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.ThreatMessage")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.ThreatMessage")


class ProcCarCateg3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or
                 theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                not theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 300, "CARIBE"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg4a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or
                 theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 1000, "CARIBE"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.ThreatMessage")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.ThreatMessage")


class ProcCarCateg4b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or
                 theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                not theTRECSTool.isWithinDistanceKmOfWarningPoints(0, 1000, "CARIBE"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")


class ProcCarCateg5a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        # No forecast either means return False (when autotesting) or Exception
        if theTRECSTool.timeOfArrivalForecast is None:
            if theTRECSTool.suppressTTTMissingErrors:
                return False
            else:
                raise Exception(f"{type(self).__name__} " + theTRECSTool.NO_TTT_AVAILABLE_ERROR)

        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or
                 theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                theTRECSTool.isWithinTimeOfArrivalOfWarningPoints(3, "CARIBE"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.ThreatMessage")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.ThreatMessage")


class ProcCarCateg5b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        # No forecast either means return False (when autotesting) or Exception
        if theTRECSTool.timeOfArrivalForecast is None:
            if theTRECSTool.suppressTTTMissingErrors:
                return False
            else:
                raise Exception(f"{type(self).__name__} " + theTRECSTool.NO_TTT_AVAILABLE_ERROR)

        return ((theTRECSTool.isInAtlanticEarthquakeSourceZone() or theTRECSTool.isInSouthAmericaDualProcRegion() or
                 theTRECSTool.isInCaribbeanEarthquakeSourceZone() or theTRECSTool.isInCentralAmericaDualProcRegion()) and
                theTRECSTool.isInMagnitudeRange(7.9, 9.9) and
                theTRECSTool.isShallowKm(100) and
                theTRECSTool.isOffshore() and
                not theTRECSTool.isWithinTimeOfArrivalOfWarningPoints(3, "CARIBE"))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent(theTRECSTool.CARIB_PRODUCT_REGION, "TS.S", hazardAttributes={"tisType": "tisHigh"})
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, theTRECSTool.CARIB_PRODUCT_REGION, "TS.S")

