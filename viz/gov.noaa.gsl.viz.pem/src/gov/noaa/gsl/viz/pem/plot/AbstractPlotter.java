package gov.noaa.gsl.viz.pem.plot;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.swt.widgets.TabFolder;

import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.capabilities.Capabilities;

/**
 * Plotter / Renderer for the PEMMapDisplay that can render it's "data".
 *
 * @author awips
 *
 */
public abstract class AbstractPlotter {

    /**
     * The configuration used by this Plotter
     */
    private PlotConfig config;

    /**
     * Our listener for our PlotConfig
     */
    private PlotConfigListener regularPlotConfigListener = new OurRegularPlotConfigListener();

    /**
     * Our listener for all child configs
     */
    private PlotConfigListener childPlotConfigListener = new OurChildPlotConfigListener();

    /**
     * The thing(s) we're plotting
     */
    private Object data;

    /**
     * True when the config widgets have been instantiated
     */
    private boolean buildConfigWidgetsComplete = false;

    /**
     * Aggregated child plotters
     */
    private List<AbstractPlotter> childPlotters = new ArrayList<>();

    public AbstractPlotter(PlotConfig config) {
        this.config = config;
        this.config.addPlotConfigListener(regularPlotConfigListener);
    }

    public PlotConfig getPlotConfig() {
        return config;
    }

    protected void setData(Object data) {
        this.data = data;
    }

    protected Object getData() {
        return data;
    }

    /**
     * This default implementation will do nothing, and then delegate further
     * drawing to the childPlotters.
     *
     * @param pePlotter
     * @param target
     * @param paintProps
     * @param descriptor
     * @param drawCapabilities
     */
    public void plot(IGraphicsTarget target, PaintProperties paintProps,
            IMapDescriptor descriptor, Capabilities drawCapabilities) {

        // Do your own plotting here.

        // And then delegate to the child plotters
        plotChildren(target, paintProps, descriptor, drawCapabilities);
    }

    protected void plotChildren(IGraphicsTarget target,
            PaintProperties paintProps, IMapDescriptor descriptor,
            Capabilities drawCapabilities) {

        for (AbstractPlotter childPlotter : childPlotters) {
            childPlotter.plot(target, paintProps, descriptor, drawCapabilities);
        }
    }

    public void addChildPlotter(AbstractPlotter plotter) {
        if (plotter != null) {
            childPlotters.add(plotter);
            plotter.getPlotConfig()
                    .addPlotConfigListener(childPlotConfigListener);
        }
    }

    public boolean removeChildPlotter(AbstractPlotter plotter) {
        if (plotter != null) {
            plotter.getPlotConfig()
                    .removePlotConfigListener(childPlotConfigListener);
            return childPlotters.remove(plotter);
        }
        return false;
    }

    public void clearChildPlotters() {
        for (AbstractPlotter plotter : childPlotters) {
            plotter.getPlotConfig()
                    .removePlotConfigListener(childPlotConfigListener);
        }
        childPlotters.clear();
    }

    protected List<AbstractPlotter> getChildPlotters() {
        return childPlotters;
    }

    /**
     * Override to reinitialize already created configuration widgets
     */
    protected abstract void reinitConfigWidgets();

    /**
     * Override to create and layout your configuration widgets
     *
     * @param tabFolder
     */
    public abstract void buildPlotterConfigTabItems(TabFolder tabFolder);

    /**
     * Marks the configuration widgets as "built / completed"
     *
     * @param complete
     */
    protected void setBuildConfigWidgetsComplete(boolean complete) {
        buildConfigWidgetsComplete = complete;
    }

    /**
     * Returns whether the widgets have been built / created
     *
     * @return
     */
    protected boolean isBuildConfigWidgetsComplete() {
        return buildConfigWidgetsComplete;
    }

    private class OurChildPlotConfigListener implements PlotConfigListener {

        @Override
        public void plotConfigChanged(PlotConfig config) {
            getPlotConfig().firePlotConfigChanged();
        }
    }

    private class OurRegularPlotConfigListener implements PlotConfigListener {
        @Override
        public void plotConfigChanged(PlotConfig config) {
            if (config != null && config == getPlotConfig()) {
                reinitConfigWidgets();
            }
        }
    }

    protected void firePlotConfigChanged(PlotConfig config) {
        getPlotConfig().firePlotConfigChanged();
    }
}