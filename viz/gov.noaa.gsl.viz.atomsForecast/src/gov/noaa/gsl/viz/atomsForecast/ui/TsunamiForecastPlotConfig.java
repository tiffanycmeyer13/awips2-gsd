/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atomsForecast.ui;

import gov.noaa.gsl.viz.pem.plot.PlotConfigBase;

/**
 * Plot / Rendering configuration for tsunami forecasts. Other options may
 * include colored grids, or filtering for a specified time period, or color
 * scale amplitude dots
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
 * @author awips
 *
 */

public class TsunamiForecastPlotConfig extends PlotConfigBase {

    public class FcstAmpLevel {
        private final String label;

        private boolean selected = true;

        private float lowValue = 0.0F;

        private float highValue = Float.MAX_VALUE;

        private boolean nansOnly = false;

        private boolean zerosOnly = false;

        FcstAmpLevel(String label, float lowValue, float highValue) {
            this.label = label;
            this.lowValue = lowValue;
            this.highValue = highValue;
        }

        /**
         * NaNs (true) or Zeros (false) only version
         *
         * @param label
         */
        FcstAmpLevel(String label, boolean nansOnly) {
            this.label = label;
            if (nansOnly) {
                this.nansOnly = true;
                this.zerosOnly = false;
            } else {
                this.nansOnly = false;
                this.zerosOnly = true;
            }
        }

        public boolean isInRange(Float value) {
            if (nansOnly) {
                if (Float.isNaN(value)) {
                    return true;
                } else {
                    return false;
                }
            } else if (zerosOnly) {
                if (value == 0.0F) {
                    return true;
                } else {
                    return false;
                }
            } else {
                return (value >= lowValue && value < highValue);
            }
        }

        public String getLabel() {
            return label;
        }

        public boolean isSelected() {
            return selected;
        }

        public void setSelected(boolean selected) {
            this.selected = selected;
            firePlotConfigChanged();
        }
    }

    private boolean showArrivalTime = false;

    private boolean showAmplitudeValue = false;

    private boolean showAmplitudeCircle = false;

    private boolean showStationName = false;

    private boolean showStationId = false;

    private boolean autoDensityControl = true;

    private boolean warningPointsOnly = false;

    private boolean showPtwsDomain = true;

    private boolean showCaribeDomain = true;

    private boolean showOtherDomain = true;

    private boolean showTravelTimeWrtNow = false;

    private boolean showTravelTimeWrtOrigin = false;

    private boolean applyAmpFilters = false;

    private boolean applyTimeOfArrivalFilters = false;

    private boolean filterByWithinHrsOfNow = false;

    // null means ANY
    private Integer withinHrsOfNow = null;

    private boolean filterByWithinHrsOfOrigin = false;

    // null means ANY
    private Integer withinHrsOfOrigin = null;

    private FcstAmpLevel NANS = new FcstAmpLevel("Amp == NaN", true);

    private FcstAmpLevel ZEROS = new FcstAmpLevel("Amp == 0.0", false);

    private FcstAmpLevel LOW = new FcstAmpLevel("Amp < 0.3m", 0.0F, 0.3F);

    private FcstAmpLevel MED_LOW = new FcstAmpLevel("0.3m <= Amp < 1.0m", 0.3F,
            1.0F);

    private FcstAmpLevel MED_HIGH = new FcstAmpLevel("1.0m <= Amp < 3.0m", 1.0F,
            3.0F);

    private FcstAmpLevel HIGH = new FcstAmpLevel("Amp >= 3.0m", 3.0F,
            Float.MAX_VALUE);

    private final FcstAmpLevel[] fcstAmpLevels = { NANS, ZEROS, LOW, MED_LOW,
            MED_HIGH, HIGH };

    private static TsunamiForecastPlotConfig instance = new TsunamiForecastPlotConfig();

    private TsunamiForecastPlotConfig() {
        super();
    }

    public static TsunamiForecastPlotConfig getInstance() {
        return instance;
    }

    public boolean isShowTravelTimeWrtNow() {
        return showTravelTimeWrtNow;
    }

    public void setShowTravelTimeWrtNow(boolean showTravelTimeWrtNow) {
        if (this.showTravelTimeWrtNow != showTravelTimeWrtNow) {
            this.showTravelTimeWrtNow = showTravelTimeWrtNow;
            firePlotConfigChanged();
        }
    }

    public boolean isShowTravelTimeWrtOrigin() {
        return showTravelTimeWrtOrigin;
    }

