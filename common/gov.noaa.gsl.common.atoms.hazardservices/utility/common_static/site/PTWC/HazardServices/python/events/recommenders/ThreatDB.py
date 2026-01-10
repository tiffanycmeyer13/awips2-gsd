# *** Override behavior of ThreatDB.py ***
# -- Override ability: Class-based
# -- Levels: All
"""
@since: Sep 2023
@author: GSL Hazard Services Team
"""
import AbstractThreatDB


class ThreatDB(AbstractThreatDB.AbstractThreatDB):

    def __init__(self):
        super(ThreatDB, self).__init__()

    def getThreatDBConfigDict(self):
        threatDBConfig = {
            "As-Warning-14.00S-176.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.00S-175.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.00S-175.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.00S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.00S-174.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.00S-173.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-176.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-175.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-175.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-174.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-173.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-173.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-14.50S-172.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-176.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-175.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-175.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-174.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-173.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-173.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-172.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.00S-172.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-176.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-175.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-175.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-174.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-173.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-173.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-172.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-172.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-15.50S-171.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-176.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-175.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-175.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-174.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-173.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-173.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-172.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-172.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.00S-171.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.50S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.50S-174.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.50S-173.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.50S-173.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.50S-172.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.50S-172.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-16.50S-171.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.00S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.00S-174.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.00S-173.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.00S-173.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.00S-172.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.00S-172.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.00S-171.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-175.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-174.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-173.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-173.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-172.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-172.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-17.50S-171.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-175.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-174.50W": {
                "minMagnitude": 8.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-174.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-173.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-173.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-172.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-172.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.00S-171.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-175.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-174.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-174.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-173.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-173.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-172.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-172.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-18.50S-171.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-175.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-175.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-174.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-174.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-173.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-173.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-172.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.00S-172.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-175.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-175.00W": {
                "minMagnitude": 8.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-174.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-174.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-173.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-173.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-172.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-19.50S-172.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-176.00W": {
                "minMagnitude": 8.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-175.50W": {
                "minMagnitude": 8.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-175.00W": {
                "minMagnitude": 8.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-174.50W": {
                "minMagnitude": 8.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-174.00W": {
                "minMagnitude": 8.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-173.50W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-173.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Warning-20.00S-172.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.00S-176.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.00S-175.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.00S-175.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.00S-174.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.00S-174.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.00S-173.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-176.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-175.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-175.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-174.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-174.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-173.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-173.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-14.50S-172.50W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-176.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-175.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-175.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-174.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-174.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-173.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-173.00W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-172.50W": {
                "minMagnitude": 6.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.00S-172.00W": {
                "minMagnitude": 6.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-176.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-175.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-175.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-174.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-174.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-173.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-173.00W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-172.50W": {
                "minMagnitude": 6.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-172.00W": {
                "minMagnitude": 6.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-15.50S-171.50W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-176.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-175.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-175.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-174.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-174.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-173.50W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-173.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-172.50W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-172.00W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.00S-171.50W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.50S-174.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.50S-174.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.50S-173.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.50S-173.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.50S-172.50W": {
                "minMagnitude": 7.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.50S-172.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-16.50S-171.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.00S-174.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.00S-174.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.00S-173.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.00S-173.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.00S-172.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.00S-172.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.00S-171.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-175.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-174.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-174.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-173.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-173.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-172.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-172.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-17.50S-171.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-175.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-174.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-174.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-173.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-173.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-172.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-172.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.00S-171.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-175.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-174.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-174.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-173.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-173.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-172.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-172.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-18.50S-171.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-175.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-175.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-174.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-174.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-173.50W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-173.00W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-172.50W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.00S-172.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-175.50W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-175.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-174.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-174.00W": {
                "minMagnitude": 8.0,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-173.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-173.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-172.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-19.50S-172.00W": {
                "minMagnitude": 7.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-176.00W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-175.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-175.00W": {
                "minMagnitude": 8.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-174.50W": {
                "minMagnitude": 8.2,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-174.00W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-173.50W": {
                "minMagnitude": 7.8,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-173.00W": {
                "minMagnitude": 7.6,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            },
            "As-Advisory-20.00S-172.50W": {
                "minMagnitude": 7.4,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": ["American Samoa"],
                    }
                ]
            }
        }
        return threatDBConfig
