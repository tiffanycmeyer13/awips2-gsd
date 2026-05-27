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

import java.awt.geom.Point2D;

import org.eclipse.swt.graphics.RGB;
import org.geotools.referencing.GeodeticCalculator;
import org.locationtech.jts.geom.Coordinate;

import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.LineStyle;
import com.raytheon.uf.viz.core.drawables.IWireframeShape;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;

/**
 * This render is for display a circle of km radius.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023                          Initial Creation
 *
 * </pre>
 *
 * @author
 *
 * @version 1.0
 */
public class RangeRingRenderer {

    private static final int NUM_VERTICES = 50;

    private static final double ANGLE_STEP = 360.0 / NUM_VERTICES;

    private float radiusKm;

    private double screenY;

    private double screenX;

    private static GeodeticCalculator gc = new GeodeticCalculator();

    public RangeRingRenderer(float radiusKm, double[] screenLocation) {
        this.radiusKm = radiusKm;
        this.screenX = screenLocation[0];
        this.screenY = screenLocation[1];
    }

    private Coordinate[] getRing(double screenX, double screenY,
            double radiusKm) {

        Coordinate center = new Coordinate(screenX, screenY);
        gc.setStartingGeographicPoint(center.x, center.y);
        Coordinate ring[] = new Coordinate[NUM_VERTICES + 1];
        for (int i = 0; i < NUM_VERTICES; i++) {
            double azimuth = -180.0 + i * ANGLE_STEP;
            gc.setDirection(azimuth, radiusKm * 1000); // Needs radius in meters
            Point2D p = gc.getDestinationGeographicPoint();
            ring[i] = new Coordinate(p.getX(), p.getY());
        }
        ring[NUM_VERTICES] = ring[0];
        return ring;
    }

    /**
     * Plots ta circle of km radius
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plot(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color) {

        // See RangeRingsLayer for where I got the code from
        try {
            IWireframeShape shape = target.createWireframeShape(false,
                    descriptor);
            double[] worldCenter = descriptor
                    .pixelToWorld(new double[] { screenX, screenY });
            Coordinate[] coords = getRing(worldCenter[0], worldCenter[1],
                    radiusKm);
            shape.addLineSegment(coords);
            target.drawWireframeShape(shape, color, 1.5f, LineStyle.SOLID);
        } catch (VizException ve) {
            ve.printStackTrace(System.err);
        }
    }
}
