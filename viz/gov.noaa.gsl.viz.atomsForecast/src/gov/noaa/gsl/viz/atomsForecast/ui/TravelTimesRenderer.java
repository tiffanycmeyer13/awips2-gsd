package gov.noaa.gsl.viz.atomsForecast.ui;

import java.util.concurrent.TimeUnit;

import org.eclipse.swt.graphics.RGB;

import com.raytheon.uf.common.time.SimulatedTime;
import com.raytheon.uf.viz.core.DrawableString;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.HorizontalAlignment;
import com.raytheon.uf.viz.core.IGraphicsTarget.VerticalAlignment;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.capabilities.Capabilities;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiStationForecast;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

public class TravelTimesRenderer {

    /*
     * Either fromNow, or from origin time of the physical event
     */
    private boolean fromNow = false;

    private IPhysicalEvent event;

    private TsunamiStationForecast stnFcst;

    private Capabilities drawCapabilities = null;

    public TravelTimesRenderer(IPhysicalEvent phyEvt,
            TsunamiStationForecast stnFcst) {
        this.stnFcst = stnFcst;
        this.event = phyEvt;
    }

    public void setCapabilities(Capabilities drawCapabilities) {
        this.drawCapabilities = drawCapabilities;
    }

    /*
     * If fromNow, travel times will be calculated as arrivalTime -
     * getSimulatedTime(). Otherwise travel times will be calculated as
     * arrivalTime - event.getOriginTime()
     */
    public void setFromNow(boolean fromNow) {
        this.fromNow = fromNow;
    }

    public boolean isFromNow() {
        return fromNow;
    }

    private long getSimulatedTime() {
        SimulatedTime sim = SimulatedTime.getSystemTime();
        return sim.getMillis();
    }

    /**
     * Plots travel time for a tsu stn forecast.
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
        if (event == null || stnFcst == null) {
            return;
        }

        String elapsedTimeString = "N/A";
        if (stnFcst.getArrivalTime() != null) {
            long elapsedTimeMillis;
            if (fromNow) {
                elapsedTimeMillis = stnFcst.getArrivalTime().getTime()
                        - getSimulatedTime();
            } else {
                elapsedTimeMillis = stnFcst.getArrivalTime().getTime()
                        - event.getRefTime().getTime();
            }
            long HH = TimeUnit.MILLISECONDS.toHours(elapsedTimeMillis);
            long MM = TimeUnit.MILLISECONDS.toMinutes(elapsedTimeMillis) % 60;
            // long SS = TimeUnit.MILLISECONDS.toSeconds(elapsedTimeMillis) %
            // 60;
            // elapsedTimeString = String.format("%02d:%02d:%02d", HH, MM, SS);
            elapsedTimeString = String.format("%02d:%02d", HH, MM);
        }
        DrawableString plot = new DrawableString(elapsedTimeString + " ",
                color);
        plot.setCoordinates(screenLoc[0], screenLoc[1]);
        plot.verticallAlignment = VerticalAlignment.TOP;
        plot.horizontalAlignment = HorizontalAlignment.RIGHT;
        target.drawStrings(plot);
    }

}
