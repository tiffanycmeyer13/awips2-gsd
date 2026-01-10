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

import java.util.ArrayList;
import java.util.List;

/**
 * A base class implementation for the PEPlotConfig interface.
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
public abstract class PlotConfigBase implements PlotConfig {

    private List<PlotConfigListener> listeners = new ArrayList<>();

    public PlotConfigBase() {
    }

    /**
     * Hhhm shouldnt be public, but helps in some way.
     */
    public void firePlotConfigChanged() {
        firePlotConfigChanged(this);
    }

    @Override
    public void addPlotConfigListener(PlotConfigListener lister) {
        if (lister == null) {
            return;
        }

        listeners.add(lister);
    }

    @Override
    public boolean removePlotConfigListener(PlotConfigListener lister) {
        if (lister == null) {
            return false;
        }

        return listeners.remove(lister);
    }

    @Override
    public void clearPlotConfigListeners() {
        listeners.clear();
    }

    protected void firePlotConfigChanged(PlotConfig config) {
        for (PlotConfigListener listener : listeners) {
            listener.plotConfigChanged(config);
        }
    }
}
