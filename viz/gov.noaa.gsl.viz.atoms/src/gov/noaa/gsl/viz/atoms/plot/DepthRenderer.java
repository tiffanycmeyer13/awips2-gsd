/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atoms.plot;

import java.math.RoundingMode;
import java.text.DecimalFormat;

import javax.measure.MetricPrefix;
import javax.measure.UnitConverter;

import org.eclipse.swt.graphics.RGB;

import com.raytheon.uf.viz.core.DrawableString;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.HorizontalAlignment;
import com.raytheon.uf.viz.core.IGraphicsTarget.VerticalAlignment;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;

import si.uom.SI;
import systems.uom.common.USCustomary;

/**
 * This render is for display a depth in the map.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023             jing             Initial Creation
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 */
public class DepthRenderer {

    private static final UnitConverter MILES_TO_KM = USCustomary.MILE
            .getConverterTo(MetricPrefix.KILO(SI.METRE));

    private static DecimalFormat DEPTH_FORMATTER = new DecimalFormat("0.0");

    static {
        DEPTH_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    /*
     * In Miles
     */
    private double depthMi;

    private double screenY;

    private double screenX;

    public DepthRenderer(double depthMi, double[] screenLocation) {
        this.depthMi = depthMi;
        this.screenX = screenLocation[0];
        this.screenY = screenLocation[1];
    }

    /**
     * Plots the depth of a seismic event.
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plot(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color) {

        try {
            if (((Double) screenX).isNaN() || ((Double) screenY).isNaN()) {
                return;
            }
            DrawableString string = new DrawableString(" "
                    + DEPTH_FORMATTER.format(depthMi) + "mi/"
                    + DEPTH_FORMATTER.format(
                            (float) MILES_TO_KM.convert(depthMi))
                    + "km", color);
            string.setCoordinates(screenX, screenY);
            string.verticallAlignment = VerticalAlignment.TOP;
            string.horizontalAlignment = HorizontalAlignment.LEFT;
            target.drawStrings(string);

        } catch (VizException ve) {
            ve.printStackTrace(System.err);
        }
    }

}
