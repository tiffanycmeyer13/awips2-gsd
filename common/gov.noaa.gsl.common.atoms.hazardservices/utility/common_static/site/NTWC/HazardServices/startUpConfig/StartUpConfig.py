# NTWC site override file of StartUpConfig.py

StartUpConfig = {
    "defaultSettings": "Tsunami",
    "national": True,
    "hazardDetailTabText": ["eventID", "hazardType"],
    # Turn off features for other hazard categories
    "hydrology_features": {
        "practice_mode": False,
        "test_mode": False,
        "operational_mode": False,
        },
    "shortFuse_features": {
        "practice_mode": False,
        "test_mode": False,
        "operational_mode": False,
        },
    "nonPrecip_features": {
        "practice_mode": False,
        "test_mode": False,
        "operational_mode": False,
        },
    "winter_features": {
        "practice_mode": False,
        "test_mode": False,
        "operational_mode": False,
        },
    "marine_features": {
        "practice_mode": False,
        "test_mode": False,
        "operational_mode": False,
        },
    "fireWeather_features": {
        "practice_mode": False,
        "test_mode": False,
        "operational_mode": False,
        },
    "aviation_features": {
        "practice_mode": False,
        "test_mode": False,
        "operational_mode": False,
        },
    "tsunami_features": {
        "practice_mode": True,
        "test_mode": True,
        "operational_mode": True,
        },
    "unassociated_features": {
        "settings": {"AllHazards": False, "AllHazards_NonRiver": False},
        },
}
