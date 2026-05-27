package gov.noaa.gsl.edex.atomsSeaLevelObs;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;
import java.util.TimeZone;

import org.dom4j.Document;
import org.dom4j.Element;
import org.dom4j.io.SAXReader;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.time.DataTime;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SLOObsType;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SLOSensorType;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObs;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObservations;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelStation;

public class SeaLevelObsDecoder {

    private static final IUFStatusHandler logger = UFStatus
            .getHandler(SeaLevelObsDecoder.class);

    private static final String EVENTID_ELEM = "EventID";

    private static final String SOURCE_ELEM = "Source";

    private static final String CREATETIME_ELEM = "CreationTime";

    private static final String RECORD_ELEM = "atomsSeaLevelRecord";

    private static final String STN_ID_ELEM = "StationID";

    private static final String SENSORTYPE_ELEM = "SensorType";

    private static final String OBSTYPE_ELEM = "ObservationType";

    private static final String STARTTIME_ELEM = "StartTime";

    private static final String ENDTIME_ELEM = "EndTime";

    private static final String AMP_ELEM = "Amplitude";

    private static final String PERIOD_ELEM = "Period";

    private static final String FIRSTWAVE_ELEM = "FirstWavePositive";

    private static final String TSUDETECTED_ELEM = "TsunamiDetected";

    private static final String MSRMT1_ELEM = "Measurement1Clipped";

    private static final String MSRMT2_ELEM = "Measurement2Clipped";

    // The date format will be 2021-04-30T13:32:04, but let's make sure it's
    // zulu/utc
    private static final SimpleDateFormat dateFormatter;

    static {
        dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    }

    private String getErrorMessage(File xmlFile, String badElemName,
            String identifyingString, String[] legalValues) {

        if (identifyingString == null) {
            identifyingString = "";
        }
        String legalValuesString = String.join(", ", legalValues);
        String errorMsg = getClass().getName()
                + " decode method received an invalid " + badElemName
                + " XML element "
                + (!"".equals(identifyingString)
                        ? ("(" + identifyingString + ") ")
                        : "")
                + "in the file " + xmlFile.getAbsolutePath() + ". Valid value"
                + (legalValues.length == 1 ? " is " : "s are ")
                + legalValuesString;

        return errorMsg;
    }

