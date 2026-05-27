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

import java.util.Date;

import org.eclipse.swt.graphics.RGB;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.LineString;

import com.raytheon.uf.common.time.SimulatedTime;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.LineStyle;
import com.raytheon.uf.viz.core.drawables.IWireframeShape;
import com.raytheon.uf.viz.core.drawables.JTSCompiler;
import com.raytheon.uf.viz.core.drawables.JTSCompiler.JTSGeometryData;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.capabilities.Capabilities;
import com.raytheon.uf.viz.core.rsc.capabilities.OutlineCapability;
import com.raytheon.uf.viz.core.rsc.capabilities.ShadeableCapability;

import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import si.uom.SI;

/**
 * This render displays the real-time PWave including the historical every
 * minute with dot line.
 *
 *
 * Only shows the PWave of a seismic event in 20 minutes. The calculation is
 * referred to the TOPS.
 *
 * TODO: Save renderables to avoid repeat rendering.
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
 *
 */
public class PWaveRenderer {

    /**
     * currently set to only draw primary waves that are less than 20 minutes
     * old unit is in milliseconds
     */
    public static final long MAX_AGE_TO_DRAW_PWAVE = 1000l * 60l
            * /* minutes= */20l;

    /**
     * Must be in existence.
     */
    public static final long MIN_AGE_TO_DRAW_PWAVE = 0;

    /**
     * The interval to display P wave history is one minutes
     */
    private static final long PWAVE_HISTORY_INERVAL = 1000l * 60l;

    private IPhysicalEvent event;

    private boolean isHistoricMinutesLine = true;

    public PWaveRenderer(IPhysicalEvent event) {
        this.event = event;
    }

    public void setHistoricMinutesLine(boolean isHistoricMinuesLine) {
        this.isHistoricMinutesLine = isHistoricMinuesLine;
    }

    public void plot(IGraphicsTarget target, PaintProperties paintProps,
            IMapDescriptor descriptor, Capabilities drawCapabilities, RGB color)
            throws VizException, InterruptedException {
        /* Draw P wave in 20 minutes if seismic plot type includes P wave */
        Date originTime = event.getRefTime();
        long timeElapsed = SimulatedTime.getSystemTime().getMillis()
                - originTime.getTime();
        /* check if event age is < max age */
        if (timeElapsed < MAX_AGE_TO_DRAW_PWAVE
                && timeElapsed > MIN_AGE_TO_DRAW_PWAVE) {
            Coordinate originLocation = new Coordinate();
            originLocation.x = event.getLongitude();
            originLocation.y = event.getLatitude();
            originLocation.z = ((SeismicEventData) event.getData()).getDepth();
            /* Draw event if young enough */
            paintPWaveAndHistory(target, paintProps, originLocation, originTime,
                    descriptor, drawCapabilities, color);
        }
    }

    /**
     * Paint the current and history P waves. The history P wave interval is 1
     * minutes.
     *
     * @param target
     * @param paintProps
     * @param epicenter
     * @param origin
     * @param descriptor
     * @throws VizException
     * @throws InterruptedException
     */
    private void paintPWaveAndHistory(IGraphicsTarget target,
            PaintProperties paintProps, Coordinate epicenter, Date origin,
            IMapDescriptor descriptor, Capabilities drawCapabilities, RGB color)
            throws VizException, InterruptedException {
        long timeElapsed = SimulatedTime.getSystemTime().getMillis()
                - origin.getTime();
        paintPWave(target, paintProps, epicenter, origin, 0l, descriptor, false,
                drawCapabilities, color);
        if (isHistoricMinutesLine) {
            int i = 1;
            while (i * PWAVE_HISTORY_INERVAL < timeElapsed) {
                long timei = i * PWAVE_HISTORY_INERVAL;
                paintPWave(target, paintProps, epicenter, null, timei,
                        descriptor, true, drawCapabilities, color);
                i++;
            }
        }
    }

