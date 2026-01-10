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
 * An object that looksup the PWave displacement and velocity, given a depth and
 * elapsed millisecond
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
 *
 * </pre>
 *
 * @author abenak
 * @version 1.0
 */
public interface PWaveTravelTimeLookup {

    double getVelocity(double ellapsedMillis);

    double getDisplacement(double ellapsedMillis);

    double getDepth();
}
