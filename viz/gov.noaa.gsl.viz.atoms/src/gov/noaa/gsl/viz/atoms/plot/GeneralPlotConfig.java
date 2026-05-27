package gov.noaa.gsl.viz.atoms.plot;

import gov.noaa.gsl.viz.pem.plot.PlotConfig;
import gov.noaa.gsl.viz.pem.plot.PlotConfigBase;
import gov.noaa.gsl.viz.pem.plot.PlotConfigListener;

public class GeneralPlotConfig extends PlotConfigBase {

    private boolean showCustomId = true;

    private boolean autoDensityControl = true;

    private PlotConfigListener rangeRingPlotConfigListener = new RangeRingPlotConfigListener();

    public GeneralPlotConfig() {
        RangeRingPlotConfig.getInstance()
                .addPlotConfigListener(rangeRingPlotConfigListener);
    }

    public boolean isShowCustomId() {
        return showCustomId;
    }

    public void setShowCustomId(boolean showCustomId) {
        if (this.showCustomId != showCustomId) {
            this.showCustomId = showCustomId;
            firePlotConfigChanged();
        }
    }

    public boolean isShowRangeRing() {
        return RangeRingPlotConfig.getInstance().isShowRangeRing();
    }

    public void setShowRangeRing(boolean showRangeRing) {
        RangeRingPlotConfig.getInstance().setShowRangeRing(showRangeRing);
    }

    public float getRangeRingRadiusKm() {
        return RangeRingPlotConfig.getInstance().getRangeRingRadiusKm();
    }

    public void setRangeRingRadiusKm(float rangeRingRadiusKm) {
        RangeRingPlotConfig.getInstance()
                .setRangeRingRadiusKm(rangeRingRadiusKm);
    }

    public boolean isAutoDensityControl() {
        return autoDensityControl;
    }

    public void setAutoDensityControl(boolean autoDensityControl) {
        if (this.autoDensityControl != autoDensityControl) {
            this.autoDensityControl = autoDensityControl;
            firePlotConfigChanged();
        }
    }

    protected void setShowAll(boolean firePlotConfigChanged) {
        showCustomId = true;
        RangeRingPlotConfig.getInstance().setShowRangeRing(true, false);
        if (firePlotConfigChanged) {
            firePlotConfigChanged();
        }
    }

    protected void setShowNone(boolean firePlotConfigChanged) {
        showCustomId = false;
        RangeRingPlotConfig.getInstance().setShowRangeRing(false, false);
        if (firePlotConfigChanged) {
            firePlotConfigChanged();
        }
    }

    private class RangeRingPlotConfigListener implements PlotConfigListener {

        @Override
        public void plotConfigChanged(PlotConfig config) {
            firePlotConfigChanged();
        }
    }
}
