package gov.noaa.gsl.common.dataplugin.atomsForecast;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TimeZone;
import java.util.TreeMap;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

@DynamicSerialize
public class TsunamiForecastInfo {

    @DynamicSerializeElement
    private String physicalEventCustomId;

    @DynamicSerializeElement
    private TsunamiForecastType forecastType;

    @DynamicSerializeElement
    private Date runTime;

    public TsunamiForecastInfo() {
    }

    public TsunamiForecastInfo(String eventId, TsunamiForecastType type,
            Date runTime) {
        if (eventId == null || eventId.isEmpty() || type == null
                || runTime == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + " constructor received a null argument.");
        }

        this.physicalEventCustomId = eventId;
        this.forecastType = type;
        this.runTime = runTime;
    }

    public String getPhysicalEventCustomId() {
        return physicalEventCustomId;
    }

    public void setPhysicalEventCustomId(String physicalEventCustomId) {
        this.physicalEventCustomId = physicalEventCustomId;
    }

    public TsunamiForecastType getForecastType() {
        return forecastType;
    }

    public void setForecastType(TsunamiForecastType forecastType) {
        this.forecastType = forecastType;
    }

    public Date getRunTime() {
        return runTime;
    }

    public void setRunTime(Date runTime) {
        this.runTime = runTime;
    }

    // --------------------- Helper methods below -------------------

    public static List<TsunamiForecastType> getFcstTypes(
            List<TsunamiForecastInfo> fcstInfos) {
        Set<TsunamiForecastType> types = new HashSet<>();
        for (TsunamiForecastInfo info : fcstInfos) {
            types.add(info.getForecastType());
        }

        List<TsunamiForecastType> list = new ArrayList<>(types);
        return list;
    }

    public static List<TsunamiForecastType> getFcstTypes(
            List<TsunamiForecastInfo> fcstInfos, Date runTime) {
        Set<TsunamiForecastType> types = new HashSet<>();
        for (TsunamiForecastInfo info : fcstInfos) {
            if (info.getRunTime().equals(runTime)) {
                types.add(info.getForecastType());
            }
        }

        List<TsunamiForecastType> list = new ArrayList<>(types);
        return list;
    }

    public static List<Date> getFcstRunTimes(
            List<TsunamiForecastInfo> fcstInfos) {
        Set<Date> runTimes = new HashSet<>();
        for (TsunamiForecastInfo info : fcstInfos) {
            runTimes.add(info.getRunTime());
        }

        List<Date> list = new ArrayList<>(runTimes);
        return list;
    }

    public static List<Date> getFcstRunTimes(
            List<TsunamiForecastInfo> fcstInfos, TsunamiForecastType type) {
        Set<Date> runTimes = new HashSet<>();
        for (TsunamiForecastInfo info : fcstInfos) {
            if (info.getForecastType().equals(type)) {
                runTimes.add(info.getRunTime());
            }
        }

        List<Date> list = new ArrayList<>(runTimes);
        return list;
    }

    public static List<TsunamiForecastInfo> getTsunamiForecastInfos(
            List<TsunamiForecastInfo> fcstInfos, TsunamiForecastType type) {
        List<TsunamiForecastInfo> infos = new ArrayList<>();
        for (TsunamiForecastInfo info : fcstInfos) {
            if (info.getForecastType().equals(type)) {
                infos.add(info);
            }
        }
        return infos;
    }

    public static TsunamiForecastInfo getMostRecentTsunamiForecastInfo(
            List<TsunamiForecastInfo> fcstInfos) {

        /**
         * Why the heck is Eclipse replacing my code with this lambda nonsense?
         */
        Collections.sort(fcstInfos,
                Comparator.comparing(TsunamiForecastInfo::getRunTime));

        return fcstInfos.get(fcstInfos.size() - 1);
    }

    public static TsunamiForecastInfo getMostRecentTsunamiForecastInfo(
            List<TsunamiForecastInfo> fcstInfos, TsunamiForecastType type) {

        List<TsunamiForecastInfo> infos = getTsunamiForecastInfos(fcstInfos,
                type);
        /**
         * Why the heck is Eclipse replacing my code with this lambda nonsense?
         */
        Collections.sort(infos,
                Comparator.comparing(TsunamiForecastInfo::getRunTime));

        return (infos.size() == 0 ? null : infos.get(infos.size() - 1));
    }

    /**
     * Returns a sorted map where the keys/entries are sorted alphabetically by
     * TsunamiForecasType's label, and the values are Lists of
     * TsunamiForecastInfo sorted by runtime with mostRecentFirst (or in reverse
     * if passed false).
     *
     * @param fcstInfos
     * @param mostRecentFirst
     * @return
     */
    public static Map<TsunamiForecastType, List<TsunamiForecastInfo>> sortTsunamiForecastInfos(
            List<TsunamiForecastInfo> fcstInfos, boolean mostRecentFirst) {

        Map<TsunamiForecastType, List<TsunamiForecastInfo>> result = new TreeMap<>(
                Comparator.comparing(TsunamiForecastType::getLabel));
        if (fcstInfos == null || fcstInfos.size() == 0) {
            return result;
        }

        Comparator<TsunamiForecastInfo> ascendingComp = Comparator
                .comparing(TsunamiForecastInfo::getRunTime);
        Comparator<TsunamiForecastInfo> descendingComp = ascendingComp
                .reversed();

        // First get types, and sort em by value
        List<TsunamiForecastType> types = getFcstTypes(fcstInfos);

        for (TsunamiForecastType type : types) {
            List<TsunamiForecastInfo> typedListOfTFIs = getTsunamiForecastInfos(
                    fcstInfos, type);
            Collections.sort(typedListOfTFIs,
                    (mostRecentFirst ? descendingComp : ascendingComp));
            result.put(type, typedListOfTFIs);
        }

        return result;
    }

    @Override
    public int hashCode() {
        return Objects.hash(forecastType, physicalEventCustomId, runTime);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        TsunamiForecastInfo other = (TsunamiForecastInfo) obj;
        return forecastType == other.forecastType
                && Objects.equals(physicalEventCustomId,
                        other.physicalEventCustomId)
                && Objects.equals(runTime, other.runTime);
    }

    @Override
    public String toString() {
        return "TsunamiForecastInfo [physicalEventCustomId="
                + physicalEventCustomId + ", forecastType=" + forecastType
                + ", runTime=" + runTime + "]";
    }

    ///////////////////////////////////////////////////
    public static void main(String args[]) throws Exception {
        SimpleDateFormat dateFormatter;

        dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));

        List<TsunamiForecastInfo> fcstInfos = new ArrayList<>();

        TsunamiForecastType[] types = TsunamiForecastType.values();
        for (int i = 0; i < 25; i++) {
            int typeIndex = getRandomNumber(0, types.length);
            int hour = getRandomNumber(0, 23);
            int minute = getRandomNumber(0, 59);

            String hourString = (hour < 10 ? "0" + hour : "" + hour);
            String minuteString = (minute < 10 ? "0" + minute : "" + minute);

            Date runTime = dateFormatter.parse(
                    "2022-09-01T" + hourString + ":" + minuteString + ":00");

            TsunamiForecastInfo fcstInfo = new TsunamiForecastInfo("123",
                    types[typeIndex], runTime);
            fcstInfos.add(fcstInfo);
        }

        Map<TsunamiForecastType, List<TsunamiForecastInfo>> descendingMap = sortTsunamiForecastInfos(
                fcstInfos, true);
        Map<TsunamiForecastType, List<TsunamiForecastInfo>> ascendingMap = sortTsunamiForecastInfos(
                fcstInfos, false);

        dumpMap(descendingMap, dateFormatter);
        dumpMap(ascendingMap, dateFormatter);

    }

    private static void dumpMap(
            Map<TsunamiForecastType, List<TsunamiForecastInfo>> map,
            SimpleDateFormat formatter) {

        for (Map.Entry<TsunamiForecastType, List<TsunamiForecastInfo>> entry : map
                .entrySet()) {
            System.out.println(entry.getKey());
            for (TsunamiForecastInfo info : entry.getValue()) {
                System.out.println(info.getForecastType() + " "
                        + formatter.format(info.getRunTime()));
            }
        }
        System.out.println("------------");
    }

    private static int getRandomNumber(int min, int max) {
        return (int) ((Math.random() * (max - min)) + min);
    }

}
