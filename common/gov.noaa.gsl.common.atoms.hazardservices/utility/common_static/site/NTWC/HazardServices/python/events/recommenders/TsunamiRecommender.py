# *** Override behavior of TsunamiRecommender.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
Tsunami Recommender (T-RECS) (NTWC)

@since: June 2022
@author: GSL Hazard Services Team
"""
import logging, UFStatusHandler
import EventSetFactory
import TsunamiRecommenderCommon
from gov.noaa.gsl.viz.atoms.trecs import TrecsExecDialog
from com.raytheon.viz.gfe.ui.runtimeui import DisplayMessageDialog

# from com.raytheon.uf.common.python import PyJavaUtil


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()
        self.logger = logging.getLogger("TsunamiRecommender")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsd.uf.common.recommenders.hydro", "TsunamiRecommender", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

        self.PROC_611 = "Section 6.1.1 BcWc"
        self.PROC_6121 = "Section 6.1.2.1 Alaska"
        self.PROC_6122 = "Section 6.1.2.2 Bering"
        self.PROC_6123 = "Section 6.1.2.3 Arctic"
        self.PROC_613 = "Section 6.1.3 Pacific and Indian Oceans"
        self.PROC_615 = "Section 6.1.5 US/Canada Atlantic and Gulf of America"
        self.PROC_6151 = "Section 6.1.5.1 Caribbean"
        self.PROC_616 = "Section 6.1.6 Atlantic non-AOR"

        self.procsListDict = self.buildTrecsProceduresDict()

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the recommender, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiRecommender (NTWC)",
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
            "Tsunami Conference Call (TS.ConferenceCall)",
            "Tsunami Observatory Message (TS.ObservatoryMessage)"
            ]

    def setSelectedTrecsExecProcsAndCategs(self, productRegions):
        self.trecsExecInfo.deselectAllProcedures()

        basinProcs = []
        if self.isBritishColumbiaProcRegion() or self.isUsWestCoastProcRegion():
            basinProcs.append(self.PROC_611)
        if self.isAlaskaProcRegion():
            basinProcs.append(self.PROC_6121)
        if self.isBeringSeaProcRegion():
            basinProcs.append(self.PROC_6122)
        if self.isArcticOceanProcRegion():
            basinProcs.append(self.PROC_6123)
        # Is it IN the Pacific/Indian, or is it in the dual procs region?
        if (self.isPacificNonAORProcRegion() or self.isIndianOceanProcRegion() or
            self.isInCentralAmericaDualProcRegion() or self.isInSouthAmericaDualProcRegion()):
            basinProcs.append(self.PROC_613)
        if self.isUsEastCoastProcRegion() or self.isEastCanadaProcRegion() or self.isGulfAmericaProcRegion() or self.isGulfStLawProcRegion():
            basinProcs.append(self.PROC_615)
        # Is it IN the Caribbean, or is it in the dual procs region?
        if (self.isCaribbeanProcRegion() or self.isInCentralAmericaDualProcRegion()):
            basinProcs.append(self.PROC_6151)
        # Is it IN the Atlantic, or is it in the dual procs region?
        if (self.isAtlanticBasinProcRegion() or self.isAtlanticRidgeProcRegion() or self.isInSouthAmericaDualProcRegion()):
            basinProcs.append(self.PROC_616)

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
        Note that we use reflection with pythonExecClassName since we cant really pass the python object
        to Java (the trecsExecInfo dialog) and then get it back to execute its methods. See
        AbstractTsunamiRecommender
        @return: The Procedures List Dict - a dictionary by product region to a list of procedures
        """
        procsListDict = {
            "AkBcWc": [
                {
                    "procName": self.PROC_611,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "Proc611Categ1a",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "Within 50km of US/Can Coast"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "Proc611Categ1b",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "Greater than 50km from US/Can Coast"],
                                "actions": ["Process routinely."]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "Proc611Categ2a",
                                "conditions": ["4.5 <= M < 5.5 AND",
                                               "Far onshore (> 100km) AND not likely felt"],
                                "actions": ["Process routinely."]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "Proc611Categ2b",
                                "conditions": ["4.5 <= M <= 6.4 AND",
                                               "(Not \"far onshore\" (<=100km) OR M >= 5.5)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 3",
                                "pythonExecClassName": "Proc611Categ3",
                                "conditions": ["6.5 <= M <= 7.0 OR",
                                               "7.1 <= M <= 7.8 AND h > 100km Deep OR",
                                               "(7.1 <= M <= 7.5 AND > 30 km inland) OR",
                                               "(7.6 <= M <= 7.8 AND > 50 km inland) OR",
                                               "(M >= 7.9 AND > 80 km inland)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 4a",
                                "pythonExecClassName": "Proc611Categ4a",
                                "conditions": ["7.1 <= M <= 7.5 AND h <= 100km Shallow AND",
                                               "(Offshore Warning Region per Figure 1 OR <= 30km onshore)"],
                                "actions": ["Create Tsunami Warning (TS.W) extending to first break points beyond 250km"]
                            },
                            {
                                "name": "Category 4b",
                                "pythonExecClassName": "Proc611Categ4b",
                                "conditions": ["7.1 <= M <= 7.5 AND h <= 100km Shallow AND",
                                               "Advisory Region per Figure 1"],
                                "actions": ["Create Tsunami Advisory (TS.Y) extending to first break points beyond 250km"]
                            },
                            {
                                "name": "Category 5",
                                "pythonExecClassName": "Proc611Categ5",
                                "conditions": ["7.6 <= M <= 7.8 AND h <= 100km Shallow AND",
                                               "(Offshore OR <= 50 km onshore)"],
                                "actions": ["Create Tsunami Warning (TS.W) out to 500 km",
                                            "Create Tsunami Advisory (TS.Y) between 500 km and 1000 km"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "Proc611Categ6",
                                "conditions": ["M >= 7.9 AND ",
                                               "(Offshore OR <= 80 km onshore)"],
                                "actions": ["Create Tsunami Warning (TS.W) within 3 hours of NOW",
                                            "Create Tsunami Watch (TS.A) for rest of AOR"]
                            },
                        ],
                },
                {
                    "procName": self.PROC_6121,
                    "categories":
                        [
                            {
                                "name": "Category 1",
                                "pythonExecClassName": "Proc6121Categ1",
                                "conditions": ["4.0 <= M <= 4.9 AND",
                                               "West of 155W"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "Proc6121Categ2a",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "East of 155W AND",
                                               "Within 50km of Ak/Can Coast"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"],
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "Proc6121Categ2b",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "East of 155W AND",
                                               "Greater than 50km from Ak/Can Coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "Proc6121Categ3a",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "East of 155W AND",
                                               "Far ONshore (100km+) and not likely felt at the coast)"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "Proc6121Categ3b",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "East of 155W AND",
                                               "Not \"Far onshore\" (<=100km)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 4a",
                                "pythonExecClassName": "Proc6121Categ4a",
                                "conditions": ["(5.0 <= M <= 5.4) AND",
                                               "Far ONshore (100km+) and not likely felt at the coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 4b",
                                "pythonExecClassName": "Proc6121Categ4b",
                                "conditions": ["(5.0 <= M <= 6.4) AND",
                                               "(Not \"far onshore\" (<=100km) OR M >= 5.5)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 5",
                                "pythonExecClassName": "Proc6121Categ5",
                                "conditions": ["6.5 <= M <= 7.0 OR",
                                               "7.1 <= M <= 7.8 AND h > 100km Deep OR",
                                               "(7.1 <= M <= 7.5 AND > 30 km inland) OR",
                                               "(7.6 <= M <= 7.8 AND > 50 km inland) OR",
                                               "(M >= 7.9 AND > 80 km inland)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 6a",
                                "pythonExecClassName": "Proc6121Categ6a",
                                "conditions": ["7.1 <= M <= 7.5 AND h <= 100km Shallow AND",
                                               "(Offshore Warning Region per Figure 1 OR <= 30km onshore)"],
                                "actions": ["Create Tsunami Warning (TS.W) to first break points beyond 250 km"]
                            },
                            {
                                "name": "Category 6b",
                                "pythonExecClassName": "Proc6121Categ6b",
                                "conditions": ["7.1 <= M <= 7.5 AND h <= 100km Shallow AND",
                                               "Advisory Region per Figure 1"],
                                "actions": ["Create Tsunami Advisory (TS.Y) to first break points beyond 250 km"]
                            },
                            {
                                "name": "Category 7",
                                "pythonExecClassName": "Proc6121Categ7",
                                "conditions": ["7.6 <= M <= 7.8 AND h <= 100km Shallow AND",
                                               "(Offshore OR <= 50 km onshore)"],
                                "actions": ["Create Tsunami Warning (TS.W) out to 500 km",
                                            "Create Tsunami Advisory (TS.Y) between 500 km and 1000 km"]
                            },
                            {
                                "name": "Category 8",
                                "pythonExecClassName": "Proc6121Categ8",
                                "conditions": ["M >= 7.9 AND ",
                                               "(Offshore OR <= 80 km onshore)"],
                                "actions": ["Create Tsunami Warning (TS.W) within 3 hours of NOW",
                                            "Create Tsunami Watch (TS.A) for rest of AOR"]
                            }
                        ],
                },
                {
                    "procName": self.PROC_6122,
                    "categories":
                        [
                            {
                                "name": "Category 1",
                                "pythonExecClassName": "Proc6122Categ1",
                                "conditions": ["4.0 <= M <= 4.9 AND",
                                               "Bering Sea Deep Region"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "Proc6122Categ2a",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "Bering Sea Shallow Region AND",
                                               "Within 50km of Ak/Can Coast"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"],
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "Proc6122Categ2b",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "Bering Sea Shallow Region AND",
                                               "Greater than 50km from Ak/Can Coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "Proc6122Categ3a",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "Bering Sea Shallow Region AND",
                                               "Far (TODO Assuming >150km) from coast)"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "Proc6122Categ3b",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "Bering Sea Shallow Region AND",
                                               "Far ONshore (100km+) and not likely felt at the coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3c",
                                "pythonExecClassName": "Proc6122Categ3c",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "Bering Sea Shallow Region AND",
                                               "Not \"Far onshore\" (<=100km)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 4a",
                                "pythonExecClassName": "Proc6122Categ4a",
                                "conditions": ["(5.0 <= M <= 6.4) AND",
                                               "Very Far (TODO Assuming >200km) from coast)"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 4b",
                                "pythonExecClassName": "Proc6122Categ4b",
                                "conditions": ["(5.0 <= M <= 5.4) AND",
                                               "Far ONshore (100km+) and not likely felt at the coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 4c",
                                "pythonExecClassName": "Proc6122Categ4c",
                                "conditions": ["(5.0 <= M <= 6.4) AND",
                                               "(Not \"far onshore\" (<=100km) OR M >= 5.5)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 5",
                                "pythonExecClassName": "Proc6122Categ5",
                                "conditions": ["(6.5 <= M <= 7.0) OR",
                                               "(7.1 <= M <= 7.8 AND h > 100km Deep) OR",
                                               "(Bering Sea Shallow Region AND",
                                               " ((7.1 <= M <= 7.8 AND > 50 km from coast) OR",
                                               "  (M >= 7.9 AND > 80 km from coast)))"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "Proc6122Categ6",
                                "conditions": ["Bering Sea Deep Region AND ",
                                               "((M >= 7.1 AND h <= 100km Shallow) OR",
                                               " (M >= 7.9))"],
                                "actions": ["Create Tsunami Warning (TS.W) for the Pribilof and Aleutian Islands"]
                            },
                            {
                                "name": "Category 7",
                                "pythonExecClassName": "Proc6122Categ7",
                                "conditions": ["Bering Sea Shallow Region AND",
                                               "((M >= 7.1 AND h <= 100km Shallow AND",
                                               "  within 50 km of coast) OR",
                                               " (M >= 7.9 AND within 80 km of coast))"],
                                "actions": ["Create Tsunami Advisory (TS.Y) for Western Alaska"]
                            }
                        ],
                },
                {
                    "procName": self.PROC_6123,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "Proc6123Categ1a",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "Within 50km of Ak/Can Coast"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"],
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "Proc6123Categ1b",
                                "conditions": ["4.0 <= M <= 4.4 AND",
                                               "Greater than 50km from Ak/Can Coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "Proc6123Categ2a",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "Far (TODO Assuming >150km) from coast)"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "Proc6123Categ2b",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "Far ONshore (100km+) and not likely felt at the coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 2c",
                                "pythonExecClassName": "Proc6123Categ2c",
                                "conditions": ["(4.5 <= M <= 4.9) AND",
                                               "Not \"Far onshore\" (<=100km)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "Proc6123Categ3a",
                                "conditions": ["(5.0 <= M <= 6.4) AND",
                                               "Very Far (TODO Assuming >200km) from coast)"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "Proc6123Categ3b",
                                "conditions": ["(5.0 <= M <= 5.4) AND",
                                               "Far ONshore (100km+) and not likely felt at the coast"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3c",
                                "pythonExecClassName": "Proc6123Categ3c",
                                "conditions": ["(5.0 <= M <= 6.4) AND",
                                               "(Not \"far onshore\" (<=100km) OR M >= 5.5)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 4",
                                "pythonExecClassName": "Proc6123Categ4",
                                "conditions": ["(6.5 <= M <= 7.0) OR",
                                               "(7.1 <= M <= 7.8 AND h > 100km Deep) OR",
                                               "(7.1 <= M <= 7.8 AND > 50 km from coast) OR",
                                               "(M >= 7.9 AND > 80 km from coast)"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 5a",
                                "pythonExecClassName": "Proc6123Categ5a",
                                "conditions": ["Arctic Ocean AOR Region AND ",
                                               "((M >= 7.1 AND h <= 100km Shallow AND",
                                               "  within 50 km of coast) OR",
                                               " (M >= 7.9 AND within 80 km of coast)) AND",
                                               "(latitude south of 75N and longitude west of 138W)"],
                                "actions": ["Create Tsunami Advisory (TS.Y) for Arctic coast"]
                            },
                            {
                                "name": "Category 5b",
                                "pythonExecClassName": "Proc6123Categ5b",
                                "conditions": ["Arctic Ocean AOR Region AND ",
                                               "((M >= 7.1 AND h <= 100km Shallow AND",
                                               "  within 50 km of coast) OR",
                                               " (M >= 7.9 AND within 80 km of coast)) AND",
                                               "(latitude north of 75N or longitude east of 138W)"],
                                "actions": ["Create Tsunami Information Statement (TS.S HI)"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "Proc6123Categ6",
                                "conditions": ["Arctic Ocean non-AOR Region AND",
                                               "(M >= 7.1)"],
                                "actions": ["Create Tsunami Information Statement (TS.S HI or LOW)"]
                            }
                        ],
                },
                {
                    "procName": self.PROC_613,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "Proc613Categ1a",
                                "conditions": ["Indian Ocean Basin and M <= 5.7"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "Proc613Categ1b",
                                "conditions": ["Indian Ocean Basin and M >= 5.8"],
                                "actions": ["Create Observatory Message"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "Proc613Categ2a",
                                "conditions": ["M <= 5.7"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "Proc613Categ2b",
                                "conditions": ["5.8 <= M <= 6.4"],
                                "actions": ["Create Observatory Message"]
                            },
                            {
                                "name": "Category 3",
                                "pythonExecClassName": "Proc613Categ3",
                                "conditions": ["6.5 <= M <= 7.5"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"],
                            },
                            {
                                "name": "Category 4",
                                "pythonExecClassName": "Proc613Categ4",
                                "conditions": ["7.6 <= M <= 7.8 AND h < 100km"],
                                "actions": ["Create Tsunami Advisory (TS.Y) to 1000 km;",
                                            "If no break points/AOR within 1000km then ",
                                            "create a Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 5a",
                                "pythonExecClassName": "Proc613Categ5a",
                                "conditions": ["M >= 7.6 AND M <= 7.8 AND h > 100km"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 5b",
                                "pythonExecClassName": "Proc613Categ5b",
                                "conditions": ["M >= 7.9 AND h > 100km"],
                                "actions": ["Create Tsunami Information Statement (TS.S.High / Potential Danger)"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "Proc613Categ6",
                                "conditions": ["M >= 7.9"],
                                "actions": ["If Travel time < 6 hrs AND likely danger",
                                            "  Then Tsunami Warning (TS.W) for <= 3 hours",
                                            "    and Tsunami Watch (TS.A) for rest of the AOR",
                                            "Otherwise ",
                                            "    Create Tsunami Information Statement (TS.S.High / Potential Danger)"]
                            }
                        ],
                }
            ],
            "EcGc": [
                {
                    "procName": self.PROC_615,
                    "categories":
                        [
                            {
                                "name": "Category 1",
                                "pythonExecClassName": "Proc615Categ1",
                                "conditions": ["M < 4.0", "Atlantic AOR"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 2a",
                                "pythonExecClassName": "Proc615Categ2a",
                                "conditions": ["(4.0 <= M <= 4.9) AND",
                                               "(Within 150 km of US/Canada coast)",
                                               "Atlantic AOR"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 2b",
                                "pythonExecClassName": "Proc615Categ2b",
                                "conditions": ["(4.0 <= M <= 4.9) AND",
                                               "(Greater than 150 km from US/Canada coast)",
                                               "Atlantic AOR"],
                                "actions": ["Process Routinely"]
                            },

                            {
                                "name": "Category 3a",
                                "pythonExecClassName": "Proc615Categ3a",
                                "conditions": ["(5.0 <= M <= 5.9) AND",
                                               "(Far ONshore (> 100 km))",
                                               "Atlantic AOR"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 3b",
                                "pythonExecClassName": "Proc615Categ3b",
                                "conditions": ["(5.0 <= M <= 5.9) AND",
                                               "(not far onshore)",
                                               "Atlantic AOR"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 4",
                                "pythonExecClassName": "Proc615Categ4",
                                "conditions": ["(6.0 <= M <= 6.4) OR",
                                               "(ONshore <= 400 miles AND",
                                               " ((6.5 <= M <= 7.5 AND greater than 30 km inland) OR",
                                               "  (7.6 <= M <= 7.8 AND greater than 50 km inland) OR",
                                               "  (M >= 7.9 AND greater than 80 km inland)))",
                                               "Atlantic AOR"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 5",
                                "pythonExecClassName": "Proc615Categ5",
                                "conditions": ["(M >= 6.5) AND",
                                               "(OFFshore OR",
                                               " (6.5 <= M <= 7.5 AND within 30 km inland) OR",
                                               " (7.6 <= M <= 7.8 AND within 50 km inland) OR",
                                               " (M >= 7.9 AND within 80 km inland))",
                                               "Gulf of America"],
                                "actions": ["Create Warning (TS.W) for the US Gulf of America coast"]
                            },
                            {
                                "name": "Category 6",
                                "pythonExecClassName": "Proc615Categ6",
                                "conditions": ["(M >= 6.5) AND",
                                               "(OFFshore OR",
                                               " (6.5 <= M <= 7.5 AND within 30 km inland) OR",
                                               " (7.6 <= M <= 7.8 AND within 50 km inland) OR",
                                               " (M >= 7.9 AND within 80 km inland))",
                                               "Gulf of St Lawrence"],
                                "actions": ["Create Warning (TS.W) for the Canadian Gulf of St. Lawrence coast"]
                            },
                            {
                                "name": "Category 7",
                                "pythonExecClassName": "Proc615Categ7",
                                "conditions": ["(6.5 <= M <= 7.5) AND",
                                               "(OFFshore OR within 30 km inland)",
                                               "East Coast and Eastern Canada Regions"],
                                "actions": ["Create Warning (TS.W) to first break points beyond 250 km"]
                            },
                            {
                                "name": "Category 8",
                                "pythonExecClassName": "Proc615Categ8",
                                "conditions": ["(7.6 <= M <= 7.8) AND",
                                               "(OFFshore OR within 50 km inland)",
                                               "East Coast and Eastern Canada Regions"],
                                "actions": ["Create Warning (TS.W) to first break points beyond 500 km",
                                            "Create Advisory (TS.Y) from 500 - 1000 km"]
                            },
                            {
                                "name": "Category 9",
                                "pythonExecClassName": "Proc615Categ9",
                                "conditions": ["(M >= 7.9) AND",
                                               "(OFFshore OR within 80 km inland)",
                                               "East Coast and Eastern Canada Regions"],
                                "actions": ["Create Warning (TS.W) to first break points beyond 1000 km",
                                            "Create Watch (TS.A) for remaining AOR"]
                            },
                        ],
                },
                {
                    "procName": self.PROC_6151,
                    "categories":
                        [
                            {
                                "name": "Category 1",
                                "pythonExecClassName": "Proc6151Categ1",
                                "conditions": ["M < 6.0"],
                                "actions": ["Process routinely"]
                            },
                            {
                                "name": "Category 2",
                                "pythonExecClassName": "Proc6151Categ2",
                                "conditions": ["(6.0 <= M <= 7.8) OR ",
                                               "(M >= 7.9 AND ",
                                               " (h > 100km OR greater than 80 km inland))"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"]
                            },
                            {
                                "name": "Category 3",
                                "pythonExecClassName": "Proc6151Categ3",
                                "conditions": ["M >= 7.9 AND h <= 100km AND",
                                               " (OFFshore OR within 80 km inland)"],
                                "actions": ["Create Tsunami Information Statement (TS.S.High / Potential Danger)"]
                            }
                        ],
                },
                {
                    "procName": self.PROC_616,
                    "categories":
                        [
                            {
                                "name": "Category 1a",
                                "pythonExecClassName": "Proc616Categ1a",
                                "conditions": ["M <= 5.7"],
                                "actions": ["Process Routinely"]
                            },
                            {
                                "name": "Category 1b",
                                "pythonExecClassName": "Proc616Categ1b",
                                "conditions": ["5.8 <= M <= 6.4"],
                                "actions": ["Create Observatory Message"]
                            },
                            {
                                "name": "Category 2",
                                "pythonExecClassName": "Proc616Categ2",
                                "conditions": ["6.5 <= M <= 7.8"],
                                "actions": ["Create Tsunami Information Statement (TS.S)"],
                            },
                            {
                                "name": "Category 3",
                                "pythonExecClassName": "Proc616Categ3",
                                "conditions": ["M >= 7.9"],
                                "actions": ["Create Tsunami Information Statement (TS.S.High / Potential Danger)"]
                            }
                        ],
                }
            ]
         }

        return procsListDict

    def getTrecsExecClass(self, thePythonClassName):
        return globals()[thePythonClassName]

'''
PROCEDURES 6.1.1 - B.C. and U.S. West Coast
'''


class Proc611Categ1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent("AkBcWc", "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc611Categ1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                not theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        # Process routinely
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc611Categ2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 5.4) and
                theTRECSTool.isFarOnshoreKm())

    def applyActions(self, theTRECSTool):
        # Process routinely
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc611Categ2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 6.4))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent("AkBcWc", "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc611Categ3(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.5, 7.0) or
                (theTRECSTool.isInMagnitudeRange(7.1, 7.8) and theTRECSTool.isDeepKm()) or
                (theTRECSTool.isInMagnitudeRange(7.1, 7.5) and theTRECSTool.isFarOnshoreKm(30)) or
                (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and theTRECSTool.isFarOnshoreKm(50)) or
                (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isFarOnshoreKm(80)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [
            theTRECSTool.recommendEvent("AkBcWc", "TS.S")
            ]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc611Categ4a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                (theTRECSTool.isWithinKmOfCoast(30) or
                 (theTRECSTool.isOffshore() and theTRECSTool.isInAkBcWcWarningRegion())))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        resultList = theTRECSTool.createEventDictsByDistanceCriteria({"TS.W": [0, 250]})
        if not resultList and theTRECSTool.isInAkBcWcWarningRegion():
            resultList = theTRECSTool.createEventDictsByClosestBreakPoint("AkBcWc", "TS.W")
        return resultList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.W")


class Proc611Categ4b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                not theTRECSTool.isWithinKmOfCoast(30) and
                theTRECSTool.isInAkBcWcAdvisoryRegion())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        resultList = theTRECSTool.createEventDictsByDistanceCriteria({"TS.Y": [0, 250]})
        if not resultList and theTRECSTool.isInAkBcWcAdvisoryRegion():
            resultList = theTRECSTool.createEventDictsByClosestBreakPoint("AkBcWc", "TS.Y")
        return resultList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.Y")


class Proc611Categ5(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                (theTRECSTool.isOffshore() or
                 theTRECSTool.isOnshoreWithinKm(50)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        criteriaDict = {
            "TS.W": [0, 500],
            "TS.Y": [500, 1000]
            }
        eventDicts = theTRECSTool.createEventDictsByDistanceCriteria(criteriaDict)
        return eventDicts

    def assertActions(self, theTRECSTool, eventSet):
        return (self.assertHazardEvent(eventSet, "AkBcWc", "TS.Y") and self.assertHazardEvent(eventSet, "AkBcWc", "TS.W"))


class Proc611Categ6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        if theTRECSTool.timeOfArrivalForecast is None:
            raise Exception(f"{type(self).__name__} " + theTRECSTool.NO_TTT_AVAILABLE_ERROR)

        return (theTRECSTool.isInMagnitudeRange(7.9) and
                (theTRECSTool.isOffshore() or theTRECSTool.isWithinKmOfCoast(80)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        eventDicts = theTRECSTool.createWarningToVariableHoursAndWatchForRemainingAOR("AkBcWc", 3)
        return eventDicts

    def assertActions(self, theTRECSTool, eventSet):
        return (self.assertHazardEvent(eventSet, "AkBcWc", "TS.A") and self.assertHazardEvent(eventSet, "AkBcWc", "TS.W"))

'''
PROCEDURES 6.1.2.1 - Alaska
'''


class Proc6121Categ1(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.9) and
                theTRECSTool.isWestOfLongitude(-155))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        wwaAreaDictList = []
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6121Categ2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                theTRECSTool.isEastOfLongitude(-155) and
                theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6121Categ2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                theTRECSTool.isEastOfLongitude(-155) and
                not theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        wwaAreaDictList = []
        super().appendToTrace(theTRECSTool)
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6121Categ3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                theTRECSTool.isEastOfLongitude(-155) and
                theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        wwaAreaDictList = []
        super().appendToTrace(theTRECSTool)
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6121Categ3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                theTRECSTool.isEastOfLongitude(-155))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6121Categ4a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 5.4) and
                theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        wwaAreaDictList = []
        super().appendToTrace(theTRECSTool)
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6121Categ4b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return theTRECSTool.isInMagnitudeRange(5.0, 6.4)

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6121Categ5(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.5, 7.0) or
                (theTRECSTool.isInMagnitudeRange(7.1, 7.8) and theTRECSTool.isDeepKm()) or
                (theTRECSTool.isInMagnitudeRange(7.1, 7.5) and theTRECSTool.isFarOnshoreKm(30)) or
                (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and theTRECSTool.isFarOnshoreKm(50)) or
                (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isFarOnshoreKm(80)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6121Categ6a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return ((theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                 theTRECSTool.isShallowKm(100)) and
                (theTRECSTool.isWithinKmOfCoast(30) or
                 (theTRECSTool.isOffshore() and theTRECSTool.isInAkBcWcWarningRegion())))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        resultList = theTRECSTool.createEventDictsByDistanceCriteria({"TS.W": [0, 250]})
        if not resultList and theTRECSTool.isInAkBcWcWarningRegion():
            resultList = theTRECSTool.createEventDictsByClosestBreakPoint("AkBcWc", "TS.W")
        return resultList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.W")


class Proc6121Categ6b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.1, 7.5) and
                theTRECSTool.isShallowKm(100) and
                not theTRECSTool.isWithinKmOfCoast(30) and theTRECSTool.isInAkBcWcAdvisoryRegion())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        resultList = theTRECSTool.createEventDictsByDistanceCriteria({"TS.Y": [0, 250]})
        if not resultList and theTRECSTool.isInAkBcWcAdvisoryRegion():
            resultList = theTRECSTool.createEventDictsByClosestBreakPoint("AkBcWc", "TS.Y")
        return resultList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.Y")


class Proc6121Categ7(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                theTRECSTool.isShallowKm(100) and
                (theTRECSTool.isOffshore() or
                 theTRECSTool.isOnshoreWithinKm(50)))

    def applyActions(self, theTRECSTool):
        criteriaDict = {
            "TS.W": [0, 500],
            "TS.Y": [500, 1000]
            }
        eventDicts = theTRECSTool.createEventDictsByDistanceCriteria(criteriaDict)
        super().appendToTrace(theTRECSTool)
        return eventDicts

    def assertActions(self, theTRECSTool, eventSet):
        return (self.assertHazardEvent(eventSet, "AkBcWc", "TS.Y") and self.assertHazardEvent(eventSet, "AkBcWc", "TS.W"))


class Proc6121Categ8(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        if theTRECSTool.timeOfArrivalForecast is None:
            raise Exception(f"{type(self).__name__} " + theTRECSTool.NO_TTT_AVAILABLE_ERROR)

        return (theTRECSTool.isInMagnitudeRange(7.9) and
                (theTRECSTool.isOffshore() or theTRECSTool.isOnshoreWithinKm(80)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        eventDicts = theTRECSTool.createWarningToVariableHoursAndWatchForRemainingAOR("AkBcWc", 3)
        return eventDicts

    def assertActions(self, theTRECSTool, eventSet):
        return (self.assertHazardEvent(eventSet, "AkBcWc", "TS.A") and self.assertHazardEvent(eventSet, "AkBcWc", "TS.W"))

'''
PROCEDURES 6.1.2.2 - Bering Sea
'''


class Proc6122Categ1(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.9) and
                theTRECSTool.isBeringSeaDeepProcRegion())

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6122Categ2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                theTRECSTool.isBeringSeaShallowProcRegion() and
                theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6122Categ2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                theTRECSTool.isBeringSeaShallowProcRegion() and
                not theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6122Categ3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                theTRECSTool.isBeringSeaShallowProcRegion() and
                theTRECSTool.isGreaterThanKmFromCoast(150))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6122Categ3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                theTRECSTool.isBeringSeaShallowProcRegion() and
                theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6122Categ3c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                theTRECSTool.isBeringSeaShallowProcRegion() and
                not theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6122Categ4a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 6.4) and
                theTRECSTool.isGreaterThanKmFromCoast(200))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6122Categ4b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 5.4) and
                theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6122Categ4c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 6.4))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6122Categ5(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.5, 7.0) or
                (theTRECSTool.isInMagnitudeRange(7.1, 7.8) and theTRECSTool.isDeepKm(100)) or
                (theTRECSTool.isBeringSeaShallowProcRegion() and
                 ((theTRECSTool.isInMagnitudeRange(7.1, 7.8) and theTRECSTool.isGreaterThanKmFromCoast(50)) or
                  (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isGreaterThanKmFromCoast(80)))))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6122Categ6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isBeringSeaDeepProcRegion() and
                ((theTRECSTool.isInMagnitudeRange(7.1) and theTRECSTool.isShallowKm(100)) or
                 (theTRECSTool.isInMagnitudeRange(7.9))))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        wwaAreaDictList = []
        segmentNameList = [
            "Chignik Bay to Unimak Pass",
            "Unimak Pass to Samalga Pass",
            "Samalga Pass to Amchitka Pass",
            "Amchitka Pass to Attu"
            ]
        attributeDict = {"hazardLocations": segmentNameList}
        segmentQueryResults = theTRECSTool.amu.getBreakPointSegmentsBySegmentNames(segmentNameList)
        warningGeom = theTRECSTool.amu.getUnionedGeometryFromQueryResults(segmentQueryResults)
        wwaAreaDictList.append(theTRECSTool.recommendEvent("AkBcWc", "TS.W", warningGeom, attributeDict))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.W")


class Proc6122Categ7(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isBeringSeaShallowProcRegion() and
                ((theTRECSTool.isInMagnitudeRange(7.1) and theTRECSTool.isShallowKm(100) and
                  theTRECSTool.isWithinKmOfCoast(50)) or
                 (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isWithinKmOfCoast(80))))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        wwaAreaDictList = []
        specProcNames = ["Bristol Bay and the Pribilof Islands"]
        segmentQueryResults = theTRECSTool.amu.getBreakPointSegmentsBySegmentNames(specProcNames)
        warningGeom = theTRECSTool.amu.getUnionedGeometryFromQueryResults(segmentQueryResults)
        attrDict = {
            "wwaLocationCoverage": "specialAreas",
            "hazardLocations": specProcNames,
            }
        wwaAreaDictList.append(theTRECSTool.recommendEvent("AkBcWc", "TS.W", warningGeom, attrDict))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.W")

'''
PROCEDURES 6.1.2.3 - Arctic Ocean
'''


class Proc6123Categ1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6123Categ1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.4) and
                not theTRECSTool.isWithinKmOfCoast(50))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6123Categ2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                theTRECSTool.isGreaterThanKmFromCoast(150))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6123Categ2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6123Categ2c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.5, 4.9) and
                not theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6123Categ3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 6.4) and
                theTRECSTool.isGreaterThanKmFromCoast(200))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6123Categ3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 5.4) and
                theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6123Categ3c(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 6.4) and
                not theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6123Categ4(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.5, 7.0) or
                (theTRECSTool.isInMagnitudeRange(7.1, 7.8) and theTRECSTool.isDeepKm(100)) or
                (theTRECSTool.isInMagnitudeRange(7.1, 7.8) and theTRECSTool.isGreaterThanKmFromCoast(50)) or
                (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isGreaterThanKmFromCoast(80)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc6123Categ5a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isArcticAORProcRegion() and
                ((theTRECSTool.isInMagnitudeRange(7.1) and theTRECSTool.isShallowKm(100) and
                  theTRECSTool.isWithinKmOfCoast(50)) or
                 (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isWithinKmOfCoast(80))) and
                (theTRECSTool.isSouthOfLatitude(75) and theTRECSTool.isWestOfLongitude(-138)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        wwaAreaDictList = []
        specProcNames = [
            "Western AK from Cape Prince of Wales to Wainwright",
            "Northern AK Border from Wainwright to the Canadian Border",
            ]
        segmentQueryResults = theTRECSTool.amu.getBreakPointSegmentsBySegmentNames(specProcNames)
        warningGeom = theTRECSTool.amu.getUnionedGeometryFromQueryResults(segmentQueryResults)
        attrDict = {
            "wwaLocationCoverage": "specialAreas",
            "hazardLocations": specProcNames,
            }
        wwaAreaDictList.append(theTRECSTool.recommendEvent("AkBcWc", "TS.Y", warningGeom, attrDict))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.Y")


class Proc6123Categ5b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isArcticAORProcRegion() and
                ((theTRECSTool.isInMagnitudeRange(7.1) and theTRECSTool.isShallowKm(100) and
                  theTRECSTool.isWithinKmOfCoast(50)) or
                 (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isWithinKmOfCoast(80))) and
                (theTRECSTool.isNorthOfLatitude(75) or theTRECSTool.isEastOfLongitude(-138)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S", hazardAttributes={"tisType": "tisHigh"})]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEventAndAttribute(eventSet, "AkBcWc", "TS.S", "tisType", "tisHigh")


class Proc6123Categ6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isArcticNonAORProcRegion() and
                theTRECSTool.isInMagnitudeRange(7.1))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        isHigh = theTRECSTool.isReasonToExpectTsunami()
        if isHigh:
            return [theTRECSTool.recommendEvent("AkBcWc", "TS.S", hazardAttributes={"tisType": "tisHigh"})]
        else:
            return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")

'''
PROCEDURES 6.1.3 - Pacific Ocean and Indian Ocean outside NTWC AOR
'''


class Proc613Categ1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isIndianOceanProcRegion() and theTRECSTool.isInMagnitudeRange(0, 5.7))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # Process Routinely
        wwaAreaDictList = []
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc613Categ1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isIndianOceanProcRegion() and theTRECSTool.isInMagnitudeRange(5.8))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # OM
        wwaAreaDictList = []
        wwaAreaDictList.append(theTRECSTool.recommendEvent("AkBcWc", "TS.ObservatoryMessage"))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.ObservatoryMessage")


class Proc613Categ2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(0, 5.7))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # Process Routinely
        wwaAreaDictList = []
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc613Categ2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.8, 6.4))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # OM
        wwaAreaDictList = []
        wwaAreaDictList.append(theTRECSTool.recommendEvent("AkBcWc", "TS.ObservatoryMessage"))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.ObservatoryMessage")


class Proc613Categ3(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.5, 7.5))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc613Categ4(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def __init__(self, someConditions, someActions):
        super().__init__(someConditions, someActions)
        self.phensigCreated = None

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and theTRECSTool.isShallowKm(100))

    def applyActions(self, theTRECSTool):
        wwaAreaDictList = []
        queryResults = theTRECSTool.amu.getBreakPointsWithinDistanceRangeFromPoint(theTRECSTool.latitude, theTRECSTool.longitude, 0,
                                                                                        1000, theTRECSTool.siteID, True, True)
        breakPointNames = theTRECSTool.amu.getNamesFromQueryResults(queryResults)
        if breakPointNames:
            wwaAreaDictList.extend(theTRECSTool.createEventDictsByDistanceCriteria({"TS.Y": [0, 1000]}))
            theTRECSTool.trecsExecInfo.appendToTrace(["Break Points exist within 1000km. So ...",
                                                      "Created Advisory (TS.Y) to 1000km."])
            self.phensigCreated = "TS.Y"
        else:
            wwaAreaDictList.append(theTRECSTool.recommendEvent("AkBcWc", "TS.S"))
            theTRECSTool.trecsExecInfo.appendToTrace(["No Break Points exist within 1000km. So ...",
                                                      "Created Information Statement (TS.S)."])
            self.phensigCreated = "TS.S"
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        if self.phensigCreated is not None:
            return self.assertHazardEvent(eventSet, "AkBcWc", self.phensigCreated)
        else:
            return self.assertEmptyHazardEvents(eventSet)


class Proc613Categ5a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and theTRECSTool.isDeepKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "AkBcWc", "TS.S")


class Proc613Categ5b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isDeepKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("AkBcWc", "TS.S", hazardAttributes={"tisType": "tisHigh"})]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEventAndAttribute(eventSet, "AkBcWc", "TS.S", "tisType", "tisHigh")


class Proc613Categ6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def __init__(self, someConditions, someActions):
        super().__init__(someConditions, someActions)
        self.phensigsCreated = []

    def conditionsSatisfied(self, theTRECSTool):
        if theTRECSTool.timeOfArrivalForecast is None:
            raise Exception(f"{type(self).__name__} " + theTRECSTool.NO_TTT_AVAILABLE_ERROR)

        return (theTRECSTool.isInMagnitudeRange(7.9))

    def applyActions(self, theTRECSTool):
        theTRECSTool.trecsExecInfo.appendToTrace(f"Executed actions for {type(self).__name__}:")
        eventDicts = []
        if theTRECSTool.timeOfArrivalForecast is not None:
            # TODO need change to NOW instead!!! Using refTime is ONLY FOR TESTING!!!!
            sixHourBrkPtSegQueryResults = theTRECSTool.agu.getBreakPointSegmentsWithinTimeRange(theTRECSTool.getCurrentCAVETime(), 6,
                                                                                                     theTRECSTool.timeOfArrivalForecast,
                                                                                                     theTRECSTool.siteID, ["AkBcWc"])
            if sixHourBrkPtSegQueryResults and theTRECSTool.isDangerLikely():
                eventDicts = theTRECSTool.createWarningToVariableHoursAndWatchForRemainingAOR("AkBcWc", 3)
                theTRECSTool.trecsExecInfo.appendToTrace("Break Point Segments exist within 6 hr (TODO change to NOW) AND")
                theTRECSTool.trecsExecInfo.appendToTrace("  there is likely danger to the AOR. So ...")
                theTRECSTool.trecsExecInfo.appendToTrace("  Created Warning (TS.W) to 3 hours.")
                theTRECSTool.trecsExecInfo.appendToTrace("  Created Watch (TS.A) for remaining AOR.")
                self.phensigsCreated.append("TS.W")
                self.phensigsCreated.append("TS.A")
            else:
                eventDicts = [theTRECSTool.recommendEvent("AkBcWc", "TS.S", hazardAttributes={"tisType": "tisHigh"})]
                theTRECSTool.trecsExecInfo.appendToTrace("No Break Point Segments exist within 6 hr (TODO change to NOW) OR")
                theTRECSTool.trecsExecInfo.appendToTrace("  there is likely NO danger to the AOR. So ...")
                theTRECSTool.trecsExecInfo.appendToTrace("  Created Information Statement (TS.S.High) with potential danger.")
                self.phensigsCreated.append("TS.S")
        return eventDicts

    def assertActions(self, theTRECSTool, eventSet):
        assertive = True
        for phensig in self.phensigsCreated:
            assertive = assertive and self.assertHazardEvent(eventSet, "AkBcWc", phensig)
        return assertive

'''
PROCEDURES 6.1.5 - US / Canadian Atlantic and Gulf of America
'''


class Proc615Categ1(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(0, 4.0))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # Process Routinely
        wwaAreaDictList = []
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc615Categ2a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.9) and theTRECSTool.isWithinKmOfCoast(150))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("EcGc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.S")