    /**
     * paints a primary wave
     *
     * @param target
     * @param paintProps
     * @param epicenter
     *            coordinate latlon of the epicenter
     * @param origin
     *            time of origin
     * @throws VizException
     */
    @SuppressWarnings("unused")
    private void paintPWave(IGraphicsTarget target, PaintProperties paintProps,
            Coordinate epicenter, Date origin, long ellapsedMillis,
            IMapDescriptor descriptor, boolean isHistoryPWave,
            Capabilities drawCapabilities, RGB color) throws VizException {
        /* calculate */
        double distanceEpi;
        if (!isHistoryPWave) {
            distanceEpi = PWaveCalculateUtil.predictDistance(epicenter, origin);
        } else {
            distanceEpi = PWaveCalculateUtil.predictDistance(epicenter,
                    ellapsedMillis);
        }
        double distance = PWaveCalculateUtil
                .convertGeocentricDegreeToSILength(distanceEpi, SI.METRE);
        int numVertices = calculateNumVertices(paintProps, epicenter, distance,
                descriptor);
        double degreeIncrement = 360.0 / numVertices;
        Coordinate[] pWaveVertices = new Coordinate[numVertices + 1];
        /* populate array */
        for (int i = 0; i < pWaveVertices.length; i++) {
            pWaveVertices[i] = PWaveCalculateUtil.calculateLocation(epicenter,
                    degreesToAzimuth(degreeIncrement * i), distance);
        }
        pWaveVertices[numVertices] = new Coordinate(pWaveVertices[0]);
        /* Create pWave linestring */
        LineString ls = new GeometryFactory().createLineString(pWaveVertices);
        /* handle world wrap */
        IWireframeShape wireframeShape = target.createWireframeShape(false,
                descriptor.getGridGeometry());
        JTSCompiler jtsCompiler = new JTSCompiler(null, wireframeShape,
                descriptor);
        JTSGeometryData geomData = jtsCompiler.createGeometryData();
        geomData.setWorldWrapCorrect(true);
        jtsCompiler.handle(ls, geomData);

        /* draw wireframeshape */
        float opacity = drawCapabilities
                .getCapability(null, ShadeableCapability.class).getOpacity();
        float lineWidth = drawCapabilities
                .getCapability(null, OutlineCapability.class).getOutlineWidth();
        LineStyle lineStyle = drawCapabilities
                .getCapability(null, OutlineCapability.class).getLineStyle();
        if (isHistoryPWave) {
            lineStyle = LineStyle.DASHED;
        }
        target.drawWireframeShape(wireframeShape, color, lineWidth, lineStyle,
                opacity);
        /* free up memory */
        wireframeShape.dispose();
    }

    /**
     * converts degrees of a circle where 0 starts at the northernmost point (0
     * to 360) to azimuth degrees (0 to 180, then -179.9R to -0.1R)
     *
     * @param degrees
     *            degrees of circle
     * @return degrees of azimuth
     */
    private static double degreesToAzimuth(double degrees) {
        degrees = degrees % 360;
        if (degrees > 180.0) {
            degrees -= 360;
        }
        return degrees;
    }

    /**
     * Calculates the minimum number of vertices required to accurately draw a
     * circle based on the amount of screen pixels in the viewing area
     *
     * @return an ideal number of vertices for a circle
     * @throws InterruptedException
     */
    private int calculateNumVertices(PaintProperties paintProps,
            Coordinate epicenter, double distanceInMeters,
            IMapDescriptor descriptor) {
        /* specify the number of directions checked to find longest distance */
        final int NUM_TEST_DIRECTIONS = 4;
        final double degreeIncrement = 360.0 / NUM_TEST_DIRECTIONS;
        double longestDistance = 0.0;
        /* declare two points for a radius */
        double[] pointA = descriptor
                .worldToPixel(new double[] { epicenter.x, epicenter.y });
        double[] pointB = null;
        /*
         * find the worst case point B, namely the point on the pwave that is
         * farthest from the epicenter in pixel space between north, south,
         * east, and west
         */
        for (int i = 0; i < NUM_TEST_DIRECTIONS; i++) {
            Coordinate testDestination = PWaveCalculateUtil.calculateLocation(
                    epicenter, degreesToAzimuth(i * degreeIncrement),
                    distanceInMeters);
            double testDistance = epicenter.distance(testDestination);
            if (testDistance > longestDistance) {
                pointB = new double[] { testDestination.x, testDestination.y };
                longestDistance = testDistance;
            }
        }
        /* distance formula */
        double radius = Math.sqrt(Math.pow(pointB[0] - pointA[0], 2)
                + Math.pow(pointB[1] - pointA[1], 2));
        /* circumference of a circle */
        double circumference = 2 * Math.PI * radius;
        /* scale circumference for current zoom */
        double scalar = paintProps.getCanvasBounds().width
                / paintProps.getView().getExtent().getWidth();
        int numVertices = (int) Math.ceil(circumference * scalar);
        /* fail safe threshold for extreme cases */
        if (numVertices < 8) {
            numVertices = 8;
        } else if (numVertices > 5000) {
            numVertices = 5000;
        }
        /* return ideal number of vertices */
        return numVertices;
    }
}
