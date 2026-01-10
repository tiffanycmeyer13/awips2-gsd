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
 * Plot / Rendering configuration for Unknown physical events.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023            weingruber             Initial Creation
 *
 * </pre>
 *
 * @author awips
 *
 */
public class UnknownPlotConfig extends GeneralPlotConfig {

    public UnknownPlotConfig() {
        super();
    }

    public void setShowAll() {
        super.setShowAll(true);
    }

    public void setShowNone() {
        super.setShowNone(true);
    }
}