class Proc615Categ2b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(4.0, 4.9) and theTRECSTool.isGreaterThanKmFromCoast(150))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
         # Process Routinely
        wwaAreaDictList = []
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc615Categ3a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 5.9) and
                theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return []

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc615Categ3b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.0, 5.9) and
                not theTRECSTool.isFarOnshoreKm(100))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("EcGc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.S")


class Proc615Categ4(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.0, 6.4) or
                (theTRECSTool.isOnshoreWithinKm(400) and
                    ((theTRECSTool.isInMagnitudeRange(6.5, 7.5) and theTRECSTool.isFarOnshoreKm(30)) or
                     (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and theTRECSTool.isFarOnshoreKm(50)) or
                     (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isFarOnshoreKm(80)))))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("EcGc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.S")


class Proc615Categ5(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isGulfAmericaProcRegion() and
                theTRECSTool.isInMagnitudeRange(6.5) and
                (theTRECSTool.isOffshore() or
                    ((theTRECSTool.isInMagnitudeRange(6.5, 7.5) and theTRECSTool.isOnshoreWithinKm(30)) or
                     (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and theTRECSTool.isOnshoreWithinKm(50)) or
                     (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isOnshoreWithinKm(80)))))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        wwaAreaDictList = []
        breakPointSegmentNames = ["Brownsville to Baffin Bay", "Baffin Bay to Port OConnor",
                                  "Port OConnor to High Island", "High Island to Morgan City",
                                  "Morgan City to The Miss./Alabama Border",
                                  "The Miss./Alabama Border to Destin", "Destin to Suwannee River",
                                  "Suwannee River to Bonita Beach", "Bonita Beach to Flamingo",
                                  "Flamingo to Ocean Reef"]
        segmentQueryResults = theTRECSTool.amu.getBreakPointSegmentsBySegmentNames(breakPointSegmentNames)
        warningGeom = theTRECSTool.amu.getUnionedGeometryFromQueryResults(segmentQueryResults)
        attrDict = {
            "wwaLocationCoverage": "segmentAreas",
            "hazardLocations": breakPointSegmentNames,
            }
        wwaAreaDictList.append(theTRECSTool.recommendEvent("EcGc", "TS.W", warningGeom, attrDict))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.W")


