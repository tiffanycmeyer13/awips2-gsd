/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atomsForecast;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TimeZone;

import gov.noaa.gsl.common.dataplugin.atomsForecast.ForecastStation;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiStationForecast;

/**
 * Represents a table with each row that looks something like this:
 * 
 * ForecastStation ARRIVAL_TIME_DATE AMPLITUDE_FLOAT DURATION
 * 
 * Arrival Times are taken from the arrivalTimesFcst, and amplitudes/durations
 * are taken from the amplitudeFcst.
 * 
 * A union of stations is taken from each Forecast for the final table, such
 * that there is a row for each station.
 * 
 * @author awips
 *
 */
public class TsunamiForecastTable {

    private static final SimpleDateFormat dateFormatter;

    static {
        dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    }

    public static final Comparator<TsuFcstTableRow> STN_NAME_COMPARATOR = new Comparator<TsuFcstTableRow>() {

        @Override
        public int compare(TsuFcstTableRow row0, TsuFcstTableRow row1) {
            if (row0.getStation().getName() == null
                    || row1.getStation().getName() == null) {
                return 0;
            }
            // Compare secondarily by customId
            if (row0.getStation().getName().equals(row1.getStation().getName())
                    && row0.getStation().getCustomId() != null) {
                return row0.getStation().getCustomId()
                        .compareTo(row1.getStation().getCustomId());
            } else {
                return row0.getStation().getName()
                        .compareTo(row1.getStation().getName());
            }
        }
    };

    public static final Comparator<TsuFcstTableRow> STN_COUNTRY_COMPARATOR = new Comparator<TsuFcstTableRow>() {

        @Override
        public int compare(TsuFcstTableRow row0, TsuFcstTableRow row1) {
            if (row0.getStation().getCountry() == null
                    || row1.getStation().getCountry() == null) {
                return 0;
            }
            return row0.getStation().getCountry()
                    .compareTo(row1.getStation().getCountry());
        }
    };

    public static final Comparator<TsuFcstTableRow> STN_CUSTOMID_COMPARATOR = new Comparator<TsuFcstTableRow>() {

        @Override
        public int compare(TsuFcstTableRow row0, TsuFcstTableRow row1) {
            if (row0.getStation().getCustomId() == null
                    || row1.getStation().getCustomId() == null) {
                return 0;
            }
            // Compare secondarily by name
            if (row0.getStation().getCustomId()
                    .equals(row1.getStation().getCustomId())
                    && row0.getStation().getName() != null) {
                return row0.getStation().getName()
                        .compareTo(row1.getStation().getName());
            } else {
                return row0.getStation().getCustomId()
                        .compareTo(row1.getStation().getCustomId());
            }
        }
    };

    public static final Comparator<TsuFcstTableRow> ARRIVE_TIME_COMPARATOR = new Comparator<TsuFcstTableRow>() {

        @Override
        public int compare(TsuFcstTableRow row0, TsuFcstTableRow row1) {
            if (row0.getArrivalTime() == null
                    || row1.getArrivalTime() == null) {
                return 0;
            }
            return row0.getArrivalTime().compareTo(row1.getArrivalTime());
        }
    };

    public static final Comparator<TsuFcstTableRow> AMPLITUDE_COMPARATOR = new Comparator<TsuFcstTableRow>() {

        @Override
        public int compare(TsuFcstTableRow row0, TsuFcstTableRow row1) {
            if (row0.getAmplitude() == null || row1.getAmplitude() == null) {
                return 0;
            }
            return row0.getAmplitude().compareTo(row1.getAmplitude());
        }
    };

    public class TsuFcstTableRow {

        private ForecastStation stn = null;

        private Date arrivalTime = null;

        private Float amplitude;

        private Integer duration;

        public TsuFcstTableRow(ForecastStation stn, Date arrTime, Float amp,
                Integer duration) {
            this.stn = stn;
            this.arrivalTime = arrTime;
            this.amplitude = amp;
            this.duration = duration;
        }

