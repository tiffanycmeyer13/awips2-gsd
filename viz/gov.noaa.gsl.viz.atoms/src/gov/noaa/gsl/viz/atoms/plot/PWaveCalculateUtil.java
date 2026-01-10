/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atoms.plot;

import java.awt.geom.Point2D;
import java.util.Date;

import javax.measure.MetricPrefix;
import javax.measure.Unit;
import javax.measure.quantity.Length;

import org.geotools.referencing.GeodeticCalculator;
import org.locationtech.jts.geom.Coordinate;

import com.raytheon.uf.common.geospatial.MapUtil;
import com.raytheon.uf.common.time.SimulatedTime;

import si.uom.SI;

/**
 * The utility to calculate P Wave.
 *
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023             jing             Initial Creation
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 *
 */
public class PWaveCalculateUtil {
    public PWaveCalculateUtil() {
    }

    /**
     * given a starting coordinate, will calculate the exact position an ending
     * coordinate with degrees and distance
     *
     * @param originLocation
     *            starting loc in latlon coord
     * @param azimuthDegrees
     *            direction traveled from starting loc in azimuth degrees
     * @param distance
     *            distance traveled in meters
     * @return ending location in latlon coord
     */
    public static Coordinate calculateLocation(Coordinate originLocation,
            double azimuthDegrees, double distance) {
        /* find location */
        GeodeticCalculator gc = new GeodeticCalculator();
        gc.setStartingGeographicPoint(originLocation.x, originLocation.y);
        gc.setDirection(azimuthDegrees, distance);
        Point2D location = gc.getDestinationGeographicPoint();
        /* return location */
        return new Coordinate(location.getX(), location.getY());
    }

    public static double predictDistance(Coordinate epicenter, Date origin) {
        final long now = SimulatedTime.getSystemTime().getMillis();
        return predictDistance(epicenter, now - origin.getTime());
    }

    public static double predictDistance(Coordinate epicenter,
            long ellapsedMillis) {
        /*
         * TODO may need small changes after libseismic is fixed
         */
        PWaveTravelTimeLookup lookup = TravelTimesUtil
                .calculatePWaveDisplacement(epicenter.z);
        if (lookup != null) {
            return lookup.getDisplacement(MetricPrefix.MILLI(SI.SECOND)
                    .getConverterTo(SI.SECOND).convert(ellapsedMillis));
        }
        return Double.NaN;
    }

    /**
     * Calculate the geocentric distance between two points
     *
     * @param c1
     *            Coordinate 1 in degrees
     * @param c2
     *            Coordinate 2 in degrees
     * @return The geocentric distance in degrees between c1 and c2
     */
    public static double getGeocentricDistance(Coordinate c1, Coordinate c2) {
        double originLon = Math.toRadians(c1.x);
        double originLat = Math.toRadians(c1.y);
        double poiLon = Math.toRadians(c2.x);
        double poiLat = Math.toRadians(c2.y);
        double ED = Math.acos((Math.cos(Math.PI / 2 - originLat)
                * Math.cos(Math.PI / 2 - poiLat))
                + (Math.sin(Math.PI / 2 - originLat)
                        * Math.sin(Math.PI / 2 - poiLat)
                        * Math.cos(Math.abs(originLon - poiLon))));
        return Math.toDegrees(ED);
    }

    /**
     * @param c1
     * @param c2
     * @param unit
     * @return Geocentric distance in the units desired
     */
    public static double getGeocentricDistance(Coordinate c1, Coordinate c2,
            Unit<Length> unit) {
        double distanceInDeg = getGeocentricDistance(c1, c2);
        return convertGeocentricDegreeToSILength(distanceInDeg, unit);
    }

    /**
     * Converts a geocentric degree to distance in SI length
     *
     * @param geocDegrees
     * @return
     */
    public static double convertGeocentricDegreeToSILength(double geocDegrees,
            Unit<Length> unit) {
        return SI.METRE.getConverterTo(unit).convert(
                MapUtil.AWIPS_EARTH_RADIUS * Math.toRadians(geocDegrees));
    }
}
