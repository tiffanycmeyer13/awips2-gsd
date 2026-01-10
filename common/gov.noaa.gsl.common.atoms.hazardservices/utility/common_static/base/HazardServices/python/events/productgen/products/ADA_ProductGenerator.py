# *** Override behavior of ADA_ProductGenerator.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Product Generator for the Tsunami Conference Call products.

    @author: GSL Hazard Services Team
    @version 1.0
    @since February 2023

'''

import NWS_Base_Generator
import TimeUtil


class Product(NWS_Base_Generator.Product):

    def __init__(self):
        super(Product, self).__init__()
        # Used by the VTECEngineWrapper to access the productGeneratorTable
        self.productGeneratorName = "ADA_ProductGenerator"

    def initialize(self):
        super(Product, self).initialize()
        self.productID = "ADA"
        self.productCategory = "ADA"
        self.productName = "Tsunami Conference Call"
        self.productLabel = "Tsunami Conference Call"

        # Polygon-based, so locations listed will be limited to within the polygon rather than county area
        self.polygonBased = False
        self.vtecProduct = False

    def getPurgeHours(self, hazardType):
        '''
        @summary: Get the purge hours to use for events with the given hazard type. This is the
        number of hours past issuance that the event's expiration time should be.
        @param hazardType: The hazard type (e.g., FA.W) to determine purge hours for
        @return: The purge hours, or -1.0 to indicate that the purge time should
        match the event's end time
        '''
        return -1.0

    def defineScriptMetadata(self):
        '''
        @summary: Defines basic information about the product generator, such as author,
        description, and script version.
        @return: A dictionary
        '''
        return {
            "author": "GSL",
            "description": "Product generator for the Tsunami Conference Call",
            "version": "1.0",
            }

    def defineDialog(self, eventSet):
        '''
        @return: dialog definition to solicit user input before running tool
        '''
        return {}

    def execute(self, eventSet, dialogInputMap):
        self.initialize()

        # Extract information for execution
        self.getVariables(eventSet, dialogInputMap)
        eventSetAttributes = eventSet.getAttributes()

        if not self.inputHazardEvents:
            return [], []

        productDicts, hazardEvents = self.makeNonVtecProducts_FromHazardEvents(self.inputHazardEvents,
                                                                               eventSetAttributes)
        return productDicts, hazardEvents

    def getMetadata(self):
        return self.metadata

    def createProductLevelProductDictionaryData(self, productDict, hazardEvents):
        '''
        @summary: Add additional attributes to the product-level of the product
        dictionary
        @param productDict: The product dictionary
        @param hazardEvents: A list of hazard events brought into product generation
        @return: An updated productDict in memory
        '''
        hazardEvent = hazardEvents[0]
        productDict["productRegion"] = hazardEvent.get("productRegion")
        productDict["customId"] = hazardEvent.get("customId")
        productDict["callLocation"] = hazardEvent.get("callLocation")
        productDict["callTime"] = hazardEvent.get("callTime")
