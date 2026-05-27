/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.plot;

/**
 * Interface representing Physical Event Plotter or Rendering Configuration.
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
public interface PlotConfig {

    /**
     * Child plotters can be added to a parent plotter, and the parent will be
     * notified when a child PlotConfig changes. By providing the
     * firePlotConfigChanged() method, the parent PLOTTER can fire a
     * notification for it's own PlotConfig indicating that a child CONFIG has
     * changed (and therefore the parent's PlotConfig as well).
     */
    void firePlotConfigChanged();

    void addPlotConfigListener(PlotConfigListener lister);

    boolean removePlotConfigListener(PlotConfigListener lister);

    void clearPlotConfigListeners();
}
