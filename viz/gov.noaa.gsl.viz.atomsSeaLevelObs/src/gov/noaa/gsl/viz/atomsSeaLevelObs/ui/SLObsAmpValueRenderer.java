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
public class SLObsAmpValueRenderer {

    private static DecimalFormat AMP_FORMATTER = new DecimalFormat("0.00");

    static {
        AMP_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    private SeaLevelObs slob;

    private Capabilities drawCapabilities = null;

    public SLObsAmpValueRenderer(SeaLevelObs slob) {
        if (slob == null) {
            return;
        }
        this.slob = slob;
    }

    public void setCapabilities(Capabilities drawCapabilities) {
        this.drawCapabilities = drawCapabilities;
    }

    /**
     * Plots station amplitude value
     *
     * @param target
     * @param descriptor
     * @throws VizException
     */
    public void plot(IGraphicsTarget target, IMapDescriptor descriptor,
            PaintProperties paintProps, double magnification, RGB color,
            double[] screenLoc) throws VizException {

        String amplString = "NaN";
        Float amplitudeF = slob.getAmplitude();
        if (amplitudeF != null && !amplitudeF.isNaN()) {
            amplString = AMP_FORMATTER.format(amplitudeF) + "m";
        } else {
            amplString = "NaN";
        }
        DrawableString plot = new DrawableString(" " + amplString, color);
        plot.setCoordinates(screenLoc[0], screenLoc[1]);
        plot.verticallAlignment = VerticalAlignment.TOP;
        plot.horizontalAlignment = HorizontalAlignment.LEFT;
        target.drawStrings(plot);
    }
}
