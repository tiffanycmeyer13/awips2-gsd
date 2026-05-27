# *** Override behavior of TSU_Spanish_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Spanish Formatter for TSU products
    @since: July 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsMessageMethods
import HazardProductParts
import NWS_Base_Formatter
import PhraseMethodsUtil
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
        self.amm = AtomsMessageMethods.AtomsMessageMethods()
        self.hazardProductParts = HazardProductParts.HazardProductParts()
        self.pmUtil = PhraseMethodsUtil.PhraseMethodsUtil()

        self.fieldNameSuffix = f"_{productDict.get('productLabel')}"
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
        productRegion = productDict.get("productRegion")
        if productRegion in self.getValidProductRegions():
            self.initialize(productDict)
            legacyText = self.createTextProduct()
            legacyText = ProductUtils.wrapLegacy(legacyText)
            self.validateText(legacyText)
            return [legacyText]
        else:
            return []

    def recordGeneratedText(self, productDict, textProductList):
        '''
        @summary: Write the text product(s) from this formatter to a physical file
        @param productDict: The product-level dictionary
        @param textProductList: A list of text product(s) created by the formatter
        @return: None
        '''
        if self.issueFlag:
            AtomsDisseminationUtilities.AtomsDisseminationUtilities().writeAtomsFile(productDict,
                                                                                     textProductList,
                                                                                     self.__module__)

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary
        '''
        productParts = self.hazardProductParts.productParts_TSU(self.productDict,
                                                                self.productRegion, "Pub")

        return productParts

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
    def wmoHeader(self, productDict):
        '''
        @summary: Create the wmoHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        header = self.processPartValue(productDict.get("productBeginDict"), "wmoHeader_spn",
                                       self.wmoHeader_text, productDict, True)
        return self.getFormattedText(header, endText="\n")

    def productHeader(self, productDict):
        '''
        @summary: Create the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "productHeader_spn",
                                     self.productHeader_text, productDict, True)
        return text

    def updatesBullet(self, productDict):
        '''
        @summary: Create the updatesBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict, "updatesBullet_spn",
                                     self.updatesBullet_text, productDict)
        return text

    def ugcHeader(self, productDict):
        '''
        @summary: Create the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "ugcHeader",
                                     self.ugcHeader_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def vtecString(self, productDict):
        '''
        @summary: Create the vtecString product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "vtecString",
                                     self.vtecString_text, productDict, True)
        return text

    def summaryHeadlines(self, productDict):
        '''
        @summary: Create the summaryHeadlines product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "summaryHeadlines_spn",
                                     self.summaryHeadlines_text, productDict)
        return text

    def areaList(self, productDict):
        '''
        @summary: Create the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "areaList_spn",
                                     self.areaList_text, productDict)
        return text

    def dangerEvaluation(self, productDict):
        '''
        @summary: Create the dangerEvaluation product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "dangerEvaluation_spn",
                                     self.dangerEvaluation_text, productDict)
        return self.getFormattedText(text, endText="\n\n")

    def audienceBullet(self, productDict):
        '''
        @summary: Create the audienceBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "audienceBullet_spn",
                                     self.audienceBullet_text, productDict)
        return text

    def evaluationBullet(self, productDict):
        '''
        @summary: Create the evaluationBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "evaluationBullet_spn",
                                     self.evaluationBullet_text, productDict)
        return text

    def physicalEventParametersBullet(self, productDict):
        '''
        @summary: Create the physicalEventParametersBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"),
                                     "physicalEventParametersBullet_spn",
                                     self.physicalEventParametersBullet_text, productDict)
        return text

    def tsunamiForecastsBullet(self, productDict):
        '''
        @summary: Create the tsunamiForecastsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"),
                                     "tsunamiForecastsBullet_spn",
                                     self.tsunamiForecastsBullet_text, productDict)
        return self.getFormattedText(text, endText="\n\n")

    def tsunamiObservationsBullet(self, productDict):
        '''
        @summary: Create the tsunamiObservationsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"),
                                     "tsunamiObservationsBullet_spn",
                                     self.tsunamiObservationsBullet_text, productDict)
        return self.getFormattedText(text, endText="\n\n")

    def recommendedActionsBullet(self, productDict):
        '''
        @summary: Create the recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"),
                                     "recommendedActionsBullet_spn",
                                     self.recommendedActionsBullet_text, productDict)
        startText = self.actionsStartText(productDict)
        return self.getFormattedText(text, startText=startText)

    def tsunamiImpactsBullet(self, productDict):
        '''
        @summary: Create the tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"), "tsunamiImpactsBullet_spn",
                                     self.tsunamiImpactsBullet_text, productDict)
        startText = self.impactStartText(productDict)
        return self.getFormattedText(text, startText=startText)

    def additionalInfoStatement(self, productDict):
        '''
        @summary: Create the additionalInfoStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productEndDict"),
                                     "additionalInfoStatement_spn",
                                     self.additionalInfoStatement_text, productDict)
        return text

    ###### Helper functions
    def wmoHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the wmoHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.wmoHeader_text(productDict, self.issueTime, self.productRegion, "Spanish")

    def productHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the productHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        startText = self.amm.productHeaderStart_text(productDict, "TSU", "Spanish")
        officeLoc = self.amm.getOfficeLocation(self.siteID, self.backupSiteID, "Spanish")
        bestTimezone = self.amm.getProductLevelTimezone(productDict)
        timeText = self.getIssuanceTimeDate([bestTimezone])
        return f"{startText}{officeLoc}\n{timeText}"

    def ugcHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        ugcHeader = ""
        for segmentDict in productDict.get("segments"):
            ugcHeader += self.slm.ugcHeader_text(segmentDict)
        return ugcHeader

    def vtecString_text(self, productDict):
        '''
        @summary: Supports the creation of the vtecString product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        vtecString = ""
        for segmentDict in productDict.get("segments"):
            vtecString += f"{self.slm.vtecString_text(segmentDict)}\n"
        return vtecString

    def summaryHeadlines_text(self, productDict):
        '''
        @summary: Supports the creation of the summaryHeadlines product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        if self.siteID == "NTWC":
            headlineText = self.amm.getNTWC_SummaryHeadlines(productDict, "Spanish")
        else:
            headlineText = self.amm.getPTWC_SummaryHeadlines(productDict, "Spanish")
        return headlineText

    def areaList_text(self, productDict):
        '''
        @summary: Supports the creation of the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        if self.productRegion == "Pr":
            areaPhrase = ("Zonas costeras de Puerto Rico: las Islas Vírgenes de los "
                          "Estados Unidos y las Islas Vírgenes Británicas")
            areaListText = f"{self.amm.wrapText(areaPhrase, '', '')}\n"
        else:
            areaListText = self.amm.getAreaListTextProduct(productDict, "Spanish")
        return areaListText

    def dangerEvaluation_text(self, productDict):
        '''
        @summary: Supports the creation of the dangerEvaluation product part
        NOTE: This is only available for NTWC in the AkBcWc & EcGc product regions
        @param productDict: The product-level dictionary
        @return: String
        '''
        dangerIdentifier = productDict.get(f"stillEvaluatingDanger{self.fieldNameSuffix}")
        dangerMsg = ""
        # For Volcano and landslide, add more information to this section
        activeSectionDict = self.agu.getActiveSectionDicts(productDict)[0]
        vtec = activeSectionDict.get("vtecRecord")
        hazardAction = vtec.get("act")
        eventDict = activeSectionDict.get("eventDicts")[0]
        peType = eventDict.get("physicalEventType")
        if not self.agu.isPhysicalEventTypeSeismic(peType):
            dangerMsg = self.getMorePhysicalEventInformation(eventDict, peType, hazardAction)
        if self.productRegion == "AkBcWc":
            dangerMsg += ("Para otras costas del Pacifico de los Estados Unidos y Canada "
                        "en Norte America, ")
        elif self.productRegion == "EcGc":
            dangerMsg += ("Para otras costas de Estados Unidos y Canada en el Atlantico "
                         "y Golfo de America, ")
        if dangerMsg:
            if dangerIdentifier == "dangerStillBeingEvaluated":
                dangerMsg += ("el nivel de amenaza de tsunami esta siendo "
                              "evaluado.  Se proveera informacion adicional en "
                              "mensajes  suplementarios.")
            else:
                dangerMsg += ("no existe amenaza de tsunami.")
        return dangerMsg

    def updatesBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the updatesBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.getUpdatesBulletText(productDict, self.fieldNameSuffix, "Spanish")

    def audienceBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the audienceBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return ("AUDIENCIA\n"
                "--------\n"
                "Responsables de emergencia...medios le prensa...publico en general\n\n")

    def evaluationBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the evaluationBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ("EVALUACION\n"
                "----------\n")
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        phraseList = [self.amm.getPhysicalEventDescriptionString(eventDict, self.fieldNameSuffix,
                                                                 "Spanish"),
                      self.amm.getEvalutionBulletLocation_text(self.productRegion),
                      # TIB / TS.S earliest ETAs should use ReverseTTT whereas TS.WWYs should use the TTT fcst table
                      # since those ETAs may be in the product. So pass False at the end of this method call below.
                      self.amm.getEvaluationEarliestEstimatedArrivalTime_text(eventDict,
                                                                              self.fieldNameSuffix,
                                                                              self.productRegion,
                                                                              False)]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def recommendedActionsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.getRecommendedActionsText(productDict, "Spanish")

    def actionsStartText(self, productDict):
        '''
        @summary: Generate the starting text that will appear above the
        recommendedActionsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''

        if self.agu.areAllSegmentsEnding(productDict):
            headerText = "ACCIONES RECOMENDADAS - ACTUALIZADAS"
        else:
            headerText = "ACCIONES RECOMENDADAS"
        dashText = self.tpc.getDashesUnderString(headerText, "\n")
        startText = f"{headerText}\n{dashText}"
        return startText

    def tsunamiForecastsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiForecastsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        tableText = self.amm.getTsunamiForecastRunsTableText(productDict,
                                                             self.officeTimeZone,
                                                             self.fieldNameSuffix,
                                                             "Spanish")
        if tableText.strip():
            headerText = ("PRONOSTICOS DEL TSUNAMI\n"
                          "--------------------\n")
            forecastPhrase = ("Se pronostica que la actividad del tsunami comience en los "
                              "siguientes puntos a loas horas indicadas.")
            headerText += f"{self.amm.wrapText(forecastPhrase)}\n\n"
            text = f"{headerText}{tableText}"
        return text

    def tsunamiObservationsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiObservationsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ""
        tableText = self.amm.getTsunamiObservationTableText(productDict,
                                                            self.officeTimeZone,
                                                            self.fieldNameSuffix)
        text = ("OBSERVACIONES DEL TSUNAMI\n"
                "-------------------------\n")
        if tableText.strip():
            text += tableText
        else:
            obsPhrase = "No hay observaciones del tsunami disponibles para reportar."
            text += self.amm.wrapText(obsPhrase)
        return text

    def physicalEventParametersBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the physicalEventParametersBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.physicalEventParametersBullet_text(productDict, self.fieldNameSuffix,
                                                           "Spanish")

    def tsunamiImpactsBullet_text(self, productDict):
        '''
        @summary: Supports the creation of the tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        return self.amm.getImpactsBulletText(productDict, self.fieldNameSuffix, "Spanish")

    def impactStartText(self, productDict):
        '''
        @summary: Generate the starting text that will appear above the
        tsunamiImpactsBullet product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        if self.agu.areAllSegmentsEnding(productDict):
            headerText = "IMPACTOS - ACTUALIZADOS"
        else:
            headerText = "IMPACTOS"
        dashText = self.tpc.getDashesUnderString(headerText, "\n")
        startText = f"{headerText}\n{dashText}"
        return startText

    def additionalInfoStatement_text(self, productDict):
        '''
        @summary: Supports the creation of the additionalInfoStatement product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = ("INFORMACION ADICIONAL Y PROXIMA ACTUALIZACION\n"
                "---------------------------------------------\n")
        siteID = productDict.get("siteID")
        phraseList = []
        if self.agu.areAllSegmentsEnding(productDict):
            phraseList += [
                "Este será el mensaje final emitido para este evento.",
                ]
        else:
            phraseList += [
                self.amm.getNextMsgText(productDict, "Spanish", self.fieldNameSuffix),
                "Consulte el sitio web tsunami.gov para obtener más información.",
                ("Se puede obtener información fidedigna sobre el terremoto de la "
                 "red sísmica regional correspondiente o del Servicio Geológico "
                 "de Estados Unidos en Internet en earth.usgs.gov.")
                ]
        if siteID == "NTWC":
            if self.productRegion == "AkBcWc":
                phraseList += [
                    ("Regiones costeras del Pacifico fuera de California, Oregon, "
                     "Washington, Columbia Britanica y Alaska deben referirse a "
                     "los mensanjes del Centro de Alerta de Tsunami del Pacifico "
                     "en tsunami.gov."),
                    ]
            elif self.productRegion == "EcGc":
                phraseList += [
                    ("Regiones costeras del Caribe incluido de Puerto Rico, Islas "
                     "Virgenes de los Estados Unidos e Islas Virgenes Britanicas "
                     "deben consultar los mensajes emitidos por el Centro "
                     "de Alerta de Tsunami del Pacifico en su sitio de internet "
                     "tsunami.gov."),
                    ]
        elif siteID == "PTWC" and self.productRegion == "Pr":
            phraseList += [
                ("Se puede encontrar más información sobre este evento y cualquier "
                 "amenaza de tsunami para Puerto Rico y las Islas Vírgenes en "
                 "Internet en www.tsunami.gov."),
                ("El Centro Nacional de Alerta de Tsunamis de los EE. UU. emitirá "
                 "información sobre cualquier amenaza de tsunami para las costas "
                 "del Golfo de América o del Atlántico y se podrá encontrar en "
                 "Internet en www.tsunami.gov.")
                ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def getValidProductRegions(self):
        '''
        @summary: Get the valid product regions where the spanish format will appear
        @return: List of strings
        '''
        return AtomsMessageMethods.AtomsMessageMethods().productRegionsWithSpanish()

    def getMorePhysicalEventInformation(self, eventDict, physicalEventType, hazardAction):
        '''
        @summary: Generate extra physical event information
        @param eventDict: The event level dictionary
        @param physicalEventType: The physical event type such volcano, landslide
        @param hazardAction: The hazard event action such as NEW or CON
        @return: String
        '''
        text = ""
        actionText = ""
        peName = eventDict.get(f"peName{self.fieldNameSuffix}")
        suffix = "peligroso para las costas en el área de advertencia."
        if self.agu.isPhysicalEventTypeVolcanic(physicalEventType):
            if peName:
                volcanoText = f"{peName} Volcán"
            else:
                volcanoText = "un volcan"
            if hazardAction == "NEW":
                actionText = "el potencial de desencadenar"
            elif hazardAction == "CON":
                actionText = "generada"
            if actionText:
                text = (f"Una erupción en {volcanoText} ha ocurrido lo que ha "
                        f"{actionText} un tsunami {suffix}")
        elif self.agu.isPhysicalEventTypeLandslide(physicalEventType):
            if peName:
                landslideText = peName
            else:
                landslideText = "un deslizamiento de tierra"
            if hazardAction == "NEW":
                actionText = (f"han sido observados en {landslideText} indicativo de un posible "
                              "tsunami por deslizamiento de tierra")
            elif hazardAction == "CON":
                actionText = (f"continuar en {landslideText} indicativo de actividad continua "
                              "de tsunami")
            if actionText:
                text = f"Fluctuaciones significativas del nivel del agua {actionText} {suffix}"
        elif self.agu.isPhysicalEventTypeUnknown(physicalEventType):
            text = ("Se han observado olas de tsunami. La fuente del "
                    "se desconocen actualmente las olas del tsunami y hay grandes "
                    "incertidumbre en la estimación de los impactos.")
        if text:
            text = f"{self.amm.wrapText(text, '', '')}\n\n"
        return text
