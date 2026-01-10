# *** Override behavior of TIB_Verbal_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Verbal Formatter for Tsunami Information Statement products
    @since: July 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMessageMethods
import NWS_Base_Formatter
from com.raytheon.uf.common.hazards.productgen import ProductUtils


class Format(NWS_Base_Formatter.Format):

    def initialize(self, productDict):
        '''
        @summary: Create instance variables visible to all methods
        in this class
        @param productDict: The product-level dictionary
        @return: New instance variables (i.e., self.hazardProductParts)
        '''
        super(Format, self).initialize(productDict)

        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()

        self.fieldNameSuffix = ""
        self.productRegion = productDict.get("productRegion")
        self.sectionDict = self.agu.getSectionDict(productDict)

    def execute(self, productDict):
        '''
        @summary: Creates the message text for this formatter
        based on the contents of the product dictionary created
        by the product generator
        @param productDict: The product-level dictionary
        @return: A list of strings, each containing a block of
        text for a single message
        '''
        self.initialize(productDict)
        legacyText = self.createTextProduct()
        legacyText = ProductUtils.wrapLegacy(legacyText)
        return [legacyText]

    def recordGeneratedText(self, productDict, textProductList):
        '''
        @summary: Write the text product(s) from this formatter to a physical file
        @param productDict: The product-level dictionary
        @param textProductList: A list of text product(s) created by the formatter
        @return: None
        '''
        if self.issueFlag:
            AtomsDisseminationUtilities.AtomsDisseminationUtilities().writeAtomsFile(productDict, textProductList, self.__module__)

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary
        '''
        self.tisType = "tisLow"
        eventDicts = self.agu.getAllEventDicts(self.productDict)
        for eventDict in eventDicts:
            tisType = eventDict.get("tisType")
            if tisType:
                self.tisType = tisType
                break
        return ["fullText"]

    def getProductValidationChecks(self):
        '''
        @summary: A optional list of product validators that will be called to
        verify the message contents are accurate
        @return: A list of validation python files, each one will need to be
        imported at the top of this file
        '''
        return []

    def fullText(self, productDict):
        eventDict = self.agu.getAllEventDicts(self.sectionDict)[0]
        text = ""
        updateStr = self.sectionDict.get("updatesBullet")
        if updateStr is not None:
            text += f"{updateStr}\n\n"

        text += "This is a Tsunami Information Statement"

        if self.tisType != "tisLow":
            regionName = self.alu.getProductRegionNameFromAbbreviation(self.productRegion)
            text += f" for {regionName}"

        paramString = self.amm.getPhysicalEventDescriptionString(eventDict, "")
        text += f".\n\n{paramString}\n\n"

        warningCenter = self.amm.getWarningCenterByEventDict(eventDict)
        phraseList = []
        if self.tisType == "tisLow":
            phraseList += [
                ("No tsunami is expected. This will be the only message issued for this event "
                 "unless additional information becomes available."),
                ]
        elif self.tisType == "tisHigh":
            phraseList += [
                ("Earthquakes of this size are known to generate tsunamis potentially "
                 "dangerous to coasts outside the source region."),
                (f"The {warningCenter} is analyzing the event to determine the level of "
                 "danger. More information will be issued as it becomes available."),
                ("Messages will be issued hourly to keep you informed of the progress "
                 "of this event."),
                ]
        elif self.tisType == "tisFinal":
            phraseList += [(f"This will be the final {warningCenter} statement issued "
                            "for this event unless additional information becomes available.")]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase, "", "")
            text += f"{wrappedPhrase}\n\n"

        if self.tisType in ["tisHigh", "tisFinal"]:
            eventParameters = self.sectionDict.get("physicalEventParametersBullet")
            text += ("*** -------------- Stop Reading Here ---------------\n\n"
                    f"{eventParameters}")
        return text
