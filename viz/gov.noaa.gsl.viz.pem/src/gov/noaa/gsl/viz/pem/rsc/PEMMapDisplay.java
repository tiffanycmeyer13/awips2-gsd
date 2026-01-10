/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.rsc;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.locationtech.jts.geom.Coordinate;

import com.raytheon.uf.common.time.TimeRange;
import com.raytheon.uf.viz.core.IDisplayPaneContainer;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.AbstractVizResource;
import com.raytheon.uf.viz.core.rsc.LoadProperties;
import com.raytheon.viz.ui.EditorUtil;
import com.raytheon.viz.ui.editor.AbstractEditor;
import com.raytheon.viz.ui.input.InputAdapter;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEventMgrListener;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventManager;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.viz.pem.dialog.PEMDialogConfigManager;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;
import gov.noaa.gsl.viz.pem.plot.PlotConfig;
import gov.noaa.gsl.viz.pem.plot.PlotConfigListener;

public class PEMMapDisplay
        extends AbstractVizResource<PEMMapResourceData, IMapDescriptor>
        implements IPhysicalEventMgrListener {

    /*
     * Plotters used to render the physical events
     */
    private Map<PhysicalEventType, PEPlotter> plotters = new HashMap<>();

    /*
     * Listener for plot config changes, triggering redraws.
     */
    private PlotConfigListener plotConfigListener = new OurPlotConfigListener();

    private AbstractEditor editor;

    private OurMouseAdapter mouseAdapter = new OurMouseAdapter();

    protected PEMMapDisplay(PEMMapResourceData resourceData,
            LoadProperties loadProperties) {
        super(resourceData, loadProperties);
        // TODO Auto-generated constructor stub
        PhysicalEventManager.getInstance().addPEMListener(this);

        plotters.putAll(PEMDialogConfigManager.getInstance().getPlotters());
        for (PEPlotter plotter : plotters.values()) {
            PlotConfig config = plotter.getPlotConfig();
            if (config != null) {
                config.addPlotConfigListener(plotConfigListener);
            }
        }
    }

    @Override
    protected void disposeInternal() {
        // TODO Is this a good thing to do here?
        PhysicalEventManager.getInstance().removePEMListener(this);
        for (PEPlotter plotter : plotters.values()) {
            PlotConfig config = plotter.getPlotConfig();
            if (config != null) {
                config.removePlotConfigListener(plotConfigListener);
            }
        }

        if (editor != null) {
            editor.unregisterMouseHandler(mouseAdapter);
        }

    }

    @Override
    protected void paintInternal(IGraphicsTarget target,
            PaintProperties paintProps) throws VizException {

        Map<PhysicalEventType, List<IPhysicalEvent>> events = PhysicalEventManager
                .getInstance().getPhysicalEvents();

        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : events
                .entrySet()) {

            PEPlotter plotter = plotters.get(entry.getKey());
            if (plotter == null) {
                continue;
            }

            plotter.setPhysicalEvents(entry.getValue());
            plotter.plot(target, paintProps, descriptor, getCapabilities());
        }
    }

    @Override
    public String getName() {
        return "PEM Map Display";
    }

    @Override
    protected void initInternal(IGraphicsTarget target) throws VizException {
        editor = ((AbstractEditor) EditorUtil.getActiveEditor());
        if (editor != null) {
            editor.registerMouseHandler(mouseAdapter);
        }
    }

    @Override
    public void physicalEventAdded(String id, PhysicalEventType type) {
        issueRefresh();
    }

    @Override
    public void physicalEventChanged(String id, PhysicalEventType type) {
        issueRefresh();
    }

    @Override
    public void physicalEventRemoved(String id, PhysicalEventType type) {
        issueRefresh();
    }

    @Override
    public void timeWindowChanged(TimeRange newTimeRange) {
        /*
         * Do nothing. We dont care if the timeWindow changes because we will
         * get notified if and when the set of PhysicalEvents changes as well.
         */
    }

    @Override
    public void activeOptionChanged(ActiveOption newActiveOption) {
        /*
         * Do nothing. We dont care if the activeOnly flag changes because we
         * will get notified if and when the set of PhysicalEvents changes as
         * well. TODO - not being notified of phyevents changing
         */
        issueRefresh();
    }

    @Override
    public void filtersChanged(List<PhysicalEventType> newFilters) {
        issueRefresh();
    }

    @Override
    public void selectionsChanged(Set<String> newSelections) {
        issueRefresh();
    }

    ////////////////////////////////////////////////////////////////////////////////

    private class OurPlotConfigListener implements PlotConfigListener {

        @Override
        public void plotConfigChanged(PlotConfig config) {
            issueRefresh();
        }
    }

    ////////////////////////////////////////////////////////////////////////////////

    private class OurMouseAdapter extends InputAdapter {

        @Override
        public boolean handleDoubleClick(int x, int y, int button) {

            IDisplayPaneContainer container = getResourceContainer();
            if (container == null) {
                return false;
            }

            final double BUFFER_NUM_PIXELS = 7;

            Coordinate lonLatCoord = container.translateClick(x, y);
            Coordinate upLeftCoord = container.translateClick(
                    x - BUFFER_NUM_PIXELS, y - BUFFER_NUM_PIXELS);
            Coordinate upRightCoord = container.translateClick(
                    x + BUFFER_NUM_PIXELS, y - BUFFER_NUM_PIXELS);
            Coordinate lowLeftCoord = container.translateClick(
                    x - BUFFER_NUM_PIXELS, y + BUFFER_NUM_PIXELS);
            Coordinate lowRightCoord = container.translateClick(
                    x + BUFFER_NUM_PIXELS, y + BUFFER_NUM_PIXELS);

            if (lonLatCoord != null && upLeftCoord != null
                    && upRightCoord != null && lowLeftCoord != null
                    && lowRightCoord != null) {
                List<IPhysicalEvent> events = PhysicalEventManager.getInstance()
                        .getPhysicalEventsList();
                for (IPhysicalEvent pEvt : events) {
                    if (pEvt.getLongitude() >= upLeftCoord.x
                            && pEvt.getLongitude() <= upRightCoord.x
                            && pEvt.getLatitude() <= upLeftCoord.y
                            && pEvt.getLatitude() >= lowLeftCoord.y) {
                        PhysicalEventManager.getInstance().setSelected(pEvt);
                        return true;
                    }
                }
            }
            return false;
        }
    }
}
