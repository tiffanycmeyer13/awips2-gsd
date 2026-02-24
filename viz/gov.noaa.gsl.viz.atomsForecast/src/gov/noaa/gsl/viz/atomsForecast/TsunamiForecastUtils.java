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

import java.util.Collection;
import java.util.Comparator;
import java.util.Date;

import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;

import com.raytheon.uf.common.dataplugin.events.hazards.event.IReadableHazardEvent;

import gov.noaa.gsd.common.utilities.geometry.GeometryUtilities;
import gov.noaa.gsl.common.dataplugin.atomsForecast.ForecastStation;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastInfo;
import gov.noaa.gsl.viz.atomsForecast.TsunamiForecastTable.TsuFcstTableRow;

public class TsunamiForecastUtils {

    private final static double DEG_TO_RAD = 0.017453292;

    /*
     * =========================================================================
     * Helper methods
     * =========================================================================
     */

    /**
     * Returns a table with each row that looks something like this:
     *
     * ForecastStation ARRIVAL_TIME_DATE AMPLITUDE_FLOAT DURATION
     *
     * Arrival Times are taken from the arrivalTimesFcst, and
     * amplitudes/durations are taken from the amplitudeFcst.
     *
     * A union of stations is taken from each Forecast for the final table, such
     * that there is one row for each station.
     *
     * @param arrivalTimesFcst
     *            optional
     * @param amplitudeFcst
     *            optional
     * @return
     */
    public static TsunamiForecastTable createForecastTable(
            TsunamiForecast arrivalTimesFcst, TsunamiForecast amplitudeFcst) {

        return new TsunamiForecastTable(arrivalTimesFcst, amplitudeFcst);
    }

    /**
     * See doc for the other createForecastTable(...) method
     *
     * @param arrivalTimesFcstInfo
     *            optional
     * @param amplitudeFcstInfo
     *            optional
     * @return
     */
    public static TsunamiForecastTable createForecastTable(
            TsunamiForecastInfo arrivalTimesFcstInfo,
            TsunamiForecastInfo amplitudeFcstInfo) {

        return createForecastTable(
                TsunamiForecastDao.getInstance()
                        .getTsunamiForecast(arrivalTimesFcstInfo),
                TsunamiForecastDao.getInstance()
                        .getTsunamiForecast(amplitudeFcstInfo));
    }

    /**
     * For all TsunamiStationForecasts within the given TsunamiForecasts, return
     * a Table of all of them that geographically fall within the hazard area of
     * the given HazardEvent. The table will be sorted by Station name. Each row
     * will have an arrival time coming from the arrivalTimeFcst, and an
     * amplitude from the amplitudeFcst.
     *
     * @param evt
     * @param arrivalTimesFcst
     *            optional
     * @param amplitudeFcst
     *            optional
     * @return
     */
    public static TsunamiForecastTable getStationFcstsWithinHazardArea(
            IReadableHazardEvent evt, TsunamiForecast arrivalTimesFcst,
            TsunamiForecast amplitudeFcst) {
        return getStationFcstsWithinHazardArea(evt, arrivalTimesFcst,
                amplitudeFcst, TsunamiForecastTable.STN_NAME_COMPARATOR);
    }

    /**
     * NOTE the "s" at the end of the method name.
     *
     * For all TsunamiStationForecasts within the given TsunamiForecasts, return
     * a Table of all of them that geographically fall within the hazard areas
     * of the given HazardEvents. The table will be sorted by the given
     * comparator. Each row will have an arrival time coming from the
     * arrivalTimeFcst, and an amplitude from the amplitudeFcst.
     *
     * @param evts
     * @param arrivalTimesFcst
     *            optional
     * @param amplitudeFcst
     *            optional
     * @param comparator
     * @return One big table
     */
    public static TsunamiForecastTable getStationFcstsWithinHazardAreas(
            Collection<IReadableHazardEvent> evts,
            TsunamiForecast arrivalTimesFcst, TsunamiForecast amplitudeFcst,
            Comparator<TsuFcstTableRow> comparator) {

        TsunamiForecastTable table = new TsunamiForecastTable(comparator);
        if (evts == null) {
            return table;
        }

        for (IReadableHazardEvent event : evts) {
            TsunamiForecastTable evtTable = getStationFcstsWithinHazardArea(
                    event, arrivalTimesFcst, amplitudeFcst, comparator);
            table.addAll(evtTable.getRows());
        }
        return table;
    }

    /**
     * For all TsunamiStationForecasts within the given TsunamiForecasts, return
     * a Table of all of them that geographically fall within the hazard area of
     * the given HazardEvent. The table will be sorted by the given comparator.
     * Each row will have an arrival time coming from the arrivalTimeFcst, and
     * an amplitude from the amplitudeFcst.
     *
     * @param evt
     * @param arrivalTimesFcst
     *            optional
     * @param amplitudeFcst
     *            optional
     * @param comparator
     * @return
     */
    public static TsunamiForecastTable getStationFcstsWithinHazardArea(
            IReadableHazardEvent evt, TsunamiForecast arrivalTimesFcst,
            TsunamiForecast amplitudeFcst,
            Comparator<TsuFcstTableRow> comparator) {

        TsunamiForecastTable table = new TsunamiForecastTable(arrivalTimesFcst,
                amplitudeFcst, comparator);

        /*
         * For each station, check if it's in any of the coverage geometries. If
         * not, remove the station from the table.
         */
        GeometryFactory factory = new GeometryFactory();
        Geometry evtGeom = evt.getFlattenedGeometry();
        for (TsuFcstTableRow row : table.getRows()) {
            ForecastStation station = row.getStation();
            Coordinate stationCoord = new Coordinate(station.getLongitude(),
                    station.getLatitude());
            Point stationPoint = factory.createPoint(stationCoord);
            if (!GeometryUtilities.intersects(evtGeom, stationPoint)) {
                table.removeRow(station);
            }
        }
        return table;
    }

