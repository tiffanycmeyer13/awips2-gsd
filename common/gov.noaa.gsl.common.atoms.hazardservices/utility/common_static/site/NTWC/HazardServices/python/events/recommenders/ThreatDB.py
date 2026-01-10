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
            "Augustine_Volcano_SP": {
                "minMagnitude": 4.5,
                "maxMagnitude": 7.0,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Lower Cook Inlet Region south of Kalgin Island"
                        ]
                    },
                ]
            },
            "Barry_Arm_Landslide_SP": {
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance"
                        ]
                    }
                ]
            },
            "Cook_Inlet_SP": {
                "minMagnitude": 7.1,
                "maxMagnitude": 7.5,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Lower Cook Inlet Region south of Kalgin Island",
                            "Northwest Kenai Peninsula",
                            "Upper Cook Inlet",
                        ]
                    },
                ]
            },
            "DBRegion007aE": {
                "minMagnitude": 7.1,
                "maxMagnitude": 7.8,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu",
                        ]
                    }
                ]
            },
            "DBRegion007aW": {
                "minMagnitude": 7.1,
                "maxMagnitude": 7.8,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu",
                        ]
                    }
                ]
            },
            "DBRegion007bE": {
                "minMagnitude": 7.8,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu",
                        ]
                    }
                ]
            },
            "DBRegion007bW": {
                "minMagnitude": 7.8,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu",
                        ]
                    }
                ]
            },
            "DBRegion008": {
                "minMagnitude": 7.1,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Bristol Bay and the Pribilof Islands",
                        ]
                    }
                ]
            },
            "DBRegion009": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.6,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "Strait of Georgia",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "Puget Sound"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass"
                        ]
                    }
                ]
            },
            "DBRegion010": {
                "minMagnitude": 8.6,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "Strait of Georgia",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "Puget Sound"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion011": {
                "minMagnitude": 8.4,
                "maxMagnitude": 8.8,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport"
                        ]
                    }
                ]
            },
            "DBRegion012": {
                "minMagnitude": 8.8,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion013": {
                "minMagnitude": 8.8,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point"
                        ]
                    }
                ]
            },
            "DBRegion014": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.4,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line"
                        ]
                    }
                ]
            },
            "DBRegion015": {
                "minMagnitude": 8.4,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion016": {
                "minMagnitude": 7.6,
                "maxMagnitude": 8.4,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino"
                        ]
                    }
                ]
            },
            "DBRegion017": {
                "minMagnitude": 8.4,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion018": {
                "minMagnitude": 7.6,
                "maxMagnitude": 8.4,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line"
                        ]
                    }
                ]
            },
            "DBRegion019": {
                "minMagnitude": 8.4,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion020": {
                "minMagnitude": 7.6,
                "maxMagnitude": 8.4,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head"
                        ]
                    }
                ]
            },
            "DBRegion021": {
                "minMagnitude": 8.4,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion022": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border"
                        ]
                    }
                ]
            },
            "DBRegion023": {
                "minMagnitude": 8.2,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion024": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.3,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion025": {
                "minMagnitude": 8.3,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion026": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Wash./BC Border to North Vancouver Island"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    }
                ]
            },
            "DBRegion027": {
                "minMagnitude": 8.2,
                "maxMagnitude": 8.6,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass"
                        ]
                    }
                ]
            },
            "DBRegion028": {
                "minMagnitude": 8.6,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion029": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.4,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion030": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.3,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion031": {
                "minMagnitude": 8.3,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    }
                ]
            },
            "DBRegion032": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion034": {
                "minMagnitude": 8.2,
                "maxMagnitude": 8.6,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass"
                        ]
                    }
                ]
            },
            "DBRegion036": {
                "minMagnitude": 8.6,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass"
                        ]
                    }
                ]
            },
            "DBRegion038": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion039": {
                "minMagnitude": 8.2,
                "maxMagnitude": 8.8,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass"
                        ]
                    }
                ]
            },
            "DBRegion040": {
                "minMagnitude": 8.8,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    }
                ]
            },
            "DBRegion041": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion042": {
                "minMagnitude": 8.2,
                "maxMagnitude": 8.8,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    }
                ]
            },
            "DBRegion043": {
                "minMagnitude": 8.8,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    }
                ]
            },
            "DBRegion044": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass"
                        ]
                    }
                ]
            },
            "DBRegion045": {
                "minMagnitude": 8.2,
                "maxMagnitude": 8.8,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance"
                        ]
                    }
                ]
            },
            "DBRegion046": {
                "minMagnitude": 8.8,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance"
                        ]
                    }
                ]
            },
            "DBRegion048": {
                "minMagnitude": 8.2,
                "maxMagnitude": 8.8,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island",
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance"
                        ]
                    }
                ]
            },
            "DBRegion049": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Amchitka Pass to Attu"
                        ]
                    }
                ]
            },
            "DBRegion050": {
                "minMagnitude": 8.2,
                "maxMagnitude": 8.5,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Amchitka Pass to Attu"
                        ]
                    },
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The Cal./Mexico Border to Orange/San Diego Line",
                            "Orange/San Diego Line to Rincon Point",
                            "Rincon Point to Point Conception",
                            "Point Conception to Ragged Point",
                            "Ragged Point to Davenport",
                            "Davenport to Gualala River",
                            "Gualala River to Mendo/Hum County Line",
                            "Mendo/Hum County Line to Cape Mendocino",
                            "Cape Mendocino to Humboldt/Del Norte Line",
                            "Humboldt/Del Norte Line to The Oregon/Cal. Border",
                            "The Oregon/Cal. Border to Douglas/Lane Line",
                            "Douglas/Lane Line to Cascade Head",
                            "Cascade Head to The Oregon/Wash. Border",
                            "The Oregon/Wash. Border to The Wash./BC Border",
                            "The Wash./BC Border to North Vancouver Island"
                        ]
                    }
                ]
            },
            "DBRegion051": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.2,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass"
                        ]
                    }
                ]
            },
            "DBRegion052": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.0,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass"
                        ]
                    }
                ]
            },
            "DBRegion053": {
                "minMagnitude": 7.9,
                "maxMagnitude": 8.0,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision"
                        ]
                    },
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass"
                        ]
                    }
                ]
            },
            "DBRegion054E": {
                "minMagnitude": 7.1,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Norton Sound/Saint Lawrence Island/Western AK Coast",
                        ]
                    },
                ]
            },
            "DBRegion054W": {
                "minMagnitude": 7.1,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Norton Sound/Saint Lawrence Island/Western AK Coast",
                        ]
                    },
                ]
            },
            "DBRegion055": {
                "minMagnitude": 7.1,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Western AK from Cape Prince of Wales to Wainwright",
                        ]
                    },
                ]
            },
            "DBRegion056": {
                "minMagnitude": 7.1,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.Y",
                        "hazardAreas": [
                            "Northern AK Border from Wainwright to the Canadian Border",
                        ]
                    },
                ]
            },
            "DBRegion057": {
                "minMagnitude": 6.5,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Gulf of Saint Lawrence",
                        ]
                    },
                ]
            },
            "DBRegion058": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "North Vancouver Island to The BC/Alaska Border",
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                        ]
                    },
                ]
            },
            "DBRegion059": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "The BC/Alaska Border to Cape Decision",
                            "Cape Decision to Salisbury Sound",
                            "Salisbury Sound to Cape Fairweather",
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                        ]
                    },
                ]
            },
            "DBRegion060": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Amchitka Pass to Attu",
                        ]
                    },
                ]
            },
            "DBRegion061": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Amchitka Pass to Attu",
                        ]
                    },
                ]
            },
            "DBRegion062": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Amchitka Pass to Attu",
                        ]
                    },
                ]
            },
            "DBRegion063": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Amchitka Pass to Attu",
                        ]
                    },
                ]
            },
            "DBRegion064": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu",
                        ]
                    },
                ]
            },
            "DBRegion065": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                            "Amchitka Pass to Attu",
                        ]
                    },
                ]
            },
            "DBRegion066": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                            "Samalga Pass to Amchitka Pass",
                        ]
                    },
                ]
            },
            "DBRegion067": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                            "Unimak Pass to Samalga Pass",
                        ]
                    },
                ]
            },
            "DBRegion069": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 800,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                            "Chignik Bay to Unimak Pass",
                        ]
                    },
                ]
            },
            "DBRegion070": {
                "minMagnitude": 7.9,
                "maxMagnitude": 9.9,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.A",
                        "hazardAreas": [
                            "Cape Fairweather to Cape Suckling",
                            "Cape Suckling to Hinchinbrook Entrance",
                            "Hinchinbrook Entrance to Kennedy Entrance",
                            "Kennedy Entrance to Chignik Bay",
                        ]
                    },
                ]
            },
            "Juan_de_Fuca_SP": {
                "minMagnitude": 7.1,
                "maxMagnitude": 7.5,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Southern Strait of Juan de Fuca",
                            "Northern Strait of Juan de Fuca",
                            "Island County",
                            "Possession Sound",
                            "Western Skagit and Northwestern Snohomish Counties",
                            "San Juan Islands",
                            "Western Whatcom County",
                        ]
                    },
                ]
            },
            "Puget_Sound_SP": {
                "minMagnitude": 7.1,
                "maxMagnitude": 7.5,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Puget Sound",
                            "Island County",
                            "Possession Sound",
                            "Western Skagit and Northwestern Snohomish Counties",
                        ]
                    },
                ]
            },
            "SF_Bay_SP": {
                "minMagnitude": 7.1,
                "maxMagnitude": 7.5,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "San Francisco Bay",
                            "Suisun Bay",
                        ]
                    },
                ]
            },
            "Strait_of_Georgia_SP": {
                "minMagnitude": 7.1,
                "maxMagnitude": 7.5,
                "maxDepthKm": 100,
                "hazardTypes": [
                    {
                        "hazardType": "TS.W",
                        "hazardAreas": [
                            "Strait of Georgia",
                            "San Juan Islands",
                            "Western Skagit and Northwestern Snohomish Counties",
                            "Western Whatcom County",
                        ]
                    },
                ]
            },

        }
        return threatDBConfig