        public TsuFcstTableRow(ForecastStation stn) {
            if (stn == null) {
                return;
            }

            this.stn = stn;
        }

        public ForecastStation getStation() {
            return stn;
        }

        public void setStation(ForecastStation stn) {
            this.stn = stn;
        }

        public Date getArrivalTime() {
            return arrivalTime;
        }

        public void setArrivalTime(Date arrivalTime) {
            this.arrivalTime = arrivalTime;
        }

        public Float getAmplitude() {
            return amplitude;
        }

        public void setAmplitude(Float amplitude) {
            this.amplitude = amplitude;
        }

        public Integer getDuration() {
            return duration;
        }

        public void setDuration(Integer duration) {
            this.duration = duration;
        }
    }

    private TsunamiForecast arrivalTimeFcst = null;

    private TsunamiForecast amplitudeFcst = null;

    private List<TsuFcstTableRow> rowsList = new LinkedList();

    private Map<ForecastStation, TsuFcstTableRow> rowsMap = new HashMap<>();

    private Comparator<TsuFcstTableRow> comparator = STN_NAME_COMPARATOR;

    /**
     * Constructor
     * 
     * @param arrFcst
     * @param ampFcst
     * @param comparator
     */
    public TsunamiForecastTable(TsunamiForecast arrFcst,
            TsunamiForecast ampFcst, Comparator<TsuFcstTableRow> comparator) {

        if (comparator == null) {
            comparator = STN_NAME_COMPARATOR;
        }
        this.comparator = comparator;

        setArrivalTimeFcst(arrFcst);
        setAmplitudeFcst(ampFcst);

        Collections.sort(rowsList, this.comparator);
    }

    /**
     * Constructor
     * 
     * @param arrTimeFcst
     * @param ampFcst
     */
    public TsunamiForecastTable(TsunamiForecast arrTimeFcst,
            TsunamiForecast ampFcst) {

        this(arrTimeFcst, ampFcst, STN_NAME_COMPARATOR);
    }

    /**
     * Constructor
     * 
     */
    public TsunamiForecastTable(Comparator<TsuFcstTableRow> comparator) {

        this(null, null, comparator);
    }

    /**
     * Constructor
     * 
     */
    public TsunamiForecastTable() {

        this(null, null, STN_NAME_COMPARATOR);
    }

    public void sortByStationName() {
        if (comparator == STN_NAME_COMPARATOR) {
            return;
        }
        Collections.sort(rowsList, STN_NAME_COMPARATOR);
        comparator = STN_NAME_COMPARATOR;
    }

    public void sortByStationCustomId() {
        if (comparator == STN_CUSTOMID_COMPARATOR) {
            return;
        }

        Collections.sort(rowsList, STN_CUSTOMID_COMPARATOR);
        comparator = STN_CUSTOMID_COMPARATOR;
    }

    public void sortByStationCountry() {
        if (comparator == STN_COUNTRY_COMPARATOR) {
            return;
        }

        Collections.sort(rowsList, STN_COUNTRY_COMPARATOR);
        comparator = STN_COUNTRY_COMPARATOR;
    }

    public void sortByArrivalTime() {
        if (comparator == ARRIVE_TIME_COMPARATOR) {
            return;
        }

        Collections.sort(rowsList, ARRIVE_TIME_COMPARATOR);
        comparator = ARRIVE_TIME_COMPARATOR;
    }

    public void sortByAmplitude() {
        if (comparator == AMPLITUDE_COMPARATOR) {
            return;
        }

        Collections.sort(rowsList, AMPLITUDE_COMPARATOR);
        comparator = AMPLITUDE_COMPARATOR;
    }