    /**
     * For all TsunamiStationForecasts within the given TsunamiForecasts, return
     * a Table of all of them that geographically fall within the kilometer
     * distance of the given lonLatOrigin. The table will be sorted by the given
     * comparator. Each row will have an arrival time coming from the
     * arrivalTimeFcst, and an amplitude from the amplitudeFcst.
     *
     * @param arrivalTimesFcst
     *            optional
     * @param amplitudeFcst
     *            optional
     * @param comparator
     *            optional
     * @param lonLatOrigin
     *            lon X and lat Y origin
     * @param distanceKm
     *            distance in kilometers
     * @return
     */
    public static TsunamiForecastTable getStationFcstsWithinDistance(
            TsunamiForecast arrivalTimesFcst, TsunamiForecast amplitudeFcst,
            Comparator<TsuFcstTableRow> comparator, Coordinate lonLatOrigin,
            double distanceKm) {

        TsunamiForecastTable table = new TsunamiForecastTable(arrivalTimesFcst,
                amplitudeFcst, comparator);

        /*
         * For each station, check if it's in the distance. If not, remove the
         * station from the table.
         */
        for (TsuFcstTableRow row : table.getRows()) {
            ForecastStation station = row.getStation();
            if (calcDistanceInKm(lonLatOrigin.x, lonLatOrigin.y,
                    station.getLongitude(),
                    station.getLatitude()) > distanceKm) {
                table.removeRow(station);
            }
        }
        return table;
    }

    public static double calcDistanceInKm(double lon1, double lat1, double lon2,
            double lat2) {
        final double R = 6371.0;
        lat1 = lat1 * DEG_TO_RAD;
        lon1 = lon1 * DEG_TO_RAD;
        lat2 = lat2 * DEG_TO_RAD;
        lon2 = lon2 * DEG_TO_RAD;
        double dist = Math.acos(Math.sin(lat1) * Math.sin(lat2)
                + Math.cos(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1)) * R;
        return dist;
    }

    /**
     * For all TsunamiStationForecasts within the given TsunamiForecasts, return
     * a Table of all of them that have an arrivalTime that falls before the NOW
     * + travelTimeMillis. The table will be sorted by station name. Each row
     * will have an arrival time coming from the arrivalTimeFcst, and an
     * amplitude from the amplitudeFcst.
     *
     * @param travelTimeMillis
     * @param arrivalTimesFcst
     * @param amplitudeFcst
     * @return
     */
    public static TsunamiForecastTable getStationFcstsWithinTravelTime(
            long travelTimeMillis, TsunamiForecast arrivalTimesFcst,
            TsunamiForecast amplitudeFcst) {
        return getStationFcstsWithinTravelTime(new Date(), travelTimeMillis,
                arrivalTimesFcst, amplitudeFcst,
                TsunamiForecastTable.STN_NAME_COMPARATOR);
    }

    /**
     * For all TsunamiStationForecasts within the given TsunamiForecasts, return
     * a Table of all of them that have an arrivalTime that falls before the
     * originTime + travelTimeMillis. The table will be sorted by station name.
     * Each row will have an arrival time coming from the arrivalTimeFcst, and
     * an amplitude from the amplitudeFcst.
     *
     * @param originTime
     * @param travelTimeMillis
     * @param arrivalTimesFcst
     *            optional
     * @param amplitudeFcst
     *            optional
     * @return
     */
    public static TsunamiForecastTable getStationFcstsWithinTravelTime(
            Date originTime, long travelTimeMillis,
            TsunamiForecast arrivalTimesFcst, TsunamiForecast amplitudeFcst) {
        return getStationFcstsWithinTravelTime(originTime, travelTimeMillis,
                arrivalTimesFcst, amplitudeFcst,
                TsunamiForecastTable.STN_NAME_COMPARATOR);
    }

    /**
     * For all TsunamiStationForecasts within the given TsunamiForecasts, return
     * a Table of all of them that have an arrivalTime that falls before the
     * originTime + travelTimeMillis but >= the originTime. The table will be
     * sorted by the given comparator. Each row will have an arrival time coming
     * from the arrivalTimeFcst, and an amplitude from the amplitudeFcst.
     *
     * @param originTime
     * @param travelTimeMillis
     * @param arrivalTimesFcst
     *            optional
     * @param amplitudeFcst
     *            optional
     * @param comparator
     * @return
     */
    public static TsunamiForecastTable getStationFcstsWithinTravelTime(
            Date originTime, long travelTimeMillis,
            TsunamiForecast arrivalTimesFcst, TsunamiForecast amplitudeFcst,
            Comparator<TsuFcstTableRow> comparator) {

        if (originTime == null) {
            return new TsunamiForecastTable();
        }

        TsunamiForecastTable table = new TsunamiForecastTable(arrivalTimesFcst,
                amplitudeFcst, comparator);

        /*
         * For each station, check if it's in the travel time. If not, remove
         * the station from the table.
         */
        long timeDeadline = originTime.getTime() + travelTimeMillis;

        for (TsuFcstTableRow row : table.getRows()) {
            ForecastStation station = row.getStation();
            Date arrivalTime = row.getArrivalTime();
            if (arrivalTime == null || arrivalTime.getTime() > timeDeadline
                    || arrivalTime.getTime() < originTime.getTime()) {
                table.removeRow(station);
            }
        }
        return table;
    }

}