class Proc615Categ6(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isGulfStLawProcRegion() and
                theTRECSTool.isInMagnitudeRange(6.5) and
                (theTRECSTool.isOffshore() or
                    ((theTRECSTool.isInMagnitudeRange(6.5, 7.5) and theTRECSTool.isOnshoreWithinKm(30)) or
                     (theTRECSTool.isInMagnitudeRange(7.6, 7.8) and theTRECSTool.isOnshoreWithinKm(50)) or
                     (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isOnshoreWithinKm(80)))))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        wwaAreaDictList = []
        specProcNames = ["Gulf of Saint Lawrence"]
        segmentQueryResults = theTRECSTool.amu.getBreakPointSegmentsBySegmentNames(specProcNames)
        warningGeom = theTRECSTool.amu.getUnionedGeometryFromQueryResults(segmentQueryResults)
        attrDict = {
            "wwaLocationCoverage": "specialAreas",
            "hazardLocations": specProcNames,
            }
        wwaAreaDictList.append(theTRECSTool.recommendEvent("EcGc", "TS.W", warningGeom, attrDict))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.W")


class Proc615Categ7(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isECoastOrECanProcRegion() and
                theTRECSTool.isInMagnitudeRange(6.5, 7.5) and
                (theTRECSTool.isOffshore() or theTRECSTool.isOnshoreWithinKm(30)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return theTRECSTool.createEventDictsByDistanceCriteria({"TS.W": [0, 250]})

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.W")


class Proc615Categ8(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isECoastOrECanProcRegion() and
                theTRECSTool.isInMagnitudeRange(7.6, 7.8) and
                (theTRECSTool.isOffshore() or theTRECSTool.isOnshoreWithinKm(50)))

    def applyActions(self, theTRECSTool):
        criteriaDict = {
            "TS.W": [0, 500],
            "TS.Y": [500, 1000]
            }
        eventDicts = theTRECSTool.createEventDictsByDistanceCriteria(criteriaDict)
        super().appendToTrace(theTRECSTool)
        return eventDicts

    def assertActions(self, theTRECSTool, eventSet):
        return (self.assertHazardEvent(eventSet, "EcGc", "TS.W") and self.assertHazardEvent(eventSet, "EcGc", "TS.Y"))


class Proc615Categ9(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isECoastOrECanProcRegion() and
                theTRECSTool.isInMagnitudeRange(7.9) and
                (theTRECSTool.isOffshore() or theTRECSTool.isOnshoreWithinKm(80)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return theTRECSTool.createWarningToSomeRangeAndWatchForRemainingAOR(1000, "EcGc")

    def assertActions(self, theTRECSTool, eventSet):
        return (self.assertHazardEvent(eventSet, "EcGc", "TS.W") and self.assertHazardEvent(eventSet, "EcGc", "TS.A"))

'''
PROCEDURES 6.1.5.1 - Caribbean
'''


class Proc6151Categ1(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(0, 5.9))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # Process Routinely
        wwaAreaDictList = []
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc6151Categ2(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.0, 7.8) or
                (theTRECSTool.isInMagnitudeRange(7.9) and
                 (theTRECSTool.isDeepKm(100) or theTRECSTool.isFarOnshoreKm(80))))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("EcGc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.S")


class Proc6151Categ3(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.9) and theTRECSTool.isShallowKm(100) and
                 (theTRECSTool.isOffshore() or theTRECSTool.isOnshoreWithinKm(80)))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("EcGc", "TS.S", hazardAttributes={"tisType": "tisHigh"})]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEventAndAttribute(eventSet, "EcGc", "TS.S", "tisType", "tisHigh")

'''
PROCEDURES 6.1.6 - Atlantic non-AOR
'''


class Proc616Categ1a(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(0, 5.7))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # Process Routinely
        wwaAreaDictList = []
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertEmptyHazardEvents(eventSet)


class Proc616Categ1b(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(5.8, 6.4))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        # OM
        wwaAreaDictList = []
        wwaAreaDictList.append(theTRECSTool.recommendEvent("EcGc", "TS.ObservatoryMessage"))
        return wwaAreaDictList

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.ObservatoryMessage")


class Proc616Categ2(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(6.5, 7.8))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("EcGc", "TS.S")]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEvent(eventSet, "EcGc", "TS.S")


class Proc616Categ3(TsunamiRecommenderCommon.TRECSPythonExecCateg):

    def conditionsSatisfied(self, theTRECSTool):
        return (theTRECSTool.isInMagnitudeRange(7.9))

    def applyActions(self, theTRECSTool):
        super().appendToTrace(theTRECSTool)
        return [theTRECSTool.recommendEvent("EcGc", "TS.S", hazardAttributes={"tisType": "tisHigh"})]

    def assertActions(self, theTRECSTool, eventSet):
        return self.assertHazardEventAndAttribute(eventSet, "EcGc", "TS.S", "tisType", "tisHigh")

