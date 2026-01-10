/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.atoms;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

import org.dom4j.Document;
import org.dom4j.Element;
import org.dom4j.io.SAXReader;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.time.DataTime;

import gov.noaa.gsl.common.dataplugin.atoms.LandslideEventData;
import gov.noaa.gsl.common.dataplugin.atoms.PrefMagnitudeType;
import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.atoms.UnknownEventData;
import gov.noaa.gsl.common.dataplugin.atoms.VolcanicEventData;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;

/**
 * A class to decode XML as defined in the ATOMS Interface Control Document
 * (ICD) as received from the TFS, and decode it all into IPhysicalEvents,
 * TsunamiForecasts, SeaLevelObservations, TfsImagery, etc
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Dec 13, 2021        Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
public class TfsPhysicalEventDecoder {

    private static final IUFStatusHandler logger = UFStatus
            .getHandler(TfsPhysicalEventDecoder.class);

    // ======== PhysicalEvent properties ===========
    private static final String ATOMS_EVENT_DATA_ELEM = "atomsEventData";

    private static final String EVENTID_ELEM = "EventID";

    private static final String EVENTTYPE_ELEM = "EventType";

    private static final String SOURCE_ELEM = "Source";

    private static final String NAME_ELEM = "Name";

    private static final String IS_TEST_ELEM = "IsTest";

    private static final String IS_KNOWN_ELEM = "IsKnown";

    private static final String LAT_ELEM = "Latitude";

    private static final String LON_ELEM = "Longitude";

    private static final String DIST_TO_COAST_ELEM = "DistanceToCoast";

    private static final String ORIGINTIME_ELEM = "OriginTime";

    private static final String CREATETIME_ELEM = "CreationTime";

    private static final String ORIGINATOR_ELEM = "Originator";

    private static final String TFSUSER_ELEM = "TfsUser";

    private static final String DATARECORD_ELEM = "atomsEventDataRecord";

    // ======== SeismicEventData properties ===========
    private static final String PREFMAG_ELEM = "PreferredMagnitude";

    private static final String PREFMAGTYPE_ELEM = "PreferredMagType";

    private static final String DEPTH_ELEM = "Depth";

    private static final String AZCVG_ELEM = "AzimuthalCoverage";

    private static final String STNS_ELEM = "Stations";

    private static final String THETA_ELEM = "Theta";

    // ======== AdditionalSeismicEventData properties ===========

    // The date format will be 2021-04-30T13:32:04, but let's make sure it's
    // zulu/utc
    private static final SimpleDateFormat dateFormatter;

    static {
        dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    }

    private String getErrorMessage(File xmlFile, String badElemName,
            String[] legalValues) {

        String legalValuesString = String.join(", ", legalValues);
        String errorMsg = getClass().getName()
                + " decode method received an invalid " + badElemName
                + " XML element in the file " + xmlFile.getAbsolutePath()
                + ". Valid value"
                + (legalValues.length == 1 ? " is " : "s are ")
                + legalValuesString;

        return errorMsg;
    }

    public PluginDataObject[] decode(File file) throws Exception {
        logger.info("Starting TfsPhysicalEventDecoder with file "
                + file.getAbsolutePath());

        SAXReader builder = new SAXReader();
        Document document = builder.read(file);
        Element atomsEventDataElement = document.getRootElement();
        if (atomsEventDataElement == null) {
            throw new IllegalArgumentException(
                    getErrorMessage(file, ATOMS_EVENT_DATA_ELEM,
                            new String[] { "a root XML element called "
                                    + ATOMS_EVENT_DATA_ELEM }));
        }

        Element eventIdElem = atomsEventDataElement.element(EVENTID_ELEM);
        Element eventTypeElem = atomsEventDataElement.element(EVENTTYPE_ELEM);
        Element sourceElem = atomsEventDataElement.element(SOURCE_ELEM);
        Element nameElem = atomsEventDataElement.element(NAME_ELEM);
        Element isTestElem = atomsEventDataElement.element(IS_TEST_ELEM);
        Element isKnownElem = atomsEventDataElement.element(IS_KNOWN_ELEM);
        Element originTimeElem = atomsEventDataElement.element(ORIGINTIME_ELEM);
        Element creationTimeElem = atomsEventDataElement
                .element(CREATETIME_ELEM);
        Element latElem = atomsEventDataElement.element(LAT_ELEM);
        Element lonElem = atomsEventDataElement.element(LON_ELEM);
        Element originatorElem = atomsEventDataElement.element(ORIGINATOR_ELEM);
        Element tfsUserElem = atomsEventDataElement.element(TFSUSER_ELEM);
        Element distToCoastKmElem = atomsEventDataElement
                .element(DIST_TO_COAST_ELEM);
        Element dataRecordElem = atomsEventDataElement.element(DATARECORD_ELEM);

        if (eventIdElem == null) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    EVENTID_ELEM, new String[] { "a String." }));
        }
        if (eventTypeElem == null) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    EVENTTYPE_ELEM, PhysicalEventType.getValidValues()));
        }
        if (sourceElem == null || (!"NTWC".equals(sourceElem.getText())
                && !"PTWC".equals(sourceElem.getText()))) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    SOURCE_ELEM, new String[] { "PTWC", "NTWC" }));
        }
        if (originatorElem == null) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    ORIGINATOR_ELEM, new String[] { "PTWC", "NTWC" }));
        }
        if (dataRecordElem == null) {
            throw new IllegalArgumentException(
                    getErrorMessage(file, DATARECORD_ELEM, new String[] {
                            "an XML element called " + DATARECORD_ELEM }));
        }

        PhysicalEvent physicalEvent = new PhysicalEvent();
        physicalEvent.setCustomId(eventIdElem.getText());
        physicalEvent.setSource(sourceElem.getText());

        if (nameElem != null) {
            physicalEvent.setName(nameElem.getText());
        }

        boolean isTest = false;
        try {
            if (isTestElem != null) {
                isTest = Boolean.parseBoolean(isTestElem.getText());
            }
        } catch (Exception e) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    IS_TEST_ELEM, new String[] { "True", "False" }));
        }
        physicalEvent.setIsTestEvent(isTest);

        boolean isKnown = false;
        try {
            if (isKnownElem != null) {
                isKnown = Boolean.parseBoolean(isKnownElem.getText());
            }
        } catch (Exception e) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    IS_KNOWN_ELEM, new String[] { "True", "False" }));
        }
        physicalEvent.setIsKnownEvent(isKnown);

        PhysicalEventType phyEventType = PhysicalEventType.UNKNOWN;
        try {
            phyEventType = PhysicalEventType
                    .valueOf(eventTypeElem.getText().toUpperCase());
        } catch (Exception e) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    EVENTTYPE_ELEM, PhysicalEventType.getValidValues()));
        }

        try {
            physicalEvent.setLatitude(Float.parseFloat(latElem.getText()));
        } catch (Exception e) {
            throw new IllegalArgumentException(getErrorMessage(file, LAT_ELEM,
                    new String[] { "a float" }));
        }

        try {
            physicalEvent.setLongitude(Float.parseFloat(lonElem.getText()));
        } catch (Exception e) {
            throw new IllegalArgumentException(getErrorMessage(file, LON_ELEM,
                    new String[] { "a float" }));
        }

        try {
            physicalEvent.setDistanceToCoastKm(
                    Float.parseFloat(distToCoastKmElem.getText()));
        } catch (Exception e) {
            try {
                physicalEvent.setDistanceToCoastKm(
                        Integer.parseInt(distToCoastKmElem.getText()));
            }

            catch (Exception e2) {
                throw new IllegalArgumentException(
                        getErrorMessage(file, DIST_TO_COAST_ELEM,
                                new String[] { "a float or integer" }));
            }
        }

        // The date string will be 2021-04-30T13:32:04, presumed UTC
        Date originTime = null;
        Date creationTime = null;
        try {
            originTime = dateFormatter.parse(originTimeElem.getText());
        } catch (Exception e) {
            throw new IllegalArgumentException(
                    getErrorMessage(file, ORIGINTIME_ELEM, new String[] {
                            "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC." }));
        }
        try {
            creationTime = dateFormatter.parse(creationTimeElem.getText());
        } catch (Exception e) {
            throw new IllegalArgumentException(
                    getErrorMessage(file, CREATETIME_ELEM, new String[] {
                            "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC." }));
        }

        DataTime dataTime = new DataTime(originTime);
        physicalEvent.setDataTime(dataTime);

        if (PhysicalEventType.SEISMIC.equals(phyEventType)) {
            Element prefMagElem = dataRecordElem.element(PREFMAG_ELEM);
            Element prefMagTypeElem = dataRecordElem.element(PREFMAGTYPE_ELEM);
            Element depthElem = dataRecordElem.element(DEPTH_ELEM);
            Element azCvgElem = dataRecordElem.element(AZCVG_ELEM);
            Element stnsElem = dataRecordElem.element(STNS_ELEM);
            Element thetaElem = dataRecordElem.element(THETA_ELEM);

            SeismicEventData seismicData = new SeismicEventData();
            seismicData.setTfsDataSource(originatorElem.getText());
            if (tfsUserElem != null) {
                seismicData.setTfsUser(tfsUserElem.getText());
            }
            seismicData.setTfsCreationTime(creationTime);
            try {
                seismicData.setPrefMagnitude(
                        Float.parseFloat(prefMagElem.getText()));
            } catch (Exception e) {
                throw new IllegalArgumentException(getErrorMessage(file,
                        PREFMAG_ELEM, new String[] { "a float" }));
            }

            try {
                seismicData.setPrefMagnitudeType(PrefMagnitudeType
                        .valueOf(prefMagTypeElem.getText().toUpperCase()));
            } catch (Exception e) {
                throw new IllegalArgumentException(getErrorMessage(file,
                        PREFMAGTYPE_ELEM, PrefMagnitudeType.getValidValues()));
            }

            try {
                seismicData.setDepthKm(Float.parseFloat(depthElem.getText()));
            } catch (Exception e) {
                throw new IllegalArgumentException(getErrorMessage(file,
                        DEPTH_ELEM, new String[] { "a float in kilometers" }));
            }

            if (azCvgElem != null) {
                try {
                    seismicData.setAzimuthalCoverage(
                            Integer.parseInt(azCvgElem.getText()));
                } catch (Exception e) {
                    throw new IllegalArgumentException(getErrorMessage(file,
                            AZCVG_ELEM, new String[] { "a integer" }));
                }
            }
            if (stnsElem != null) {
                try {
                    seismicData.setNumStations(
                            Integer.parseInt(stnsElem.getText()));
                } catch (Exception e) {
                    throw new IllegalArgumentException(getErrorMessage(file,
                            STNS_ELEM, new String[] { "a integer" }));
                }
            }
            if (thetaElem != null) {
                try {
                    seismicData.setTheta(Float.parseFloat(thetaElem.getText()));
                } catch (Exception e) {
                    throw new IllegalArgumentException(getErrorMessage(file,
                            STNS_ELEM, new String[] { "a float" }));
                }
            }
            physicalEvent.setData(seismicData);

            logger.info(
                    "TfsPhysicalEventDecoder created new SeismicEventData for event with customId = "
                            + eventIdElem.getText());
        } else if (PhysicalEventType.VOLCANIC.equals(phyEventType)) {
            VolcanicEventData volData = new VolcanicEventData();
            volData.setTfsDataSource(originatorElem.getText());
            if (tfsUserElem != null) {
                volData.setTfsUser(tfsUserElem.getText());
            }
            volData.setTfsCreationTime(creationTime);
            physicalEvent.setData(volData);

            logger.info(
                    "TfsPhysicalEventDecoder created new VolcanicEventData for event with customId = "
                            + eventIdElem.getText());
        } else if (PhysicalEventType.LANDSLIDE.equals(phyEventType)) {
            LandslideEventData landData = new LandslideEventData();
            landData.setTfsDataSource(originatorElem.getText());
            if (tfsUserElem != null) {
                landData.setTfsUser(tfsUserElem.getText());
            }
            landData.setTfsCreationTime(creationTime);
            physicalEvent.setData(landData);

            logger.info(
                    "TfsPhysicalEventDecoder created new LandslideEventData for event with customId = "
                            + eventIdElem.getText());
        } else if (PhysicalEventType.UNKNOWN.equals(phyEventType)) {

            UnknownEventData unkData = new UnknownEventData();
            unkData.setTfsDataSource(originatorElem.getText());
            if (tfsUserElem != null) {
                unkData.setTfsUser(tfsUserElem.getText());
            }
            unkData.setTfsCreationTime(creationTime);

            physicalEvent.setData(unkData);

            logger.info(
                    "TfsPhysicalEventDecoder created new UnknownEventData for event with customId = "
                            + eventIdElem.getText());
        }

        // TODO: Should we set the message data on the PDO for the DAO to deal
        // with?
        // physicalEvent.setMessageData(messageData);

        return new PluginDataObject[] { physicalEvent };
    }
}
