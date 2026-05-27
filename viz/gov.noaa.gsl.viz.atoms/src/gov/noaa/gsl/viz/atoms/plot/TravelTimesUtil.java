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

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/**
 * Utility for PWave travel times that interfaces with libseismic
 *
 * It's ported from the TOPS.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jan 10, 2023             jing             Initial Creation
 *
 * </pre>
 *
 * @author jing
 * @version 1.0
 */
public class TravelTimesUtil {
    public interface IPWaveModel {
        String getModelName();

        String getModelPath();
    }

    public enum PWaveModel implements IPWaveModel {
        IASP91("iasp91", "/usr/share/ttt/tables/");

        private final String name;

        private final String path;

        PWaveModel(String name, String path) {
            this.name = name;
            this.path = path;
        }

        @Override
        public String getModelName() {
            return name;
        }

        @Override
        public String getModelPath() {
            return path;
        }
    }

    /**
     * Maps depth to a cached lookup object
     *
     * TODO When libseismic is fixed, maybe use an LRUMap with some fixed size
     * as a cache.
     */
    private static Map<Double, PWaveTravelTimeLookup> mapping = new HashMap<>();
    /**
     * TODO when libseismic is fixed, remove this
     */
    static {
        mapping.put(0d, PWaveTravelTimeCurve.create(0.00007185405144,
                0.0543536444, 0.1458801164));
        mapping.put(15d, PWaveTravelTimeCurve.create(0.00006968391701,
                0.05617750219, 0.02294570411));
        mapping.put(30d, PWaveTravelTimeCurve.create(0.00006754304744,
                0.05798243507, 0.107402541));
        mapping.put(40d, PWaveTravelTimeCurve.create(0.0000665535109,
                0.05891791648, 0.1900506355));
        mapping.put(50d, PWaveTravelTimeCurve.create(0.00006594420137,
                0.0596337009, 0.2694740101));
        mapping.put(75d, PWaveTravelTimeCurve.create(0.00006432574386,
                0.06148872862, 0.4778099918));
        mapping.put(100d, PWaveTravelTimeCurve.create(0.00006256796911,
                0.0634402393, 0.7005674027));
    }

    public static PWaveTravelTimeLookup calculatePWaveDisplacement(
            double epicenterDepth) {
        return calculatePWaveDisplacement(PWaveModel.IASP91, epicenterDepth);
    }

    public static PWaveTravelTimeLookup calculatePWaveDisplacement(
            PWaveModel model, double epicenterDepth) {
        /*
         * TODO
         *
         * ISTI's code is not working. The snippet below is a starting point on
         * how to interface with them on getting the PWave travel time. Until
         * then, we will use a couple hardcoded curve formulas
         *
         * TravelTimesLibrary ttLib = SeismicLibrary
         * .getLibraryFragment(TravelTimesLibrary.class);
         *
         * final byte[] nativeModelPath =
         * Native.toByteArray(model.getModelPath()); final byte[]
         * nativeModelName = Native.toByteArray(model.getModelName());
         *
         * DoubleByReference times = new DoubleByReference(); DoubleByReference
         * pVel = new DoubleByReference(); IntByReference numV = new
         * IntByReference();
         *
         * int ierr = ttLib.locationTraveltimesttimesCalculatePVelocity(
         * nativeModelPath, nativeModelName, epicenterDepth, 0, times, pVel,
         * numV); if (ierr == 0) {
         *
         * } else {
         *
         * }
         */
        return getBestModel(epicenterDepth);
    }

    /**
     * TODO when libseismic is fixed, remove this
     */
    private static PWaveTravelTimeLookup getBestModel(double depth) {
        final double depthKm = depth / 1000;
        Set<Double> avail = mapping.keySet();
        double diff = Double.MAX_VALUE;
        for (Double d : avail) {
            double absDiff = Math.abs(depthKm - d);
            if (absDiff < diff) {
                diff = d;
            }
        }
        return mapping.get(diff);
    }
}
