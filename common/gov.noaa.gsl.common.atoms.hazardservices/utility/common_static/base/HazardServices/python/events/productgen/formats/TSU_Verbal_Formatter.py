# *** Override behavior of TSU_Verbal_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Verbal formatter for TSU products
    @since: July 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMessageMethods
import NWS_Base_Formatter
import TextProductCommon
from com.raytheon.uf.common.hazards.productgen import ProductUtils


class Format(NWS_Base_Formatter.Format):

    def initialize(self, productDict):
        '''
        @summary: Create instance variables visible to all methods
        in this class
        @param productDict: The product-level dictionary
        @return: New instance variables (i.e., self.agu)
        '''
        super(Format, self).initialize(productDict)

        self.agu = AtomsGeneralUtilities.AtomsGeneralUtilities()
        self.alu = AtomsLocationUtilities.AtomsLocationUtilities()
        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.tpc = TextProductCommon.TextProductCommon()

        self.fieldNameSuffix = f"_{productDict.get('productLabel')}"

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
        text = self.fullText(productDict)
        text = ProductUtils.wrapLegacy(text)
        return [text]

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
        return []

    def getProductValidationChecks(self):
        '''
        @summary: A optional list of product validators that will be called to
        verify the message contents are accurate
        @return: A list of validation python files, each one will need to be
        imported at the top of this file
        '''
        return []

    ######################################################
    #  Product Part Methods
    ######################################################
    def fullText(self, productDict):
        '''
        @summary: Build a text block that will be read over the phone
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        phraseList = []
        if self.agu.areAllSegmentsEnding(productDict):
            eventDict = self.agu.getAllEventDicts(productDict)[0]
            typeText = ""
            sigs = self.agu.getSigList(productDict, True)
            typeList = []
            if "W" in sigs:
                typeList.append("warning")
            if "Y" in sigs:
                typeList.append("advisory")
            if "A" in sigs:
                typeList.append("watch")
            if typeList:
                if len(typeList) < 2:
                    isAre = "is"
                else:
                    isAre = "are"
                typeText = self.tpc.joinStringsWithOxfordComma(typeList, separator=", ",
                                                               lastSeparator=" and ")
                regionText = self.alu.getProductRegionNameFromAbbreviation(productDict.get("productRegion"))
                phraseList += [
                    f"The tsunami {typeText} {isAre} cancelled for all areas along {regionText}.",
                    ("No destructive tsunami has been recorded. No tsunami danger presently "
                     f"exists for {regionText}."),
                    f"This will be the final {self.amm.getWarningCenterByEventDict(eventDict)} message for this event."
                    ]
        else:
            if self.siteID == "NTWC":
                text += self.amm.getNTWC_SummaryHeadlines(productDict)
            else:
                text += self.amm.getPTWC_SummaryHeadlines(productDict)
            eventDict = self.agu.getAllEventDicts(productDict)[0]
            phraseList += [
                self.amm.getPhysicalEventDescriptionString(eventDict, self.fieldNameSuffix)]
            generateTsunamiText = self.getGenerateTsunamiText(eventDict)
            if generateTsunamiText:
                phraseList += [generateTsunamiText]
            phraseList += [
                f"{self.amm.getNextMsgText(eventDict, '', self.fieldNameSuffix)} The tsunami message will remain in effect until further notice."
                ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase, "", "")
            text += f"{wrappedPhrase}\n\n"
        return text

    def getGenerateTsunamiText(self, eventDict):
        text = ""
        prefix = ""
        peType = eventDict.get("physicalEventType")
        if self.agu.isPhysicalEventTypeSeismic(peType):
            prefix = "Earthquakes of this magnitude"
        elif self.agu.isPhysicalEventTypeVolcanic(peType):
            prefix = "Volcanoes of this size"
        elif self.agu.isPhysicalEventTypeLandslide(peType):
            prefix = "Landslides of this size"

        if prefix:
            text += f"{prefix} are known to generate tsunamis."
        return text
