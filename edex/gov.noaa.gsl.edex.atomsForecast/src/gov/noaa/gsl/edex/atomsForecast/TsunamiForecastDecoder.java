/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.atomsForecast;

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

import gov.noaa.gsl.common.dataplugin.atomsForecast.ForecastStation;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastType;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiStationForecast;

/**
 *
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

public class TsunamiForecastDecoder {

    private static final IUFStatusHandler logger = UFStatus
            .getHandler(TsunamiForecastDecoder.class);

    private static final String EVENTID_ELEM = "EventID";

    private static final String SOURCE_ELEM = "Source";

    private static final String FCST_TYPE_ELEM = "ForecastType";

    private static final String CREATETIME_ELEM = "CreationTime";

    private static final String FCSTRUN_TIME_ELEM = "ForecastRunTime";

    private static final String FCST_RECORD_ELEM = "atomsForecastRecord";

    private static final String STN_ID_ELEM = "StationID";

    private static final String ARRIVE_TIME_ELEM = "ArrivalTime";

    private static final String AMP_ELEM = "Amplitude";

    private static final String DURATION_ELEM = "Duration";

    private static final String DESCRIP_ELEM = "Description";

    private static final String EMPTY_ELEM_IDENTIFIER = null;

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
        Element tsuFcstRunElem = document.getRootElement();

        Element eventIdElem = tsuFcstRunElem.element(EVENTID_ELEM);
        Element sourceElem = tsuFcstRunElem.element(SOURCE_ELEM);
        Element descElem = tsuFcstRunElem.element(DESCRIP_ELEM);
        Element fcstTypeElem = tsuFcstRunElem.element(FCST_TYPE_ELEM);
        Element createTimeElem = tsuFcstRunElem.element(CREATETIME_ELEM);
        Element fcstRunTimeElem = tsuFcstRunElem.element(FCSTRUN_TIME_ELEM);
        List<Element> stnFcstRecordElems = tsuFcstRunElem
                .elements(FCST_RECORD_ELEM);

        if (eventIdElem == null) {
            throw new IllegalArgumentException(
                    getErrorMessage(file, EVENTID_ELEM, EMPTY_ELEM_IDENTIFIER,
                            new String[] { "a String." }));
        }
        if (sourceElem == null || (!"NTWC".equals(sourceElem.getText())
                && !"PTWC".equals(sourceElem.getText()))) {
            throw new IllegalArgumentException(
                    getErrorMessage(file, SOURCE_ELEM, EMPTY_ELEM_IDENTIFIER,
                            new String[] { "PTWC", "NTWC" }));
        }

        TsunamiForecast fcstRun = new TsunamiForecast();
        fcstRun.setPhyEventCustomId(eventIdElem.getText());
        fcstRun.setDescription((descElem != null ? descElem.getText() : ""));
        fcstRun.setTfsDataSource(sourceElem.getText());
        try {
            fcstRun.setFcstType(
                    TsunamiForecastType.valueOf(fcstTypeElem.getText()));
        } catch (Exception e) {
            throw new IllegalArgumentException(
                    getErrorMessage(file, FCST_TYPE_ELEM, EMPTY_ELEM_IDENTIFIER,
                            TsunamiForecastType.getValidValues()));
        }

        try {
            Date fcstRunTime = dateFormatter.parse(fcstRunTimeElem.getText());
            fcstRun.setDataTime(new DataTime(fcstRunTime));
        } catch (Exception e) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    FCSTRUN_TIME_ELEM, EMPTY_ELEM_IDENTIFIER, new String[] {
                            "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC." }));
        }

        try {
            Date creationTime = dateFormatter.parse(createTimeElem.getText());
            fcstRun.setCreationTime(creationTime);
        } catch (Exception e) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    CREATETIME_ELEM, EMPTY_ELEM_IDENTIFIER, new String[] {
                            "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC." }));
        }

        if (stnFcstRecordElems == null) {
            throw new IllegalArgumentException(getErrorMessage(file,
                    FCST_RECORD_ELEM, EMPTY_ELEM_IDENTIFIER,
                    new String[] { " the " + FCST_RECORD_ELEM + " element." }));
        }

        List<TsunamiStationForecast> stationFcsts = new LinkedList<>();
        for (Element stnFcstRecordElem : stnFcstRecordElems) {

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
            ForecastStation station = new ForecastStation();
            String tempId = "";
            try {
                tempId = stnFcstRecordElem.elementText(STN_ID_ELEM);
                station.setCustomId(tempId.toUpperCase());
            } catch (Exception e) {
                String tempIdentifyingString = "where " + STN_ID_ELEM + " = "
                        + tempId;
                logger.error(getErrorMessage(file, STN_ID_ELEM,
                        tempIdentifyingString,
                        new String[] { " a " + STN_ID_ELEM
                                + " element with a valid station id." })
                        + " Skipping " + FCST_RECORD_ELEM);
                continue;
            }

            final String elemIdentifyingString = "where " + STN_ID_ELEM + " = "
                    + station.getCustomId();

            TsunamiStationForecast stationForecast = new TsunamiStationForecast();
            stationForecast.setStation(station);

            // arriveTime is required for TTT
            Element arriveTimeElem = stnFcstRecordElem
                    .element(ARRIVE_TIME_ELEM);
            if (arriveTimeElem == null) {
                if (TsunamiForecastType.TTT.equals(fcstRun.getFcstType())) {
                    logger.error(getErrorMessage(file, ARRIVE_TIME_ELEM,
                            elemIdentifyingString,
                            new String[] {
                                    "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC. " })
                            + ARRIVE_TIME_ELEM + " is required for "
                            + TsunamiForecastType.TTT.toString() + " "
                            + FCST_TYPE_ELEM + ". Skipping "
                            + FCST_RECORD_ELEM);
                    continue;
                }
            } else {
                try {
                    Date arrivalTime = dateFormatter.parse(
                            stnFcstRecordElem.elementText(ARRIVE_TIME_ELEM));
                    stationForecast.setArrivalTime(arrivalTime);
                } catch (Exception e) {
                    logger.error(getErrorMessage(file, ARRIVE_TIME_ELEM,
                            elemIdentifyingString,
                            new String[] {
                                    "Dates, in the format \"yyyy-MM-dd'T'HH:mm:ss\" and assumed UTC." })
                            + " Skipping " + FCST_RECORD_ELEM);
                    continue;
                }
            }

            // Amplitude is required if not TTT, and ignored if it is TTT
            Element ampElem = stnFcstRecordElem.element(AMP_ELEM);
            if (ampElem == null) {
                if (!TsunamiForecastType.TTT.equals(fcstRun.getFcstType())) {
                    logger.error(getErrorMessage(file, AMP_ELEM,
                            elemIdentifyingString, new String[] { "a Float" })
                            + AMP_ELEM + " is required for all "
                            + FCST_TYPE_ELEM + " (except TTT). Skipping "
                            + FCST_RECORD_ELEM);
                    continue;
                }
            } else if (!TsunamiForecastType.TTT.equals(fcstRun.getFcstType())) {
                try {
                    stationForecast.setAmplitude(Float.parseFloat(
                            stnFcstRecordElem.elementText(AMP_ELEM)));
                } catch (Exception e) {
                    logger.error(getErrorMessage(file, AMP_ELEM,
                            elemIdentifyingString, new String[] { "a Float" })
                            + ". Skipping " + FCST_RECORD_ELEM);
                    continue;
                }
            }

            // Duration is optional
            if (stnFcstRecordElem.elementText(DURATION_ELEM) != null) {
                try {
                    stationForecast.setDuration(Integer.parseInt(
                            stnFcstRecordElem.elementText(DURATION_ELEM)));
                } catch (Exception e) {
                    logger.error(getErrorMessage(file, DURATION_ELEM,
                            elemIdentifyingString,
                            new String[] { "an Integer" }) + ". Skipping "
                            + FCST_RECORD_ELEM);
                    continue;
                }
            }

            stationFcsts.add(stationForecast);
        }

        fcstRun.setStationFcsts(stationFcsts);

        return new PluginDataObject[] { fcstRun };
    }
}
