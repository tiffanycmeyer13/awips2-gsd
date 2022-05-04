package gov.noaa.gsd.viz.ensemble.util;

import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.RGB;

/**
 * This class is used to map unique colors to given ensemble perturbation
 * members, which are identified by their hard-coded perturbation memeber names
 * (ctl1, ctl2, n1, n2 ... p4, p5). It has been created in support of
 * simplifying the process of allowing the user to color an entire ensemble set
 * of members using a color gradient.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date          Ticket#  Engineer  Description
 * ------------- -------- --------- --------------------------------------------
 * Oct 08, 2014  5056     polster   Initial creation
 * Jun 19,2021   93248    srussell  Updated getGradientByEnsembleId() to set
 *                                  totalSteps to the number of rscs instead of
 *                                  the hardcoded workaround of 20. Added
 *                                  getResourceCount().
 * Nov 15, 2021  97771    srussell  Updated getGradientColor()
 * May 03, 2022  103658   tjensen   Make EnsembleGFESColorChooser generic for
 *                                  any Ensemble models
 *
 * </pre>
 *
 * @author polster
 */
public class ChosenColors {

    static public ChosenColors getInstance() {
        if (SINGLETON == null) {
            SINGLETON = new ChosenColors();
        }
        return SINGLETON;
    }

    static private ChosenColors SINGLETON = null;

    private ChosenColors() {

    }

    private Color color = GlobalColor.get(GlobalColor.NEON_PURPLE);

    public Color getColor() {
        if (color.isDisposed()) {
            color = GlobalColor.get(GlobalColor.NEON_PURPLE);
        }
        return color;
    }

    public void setColor(Color c) {
        color = c;
    }

    /*-
     *
     * Create a color gradient by taking the user chosen color, getting the
     * HSB ( hue, saturation, brightness ) values, setting saturation to
     * the number of the current resource divided by the total number of
     * resources. Then use the fractioned saturation values to make a gradient
     * of shades of the user chosen color.
     *
     * int totalPerturbations - Total number of perturbations/ child resources
     *
     * int indexCurrPerturbation
     *
     *
     */

    public Color getGradientColor(int totalPerturbations,
            int indexCurrPerturbation) {

        float saturationFloor = 0.200f;
        float leftOverSatRange = 0.80f;
        float saturationIncrement = leftOverSatRange / (totalPerturbations - 1);

        RGB rgb = color.getRGB();
        float[] hsb = rgb.getHSB();

        if (indexCurrPerturbation > 1
                && indexCurrPerturbation < totalPerturbations) {
            hsb[1] = (--indexCurrPerturbation * saturationIncrement)
                    + saturationFloor;
        } else if (indexCurrPerturbation == totalPerturbations) {
            hsb[1] = 1.0f;
        } else {
            hsb[1] = saturationFloor;
        }

        RGB nrgb = new RGB(hsb[0], hsb[1], hsb[2]);

        return SWTResourceManager.getColor(nrgb);

    }

}
