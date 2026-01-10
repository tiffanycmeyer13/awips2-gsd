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

/**
 * A default implementation of a {@link PWaveTravelTimeLookup}
 *
 * TODO cache the results of the call into libseismic, once libseismic is fixed.
 * This object should contain a map of times to velocity which will then need to
 * be computed into distance.
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
 * @author abenak
 * @version 1.0
 */
public class PWaveTravelTime implements PWaveTravelTimeLookup {
    private final double depth;

    public PWaveTravelTime(double depth) {
        this.depth = depth;
    }

    @Override
    public double getVelocity(double ellapsedMillis) {
        return 0;
    }

    @Override
    public double getDisplacement(double ellapsedMillis) {
        return 0;
    }

    @Override
    public double getDepth() {
        return depth;
    }

}
