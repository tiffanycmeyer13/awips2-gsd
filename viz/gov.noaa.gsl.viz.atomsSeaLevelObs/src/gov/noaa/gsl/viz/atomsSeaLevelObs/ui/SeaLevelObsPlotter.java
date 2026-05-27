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

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;

import com.raytheon.uf.viz.core.DrawableString;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.HorizontalAlignment;
import com.raytheon.uf.viz.core.IGraphicsTarget.VerticalAlignment;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.capabilities.Capabilities;
import com.raytheon.uf.viz.core.rsc.capabilities.DensityCapability;
import com.raytheon.uf.viz.core.rsc.capabilities.MagnificationCapability;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObs;
import gov.noaa.gsl.viz.pem.plot.AbstractPlotter;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;
import gov.noaa.gsl.viz.pem.plot.ProgressiveDisclosureStrategy;

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
 * @author awips
 *
 */
public class SeaLevelObsPlotter extends PEPlotter {

    private static RGB DOT_COLOR = new RGB(0, 255, 255);

    private static final RGB WHITE = new RGB(255, 255, 255);

    public static final RGB GREEN = new RGB(0, 255, 0);

    public static final RGB YELLOW = new RGB(255, 255, 0);

    public static final RGB ORANGE = new RGB(255, 165, 0);

    public static final RGB RED = new RGB(255, 0, 0);

    public static final RGB MAGENTA = new RGB(213, 4, 239);

    private List<SeaLevelObs> allSlobs = new ArrayList<>();

    private Button configStnIdCheckbox;

    private Button configStnNameCheckbox;

    private Button configAmpCircleCheckbox;

    private Button configAmpValueCheckbox;

    private Button configStartTimeCheckbox;

    private Button configAutoDensityCheckbox;

    public SeaLevelObsPlotter() {
        super(SeaLevelObsPlotConfig.getInstance());
    }

    public SeaLevelObsPlotConfig getSLObsPlotConfig() {
        if (getPlotConfig() instanceof SeaLevelObsPlotConfig) {
            return (SeaLevelObsPlotConfig) getPlotConfig();
        }
        return null;
    }

    public List<SeaLevelObs> getSeaLevelObs() {
        return allSlobs;
    }

    public void setSeaLevelObs(List<SeaLevelObs> slobs) {
        this.allSlobs = slobs;
        getPlotConfig().firePlotConfigChanged();
    }

    /**
     * Plots a sea level obs data.
     *
     * @param target
     * @param paintProps
     * @throws VizException
     * @throws InterruptedException
     */
    @Override
    public void plot(IGraphicsTarget target, PaintProperties paintProps,
            IMapDescriptor descriptor, Capabilities drawCapabilities) {

        try {
            if (getSeaLevelObs() == null || getSeaLevelObs().isEmpty()) {
                return;
            }

            double magnification = drawCapabilities
                    .getCapability(null, MagnificationCapability.class)
                    .getMagnification();

            SeaLevelObsPlotConfig plotConfig = getSLObsPlotConfig();
            Collection<SeaLevelObs> slobs = getSeaLevelObs();
            // Progressive disclosure / density control
            if (plotConfig.isAutoDensityControl()) {
                double density = drawCapabilities
                        .getCapability(null, DensityCapability.class)
                        .getDensity();
                ProgressiveDisclosureStrategy<SeaLevelObs> progDisc = new ProgressiveDisclosureStrategy<>(
                        paintProps, descriptor);
                progDisc.setDensity(density);
                progDisc.setMagnification(magnification);
                slobs = progDisc.progDisc(slobs, target);
            }

            for (SeaLevelObs obs : slobs) {
                // TODO We should not be reprojecting AGAIN, since we did that
                // in progDisc already. Hurts performance.
                double[] screenLoc = descriptor.worldToPixel(
                        new double[] { obs.getLongitude(), obs.getLatitude() });
                if (((Double) screenLoc[0]).isNaN()
                        || ((Double) screenLoc[1]).isNaN()) {
                    continue;
                }

                /* Station location */
                if (!plotConfig.isShowNone()) {
                    DrawableString locationStr = new DrawableString("+",
                            DOT_COLOR);
                    locationStr.setCoordinates(screenLoc[0], screenLoc[1]);
                    locationStr.verticallAlignment = VerticalAlignment.MIDDLE;
                    locationStr.horizontalAlignment = HorizontalAlignment.CENTER;
                    target.drawStrings(locationStr);
                }
                if (plotConfig.isShowStationId()) {
                    SLObsStationIdRenderer rend = new SLObsStationIdRenderer(
                            obs);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }
                if (plotConfig.isShowStationName()) {
                    SLObsStationNameRenderer rend = new SLObsStationNameRenderer(
                            obs);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }
                if (plotConfig.isShowAmplitudeValue()) {
                    SLObsAmpValueRenderer rend = new SLObsAmpValueRenderer(obs);
                    rend.plot(target, descriptor, paintProps, magnification,
                            getAmplitudeColorRGB(obs.getAmplitude()),
                            screenLoc);
                }
                if (plotConfig.isShowAmplitudeCircle()) {
                    SLObsAmpCircleRenderer rend = new SLObsAmpCircleRenderer(
                            obs);
                    rend.plot(target, descriptor, paintProps, magnification,
                            getAmplitudeColorRGB(obs.getAmplitude()),
                            screenLoc);
                }
                if (plotConfig.isShowStartTime()) {
                    SLObsStartTimeRenderer rend = new SLObsStartTimeRenderer(
                            obs);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }
            }
            /*
             * Now delegate to child plotters
             */
            super.plot(target, paintProps, descriptor, drawCapabilities);

        } catch (Exception e) {
            e.printStackTrace(System.err);
        }
    }

