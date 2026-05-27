# *** Override behavior of ThreatDB.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
@see: Site-level overrides of this file for implementation
@since: Sep 2023
@author: GSL Hazard Services Team
"""
import AbstractThreatDB


class ThreatDB(AbstractThreatDB.AbstractThreatDB):

    def __init__(self):
        super(ThreatDB, self).__init__()

    def getThreatDBConfigDict(self):
        return {}
