# *** Override behavior of Tsunami.py ***
# -- Override ability: Incremental
# -- Levels: All

Tsunami = {
    "displayName": "Tsunami",
    "visibleTypes": ["_override_replace_",
        "TS.S",
        "TS.CommunicationTest",
        "TS.ConferenceCall",
        "TS.ThreatMessage",
        "TS.W",
        "TS.Y",
        "TS.A",
        ],

    "defaultTimeDisplayDuration": 86400000,
    "defaultCategory": "Tsunami",
    "defaultDuration": 28800000,

    "possibleSites": [ "_override_replace_",
        "NTWC",
        "PTWC"
        ],
    "visibleSites": [ "_override_replace_",
        "NTWC",
        "PTWC"
        ],

    "visibleColumns": [
        "Event ID",
        "Lock\nStatus",
        "Hazard Type",
        "Physical\nEvent Type",
        "Physical\nEvent ID",
        "Product\nRegion",
        "Status",
        "Start Time",
        "End Time",
        "VTEC\nActions",
        ],

    "visibleStatuses": [],

    # Any columns specific to this settings that don't
    # belong in CommonSettings.py. Note this list is
    # added to the definitions from CommonSettings.
    "columnDefinitions": {},

    "possibleColumns": [
        "PILs",
        "UGCs",
        "Lock\nStatus",
        "Start Time",
        "VTEC\nActions",
        "Site ID",
        "Expiration Time",
        "SubStatus",
        "End Time",
        "Status",
        "Hazard Type",
        "Phen",
        "User Name",
        "Issue Time",
        "Creation Time",
        "Event ID",
        "VTEC Mode",
        "Sig",
        "Workstation",
        "Time to\nExpiration",
        "ETNs",
        "Physical\nEvent Type",
        "Physical\nEvent ID",
        "Product\nRegion",
        ],

    "rowSortOrder": ["_override_replace_",
        {"name": "Event ID", "sortDir": "ASC"},
        {"name": "Issue Time", "sortDir": "ASC"},
        ],

    "toolbarToolNames": ["_override_replace_",
        "ObservatoryMessageTool",
        "TsunamiEventChronologyTool",
        "TsunamiMessageTool",
        "TsunamiRecommender",
        "TsunamiMessageRetransmitTool",
        "TsunamiCommTestMessageTool",
        "AtomsTestTool"
        ],

    # The toolbar buttons to appear in the Console toolbar to directly
    # invoke tools.
    "toolbarToolButtons": ["_override_replace_",
        {"name": "AtomsTestTool", "iconPath": "HazardServices/settings/config/images/atomsTestTool.png"},
        {"name": "TsunamiRecommender", "iconPath": "HazardServices/settings/config/images/TsunamiRecommender.png"},
        {"name": "TsunamiMessageTool", "iconPath": "HazardServices/settings/config/images/TsunamiMessageTool.png"},
        {"name": "ObservatoryMessageTool", "iconPath": "HazardServices/settings/config/images/ObservatoryMessageTool.png"},
        {"name": "TsunamiCommTestMessageTool", "iconPath": "HazardServices/settings/config/images/TsunamiCommTestMessageTool.png"},
        ],

    "selectedMaps": [],
}
