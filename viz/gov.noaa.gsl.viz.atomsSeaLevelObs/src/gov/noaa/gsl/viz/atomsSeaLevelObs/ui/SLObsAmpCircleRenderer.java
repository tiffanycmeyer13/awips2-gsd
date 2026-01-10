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

import com.raytheon.uf.viz.core.DrawableCircle;
import com.raytheon.uf.viz.core.IGraphicsTarget;
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
 * Nov 14, 2022             we             Initial Creation
 *
 * </pre>
 *
 * @author we
 *
 * @version 1.0
 */
public class SLObsAmpCircleRenderer {

    /* default linear unit mapping for amplitude to screen */
    private static final double VALUE_PIXEL_RATE = 10d;

    private SeaLevelObs slob;

    private Capabilities drawCapabilities = null;

    public SLObsAmpCircleRenderer(SeaLevelObs slob) {
        if (slob == null) {
            return;
        }
        this.slob = slob;
    }

    public void setCapabilities(Capabilities drawCapabilities) {
        this.drawCapabilities = drawCapabilities;
    }

    /**
     * Plots station amplitude circle
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plot(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color,
            double[] screenLoc) throws VizException {

        Float amplitudeF = slob.getAmplitude();
        if (amplitudeF == null || amplitudeF.isNaN()) {
            return;
        }

        DrawableCircle circle = new DrawableCircle();
        circle.setCoordinates(screenLoc[0], screenLoc[1]);
        circle.basics.color = color;
        circle.screenRadius = amplitudeF.doubleValue();
        circle.screenRadius = getStationScreenCircleRadius(circle.screenRadius,
                magnification);
        target.drawCircle(circle);
    }

    private static double getStationScreenCircleRadius(double screenRadius,
            double magnification) {
        screenRadius *= VALUE_PIXEL_RATE * magnification;
        return screenRadius;
    }
}
