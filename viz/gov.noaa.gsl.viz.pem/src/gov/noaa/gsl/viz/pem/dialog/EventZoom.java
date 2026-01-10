package gov.noaa.gsl.viz.pem.dialog;

import com.raytheon.uf.viz.core.IDisplayPane;
import com.raytheon.uf.viz.core.drawables.IDescriptor;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.viz.ui.EditorUtil;
import com.raytheon.viz.ui.editor.VizMultiPaneEditor;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

/**
 * This class zooms in and moves to the event location. Also provides interface
 * to set zoom level and center.
 *
 * TODO:
 *
 * -The zoom level is fixed currently. May need the auto zoom level calculation.
 *
 * -The blinkEnent() and animation() are optional features.
 *
 * @author jing 10/28/2022
 */
public class EventZoom {

    private static final double DEFAULT_ZOOMLEVEL = 0.5d;

    private IPhysicalEvent event;

    private boolean isAutoZoomLevel = false;

    public EventZoom(IPhysicalEvent event) {
        this.event = event;
    }

    public boolean isAutoZoomLevel() {
        return isAutoZoomLevel;
    }

    public void setAutoZoomLevel(boolean isAutoZoomLevel) {
        this.isAutoZoomLevel = isAutoZoomLevel;
    }

    /**
     * Zooms in and moves to the event location for as the default zoom level.
     *
     */
    public void zoomToEventLocation() {
        double[] eventLocation = { event.getLongitude(), event.getLatitude() };

        // Check if it's in the window and if so, dont do anything
        IDisplayPane pane = getEditor().getActiveDisplayPane();
        IDescriptor desc = pane.getRenderableDisplay().getDescriptor();
        if (desc instanceof IMapDescriptor) {
            IMapDescriptor mapDesc = (IMapDescriptor) desc;
            double[] pixelLoc = mapDesc.worldToPixel(eventLocation);
            if (pane.getRenderableDisplay().getView().getExtent()
                    .contains(pixelLoc)) {
                return;
            }
        }

        setZoom(calculateZoom(), eventLocation);
    }

    /**
     * Set the zoom level and center.
     *
     * @param zoomLevel
     *            Zoom level to be used.
     * @param zoomCenter
     *            Zoom center point, as an array holding longitude and latitude,
     *            to be used.
     */
    public void setZoom(double zoomLevel, double[] zoomCenter) {

        // Get the pane.
        IDisplayPane pane = getEditor().getActiveDisplayPane();

        // Reset the extent.
        pane.getRenderableDisplay().getExtent().reset();

        // Recenter and zoom as appropriate, then refresh.
        pane.getRenderableDisplay().recenter(zoomCenter);
        pane.getRenderableDisplay().zoom(zoomLevel);
        pane.refresh();
    }

    private double calculateZoom() {
        // TODO auto zoom level

        return DEFAULT_ZOOMLEVEL;
    }

    private VizMultiPaneEditor getEditor() {
        return (VizMultiPaneEditor) EditorUtil.getActiveEditor();
    }

}