    public static RGB getAmplitudeColorRGB(Float amplitude) {
        if (amplitude == null || Float.isNaN(amplitude) || amplitude < 0.4f) {
            return SeaLevelObsPlotter.GREEN;
        } else if (amplitude < 1.0f) {
            return SeaLevelObsPlotter.ORANGE;
        } else if (amplitude < 3.0f) {
            return SeaLevelObsPlotter.RED;
        } else if (amplitude >= 3.0f) {
            return SeaLevelObsPlotter.MAGENTA;
        } else {
            return SeaLevelObsPlotter.GREEN;
        }
    }

    public static Color getAmplitudeColor(Float amplitude) {
        return new Color(getAmplitudeColorRGB(amplitude));
    }

    private void clearConfigWidgets() {
        configStnIdCheckbox = null;
        configStnNameCheckbox = null;
        configAmpCircleCheckbox = null;
        configAmpValueCheckbox = null;
        configStartTimeCheckbox = null;
        configAutoDensityCheckbox = null;
        setBuildConfigWidgetsComplete(false);
    }

    @Override
    public void reinitConfigWidgets() {
        if (!isBuildConfigWidgetsComplete() || configStnIdCheckbox == null
                || configStnIdCheckbox.isDisposed()) {
            return;
        }
        configStnIdCheckbox
                .setSelection(getSLObsPlotConfig().isShowStationId());
        configStnNameCheckbox
                .setSelection(getSLObsPlotConfig().isShowStationName());
        configAmpCircleCheckbox
                .setSelection(getSLObsPlotConfig().isShowAmplitudeCircle());
        configAmpValueCheckbox
                .setSelection(getSLObsPlotConfig().isShowAmplitudeValue());
        configStartTimeCheckbox
                .setSelection(getSLObsPlotConfig().isShowStartTime());
        configAutoDensityCheckbox
                .setSelection(getSLObsPlotConfig().isAutoDensityControl());
    }

    @Override
    public void buildPlotterConfigTabItems(TabFolder tabFolder) {

        TabItem tabItem = new TabItem(tabFolder, SWT.BORDER);
        tabItem.setText("Sea Level Obs");

        Composite mainComp = new Composite(tabFolder, SWT.NONE);
        GridLayout compGridLayout = new GridLayout();
        compGridLayout.numColumns = 1;
        mainComp.setLayout(compGridLayout);
        mainComp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        tabItem.setControl(mainComp);

        Group renderOptionsGroup = new Group(mainComp, SWT.NONE);
        // renderOptionsGroup.setLayout(new RowLayout(SWT.VERTICAL));
        renderOptionsGroup.setLayout(new GridLayout());
        renderOptionsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        renderOptionsGroup.setText("Select option(s) for rendering:");

        configStnIdCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configStnIdCheckbox.setText("Station Id");
        configStnIdCheckbox
                .setSelection(getSLObsPlotConfig().isShowStationId());
        configStnIdCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig()
                        .setShowStationId(configStnIdCheckbox.getSelection());
            }
        });
        configStnNameCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configStnNameCheckbox.setText("Station Name");
        configStnNameCheckbox
                .setSelection(getSLObsPlotConfig().isShowStationName());
        configStnNameCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig().setShowStationName(
                        configStnNameCheckbox.getSelection());
            }
        });
        configStartTimeCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configStartTimeCheckbox.setText("Start Time");
        configStartTimeCheckbox
                .setSelection(getSLObsPlotConfig().isShowStartTime());
        configStartTimeCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig().setShowStartTime(
                        configStartTimeCheckbox.getSelection());
            }
        });

        configAmpValueCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configAmpValueCheckbox.setText("Amplitude Value (m)");
        configAmpValueCheckbox
                .setSelection(getSLObsPlotConfig().isShowAmplitudeValue());
        configAmpValueCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig().setShowAmplitudeValue(
                        configAmpValueCheckbox.getSelection());
            }
        });
        configAmpCircleCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configAmpCircleCheckbox.setText("Amplitude Circle");
        configAmpCircleCheckbox
                .setSelection(getSLObsPlotConfig().isShowAmplitudeCircle());
        configAmpCircleCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig().setShowAmplitudeCircle(
                        configAmpCircleCheckbox.getSelection());
            }
        });

        // Now for All None buttons
        Composite allNoneComp = new Composite(mainComp, SWT.NONE);
        RowLayout rowLayout = new RowLayout();
        rowLayout.pack = true;
        allNoneComp.setLayout(rowLayout);
        Button allButton = new Button(allNoneComp, SWT.PUSH);
        allButton.setText("Select All");
        allButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig().setShowAll();
                reinitConfigWidgets();
            }
        });
        Button noneButton = new Button(allNoneComp, SWT.PUSH);
        noneButton.setText("Select None");
        noneButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig().setShowNone();
                reinitConfigWidgets();
            }
        });

        // Now for Auto Density Button
        Group otherOptionsGroup = new Group(mainComp, SWT.NONE);
        otherOptionsGroup.setLayout(new GridLayout());
        otherOptionsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        otherOptionsGroup.setText("Other options:");

        configAutoDensityCheckbox = new Button(otherOptionsGroup, SWT.CHECK);
        configAutoDensityCheckbox.setText("Auto Density Control");
        configAutoDensityCheckbox
                .setSelection(getSLObsPlotConfig().isAutoDensityControl());
        configAutoDensityCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSLObsPlotConfig().setAutoDensityControl(
                        configAutoDensityCheckbox.getSelection());
            }
        });

        for (AbstractPlotter childPlotter : getChildPlotters()) {
            childPlotter.buildPlotterConfigTabItems(tabFolder);
        }
        setBuildConfigWidgetsComplete(true);
    }
}