    public void setShowTravelTimeWrtOrigin(boolean showTravelTimeWrtOrigin) {
        if (this.showTravelTimeWrtOrigin != showTravelTimeWrtOrigin) {
            this.showTravelTimeWrtOrigin = showTravelTimeWrtOrigin;
            firePlotConfigChanged();
        }
    }

    public boolean isShowArrivalTime() {
        return showArrivalTime;
    }

    public void setShowArrivalTime(boolean showArrivalTime) {
        if (this.showArrivalTime != showArrivalTime) {
            this.showArrivalTime = showArrivalTime;
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

    public void setShowNaNAmpLevel(boolean showNaNAmpLevel) {
        if (fcstAmpLevels[0].isSelected() != showNaNAmpLevel) {
            fcstAmpLevels[0].setSelected(showNaNAmpLevel);
            firePlotConfigChanged();
        }
    }

    public boolean isShowNaNAmpLevel() {
        return fcstAmpLevels[0].isSelected();
    }

    public FcstAmpLevel getNaNAmpLevel() {
        return fcstAmpLevels[0];
    }

    public void setShowZeroAmpLevel(boolean showZeroAmpLevel) {
        if (fcstAmpLevels[1].isSelected() != showZeroAmpLevel) {
            fcstAmpLevels[1].setSelected(showZeroAmpLevel);
            firePlotConfigChanged();
        }
    }

    public boolean isShowZeroAmpLevel() {
        return fcstAmpLevels[1].isSelected();
    }

    public FcstAmpLevel getZeroAmpLevel() {
        return fcstAmpLevels[1];
    }

    public void setShowLowAmpLevel(boolean showLowAmpLevel) {
        if (fcstAmpLevels[2].isSelected() != showLowAmpLevel) {
            fcstAmpLevels[2].setSelected(showLowAmpLevel);
            firePlotConfigChanged();
        }
    }

    public boolean isShowLowAmpLevel() {
        return fcstAmpLevels[2].isSelected();
    }

    public FcstAmpLevel getLowAmpLevel() {
        return fcstAmpLevels[2];
    }

    public void setShowMedLowAmpLevel(boolean showMedLowAmpLevel) {
        if (fcstAmpLevels[3].isSelected() != showMedLowAmpLevel) {
            fcstAmpLevels[3].setSelected(showMedLowAmpLevel);
            firePlotConfigChanged();
        }
    }

    public boolean isShowMedLowAmpLevel() {
        return fcstAmpLevels[3].isSelected();
    }

    public FcstAmpLevel getMedLowAmpLevel() {
        return fcstAmpLevels[3];
    }

    public void setShowMedHighAmpLevel(boolean showMedHighAmpLevel) {
        if (fcstAmpLevels[4].isSelected() != showMedHighAmpLevel) {
            fcstAmpLevels[4].setSelected(showMedHighAmpLevel);
            firePlotConfigChanged();
        }
    }

    public boolean isShowMedHighAmpLevel() {
        return fcstAmpLevels[4].isSelected();
    }

    public FcstAmpLevel getMedHighAmpLevel() {
        return fcstAmpLevels[4];
    }

    public void setShowHighAmpLevel(boolean showHighAmpLevel) {
        if (fcstAmpLevels[5].isSelected() != showHighAmpLevel) {
            fcstAmpLevels[5].setSelected(showHighAmpLevel);
            firePlotConfigChanged();
        }
    }

    public boolean isShowHighAmpLevel() {
        return fcstAmpLevels[5].isSelected();
    }

    public FcstAmpLevel getHighAmpLevel() {
        return fcstAmpLevels[5];
    }

    public FcstAmpLevel[] getFcstAmpLevels() {
        return fcstAmpLevels;
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

    public boolean isWarningPointsOnly() {
        return warningPointsOnly;
    }

    public void setWarningPointsOnly(boolean warningPointsOnly) {
        if (this.warningPointsOnly != warningPointsOnly) {
            this.warningPointsOnly = warningPointsOnly;
            firePlotConfigChanged();
        }
    }

    public boolean isShowPtwsDomain() {
        return showPtwsDomain;
    }

    public void setShowPtwsDomain(boolean showPtwsDomain) {
        if (this.showPtwsDomain != showPtwsDomain) {
            this.showPtwsDomain = showPtwsDomain;
            firePlotConfigChanged();
        }
    }

    public boolean isShowCaribeDomain() {
        return showCaribeDomain;
    }

    public void setShowCaribeDomain(boolean showCaribeDomain) {
        if (this.showCaribeDomain != showCaribeDomain) {
            this.showCaribeDomain = showCaribeDomain;
            firePlotConfigChanged();
        }
    }

    public boolean isShowOtherDomain() {
        return showOtherDomain;
    }

    public void setShowOtherDomain(boolean showOtherDomain) {
        if (this.showOtherDomain != showOtherDomain) {
            this.showOtherDomain = showOtherDomain;
            firePlotConfigChanged();
        }
    }

    public boolean isApplyAmpFilters() {
        return applyAmpFilters;
    }

    public void setApplyAmpFilters(boolean applyAmpFilters) {
        if (this.applyAmpFilters != applyAmpFilters) {
            this.applyAmpFilters = applyAmpFilters;
            firePlotConfigChanged();
        }
    }

    public boolean isApplyTimeOfArrivalFilters() {
        return applyTimeOfArrivalFilters;
    }

    public void setApplyTimeOfArrivalFilters(
            boolean applyTimeOfArrivalFilters) {
        if (this.applyTimeOfArrivalFilters != applyTimeOfArrivalFilters) {
            this.applyTimeOfArrivalFilters = applyTimeOfArrivalFilters;
            firePlotConfigChanged();
        }
    }

    public boolean isFilterByWithinHrsOfNow() {
        return filterByWithinHrsOfNow;
    }

    public void setFilterByWithinHrsOfNow(boolean filterByWithinHrsOfNow) {
        if (this.filterByWithinHrsOfNow != filterByWithinHrsOfNow) {
            this.filterByWithinHrsOfNow = filterByWithinHrsOfNow;
            // We dont allow both ON at the same time
            if (filterByWithinHrsOfNow) {
                filterByWithinHrsOfOrigin = false;
            }
            firePlotConfigChanged();
        }
    }

    public Integer getWithinHrsOfNow() {
        return withinHrsOfNow;
    }

    public void setWithinHrsOfNow(Integer withinHrsOfNow) {
        if (this.withinHrsOfNow != withinHrsOfNow) {
            this.withinHrsOfNow = withinHrsOfNow;
            firePlotConfigChanged();
        }
    }

    public boolean isFilterByWithinHrsOfOrigin() {
        return filterByWithinHrsOfOrigin;
    }

    public void setFilterByWithinHrsOfOrigin(
            boolean filterByWithinHrsOfOrigin) {
        if (this.filterByWithinHrsOfOrigin != filterByWithinHrsOfOrigin) {
            this.filterByWithinHrsOfOrigin = filterByWithinHrsOfOrigin;
            // We dont allow both ON at the same time
            if (filterByWithinHrsOfOrigin) {
                filterByWithinHrsOfNow = false;
            }
            firePlotConfigChanged();
        }
    }

    public Integer getWithinHrsOfOrigin() {
        return withinHrsOfOrigin;
    }

    public void setWithinHrsOfOrigin(Integer withinHrsOfOrigin) {
        if (this.withinHrsOfOrigin != withinHrsOfOrigin) {
            this.withinHrsOfOrigin = withinHrsOfOrigin;
            firePlotConfigChanged();
        }
    }

    public void setShowAll() {
        showArrivalTime = true;
        showAmplitudeValue = true;
        showAmplitudeCircle = true;
        showStationName = true;
        showStationId = true;
        // For times, default to Arrival time only (so don't overwrite ea other)
        showTravelTimeWrtNow = false;
        showTravelTimeWrtOrigin = false;
        showPtwsDomain = true;
        showCaribeDomain = true;
        showOtherDomain = true;

        firePlotConfigChanged();
    }

    public void setShowNone() {
        showArrivalTime = false;
        showAmplitudeValue = false;
        showAmplitudeCircle = false;
        showStationName = false;
        showStationId = false;
        showTravelTimeWrtNow = false;
        showTravelTimeWrtOrigin = false;
        showPtwsDomain = false;
        showCaribeDomain = false;
        showOtherDomain = false;

        firePlotConfigChanged();
    }

    public boolean isShowNone() {
        return (!showArrivalTime && !showAmplitudeCircle && !showAmplitudeValue
                && !showStationName && !showStationId && !showTravelTimeWrtNow
                && !showTravelTimeWrtOrigin && !showPtwsDomain
                && !showCaribeDomain && !showOtherDomain);
    }
}