    /**
     * Consider calling clearRows() first and sort results afterwards.
     * 
     * @param arrFcst
     */
    public void setArrivalTimeFcst(TsunamiForecast arrFcst) {
        if (arrFcst != null) {
            for (TsunamiStationForecast stnFcst : arrFcst.getStationFcsts()) {

                TsuFcstTableRow rowForStn = rowsMap.get(stnFcst.getStation());
                if (rowForStn == null) {
                    rowForStn = new TsuFcstTableRow(stnFcst.getStation());
                    rowsMap.put(stnFcst.getStation(), rowForStn);
                    rowsList.add(rowForStn);
                }
                rowForStn.setArrivalTime(stnFcst.getArrivalTime());
            }
        }
        this.arrivalTimeFcst = arrFcst;
    }

    /**
     * Consider calling clearRows() first and sort results afterwards.
     * 
     * @param ampFcst
     */
    public void setAmplitudeFcst(TsunamiForecast ampFcst) {
        if (ampFcst != null) {
            for (TsunamiStationForecast stnFcst : ampFcst.getStationFcsts()) {

                TsuFcstTableRow rowForStn = rowsMap.get(stnFcst.getStation());
                if (rowForStn == null) {
                    rowForStn = new TsuFcstTableRow(stnFcst.getStation());
                    rowsMap.put(stnFcst.getStation(), rowForStn);
                    rowsList.add(rowForStn);
                }

                rowForStn.setAmplitude(stnFcst.getAmplitude());
                rowForStn.setDuration(stnFcst.getDuration());
            }
        }
        this.amplitudeFcst = ampFcst;
    }

    public void clearRows() {
        rowsList.clear();
        rowsMap.clear();
    }

    public TsuFcstTableRow removeRow(ForecastStation station) {

        Iterator iter = rowsList.iterator();
        while (iter.hasNext()) {
            TsuFcstTableRow row = (TsuFcstTableRow) iter.next();
            if (row.getStation().equals(station)) {
                iter.remove();
                break;
            }
        }
        return rowsMap.remove(station);
    }

    public int getNumRows() {
        return rowsList.size();
    }

    /**
     * 
     * @param index
     * @return
     */
    public TsuFcstTableRow getRow(ForecastStation station) {
        if (station == null) {
            return null;
        }

        return rowsMap.get(station);
    }

    public List<TsuFcstTableRow> getRows() {
        List<TsuFcstTableRow> copy = new ArrayList<>(rowsList);
        return copy;
    }

    public Set<ForecastStation> getStations() {
        return rowsMap.keySet();
    }

    /**
     * Duplicate rows by station are overwritten. Could be a very expensive
     * operation.
     * 
     * @param newRows
     */
    public void addAll(Collection<TsuFcstTableRow> newRows) {
        if (newRows == null) {
            return;
        }

        // Very expensive O(n^2) where n is rowsList size, if we are checking
        // for duplicates. If we dont check, then not expensive.
        for (TsuFcstTableRow newRow : newRows) {
            // If we have this station row already, replace the one in the list
            // and map. The commented out untested code removes duplicates:
            /*
             * if (rowsMap.get(newRow.getStation()) != null) { Iterator rowIter
             * = rowsList.iterator(); while (rowIter.hasNext()) {
             * TsuFcstTableRow existingRow = (TsuFcstTableRow) rowIter .next();
             * if (existingRow.getStation().equals(newRow.getStation())) {
             * rowIter.remove(); rowsList.add(newRow); // Concurrent
             * modification?? break; } } }
             */
            rowsList.add(newRow);
            rowsMap.put(newRow.getStation(), newRow);
        }
        Collections.sort(rowsList, comparator);
    }

    @Override
    public String toString() {
        StringBuffer lines = new StringBuffer();
        lines.append("STN | ArrivalTime | Amplitude \n");
        for (TsuFcstTableRow row : rowsList) {
            String ampString = "";
            if (row.getAmplitude() == null) {
                ampString = "null";
            } else {
                ampString = (Float.isNaN(row.getAmplitude()) ? "NaN"
                        : String.format("%s", row.getAmplitude()));
            }
            lines.append(row.getStation().getCustomId() + " | "
                    + (row.getArrivalTime() != null
                            ? dateFormatter.format(row.getArrivalTime())
                            : "null")
                    + " | " + ampString + "\n");
        }
        return lines.toString();
    }
}
