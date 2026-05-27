# *** Override behavior of TsunamiMessageTool.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
Tsunami Message Tool (BASE)

The TsunamiMessageTool displays a menu of physical event types, a list of active physical
event Id, Tsunami message types and locations. This will create Tsunami information statement,
Tsunami conference call and other Tsunami messages.

@see: Site-level overrides of this file for implementation
@since: April 2022
@author: GSL Hazard Services Team
"""

import logging, UFStatusHandler
import TsunamiRecommenderCommon


class Recommender(TsunamiRecommenderCommon.TsunamiRecommenderCommon):

    def __init__(self):
        super(Recommender, self).__init__()
        self.logger = logging.getLogger("TsunamiMessageTool")
        self.logger.addHandler(UFStatusHandler.UFStatusHandler(
            "gov.noaa.gsl.common.atoms.hazardservices", "TsunamiMessageTool", level=logging.INFO))
        self.logger.setLevel(logging.INFO)

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the tool, such as author,
        description, and script version.
        @return: A dictionary
        '''
        metaDict = {
            "toolName": "TsunamiMessageTool",
            "author": "GSL",
            "version": "1.0",
            "description": "Creates hazard events for selected physical event and message types/location"
            }
        return metaDict


def __str__(self):
    return "Tsunami Message Tool"
