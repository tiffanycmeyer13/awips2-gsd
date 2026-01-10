/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atomsForecast.ui;

import org.eclipse.swt.graphics.RGB;

import com.raytheon.uf.viz.core.DrawableString;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.HorizontalAlignment;
import com.raytheon.uf.viz.core.IGraphicsTarget.VerticalAlignment;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.capabilities.Capabilities;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiStationForecast;

/**
 * This render is for display the station forecasts' station customid string in
 * the map.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * 6/1/2023            weingruber             Initial Creation
 *
 * </pre>
 *
 * @author weingruber
 *
 * @version 1.0
 */
public class ForecastStationIdRenderer {

    private TsunamiStationForecast stnFcst;

    private Capabilities drawCapabilities = null;

    public ForecastStationIdRenderer(TsunamiStationForecast forecast) {
        this.stnFcst = forecast;
    }

    public void setCapabilities(Capabilities drawCapabilities) {
        this.drawCapabilities = drawCapabilities;
    }

    /**
     * 
     * @param target
     * @param descriptor
     * @param paintProps
     * @param magnification
     * @param color
     * @param screenLoc
     *            pixel coords, x and y
     * @throws VizException
     */
    public void plot(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color,
            double[] screenLoc) throws VizException {

        if (stnFcst == null) {
            return;
        }

        DrawableString plot = new DrawableString(
                stnFcst.getStation().getCustomId() + " ", color);
        plot.setCoordinates(screenLoc[0], screenLoc[1]);
        plot.verticallAlignment = VerticalAlignment.BOTTOM;
        plot.horizontalAlignment = HorizontalAlignment.RIGHT;
        target.drawStrings(plot);
    }
}
