# *** Override behavior of TsunamiRecommender.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
Tsunami Recommender (T-RECS) (NTWC)

@see: Site-level overrides of this file for implementation
@since: June 2022
@author: GSL Hazard Services Team
"""
import logging, UFStatusHandler
import TsunamiRecommenderCommon


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()
        self.logger = logging.getLogger("TsunamiRecommender")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsl.common.atoms.hazardservices",
            "TsunamiRecommender", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the recommender, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiRecommender",
            "author": "GSL",
            "version": 1.0,
            "description": ("Creates Tsunami hazard events based on criteria from an input "
                            "physical event and tsunami forecast information")
            }
        return metaDict


def __str__(self):
    return "TsunamiRecommender"
