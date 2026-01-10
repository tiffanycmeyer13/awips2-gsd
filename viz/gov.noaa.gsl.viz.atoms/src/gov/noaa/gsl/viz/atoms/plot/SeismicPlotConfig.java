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

import java.util.Timer;
import java.util.TimerTask;

import org.eclipse.swt.widgets.Display;

/**
 * Plot / Rendering configuration for Seismic physical events.
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
public class SeismicPlotConfig extends GeneralPlotConfig {

    private static final long UPDATE_INTERVAL_MILLIS = 2000;

    private Timer pwaveTimer = null;

    private boolean showMagnitudeValue = true;

    private boolean showMagnitudeCircle = true;

    private boolean showDepthValue = false;

    private boolean showPWave = false;

    private boolean showPWaveWithMinuteLines = false;

    public SeismicPlotConfig() {
        super();
    }

    public boolean isShowMagnitudeValue() {
        return showMagnitudeValue;
    }

    public void setShowMagnitudeValue(boolean renderMagnitudeValue) {
        if (this.showMagnitudeValue != renderMagnitudeValue) {
            this.showMagnitudeValue = renderMagnitudeValue;
            firePlotConfigChanged();
        }
    }

    public boolean isShowMagnitudeCircle() {
        return showMagnitudeCircle;
    }

    public void setShowMagnitudeCircle(boolean showMagnitudeCircle) {
        if (this.showMagnitudeCircle != showMagnitudeCircle) {
            this.showMagnitudeCircle = showMagnitudeCircle;
            firePlotConfigChanged();
        }
    }

    public boolean isShowDepthValue() {
        return showDepthValue;
    }

    public void setShowDepthValue(boolean showDepthValue) {
        if (this.showDepthValue != showDepthValue) {
            this.showDepthValue = showDepthValue;
            firePlotConfigChanged();
        }
    }

    public boolean isShowPWave() {
        return showPWave;
    }

    public void setShowPWave(boolean showPWave) {
        if (this.showPWave != showPWave) {
            this.showPWave = showPWave;
            if (this.showPWave || this.showPWaveWithMinuteLines) {
                createPWaveTimer();
            } else {
                cancelPWaveTimer();
            }
            firePlotConfigChanged();
        }
    }

    public boolean isShowPWaveWithMinuteLines() {
        return showPWaveWithMinuteLines;
    }

    public void setShowPWaveWithMinuteLines(boolean showPWaveWithMinuteLines) {
        if (this.showPWaveWithMinuteLines != showPWaveWithMinuteLines) {
            this.showPWaveWithMinuteLines = showPWaveWithMinuteLines;
            if (this.showPWave || this.showPWaveWithMinuteLines) {
                createPWaveTimer();
            } else {
                cancelPWaveTimer();
            }
            firePlotConfigChanged();
        }
    }

    public void setShowAll() {
        super.setShowAll(false);
        showMagnitudeValue = true;
        showMagnitudeCircle = true;
        showDepthValue = true;
        showPWave = true;
        showPWaveWithMinuteLines = true;
        firePlotConfigChanged();
    }

    public void setShowNone() {
        super.setShowNone(false);
        showMagnitudeValue = false;
        showMagnitudeCircle = false;
        showDepthValue = false;
        showPWave = false;
        showPWaveWithMinuteLines = false;
        firePlotConfigChanged();
    }

    private void createPWaveTimer() {
        if (pwaveTimer == null) {
            pwaveTimer = new Timer();
            pwaveTimer.schedule(new TimerTask() {
                @Override
                public void run() {
                    // Do the update on the UI thread
                    Display.getDefault().syncExec(() -> firePlotConfigChanged(SeismicPlotConfig.this));
                }
            }, 0, UPDATE_INTERVAL_MILLIS);
        }
    }

    private void cancelPWaveTimer() {
        if (pwaveTimer != null) {
            pwaveTimer.cancel();
            pwaveTimer = null;
        }
    }
}
