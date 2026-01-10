/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.plot;

import java.util.Collection;
import java.util.LinkedList;

import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.map.IMapDescriptor;

import gov.noaa.gsl.common.dataplugin.pem.ILonLat;

/**
 * Implementation of Progressive Disclosure based on minimum screen / pixel
 * distance between points. Also considers on/off screen.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023            weingruber             Initial Creation
 *
 * </pre>
 *
 * @author awips
 *
 */
public class ProgressiveDisclosureStrategy<T extends ILonLat> {

    private int minPixelDistance = 50;

    private double magnification = 1.0;

    private double density = 1.0;

    private PaintProperties paintProps;

    private IMapDescriptor mapDescriptor;

    public ProgressiveDisclosureStrategy(PaintProperties paintProps,
            IMapDescriptor mapDescriptor) {
        if (paintProps == null || mapDescriptor == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + " constructor requires non-null arguments");
        }

        this.paintProps = paintProps;
        this.mapDescriptor = mapDescriptor;
    }

    public int getMinPixelDistance() {
        return minPixelDistance;
    }

    public void setMinPixelDistance(int minPixelDistance) {
        this.minPixelDistance = minPixelDistance;
    }

    public double getMagnification() {
        return magnification;
    }

    public void setMagnification(double magnification) {
        this.magnification = magnification;
    }

    public double getDensity() {
        return density;
    }

    public void setDensity(double density) {
        this.density = density;
    }

    public PaintProperties getPaintProps() {
        return paintProps;
    }

    public void setPaintProps(PaintProperties paintProps) {
        this.paintProps = paintProps;
    }

    public IMapDescriptor getMapDescriptor() {
        return mapDescriptor;
    }

    public void setMapDescriptor(IMapDescriptor mapDescriptor) {
        this.mapDescriptor = mapDescriptor;
    }

    /**
     * Given a list of candidate points, returns a Collection of them that are
     * not too close to each other and are on the screen. Each candidate is
     * first checked if it's on screen, and if not, it's omitted from the
     * result. Then the candidate is checked to see if it's too close to an
     * already "drawn" or previously included candidate, and if so, it's omitted
     * from the result.
     *
     * @param candidates
     * @return Collection of points to draw
     */
    public Collection<T> progDisc(Collection<T> candidates,
            IGraphicsTarget target) {

        Collection<T> pointsToDraw = new LinkedList<>();

        if (candidates == null || density == 0.0) {
            return pointsToDraw;
        }

        double pixelDist = minPixelDistance / density;
        pixelDist = pixelDist * magnification;

        double[] pointPixelXY = new double[2];
        double[] otherPointPixelXY = new double[2];
        for (T point : candidates) {
            boolean draw = true;

            pointPixelXY[0] = point.getLongitude();
            pointPixelXY[1] = point.getLatitude();
            pointPixelXY = mapDescriptor.worldToPixel(pointPixelXY);

            if (!paintProps.getView().getExtent().contains(pointPixelXY)) {
                draw = false;
            } else {
                // Is this even correct? Going from world to pixel (which is
                // assumed to be the same as grid??) to screen? Seems to work.
                pointPixelXY = paintProps.getView().gridToScreen(pointPixelXY,
                        target);

                // Check progressive disclosure
                for (T otherPoint : pointsToDraw) {
                    // Make sure a does not overlap with otherStnFcst
                    otherPointPixelXY[0] = otherPoint.getLongitude();
                    otherPointPixelXY[1] = otherPoint.getLatitude();

                    otherPointPixelXY = mapDescriptor
                            .worldToPixel(otherPointPixelXY);
                    otherPointPixelXY = paintProps.getView()
                            .gridToScreen(otherPointPixelXY, target);

                    double deltaX = otherPointPixelXY[0] - pointPixelXY[0];
                    double deltaY = otherPointPixelXY[1] - pointPixelXY[1];

                    // Absolute value logic inlined for performance, according
                    // to RTS
                    deltaX = (deltaX <= 0.0D) ? 0.0D - deltaX : deltaX;
                    deltaY = (deltaY <= 0.0D) ? 0.0D - deltaY : deltaY;

                    if (deltaX < pixelDist && deltaY < pixelDist) {
                        draw = false;
                        break;
                    }
                }
            }
            if (draw) {
                pointsToDraw.add(point);
            }
        }
        return pointsToDraw;
    }
}
