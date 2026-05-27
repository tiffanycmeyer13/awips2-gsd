/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atomsSeaLevelObs.ui;

import org.eclipse.swt.graphics.RGB;

import com.raytheon.uf.viz.core.DrawableString;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.HorizontalAlignment;
import com.raytheon.uf.viz.core.IGraphicsTarget.VerticalAlignment;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.capabilities.Capabilities;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObs;

/**
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Nov 14, 2022             jing             Initial Creation
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 */
public class SLObsStationNameRenderer {

    private SeaLevelObs slob;

    private Capabilities drawCapabilities = null;

    public SLObsStationNameRenderer(SeaLevelObs slob) {
        if (slob == null) {
            return;
        }
        this.slob = slob;
    }

    public void setCapabilities(Capabilities drawCapabilities) {
        this.drawCapabilities = drawCapabilities;
    }

    /**
     * Plots station name
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plot(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color,
            double[] screenLoc) throws VizException {

        /* Station name */
        String stationName = slob.getStation().getName();
        DrawableString name = new DrawableString(" " + stationName, color);
        name.setCoordinates(screenLoc[0], screenLoc[1]);
        name.verticallAlignment = VerticalAlignment.BOTTOM;
        name.horizontalAlignment = HorizontalAlignment.LEFT;
        target.drawStrings(name);
    }
}
