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

import gov.noaa.gsl.viz.pem.plot.PlotConfigBase;

/**
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023            jing             Initial Creation
 *                         weingruber
 * </pre>
 *
 */
public class SeaLevelObsPlotConfig extends PlotConfigBase {

    private boolean showStationName = false;

    private boolean showStationId = false;

    private boolean showAmplitudeValue = false;

    private boolean showAmplitudeCircle = false;

    private boolean showStartTime = false;

    private boolean autoDensityControl = true;

    private static SeaLevelObsPlotConfig instance = new SeaLevelObsPlotConfig();

    private SeaLevelObsPlotConfig() {
        super();
    }

    public static SeaLevelObsPlotConfig getInstance() {
        return instance;
    }

    public boolean isShowStationName() {
        return showStationName;
    }

    public void setShowStationName(boolean showStationName) {
        if (this.showStationName != showStationName) {
            this.showStationName = showStationName;
            firePlotConfigChanged();
        }
    }

    public boolean isShowAmplitudeValue() {
        return showAmplitudeValue;
    }

    public void setShowAmplitudeValue(boolean showAmplitudeValue) {
        if (this.showAmplitudeValue != showAmplitudeValue) {
            this.showAmplitudeValue = showAmplitudeValue;
            firePlotConfigChanged();
        }
    }

    public boolean isShowAmplitudeCircle() {
        return showAmplitudeCircle;
    }

    public void setShowAmplitudeCircle(boolean showAmplitudeCircle) {
        if (this.showAmplitudeCircle != showAmplitudeCircle) {
            this.showAmplitudeCircle = showAmplitudeCircle;
            firePlotConfigChanged();
        }
    }

    public boolean isShowStartTime() {
        return showStartTime;
    }

    public void setShowStartTime(boolean showStartTime) {
        if (this.showStartTime != showStartTime) {
            this.showStartTime = showStartTime;
            firePlotConfigChanged();
        }
    }

    public boolean isShowStationId() {
        return showStationId;
    }

    public void setShowStationId(boolean showStationId) {
        if (this.showStationId != showStationId) {
            this.showStationId = showStationId;
            firePlotConfigChanged();
        }
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

    public void setShowAll() {
        showStartTime = true;
        showAmplitudeValue = true;
        showAmplitudeCircle = true;
        showStationName = true;
        showStationId = true;
        firePlotConfigChanged();
    }

    public void setShowNone() {
        showStartTime = false;
        showAmplitudeValue = false;
        showAmplitudeCircle = false;
        showStationName = false;
        showStationId = false;
        firePlotConfigChanged();
    }

    public boolean isShowNone() {
        return !(showStartTime || showAmplitudeCircle || showAmplitudeValue
                || showStationName || showStationId);
    }

}
