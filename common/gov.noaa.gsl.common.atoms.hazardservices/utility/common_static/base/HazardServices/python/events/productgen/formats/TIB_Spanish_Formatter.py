# *** Override behavior of TIB_Spanish_Formatter.py ***
# -- Override ability: Class-based
# -- Levels: All
'''
    Description: Formatter for Tsunami Information Statement products in Spanish
    @since: July 2022
    @author GSL Hazard Services Team
'''

import AtomsDisseminationUtilities
import AtomsGeneralUtilities
import AtomsLocationUtilities
import AtomsMapUtilities
import AtomsMessageMethods
import FramedTextCheck
import HazardProductParts
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
        self.amu = AtomsMapUtilities.AtomsMapUtilities()
        self.hazardProductParts = HazardProductParts.HazardProductParts()

        self.fieldNameSuffix = ""
        self.productRegion = productDict.get("productRegion")
        self.officeTimeZone = self.alu.getProductRegionTimeZone(self.productRegion)
        self.eventDict = self.agu.getAllEventDicts(productDict)[0]

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
            AtomsDisseminationUtilities.AtomsDisseminationUtilities().writeAtomsFile(
                                            productDict, textProductList, self.__module__)

    def determinePartsList(self):
        '''
        @summary: Get the list of product parts for this specific message
        @return: A nested list of product parts as strings and tuples that provides
        a mapping of methods to be called with information at the product, segment,
        section, and event-levels of the product dictionary
        '''
        self.tisType = self.getTisType(self.productDict)
        if self.productRegion in self.amm.productRegionsWithSpanish():
            productParts = self.hazardProductParts.productParts_TIB(self.productDict)
        else:
            productParts = []
        return productParts

    def getProductValidationChecks(self):
        '''
        @summary: A optional list of product validators that will be called to
        verify the message contents are accurate
        @return: A list of validation python files, each one will need to be
        imported at the top of this file
        '''
        if self.issueFlag:
            return [FramedTextCheck]
        else:
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

    def ugcHeader(self, productDict):
        '''
        @summary: Create the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        text = self.processPartValue(productDict.get("productBeginDict"), "ugcHeader_spn",
                                     self.ugcHeader_text, productDict, True)
        return self.getFormattedText(text, endText="\n")

    def areaList(self, productDict):
        '''
        @summary: Create the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        areaListText = self.processPartValue(productDict.get("productBeginDict"), "areaList_spn",
                                             self.areaList_text, productDict)
        return self.getFormattedText(areaListText, endText="\n")

    def summaryHeadlines(self, segmentDict):
        '''
        @summary: Create the summaryHeadlines product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        headlines = self.processPartValue(segmentDict.get("segmentBeginDict"),
                                          "summaryHeadlines_spn", self.summaryHeadlines_text,
                                          segmentDict)
        # Made the headlines statement uppercase when manual edits are made
        headlines = headlines.upper()
        return headlines

    def audienceBullet(self, sectionDict):
        '''
        @summary: Create the audienceBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "audienceBullet_spn",
                                     self.audienceBullet_text, sectionDict)
        return text

    def updatesBullet(self, sectionDict):
        '''
        @summary: Create the updatesBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        updatesText = self.processPartValue(sectionDict, "updatesBullet_spn",
                                            self.updatesBullet_text, sectionDict)
        startText = ("ACTUALIZACIONES\n"
                     "---------------\n")
        return self.getFormattedText(updatesText, startText, endText="\n\n")

    def evaluationBullet(self, sectionDict):
        '''
        @summary: Create the evaluationBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "evaluationBullet_spn",
                                     self.evaluationBullet_text, sectionDict)
        return text

    def recommendedActionsBullet(self, sectionDict):
        '''
        @summary: Create the recommendedActionsBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "recommendedActionsBullet_spn",
                                     self.recommendedActionsBullet_text, sectionDict)
        return text

    def tsunamiImpactsBullet(self, sectionDict):
        '''
        @summary: Create the tsunamiImpactsBullet product part
        @param productDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "tsunamiImpactsBullet_spn",
                                     self.tsunamiImpactsBullet_text, sectionDict)
        return text

    def physicalEventParametersBullet(self, sectionDict):
        '''
        @summary: Create the physicalEventParametersBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "physicalEventParametersBullet_spn",
                                     self.physicalEventParametersBullet_text, sectionDict)
        return text

    def tsunamiActivityObservations(self, sectionDict):
        '''
        @summary: Create the tsunamiActivityObservations product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "tsunamiActivityObservations_spn",
                                     self.tsunamiActivityObservations_text, sectionDict)
        return text

    def additionalInfoStatement(self, sectionDict):
        '''
        @summary: Create the additionalInfoStatement product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = self.processPartValue(sectionDict, "additionalInfoStatement_spn",
                                     self.additionalInfoStatement_text, sectionDict)
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
        startText = self.amm.productHeaderStart_text(productDict, "TIB", "Spanish")
        officeLoc = self.amm.getOfficeLocation(self.siteID, self.backupSiteID, "Spanish")
        bestTimezone = self.alu.getPrimaryTimezoneByProductRegionAbbreviation(self.productRegion)
        timeText = self.getIssuanceTimeDate([bestTimezone])
        return f"{startText}{officeLoc}\n{timeText}"

    def ugcHeader_text(self, productDict):
        '''
        @summary: Supports the creation of the ugcHeader product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        ugcStr = self.amm.getTisUgcsBasedOnProductRegion(self.productRegion)
        ddhhmmTime = self.tpc.getFormattedTime(self.issueTime, '%d%H%M', stripLeading=0)
        text = f"{ugcStr}-{ddhhmmTime}-"
        return text

    def areaList_text(self, productDict):
        '''
        @summary: Supports the creation of the areaList product part
        @param productDict: The product-level dictionary
        @return: String
        '''
        areaList = ("Zonas costeras de Puerto Rico - Islas Vírgenes de los Estados Unidos "
                    "Islas y las Islas Vírgenes Británicas")
        return areaList

    def summaryHeadlines_text(self, segmentDict):
        '''
        @summary: Supports the creation of the summaryHeadlines product part
        @param segmentDict: The segment-level dictionary
        @return: String
        '''
        productRegionText = ""
        if self.siteID == "PTWC" and self.tisType == "tisHigh":
            text = "...POSIBLE AMENAZA DE TSUNAMI POR UN TERREMOTO DISTANTE"
        else:
            text = "...ESTE ES UN MENSAJE INFORMATIVO DE TSUNAMI"
            highMagnitude = self.amm.isTisSignificantMagnitude(self.eventDict)
            if (self.siteID == "NTWC" and
                self.amu.isQuakeInArcticOceanProcRegion(self.eventDict, self.fieldNameSuffix)):
                productRegionText = self.amm.getArcticOceanProcRegionText("Spanish")
            elif self.tisType == "tisHigh" or highMagnitude:
                productRegionText = self.alu.getProductRegionNameFromAbbreviation(self.productRegion)
            if productRegionText:
                text += f" para {productRegionText}"
        text += "...\n"
        return text

    def audienceBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the audienceBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ""
        if self.productRegion == "Pr":
            text = ("AUDIENCIA\n"
                    "---------\n")
            phrase = ("Funcionarios gubernamentales... medios de prensa... y el "
                      "publico en general en Puerto Rico... las islas Virgenes de "
                      "los Estados Unidos... y las islas Virgenes Britanicas.")
            text += self.amm.wrapText(phrase)
            text += "\n\n"
        return text

    def updatesBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the updatesBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ""
        if self.tisType == "tisFinal":
            text = " * Final TIS"
        return text

    def evaluationBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the evaluationBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ("EVALUACION\n"
                "----------\n")
        if self.amu.isQuakeInArcticOceanProcRegion(self.eventDict, self.fieldNameSuffix):
            regionText = self.amm.getArcticOceanProcRegionText("Spanish")
        else:
            regionText = self.alu.getProductRegionNameFromAbbreviation(self.productRegion)
        warningCenter = self.amm.getWarningCenterByEventDict(self.eventDict)
        peType = self.eventDict.get("physicalEventType")
        phraseList = []
        prefix = ""
        isSupplementalMsg = self.amm.isTisSupplementalMessage(sectionDict)
        if self.tisType == "tisFinal" or (isSupplementalMsg and self.tisType != "tisHigh"):
            phraseList += [f"No hay peligro de tsunami para {regionText}."]
            if self.amm.isTisSignificantMagnitude(self.eventDict):
                phraseList += [
                    ("Algunas de las áreas mencionadas anteriormente pueden experimentar cambios "
                     "no dañinos en el nivel del mar.")
                    ]
        else:
            if self.agu.isPhysicalEventTypeSeismic(peType):
                prefix = "Un terremoto"
                if self.tisType == "tisHigh":
                    if self.amu.isQuakeInArcticOceanProcRegion(self.eventDict, self.fieldNameSuffix):
                        phraseList += [
                            "NO se espera un tsunami generalizado y dañino.",
                            ("En zonas costeras de fuertes temblores pueden producirse tsunamis "
                             "locales ser generado."),
                            ("Debido a los datos muy limitados sobre el nivel del mar de la región "
                             "de origen, No es posible para este Centro confirmar o evaluar "
                             "rápidamente La fuerza de un tsunami si se ha generado uno.")
                            ]
                    else:
                        phraseList += [
                            ("Se conoce que terremotos de este tamano pueden generar tsunamis "
                             "potencialmente peligrosos para costas fuera del lugar de origen."),
                            (f"La {warningCenter} está analizando el evento para determinar "
                             "el nivel de peligrosidad."),
                            "Informacion adicional sera emitida cuando este disponible.",
                            ("Este terremoto tiene el potencial de generar un tsunami "
                             "destructivo en el lugar de origen.")
                            ]
                # TIS low
                elif not self.amm.isTisSignificantMagnitude(self.eventDict):
                    prefix = ""
                    phraseList += [
                        "NO hay peligro de tsunami por este terremoto."
                        ]
                # TIS high
                else:
                    phraseList += [f"No hay peligro de tsunami para {regionText}"]
                    # if in the indian ocean
                    if self.amu.isQuakeInIndianOceanProcRegion(self.eventDict, self.fieldNameSuffix):
                        phraseList += [("Esta evaluación se basa en la ubicación del terremoto que "
                                        "está fuera del Pacífico.")
                                        ]
                    # If in the mid-Atlantic Ridge
                    elif self.amu.isQuakeInMidAtlanticRidgeRegion(self.eventDict, self.fieldNameSuffix):
                        phraseList += [("Basado en el lugar del terremoto cerca del dorsal del "
                                        "Atlantico no se espera un tsunami destructivo.")
                                        ]
                    # Deep evaluation
                    elif self.amm.isQuakeDeep(self.eventDict, self.fieldNameSuffix):
                        phraseList += [
                            "Debido a la profundidad del terremoto, no se espera un tsunami."
                            ]
                    # Inland evaluation
                    elif self.amm.isPhysicalEventOnshore(self.eventDict, self.fieldNameSuffix):
                        phraseList += [
                            "Debido a la ubicación del terremoto en tierra, no se espera un tsunami."
                            ]
                    elif self.siteID == "NTWC":
                        # Shallow evaluation
                        phraseList += [
                            ("Según la información sobre terremotos y los registros históricos de "
                             "tsunamis, no se espera que el terremoto genere un tsunami.")
                            ]
            elif self.agu.isPhysicalEventTypeVolcanic(peType):
                prefix = "Una erupción volcánica"
            elif self.agu.isPhysicalEventTypeLandslide(peType):
                prefix = "Un deslizamiento de tierra"
            if prefix:
                phraseList += [
                    f"{prefix} se ha producido con los parámetros que se enumeran a continuación."
                    ]
        for phrase in phraseList:
            wrappedPhrase = self.amm.wrapText(phrase)
            text += f"{wrappedPhrase}\n\n"
        return text

    def recommendedActionsBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the recommendedActionsBullet product part
        @param productDict: The section-level dictionary
        @return: String
        '''
        if self.tisType in ["tisLow", "tisFinal"] and self.productRegion != "Pr":
            return ""
        else:
            text = ("ACCIONES RECOMENDADAS\n"
                    "---------------------\n")
            phraseList = []
            if self.tisType == "tisHigh":
                regionText = self.alu.getProductRegionNameFromAbbreviation(self.productRegion)
                phraseList += [
                    ("Manténgase alerta para más información. Existe la posibilidad de "
                     "que más adelante se emita una alerta... aviso... o advertencia "
                     f"de tsunami para {regionText}.")
                    ]
            elif self.productRegion == "Pr":
                phraseList += ["No se requiere accion."]
            for phrase in phraseList:
                wrappedPhrase = self.amm.wrapText(phrase)
                text += f"{wrappedPhrase}\n\n"
            return text

    def tsunamiImpactsBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the tsunamiImpactsBullet product part
        @param productDict: The section-level dictionary
        @return: String
        '''
        if self.tisType in ["tisLow", "tisFinal"] and self.productRegion != "Pr":
            return ""
        else:
            text = ("IMPACTOS POTENCIALES\n"
                    "--------------------\n")
            phraseList = []
            if self.tisType == "tisHigh":
                phraseList += [
                    "Aún se están evaluando los posibles impactos del tsunami.",
                    ]
            elif self.productRegion == "Pr":
                phraseList += ["No se esperan impactos de tsunami debido a este terremoto."]
            for phrase in phraseList:
                wrappedPhrase = self.amm.wrapText(phrase)
                text += f"{wrappedPhrase}\n\n"
            return text

    def physicalEventParametersBullet_text(self, sectionDict):
        '''
        @summary: Supports the creation of the physicalEventParametersBullet product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        return self.amm.physicalEventParametersBullet_text(sectionDict, self.fieldNameSuffix,
                                                           "Spanish")

    def tsunamiActivityObservations_text(self, sectionDict):
        '''
        @summary: Supports the creation of the tsunamiActivityObservations product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ""
        tableText = self.amm.getTsunamiObservationTableText(sectionDict,
                                                            self.officeTimeZone,
                                                            self.fieldNameSuffix, "Spanish")
        if tableText.strip():
            text = ("OBSERVACIONES DEL TSUNAMI - ACTUALIZADAS\n"
                    "------------------------------------------\n")
            phrase = ("La altura maxima observada del tsunami es el nivel de agua "
                      "mas alto registrado sobre el nivel de la marea hasta la "
                      "emision de este mensaje.")
            text += f"{self.amm.wrapText(phrase)}\n\n"
            text += tableText
        return text

    def additionalInfoStatement_text(self, sectionDict):
        '''
        @summary: Supports the creation of the additionalInfoStatement product part
        @param sectionDict: The section-level dictionary
        @return: String
        '''
        text = ("INFORMACION ADICIONAL Y PROXIMA ACTUALIZACION\n"
                "---------------------------------------------\n")
        phraseList = []
        onlyOrFinal = "sola"
        warningCenter = self.amm.getWarningCenterByEventDict(self.eventDict)
        coastalDescription = self.getCostalDescription()
        highMagnitude = self.amm.isTisSignificantMagnitude(self.eventDict)
        isSupplementalMsg = self.amm.isTisSupplementalMessage(sectionDict)
        peType = self.eventDict.get("physicalEventType")
        if self.tisType == "tisFinal" or isSupplementalMsg:
            onlyOrFinal = "final"
        phraseList += [(f"Esta será el {onlyOrFinal} {warningCenter} declaración emitida para "
                        "este evento a menos que haya información adicional disponible.")]
        if self.tisType == "tisHigh" or self.tisType == "tisFinal" or highMagnitude:
            phraseList += [("Para acceder a informacion adicional consulte el sitio de "
                            "internet tsunami.gov."),
                           (f"{coastalDescription} deben referirse a los "
                            "mensanjes del Centro de Alerta de Tsunami del Pacifico en "
                            "tsunami.gov."), ]
            if self.tisType == "tisHigh" and not isSupplementalMsg:
                phraseList += [("Se emitiran mensajes cada hora para informar sobre la evolucion "
                                "del evento."), ]
        if self.productRegion == "Pr":
            phraseList += [
                ("Mas informacion acerca de este evento puede ser accesada en "
                 "internet en el sitio web www.tsunami.gov."),
                ("Informacion acerca del peligro de tsunami para costas "
                 "estadounidenses en el golfo de mexico y el atlantico sera "
                 "emitida por el centro nacional de alertas de tsunamis y "
                 "puede ser accesada en internet en el sitio web "
                 "www.tsunami.gov.")
                ]
        if self.agu.isPhysicalEventTypeSeismic(peType):
            phraseList += [("Informacion oficial autorizada acerca de este terremoto puede "
                            "ser proveida por la correspondiente red sismica regional o "
                            "el servicio geologico de los estados unidos en su sitio web "
                            "earthquake.usgs.gov.")]
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

    def getTisType(self, productDict):
        '''
        @summary: Get the Tsunami Information Statement type from the first
        event-level dictionary
        @param productDict: The product-level dictionary
        @return: String
        '''
        eventDict = self.agu.getAllEventDicts(productDict)[0]
        tisType = eventDict.get("tisType")
        return tisType

    def getCostalDescription(self):
        '''
        @summary: Get the coastal description
        @return: String
        '''
        text = ""
        if self.productRegion == "AkBcWc":
            text = ("Regiones costeras del Pacífico fuera de California, Oregón, "
                    "Washington, Columbia Británica y Alaska")
        elif self.productRegion == "EcGc":
            text = "regiones costeras del caribe"
        return text
