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

import java.text.SimpleDateFormat;
import java.util.TimeZone;

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
 * This render is for display the station forecasts in the map.
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
public class ArrivalTimesRenderer {

    private static final SimpleDateFormat dateFormatter = new SimpleDateFormat(
            "yyyy.MM.dd 'at' HH:mm 'Z'");
    static {
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    }

    private TsunamiStationForecast stnFcst;

    private Capabilities drawCapabilities = null;

    public ArrivalTimesRenderer(TsunamiStationForecast stnFcst) {
        this.stnFcst = stnFcst;
    }

    public void setCapabilities(Capabilities drawCapabilities) {
        this.drawCapabilities = drawCapabilities;
    }

    /**
     * Plots arrival time for a tsu stn forecast.
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plot(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color,
            double[] screenLoc) throws VizException {

        /*
         * Display tsunami station forecast for the selected forecast type and
         * run time
         */
        if (stnFcst == null) {
            return;
        }

        /* Amplitude value and arrival time */
        String arrivalTime = "N/A";
        if (stnFcst.getArrivalTime() != null) {
            arrivalTime = dateFormatter.format(stnFcst.getArrivalTime());
        }
        DrawableString plot = new DrawableString(arrivalTime + " ", color);
        plot.setCoordinates(screenLoc[0], screenLoc[1]);
        plot.verticallAlignment = VerticalAlignment.TOP;
        plot.horizontalAlignment = HorizontalAlignment.RIGHT;
        target.drawStrings(plot);
    }
}
