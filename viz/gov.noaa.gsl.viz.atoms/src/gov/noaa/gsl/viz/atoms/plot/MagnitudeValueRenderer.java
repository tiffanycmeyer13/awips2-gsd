package gov.noaa.gsl.viz.atoms.plot;

import java.math.RoundingMode;
import java.text.DecimalFormat;

import org.eclipse.swt.graphics.RGB;

import com.raytheon.uf.viz.core.DrawableString;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.HorizontalAlignment;
import com.raytheon.uf.viz.core.IGraphicsTarget.VerticalAlignment;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;

public class MagnitudeValueRenderer {

    private static DecimalFormat MAG_FORMATTER = new DecimalFormat("0.00");

    static {
        MAG_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    private double magnitude;

    private double screenY;

    private double screenX;

    public MagnitudeValueRenderer(double magnitude, double[] screenLocation) {
        this.magnitude = magnitude;
        this.screenY = screenLocation[1];
        this.screenX = screenLocation[0];
    }

    /**
     * Plots the magnitude value string of a seismic event.
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plotMagnitude(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color) {

        try {
            if (((Double) screenX).isNaN() || ((Double) screenY).isNaN()) {
                return;
            }
            DrawableString string = new DrawableString(
                    "M" + MAG_FORMATTER.format(magnitude) + " ", color);
            string.setCoordinates(screenX, screenY);
            string.verticallAlignment = VerticalAlignment.TOP;
            string.horizontalAlignment = HorizontalAlignment.RIGHT;
            target.drawStrings(string);
        } catch (VizException ve) {
            ve.printStackTrace(System.err);
        }
    }
}
