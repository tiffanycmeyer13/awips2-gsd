# *** Override behavior of TsunamiCommTestMessageTool.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
Tsunami Comms Test Message Tool (BASE)

The TsunamiCommTestMessageTool allows for creation of tsunami communications test messages.

@see: Site-level overrides of this file for implementation
@since: August 2025
@author: GSL Hazard Services Team
"""
import logging, UFStatusHandler
import TsunamiRecommenderCommon


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()
        self.logger = logging.getLogger("TsunamiCommTestMessageTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsl.common.atoms.hazardservices",
            "TsunamiCommTestMessageTool", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiCommTestMessageTool",
            "author": "GSL",
            "version": "1.0",
            "description": "Creates Communication Test hazard events"
            }
        return metaDict


def __str__(self):
    return "TsunamiCommTestMessageTool"
