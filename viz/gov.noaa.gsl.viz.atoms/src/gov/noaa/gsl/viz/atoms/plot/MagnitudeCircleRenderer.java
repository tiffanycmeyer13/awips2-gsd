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

import org.eclipse.swt.graphics.RGB;

import com.raytheon.uf.viz.core.DrawableCircle;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;

import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

/**
 * This render is for display a magnitude in the map. Current solution is a
 * simple liner scale mapping(2-2.0, 4-4.0, 6-6.0, 8-8.0, 10-10.0) from
 * magnitude value to the screen pixel, plot the value, plus circles(2.0, 4.0,
 * 6.0, 8.0...), is more direct The TOPS mapping solution in the
 * SeismicEventMapResource is with none liner mapping(0-0, 4-6.0, 8-7.5,
 * 16-9.0), with circles(1,2,3...10). Which one is better?
 *
 * TODO: May be a combined solution, none liner mapping with circles(2.0, 4.0,
 * 6.0, 8.0...) is better. A scale bar to represent the mapping maybe more
 * helpful to user under standing.
 *
 * TODO: This is the prototyping code. For the operational version,
 * MagnitudeRenter is called by updating to build MagnitudeRenderables<event>
 * (Circles,Strings...) only, need not rebuild them when painting, for better
 * performance
 *
 * TODO: The scale bar and color map are shared by multiple renders, how to
 * manager them?
 *
 * TODO: Use D2D density capability if need.
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
public class MagnitudeCircleRenderer {

    private static final double VALUE_PIXEL_RATE = 2d;

    private static final double CIRCLE_VALUE_INTERVAL = 2d;

    private double magnitude;

    private double screenY;

    private double screenX;

    private boolean isFillCircle = false;

    public MagnitudeCircleRenderer(double magnitude, double[] screenLocation) {
        this.magnitude = magnitude;
        this.screenX = screenLocation[0];
        this.screenY = screenLocation[1];
    }

    /**
     * Plots the magnitude of a seismic event.
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plotMagnitude(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color) {

        try {
            DrawableCircle circle = new DrawableCircle();
            if (((Double) screenX).isNaN() || ((Double) screenY).isNaN()) {
                return;
            }
            circle.setCoordinates(screenX, screenY);
            circle.basics.color = color;
            circle.filled = false;
            circle.screenRadius = magnitude;
            circle.screenRadius = getEventScreenCircleRadius(
                    circle.screenRadius, magnification);
            if (!isFillCircle) {
                target.drawCircle(circle);
                int circleNum = (int) (magnitude / CIRCLE_VALUE_INTERVAL);
                for (int i = 1; i <= circleNum; i++) {
                    circle.screenRadius = i * CIRCLE_VALUE_INTERVAL;
                    circle.screenRadius = getEventScreenCircleRadius(
                            circle.screenRadius, magnification);
                    target.drawCircle(circle);
                }
            } else {
                circle.filled = true;
                target.drawCircle(circle);
            }
        } catch (VizException ve) {
            ve.printStackTrace(System.err);
        }
    }

    public static double getEventScreenCircleRadius(IMapDescriptor descriptor,
            double magnification, IPhysicalEvent event) {
        double[] screenLocation = descriptor.worldToPixel(
                new double[] { event.getLongitude(), event.getLatitude() });
        if (((Double) screenLocation[0]).isNaN()
                || ((Double) screenLocation[1]).isNaN()) {
            return Double.NaN;
        }
        double screenRadius = ((SeismicEventData) (event.getData()))
                .getPrefMagnitude();
        try {
            return getEventScreenCircleRadius(screenRadius, magnification);
        } catch (Exception e) {
            return Double.NaN;
        }
    }

    private static double getEventScreenCircleRadius(double screenRadius,
            double magnification) {
        screenRadius *= VALUE_PIXEL_RATE * magnification;
        return screenRadius;
    }

    public boolean isFillCircle() {
        return isFillCircle;
    }

    public void setFillCircle(boolean isFillCircle) {
        this.isFillCircle = isFillCircle;
    }
}
