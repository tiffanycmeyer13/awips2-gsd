# *** Override behavior of CommonSettings.py ***
# -- Override ability: Incremental
# -- Levels: All

CommonSettings = {
    # Definitions for tools. The key must be the tool's
    # "toolName" which is file name without the ".py" extension.
    # The "displayName" is shown in the HSC's REC menu to select
    # the tool.
    # "toolType" is either USER_TOOL (default value) or
    # SYSTEM_TOOL. The user tool is one that can
    # be run directly by the user. The system tool  must have
    # code to support it and cannot be directly run by the user.
    "toolDefinitions": {
        "AtomsTestTool": {
            "displayName": "Atoms Test Tool",
            "toolType": "USER_TOOL"
            },
        "ModifyTsunamiTool": {
            "displayName": "Modify Tsunami Tool",
            "toolType": "USER_TOOL"
            },
        "ObservatoryMessageTool": {
            "displayName": "Observatory Message Tool (OMT)",
            "toolType": "USER_TOOL"
            },
        "ThreatDB": {
            "displayName": "",
            "toolType": "SYSTEM_TOOL"
            },
        "TsunamiCommTestMessageTool": {
            "displayName": "Tsunami Communications Test Message Tool (TCTMT)",
            "toolType": "USER_TOOL"
            },
        "TsunamiEventChronologyTool": {
            "displayName": "Tsunami Event Chronology Tool (TECT)",
            "toolType": "USER_TOOL"
            },
        "TsunamiEventUpdateNotificationTool": {
            "displayName": "Tsunami Event Update Notification Tool",
            "toolType": "USER_TOOL"
            },
        "TsunamiMessageRetransmitTool": {
            "displayName": "Tsunami Message Retransmit Tool",
            "toolType": "USER_TOOL"
            },
        "TsunamiMessageTool": {
            "displayName": "Tsunami Message Tool (TMT)",
            "toolType": "USER_TOOL"
            },
        "TsunamiRecommender": {
            "displayName": "Tsunami Recommender (T-RECS)",
            "toolType": "USER_TOOL"
            },
        "TsunamiRecommenderCommon": {
            "displayName": "",
            "toolType": "SYSTEM_TOOL"
            },
        },

    # Possible Sites -- Hazards from these sites can be selected to be visible in the Hazard Services display.
    #    They will appear in the Settings dialog as a check list from which to choose.
    #    The default when no sites is the current site (WFO).
    # Example:  "possibleSites": ["BOU","PUB","GJT","CYS","OAX","FSD","DMX","GID","EAX","TOP","RAH"],
    "possibleSites": ["PTWC", "NTWC"],

    # Visible Sites -- Hazards from these sites will be, by default, visible in the Hazard Services display
    #    The default when no sites is the current site (WFO).
    # Example:  "visibleSites":  ["BOU", "OAX"]
    "visibleSites": ["PTWC", "NTWC"],
}
