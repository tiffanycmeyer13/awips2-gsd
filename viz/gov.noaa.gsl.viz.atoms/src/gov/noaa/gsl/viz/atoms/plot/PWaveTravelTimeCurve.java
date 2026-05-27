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
 * A temporary solution for calculating PWaves. This should be removed once
 * libseismic is fixed.
 *
 * TODO remove me.
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
public abstract class PWaveTravelTimeCurve extends PWaveTravelTime {
    public PWaveTravelTimeCurve(double depth) {
        super(depth);
    }

    @Override
    public double getDisplacement(double ellapsedMillis) {
        final double c0 = getC0();
        final double c1 = getC1();
        final double c2 = getC2();
        final double xSq = Math.pow(ellapsedMillis, 2);
        final double x = ellapsedMillis;
        return (c0 * xSq) + (c1 * x) + c2;
    }

    /**
     * @return Constant multiplier against the squared value
     */
    protected abstract double getC0();

    /**
     * @return Constant multiplier against the x value
     */
    protected abstract double getC1();

    /**
     * @return Constant value
     */
    protected abstract double getC2();

    /**
     * Creates a new {@link PWaveTravelTimeCurve} with the given constants
     *
     * @return
     */
    public static PWaveTravelTimeLookup create(final double c0, final double c1,
            final double c2) {
        return new PWaveTravelTimeCurve(15) {
            @Override
            protected double getC0() {
                return c0;
            }

            @Override
            protected double getC1() {
                return c1;
            }

            @Override
            protected double getC2() {
                return c2;
            }
        };
    }
}
