package gov.noaa.gsl.viz.atoms.plot;

import gov.noaa.gsl.viz.pem.plot.PlotConfigBase;

/**
 * This is a class that provides configuration for plotting of range rngs (true
 * or false) and the radius in km.
 *
 * It's a bit of a strange class in that it's a singleton, so that all Plotters
 * that want to can use the SAME configuration for range ring plotting.
 * Otherwise you might turn on range rings for Seismic, but then not see them
 * for Volcanic which is not what they likely want.
 *
 * @author awips
 *
 */
public class RangeRingPlotConfig extends PlotConfigBase {

    private boolean showRangeRing = false;

    private float rangeRingRadiusKm = 250f;

    private static RangeRingPlotConfig instance = new RangeRingPlotConfig();

    private RangeRingPlotConfig() {
    }

    public static RangeRingPlotConfig getInstance() {
        return instance;
    }

    public boolean isShowRangeRing() {
        return showRangeRing;
    }

    public void setShowRangeRing(boolean showRangeRing) {
        if (this.showRangeRing != showRangeRing) {
            this.showRangeRing = showRangeRing;
            firePlotConfigChanged();
        }
    }

    public void setShowRangeRing(boolean showRangeRing,
            boolean firePlotChanged) {
        if (this.showRangeRing != showRangeRing) {
            this.showRangeRing = showRangeRing;
            if (firePlotChanged) {
                firePlotConfigChanged();
            }
        }
    }

    public float getRangeRingRadiusKm() {
        return rangeRingRadiusKm;
    }

    public void setRangeRingRadiusKm(float rangeRingRadiusKm) {
        if (this.rangeRingRadiusKm != rangeRingRadiusKm) {
            this.rangeRingRadiusKm = rangeRingRadiusKm;
            firePlotConfigChanged();
        }
    }

}
