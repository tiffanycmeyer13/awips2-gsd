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

import java.util.Collection;
import java.util.Date;
import java.util.Iterator;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;

import com.raytheon.uf.common.time.SimulatedTime;
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

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiStationForecast;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.viz.atomsForecast.WarningPointsUtils;
import gov.noaa.gsl.viz.atomsForecast.ui.TsunamiForecastPlotConfig.FcstAmpLevel;
import gov.noaa.gsl.viz.pem.plot.AbstractPlotter;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;
import gov.noaa.gsl.viz.pem.plot.ProgressiveDisclosureStrategy;

/**
 * Plotter for tsunami forecasts.
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

public class TsunamiForecastPlotter extends PEPlotter {

    public static final RGB DOT_COLOR = new RGB(0, 255, 255);

    public static final RGB GREEN = new RGB(0, 255, 0);

    public static final RGB YELLOW = new RGB(255, 255, 0);

    public static final RGB ORANGE = new RGB(255, 165, 0);

    public static final RGB RED = new RGB(255, 0, 0);

    public static final RGB MAGENTA = new RGB(213, 4, 239);

    public static final RGB WHITE = new RGB(255, 255, 255);

    private String ANY = "Any";

    private TsunamiForecast tsunamiForecast = null;

    private Button configStnIdCheckbox;

    private Button configStnNameCheckbox;

    private Button configArriveTimeCheckbox;

    private Button configTravelTimeNowCheckbox;

    private Button configTravelTimeOriginCheckbox;

    private Button configAmpValueCheckbox;

    private Button configAmpCircleCheckbox;

    private Button configAutoDensityCheckbox;

    private Button warningPointsOnlyCheckbox;

    private Button ptwsDomainCheckbox;

    private Button caribeDomainCheckbox;

    private Button otherDomainCheckbox;

    private Button applyAmpFiltersCheckbox;

    private Button nanAmpLevelCheckbox;

    private Button zeroAmpLevelCheckbox;

    private Button lowAmpLevelCheckbox;

    private Button medLowAmpLevelCheckbox;

    private Button medHighAmpLevelCheckbox;

    private Button highAmpLevelCheckbox;

    private Button applyTimeFiltersCheckbox;

    private Button filterByHrsOfNowCheckbox;

    private Combo hrsOfNowCombo;

    private Button filterByHrsOfOriginCheckbox;

    private Combo hrsOfOriginCombo;

    public TsunamiForecastPlotter() {
        super(TsunamiForecastPlotConfig.getInstance());
    }

    public TsunamiForecast getTsunamiForecast() {
        return tsunamiForecast;
    }

    public TsunamiForecastPlotConfig getTsuFcstPlotConfig() {
        if (getPlotConfig() instanceof TsunamiForecastPlotConfig) {
            return (TsunamiForecastPlotConfig) getPlotConfig();
        }
        return null;
    }

    public void setTsunamiForecast(TsunamiForecast tsunamiForecast) {
        this.tsunamiForecast = tsunamiForecast;
        getPlotConfig().firePlotConfigChanged();
    }

    private IPhysicalEvent getPhysicalEvent() {
        if (getPhysicalEvents().size() != 1) {
            return null;
        } else {
            return getPhysicalEvents().get(0);
        }
    }

    /**
     * Plots a seismic event data.
     *
     * @param target
     * @param paintProps
     * @throws VizException
     * @throws InterruptedException
     */
    @Override
    public void plot(IGraphicsTarget target, PaintProperties paintProps,
            IMapDescriptor descriptor, Capabilities drawCapabilities) {

        reinitConfigWidgets();

        try {
            if (getTsunamiForecast() == null) {
                return;
            }
            double magnification = drawCapabilities
                    .getCapability(null, MagnificationCapability.class)
                    .getMagnification();

            TsunamiForecastPlotConfig plotConfig = getTsuFcstPlotConfig();

            // Apply the FILTERS first, then ProgressiveDisclosure, then the
            // attribute options
            Collection<TsunamiStationForecast> stnForecasts = getTsunamiForecast()
                    .getStationFcsts();
            Iterator<TsunamiStationForecast> iter = stnForecasts.iterator();
            while (iter.hasNext()) {
                TsunamiStationForecast stnFcst = iter.next();
                if (!shouldShowAmplitude(stnFcst)) {
                    iter.remove();
                } else if (!shouldShowArrivalTime(stnFcst)) {
                    iter.remove();
                } else if (plotConfig.isWarningPointsOnly()) {
                    if (!WarningPointsUtils.isWarningPoint(
                            stnFcst.getStation().getCustomId())) {
                        iter.remove();
                    }
                    // It IS a warning point
                    else {
                        String domain = WarningPointsUtils
                                .getWarningPoint(
                                        stnFcst.getStation().getCustomId())
                                .getDomain();
                        if ((!plotConfig.isShowPtwsDomain()
                                && "PTWS".equals(domain))
                                || (!plotConfig.isShowCaribeDomain()
                                        && "CARIBE".equals(domain))
                                || (!plotConfig.isShowOtherDomain()
                                        && "OTHER".equals(domain))) {
                            iter.remove();
                        }
                    }
                }
            }

            // Do Progressive disclosure / density control with remaining stns
            if (plotConfig.isAutoDensityControl()) {
                double density = drawCapabilities
                        .getCapability(null, DensityCapability.class)
                        .getDensity();
                ProgressiveDisclosureStrategy<TsunamiStationForecast> progDisc = new ProgressiveDisclosureStrategy<>(
                        paintProps, descriptor);
                progDisc.setDensity(density);
                progDisc.setMagnification(magnification);
                stnForecasts = progDisc.progDisc(stnForecasts, target);
            }

            for (TsunamiStationForecast stnFcst : stnForecasts) {

                // TODO We should not be reprojecting AGAIN, since we did that
                // in progDisc already. Hurts performance.
                double[] screenLoc = descriptor.worldToPixel(new double[] {
                        stnFcst.getLongitude(), stnFcst.getLatitude() });
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
                    ForecastStationIdRenderer rend = new ForecastStationIdRenderer(
                            stnFcst);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }
                if (plotConfig.isShowStationName()) {
                    ForecastStationNameRenderer rend = new ForecastStationNameRenderer(
                            stnFcst);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }
                if (plotConfig.isShowArrivalTime()) {
                    ArrivalTimesRenderer rend = new ArrivalTimesRenderer(
                            stnFcst);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }
                if (plotConfig.isShowTravelTimeWrtNow()) {
                    TravelTimesRenderer rend = new TravelTimesRenderer(
                            getPhysicalEvent(), stnFcst);
                    rend.setFromNow(true);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }
                if (plotConfig.isShowTravelTimeWrtOrigin()) {
                    TravelTimesRenderer rend = new TravelTimesRenderer(
                            getPhysicalEvent(), stnFcst);
                    rend.setFromNow(false);
                    rend.plot(target, descriptor, paintProps, magnification,
                            WHITE, screenLoc);
                }

                if (plotConfig.isShowAmplitudeValue()) {
                    FcstAmpValueRenderer rend = new FcstAmpValueRenderer(
                            stnFcst);
                    rend.plot(target, descriptor, paintProps, magnification,
                            getAmplitudeColorRGB(stnFcst.getAmplitude()),
                            screenLoc);
                }
                if (plotConfig.isShowAmplitudeCircle()) {
                    FcstAmpCircleRenderer rend = new FcstAmpCircleRenderer(
                            stnFcst);
                    rend.plot(target, descriptor, paintProps, magnification,
                            getAmplitudeColorRGB(stnFcst.getAmplitude()),
                            screenLoc);
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

    private boolean shouldShowAmplitude(TsunamiStationForecast stnFcst) {
        if (stnFcst == null) {
            return false;
        }

        if (!getTsuFcstPlotConfig().isApplyAmpFilters()) {
            return true;
        }

        for (FcstAmpLevel level : getTsuFcstPlotConfig().getFcstAmpLevels()) {
            if (level.isSelected() && level.isInRange(stnFcst.getAmplitude())) {
                return true;
            }
        }
        return false;
    }

    private boolean shouldShowArrivalTime(TsunamiStationForecast stnFcst) {
        if (stnFcst == null) {
            return false;
        }

        if (!getTsuFcstPlotConfig().isApplyTimeOfArrivalFilters()) {
            return true;
        }

        // The java auto-formatting selections are atrocious
        if (stnFcst.getArrivalTime() == null) {
            if (getTsuFcstPlotConfig().isFilterByWithinHrsOfNow()
                    && getTsuFcstPlotConfig().getWithinHrsOfNow() == null) {
                return true;
            } else if (getTsuFcstPlotConfig().isFilterByWithinHrsOfOrigin()
                    && getTsuFcstPlotConfig().getWithinHrsOfOrigin() == null) {
                return true;
            } else {
                return false;
            }
        } else {
            long arrivalTimeMillis = stnFcst.getArrivalTime().getTime();
            Date refTime = null;
            int hrsWindowDelta = 0;
            if (getTsuFcstPlotConfig().isFilterByWithinHrsOfNow()) {
                if (getTsuFcstPlotConfig().getWithinHrsOfNow() == null) {
                    return true;
                } else {
                    refTime = SimulatedTime.getSystemTime().getTime();
                    hrsWindowDelta = getTsuFcstPlotConfig().getWithinHrsOfNow();
                }
            } else if (getTsuFcstPlotConfig().isFilterByWithinHrsOfOrigin()) {
                if (getTsuFcstPlotConfig().getWithinHrsOfOrigin() == null) {
                    return true;
                } else {
                    if (getPhysicalEvent() == null) {
                        return false;
                    }
                    refTime = getPhysicalEvent().getRefTime();
                    hrsWindowDelta = getTsuFcstPlotConfig()
                            .getWithinHrsOfOrigin();
                }
            } else {
                return false;
            }

            long travelTimeDelta = arrivalTimeMillis - refTime.getTime();
            if (travelTimeDelta >= 0 && travelTimeDelta <= (hrsWindowDelta * 60L
                    * 60L * 1000L)) {
                return true;
            } else {
                return false;
            }
        }

    }

    public static RGB getAmplitudeColorRGB(Float amplitude) {
        if (amplitude == null || Float.isNaN(amplitude) || amplitude < 0.3f) {
            return TsunamiForecastPlotter.GREEN;
        } else if (amplitude < 1.0f) {
            return TsunamiForecastPlotter.ORANGE;
        } else if (amplitude < 3.0f) {
            return TsunamiForecastPlotter.RED;
        } else if (amplitude >= 3.0f) {
            return TsunamiForecastPlotter.MAGENTA;
        } else {
            return TsunamiForecastPlotter.GREEN;
        }
    }

    public static Color getAmplitudeColor(Float amplitude) {
        return new Color(getAmplitudeColorRGB(amplitude));
    }

    private void clearConfigWidgets() {
        configStnIdCheckbox = null;
        configStnNameCheckbox = null;
        configArriveTimeCheckbox = null;
        configTravelTimeNowCheckbox = null;
        configTravelTimeOriginCheckbox = null;
        configAmpValueCheckbox = null;
        configAmpCircleCheckbox = null;
        configAutoDensityCheckbox = null;
        warningPointsOnlyCheckbox = null;
        applyAmpFiltersCheckbox = null;
        nanAmpLevelCheckbox = null;
        zeroAmpLevelCheckbox = null;
        lowAmpLevelCheckbox = null;
        medLowAmpLevelCheckbox = null;
        medHighAmpLevelCheckbox = null;
        highAmpLevelCheckbox = null;
        applyTimeFiltersCheckbox = null;
        filterByHrsOfNowCheckbox = null;
        filterByHrsOfOriginCheckbox = null;
        hrsOfNowCombo = null;
        hrsOfOriginCombo = null;
        setBuildConfigWidgetsComplete(false);
    }

    @Override
    protected void reinitConfigWidgets() {

        if (!isBuildConfigWidgetsComplete() || getTsuFcstPlotConfig() == null
                || configStnIdCheckbox == null
                || configStnIdCheckbox.isDisposed()) {
            return;
        }

        configStnIdCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowStationId());
        configStnNameCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowStationName());
        configArriveTimeCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowArrivalTime());
        configTravelTimeNowCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowTravelTimeWrtNow());
        configTravelTimeOriginCheckbox.setSelection(
                getTsuFcstPlotConfig().isShowTravelTimeWrtOrigin());
        configAmpValueCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowAmplitudeValue());
        configAmpCircleCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowAmplitudeCircle());
        configAutoDensityCheckbox
                .setSelection(getTsuFcstPlotConfig().isAutoDensityControl());
        warningPointsOnlyCheckbox
                .setSelection(getTsuFcstPlotConfig().isWarningPointsOnly());
        applyAmpFiltersCheckbox
                .setSelection(getTsuFcstPlotConfig().isApplyAmpFilters());
        nanAmpLevelCheckbox.setSelection(
                getTsuFcstPlotConfig().getNaNAmpLevel().isSelected());
        zeroAmpLevelCheckbox.setSelection(
                getTsuFcstPlotConfig().getZeroAmpLevel().isSelected());
        lowAmpLevelCheckbox.setSelection(
                getTsuFcstPlotConfig().getLowAmpLevel().isSelected());
        medLowAmpLevelCheckbox.setSelection(
                getTsuFcstPlotConfig().getMedLowAmpLevel().isSelected());
        medHighAmpLevelCheckbox.setSelection(
                getTsuFcstPlotConfig().getMedHighAmpLevel().isSelected());
        highAmpLevelCheckbox.setSelection(
                getTsuFcstPlotConfig().getHighAmpLevel().isSelected());
        applyTimeFiltersCheckbox.setSelection(
                getTsuFcstPlotConfig().isApplyTimeOfArrivalFilters());
        filterByHrsOfNowCheckbox.setSelection(
                getTsuFcstPlotConfig().isFilterByWithinHrsOfNow());
        if (getTsuFcstPlotConfig().getWithinHrsOfNow() == null) {
            hrsOfNowCombo.select(24);
        } else {
            int hours = getTsuFcstPlotConfig().getWithinHrsOfNow();
            hrsOfNowCombo.select(hours - 1);
        }
        filterByHrsOfOriginCheckbox.setSelection(
                getTsuFcstPlotConfig().isFilterByWithinHrsOfOrigin());
        if (getTsuFcstPlotConfig().getWithinHrsOfOrigin() == null) {
            hrsOfOriginCombo.select(24);
        } else {
            int hours = getTsuFcstPlotConfig().getWithinHrsOfOrigin();
            hrsOfOriginCombo.select(hours - 1);
        }
    }

    @Override
    public void buildPlotterConfigTabItems(TabFolder tabFolder) {

        TabItem tabItem = new TabItem(tabFolder, SWT.BORDER);
        tabItem.setText("Tsunami Forecasts");

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
        renderOptionsGroup.setText("Attribute option(s) for rendering:");

        configStnIdCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configStnIdCheckbox.setText("Station Id");
        configStnIdCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowStationId());
        configStnIdCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig()
                        .setShowStationId(configStnIdCheckbox.getSelection());
            }
        });
        configStnNameCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configStnNameCheckbox.setText("Station Name");
        configStnNameCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowStationName());
        configStnNameCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setShowStationName(
                        configStnNameCheckbox.getSelection());
            }
        });

        Group lowerLeftTimesGroup = new Group(renderOptionsGroup, SWT.NONE);
        lowerLeftTimesGroup.setLayout(new GridLayout());
        lowerLeftTimesGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
        configArriveTimeCheckbox = new Button(lowerLeftTimesGroup, SWT.RADIO);
        configArriveTimeCheckbox.setText("Arrival Time");
        configArriveTimeCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowArrivalTime());
        configArriveTimeCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setShowArrivalTime(
                        !getTsuFcstPlotConfig().isShowArrivalTime());
            }
        });
        configTravelTimeNowCheckbox = new Button(lowerLeftTimesGroup,
                SWT.RADIO);
        configTravelTimeNowCheckbox.setText("Travel Time from NOW (HH:mm)");
        configTravelTimeNowCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowTravelTimeWrtNow());
        configTravelTimeNowCheckbox
                .addSelectionListener(new SelectionAdapter() {
                    @Override
                    public void widgetSelected(SelectionEvent e) {
                        getTsuFcstPlotConfig()
                                .setShowTravelTimeWrtNow(!getTsuFcstPlotConfig()
                                        .isShowTravelTimeWrtNow());
                    }
                });
        configTravelTimeOriginCheckbox = new Button(lowerLeftTimesGroup,
                SWT.RADIO);
        configTravelTimeOriginCheckbox
                .setText("Travel Time from Origin (HH:mm)");
        configTravelTimeOriginCheckbox.setSelection(
                getTsuFcstPlotConfig().isShowTravelTimeWrtOrigin());
        configTravelTimeOriginCheckbox
                .addSelectionListener(new SelectionAdapter() {
                    @Override
                    public void widgetSelected(SelectionEvent e) {
                        getTsuFcstPlotConfig().setShowTravelTimeWrtOrigin(
                                !getTsuFcstPlotConfig()
                                        .isShowTravelTimeWrtOrigin());
                    }
                });

        // Amplitudes
        Group ampsGroup = new Group(renderOptionsGroup, SWT.NONE);
        GridLayout ampsGroupLayout = new GridLayout();
        ampsGroupLayout.numColumns = 2;
        ampsGroup.setLayout(ampsGroupLayout);
        ampsGroup.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

        configAmpValueCheckbox = new Button(ampsGroup, SWT.CHECK);
        configAmpValueCheckbox.setText("Amplitude Value (m)");
        configAmpValueCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowAmplitudeValue());
        configAmpValueCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setShowAmplitudeValue(
                        configAmpValueCheckbox.getSelection());
            }
        });
        configAmpCircleCheckbox = new Button(ampsGroup, SWT.CHECK);
        configAmpCircleCheckbox.setText("Amplitude Circle");
        configAmpCircleCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowAmplitudeCircle());
        configAmpCircleCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setShowAmplitudeCircle(
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
                getTsuFcstPlotConfig().setShowAll();
                reinitConfigWidgets();
            }
        });
        Button noneButton = new Button(allNoneComp, SWT.PUSH);
        noneButton.setText("Select None");
        noneButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setShowNone();
                reinitConfigWidgets();
            }
        });

        // Now for Filter Options
        Group filterOptionsGroup = new Group(mainComp, SWT.NONE);
        GridLayout filterOptionsLayout = new GridLayout();
        filterOptionsLayout.numColumns = 2;
        filterOptionsGroup.setLayout(filterOptionsLayout);
        filterOptionsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        filterOptionsGroup.setText("Filtering options:");

        Group ampLevelsGroup = new Group(filterOptionsGroup, SWT.NONE);
        ampLevelsGroup.setLayout(new GridLayout());
        ampLevelsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
        ampLevelsGroup.setText("Amplitude Filters");

        applyAmpFiltersCheckbox = new Button(ampLevelsGroup, SWT.CHECK);
        applyAmpFiltersCheckbox.setText("Apply Amplitude Filters as below");
        applyAmpFiltersCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setApplyAmpFilters(
                        applyAmpFiltersCheckbox.getSelection());
            }
        });

        Group ampLevelsGroup2 = new Group(ampLevelsGroup, SWT.NONE);
        ampLevelsGroup2.setLayout(new GridLayout());
        ampLevelsGroup2
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

        FcstAmpLevel nanLevel = getTsuFcstPlotConfig().getNaNAmpLevel();
        FcstAmpLevel zeroLevel = getTsuFcstPlotConfig().getZeroAmpLevel();
        FcstAmpLevel lowLevel = getTsuFcstPlotConfig().getLowAmpLevel();
        FcstAmpLevel medLowLevel = getTsuFcstPlotConfig().getMedLowAmpLevel();
        FcstAmpLevel medHighLevel = getTsuFcstPlotConfig().getMedHighAmpLevel();
        FcstAmpLevel highLevel = getTsuFcstPlotConfig().getHighAmpLevel();

        nanAmpLevelCheckbox = new Button(ampLevelsGroup2, SWT.CHECK);
        zeroAmpLevelCheckbox = new Button(ampLevelsGroup2, SWT.CHECK);
        lowAmpLevelCheckbox = new Button(ampLevelsGroup2, SWT.CHECK);
        medLowAmpLevelCheckbox = new Button(ampLevelsGroup2, SWT.CHECK);
        medHighAmpLevelCheckbox = new Button(ampLevelsGroup2, SWT.CHECK);
        highAmpLevelCheckbox = new Button(ampLevelsGroup2, SWT.CHECK);

        nanAmpLevelCheckbox.setText(nanLevel.getLabel());
        nanAmpLevelCheckbox.setSelection(nanLevel.isSelected());
        nanAmpLevelCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                nanLevel.setSelected(nanAmpLevelCheckbox.getSelection());
            }
        });

        zeroAmpLevelCheckbox.setText(zeroLevel.getLabel());
        zeroAmpLevelCheckbox.setSelection(zeroLevel.isSelected());
        zeroAmpLevelCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                zeroLevel.setSelected(zeroAmpLevelCheckbox.getSelection());
            }
        });

        lowAmpLevelCheckbox.setText(lowLevel.getLabel());
        lowAmpLevelCheckbox.setSelection(lowLevel.isSelected());
        lowAmpLevelCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                lowLevel.setSelected(lowAmpLevelCheckbox.getSelection());
            }
        });

        medLowAmpLevelCheckbox.setText(medLowLevel.getLabel());
        medLowAmpLevelCheckbox.setSelection(medLowLevel.isSelected());
        medLowAmpLevelCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                medLowLevel.setSelected(medLowAmpLevelCheckbox.getSelection());
            }
        });

        medHighAmpLevelCheckbox.setText(medHighLevel.getLabel());
        medHighAmpLevelCheckbox.setSelection(medHighLevel.isSelected());
        medHighAmpLevelCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                medHighLevel
                        .setSelected(medHighAmpLevelCheckbox.getSelection());
            }
        });

        highAmpLevelCheckbox.setText(highLevel.getLabel());
        highAmpLevelCheckbox.setSelection(highLevel.isSelected());
        highAmpLevelCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                highLevel.setSelected(highAmpLevelCheckbox.getSelection());
            }
        });

        Group arrivalTimesGroup = new Group(filterOptionsGroup, SWT.NONE);
        arrivalTimesGroup.setLayout(new GridLayout());
        arrivalTimesGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
        arrivalTimesGroup.setText("Arrival Time Filters");

        applyTimeFiltersCheckbox = new Button(arrivalTimesGroup, SWT.CHECK);
        applyTimeFiltersCheckbox.setText("Apply Arrival Time Filters as below");
        applyTimeFiltersCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setApplyTimeOfArrivalFilters(
                        applyTimeFiltersCheckbox.getSelection());
            }
        });

        Group arrivalTimesGroup2 = new Group(arrivalTimesGroup, SWT.NONE);
        arrivalTimesGroup2.setLayout(new GridLayout());
        arrivalTimesGroup2
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

        // Within hours of NOW
        Composite rowComposite = new Composite(arrivalTimesGroup2, SWT.NONE);
        rowComposite.setLayout(new RowLayout(SWT.HORIZONTAL));
        filterByHrsOfNowCheckbox = new Button(rowComposite, SWT.RADIO);
        filterByHrsOfNowCheckbox.setSelection(
                getTsuFcstPlotConfig().isFilterByWithinHrsOfNow());
        filterByHrsOfNowCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setFilterByWithinHrsOfNow(
                        !getTsuFcstPlotConfig().isFilterByWithinHrsOfNow());
            }
        });
        Label within = new Label(rowComposite, SWT.NONE);
        within.setText("Within");
        hrsOfNowCombo = new Combo(rowComposite, SWT.READ_ONLY);
        for (int i = 1; i <= 24; i++) {
            hrsOfNowCombo.add("" + i);
        }
        hrsOfNowCombo.add(ANY);
        if (getTsuFcstPlotConfig().getWithinHrsOfNow() == null) {
            hrsOfNowCombo.select(24);
        } else {
            int hours = getTsuFcstPlotConfig().getWithinHrsOfNow();
            hrsOfNowCombo.select(hours - 1);
        }
        hrsOfNowCombo.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                String hrsOfNowString = hrsOfNowCombo.getText();
                if (hrsOfNowString != null) {
                    if (hrsOfNowString.equals(ANY)) {
                        getTsuFcstPlotConfig().setWithinHrsOfNow(null);
                    } else {
                        getTsuFcstPlotConfig().setWithinHrsOfNow(
                                Integer.parseInt(hrsOfNowString));
                    }
                }
            }
        });
        Label hrsOfNow = new Label(rowComposite, SWT.NONE);
        hrsOfNow.setText("hours of NOW");

        // Within hours of ORIGIN
        Composite rowComposite2 = new Composite(arrivalTimesGroup2, SWT.NONE);
        rowComposite2.setLayout(new RowLayout(SWT.HORIZONTAL));
        filterByHrsOfOriginCheckbox = new Button(rowComposite2, SWT.RADIO);
        filterByHrsOfOriginCheckbox.setSelection(
                getTsuFcstPlotConfig().isFilterByWithinHrsOfOrigin());
        filterByHrsOfOriginCheckbox
                .addSelectionListener(new SelectionAdapter() {
                    @Override
                    public void widgetSelected(SelectionEvent e) {
                        getTsuFcstPlotConfig().setFilterByWithinHrsOfOrigin(
                                !getTsuFcstPlotConfig()
                                        .isFilterByWithinHrsOfOrigin());
                    }
                });
        Label within2 = new Label(rowComposite2, SWT.NONE);
        within2.setText("Within");
        hrsOfOriginCombo = new Combo(rowComposite2, SWT.READ_ONLY);
        for (int i = 1; i <= 24; i++) {
            hrsOfOriginCombo.add("" + i);
        }
        hrsOfOriginCombo.add(ANY);
        if (getTsuFcstPlotConfig().getWithinHrsOfOrigin() == null) {
            hrsOfOriginCombo.select(24);
        } else {
            int hours = getTsuFcstPlotConfig().getWithinHrsOfOrigin();
            hrsOfOriginCombo.select(hours - 1);
        }
        hrsOfOriginCombo.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                String hrsOfOriginString = hrsOfOriginCombo.getText();
                if (hrsOfOriginString != null) {
                    if (hrsOfOriginString.equals(ANY)) {
                        getTsuFcstPlotConfig().setWithinHrsOfOrigin(null);
                    } else {
                        getTsuFcstPlotConfig().setWithinHrsOfOrigin(
                                Integer.parseInt(hrsOfOriginString));
                    }
                }
            }
        });
        Label hrsOfOrigin = new Label(rowComposite2, SWT.NONE);
        hrsOfOrigin.setText("hours of ORIGIN");

        // Now for Auto Density Button
        Group otherFilterOptionsGroup = new Group(filterOptionsGroup, SWT.NONE);
        otherFilterOptionsGroup.setLayout(new GridLayout());
        otherFilterOptionsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        otherFilterOptionsGroup.setText("Other Filtering options:");

        configAutoDensityCheckbox = new Button(otherFilterOptionsGroup,
                SWT.CHECK);
        configAutoDensityCheckbox.setText("Auto Density Control");
        configAutoDensityCheckbox
                .setSelection(getTsuFcstPlotConfig().isAutoDensityControl());
        configAutoDensityCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setAutoDensityControl(
                        configAutoDensityCheckbox.getSelection());
            }
        });

        Group warningPointsGroup = new Group(filterOptionsGroup, SWT.NONE);
        warningPointsGroup.setLayout(new GridLayout());
        warningPointsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        warningPointsGroup.setText("PTWC Warning Points Options");

        warningPointsOnlyCheckbox = new Button(warningPointsGroup, SWT.CHECK);
        warningPointsOnlyCheckbox.setText("PTWC Warning Points Only");
        warningPointsOnlyCheckbox
                .setSelection(getTsuFcstPlotConfig().isWarningPointsOnly());
        warningPointsOnlyCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setWarningPointsOnly(
                        warningPointsOnlyCheckbox.getSelection());
            }
        });

        Group domainOptionsGroup = new Group(warningPointsGroup, SWT.NONE);
        domainOptionsGroup.setLayout(new GridLayout());
        domainOptionsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        ptwsDomainCheckbox = new Button(domainOptionsGroup, SWT.CHECK);
        ptwsDomainCheckbox.setText("Show \"PTWS\" domain");
        ptwsDomainCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowPtwsDomain());
        ptwsDomainCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig()
                        .setShowPtwsDomain(ptwsDomainCheckbox.getSelection());
            }
        });
        caribeDomainCheckbox = new Button(domainOptionsGroup, SWT.CHECK);
        caribeDomainCheckbox.setText("Show \"CARIBE\" domain");
        caribeDomainCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowCaribeDomain());
        caribeDomainCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig().setShowCaribeDomain(
                        caribeDomainCheckbox.getSelection());
            }
        });
        otherDomainCheckbox = new Button(domainOptionsGroup, SWT.CHECK);
        otherDomainCheckbox.setText("Show \"OTHER\" domain");
        otherDomainCheckbox
                .setSelection(getTsuFcstPlotConfig().isShowOtherDomain());
        otherDomainCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getTsuFcstPlotConfig()
                        .setShowOtherDomain(otherDomainCheckbox.getSelection());
            }
        });

        for (AbstractPlotter childPlotter : getChildPlotters()) {
            childPlotter.buildPlotterConfigTabItems(tabFolder);
        }
        setBuildConfigWidgetsComplete(true);
    }

}