    public PluginDataObject[] decode(File file) throws Exception {

        SAXReader builder = new SAXReader();
        Document document = builder.read(file);
        Element slobsElem = document.getRootElement();

        Element eventIdElem = slobsElem.element(EVENTID_ELEM);
        Element sourceElem = slobsElem.element(SOURCE_ELEM);
        Element createTimeElem = slobsElem.element(CREATETIME_ELEM);
        List<Element> slobRecordElems = slobsElem.elements(RECORD_ELEM);

        SeaLevelObservations slobs = new SeaLevelObservations();
        slobs.setPhyEventCustomId(eventIdElem.getText());
        slobs.setTfsDataSource(sourceElem.getText());

        Date createTime = dateFormatter.parse(createTimeElem.getText());
        slobs.setDataTime(new DataTime(createTime));

        List<SeaLevelObs> slobList = new LinkedList<>();
        for (Element slobRecordElem : slobRecordElems) {

            /*
             * TODO It would be nice if we could do the query for a valid
             * Station here, rather than in the DAO, for error-reporting and XML
             * File rejection purposes; But I am pretty sure we don't have a
             * hibernate session etc etc until we get to the DAO, nor do we have
             * utility/query methods here that are available in the CoreDao
             * superclass. Bites.
             *
             * So instead just create the Station here and hope it's good, to be
             * verified in the DAO.
             */
            SeaLevelObs slob = new SeaLevelObs();

            SeaLevelStation station = new SeaLevelStation();
            String tempId = "";
            try {
                tempId = slobRecordElem.elementText(STN_ID_ELEM);
                station.setCustomId(tempId.toUpperCase());
            } catch (Exception e) {
                String tempIdentifyingString = "where " + STN_ID_ELEM + " = "
                        + tempId;
                logger.error(getErrorMessage(file, STN_ID_ELEM,
                        tempIdentifyingString,
                        new String[] { " a " + STN_ID_ELEM
                                + " element with a valid station id." })
                        + " Skipping " + RECORD_ELEM);
            }
            slob.setStation(station);

            final String elemIdentifyingString = "where " + STN_ID_ELEM + " = "
                    + station.getCustomId();

            try {
                slob.setSensorType(SLOSensorType.fromString(
                        slobRecordElem.elementText(SENSORTYPE_ELEM)));
            } catch (Exception e) {
                logger.error(getErrorMessage(file, SENSORTYPE_ELEM,
                        elemIdentifyingString, SLOSensorType.getValidValues())
                        + ". Skipping " + RECORD_ELEM);
                continue;
            }
            try {
                slob.setObsType(SLOObsType
                        .fromString(slobRecordElem.elementText(OBSTYPE_ELEM)));
            } catch (Exception e) {
                logger.error(getErrorMessage(file, OBSTYPE_ELEM,
                        elemIdentifyingString, SLOObsType.getValidValues())
                        + ". Skipping " + RECORD_ELEM);
                continue;
            }

            try {
                Date startTime = dateFormatter
                        .parse(slobRecordElem.elementText(STARTTIME_ELEM));
                slob.setStartTime(startTime);
            } catch (Exception e) {
                logger.error(getErrorMessage(file, STARTTIME_ELEM,
                        elemIdentifyingString,
                        new String[] {
                                "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC." })
                        + ". Skipping " + RECORD_ELEM);
                continue;
            }

            /*
             * Optional below
             */
            try {
                if (slobRecordElem.elementText(ENDTIME_ELEM) != null) {
                    Date endTime = dateFormatter
                            .parse(slobRecordElem.elementText(ENDTIME_ELEM));
                    slob.setEndTime(endTime);
                }
            } catch (Exception e) {
                logger.error(getErrorMessage(file, ENDTIME_ELEM,
                        elemIdentifyingString,
                        new String[] {
                                "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC." })
                        + ". Ignoring " + ENDTIME_ELEM);
            }

            try {
                if (slobRecordElem.elementText(AMP_ELEM) != null) {
                    slob.setAmplitude(Float
                            .parseFloat(slobRecordElem.elementText(AMP_ELEM)));
                }
            } catch (Exception e) {
                logger.error(getErrorMessage(file, AMP_ELEM,
                        elemIdentifyingString, new String[] { "a Float" })
                        + ". Ignoring " + AMP_ELEM);
            }

            try {
                if (slobRecordElem.elementText(PERIOD_ELEM) != null) {
                    slob.setPeriod(Float.parseFloat(
                            slobRecordElem.elementText(PERIOD_ELEM)));
                }
            } catch (Exception e) {
                logger.error(getErrorMessage(file, PERIOD_ELEM,
                        elemIdentifyingString, new String[] { "a Float" })
                        + ". Ignoring " + PERIOD_ELEM);
            }

            // Shockingly, Boolean.parseBoolean( :String ) does NOT throw
            // if the string is != False or True (eg: OTHER)
            try {
                if (slobRecordElem.elementText(FIRSTWAVE_ELEM) != null) {
                    slob.setFirstWavePositive(parseBoolean(
                            slobRecordElem.elementText(FIRSTWAVE_ELEM)));
                }
            } catch (Exception e) {
                logger.error(getErrorMessage(file, FIRSTWAVE_ELEM,
                        elemIdentifyingString, new String[] { "a Boolean" })
                        + ". Ignoring " + FIRSTWAVE_ELEM);
            }

            try {
                if (slobRecordElem.elementText(TSUDETECTED_ELEM) != null) {
                    slob.setTsunamiDetected(parseBoolean(
                            slobRecordElem.elementText(TSUDETECTED_ELEM)));
                }
            } catch (Exception e) {
                logger.error(getErrorMessage(file, TSUDETECTED_ELEM,
                        elemIdentifyingString, new String[] { "a Boolean" })
                        + ". Ignoring " + TSUDETECTED_ELEM);
            }

            try {
                if (slobRecordElem.elementText(MSRMT1_ELEM) != null) {
                    slob.setMsrmt1Clipped(parseBoolean(
                            slobRecordElem.elementText(MSRMT1_ELEM)));
                }
            } catch (Exception e) {
                logger.error(getErrorMessage(file, MSRMT1_ELEM,
                        elemIdentifyingString, new String[] { "a Boolean" })
                        + ". Ignoring " + MSRMT1_ELEM);
            }

            try {
                if (slobRecordElem.elementText(MSRMT2_ELEM) != null) {
                    slob.setMsrmt2Clipped(parseBoolean(
                            slobRecordElem.elementText(MSRMT2_ELEM)));
                }
            } catch (Exception e) {
                logger.error(getErrorMessage(file, MSRMT2_ELEM,
                        elemIdentifyingString, new String[] { "a Boolean" })
                        + ". Ignoring " + MSRMT2_ELEM);
            }

            slobList.add(slob);
        }

        slobs.setSeaLevelObs(slobList);

        return new PluginDataObject[] { slobs };
    }

    private boolean parseBoolean(String s) throws IllegalArgumentException {
        if ("true".equalsIgnoreCase(s)) {
            return true;
        } else if ("false".equalsIgnoreCase(s)) {
            return false;
        } else {
            throw new IllegalArgumentException("Only true or false is allowed");
        }
    }

    public static void main(String args[]) {
        boolean value = Boolean.parseBoolean("BAD");
        System.err.println("value = " + value);
        System.err.println("No exception was thrown, strangely.");
    }
}
