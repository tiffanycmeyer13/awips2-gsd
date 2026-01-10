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

import java.util.Collection;
import java.util.Set;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;

import com.raytheon.uf.viz.core.DrawableCircle;
import com.raytheon.uf.viz.core.DrawableLine;
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

import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventManager;
import gov.noaa.gsl.viz.pem.plot.AbstractPlotter;
import gov.noaa.gsl.viz.pem.plot.ProgressiveDisclosureStrategy;

/**
 * Plot / Rendering for Seismic physical events.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023            jing             Initial Creation
 *                         weingruber
 *
 * </pre>
 *
 * @author awips
 *
 */

public class SeismicPlotter extends GeneralPEPlotter {

    private static final RGB GREEN = new RGB(0, 255, 0);

    private static final RGB WHITE = new RGB(255, 255, 255);

    private static final double LOCATION_DOT_RADIUS = 2d;

    private static final double SELECT_EVENT_CIRCLE_SCREEN_RADIUS_DIFF = 4d;

    private static final int CROSSHAIR_ADDL_PIXELS = 7;

    private Button configMagValueCheckbox;

    private Button configMagCircleCheckbox;

    private Button configDepthCheckbox;

    private Button configPWaveCheckbox;

    private Button configPWaveMinLinesCheckbox;

    public SeismicPlotter() {
        super(new SeismicPlotConfig());
    }

    public SeismicPlotConfig getSeismicPlotConfig() {
        if (getPlotConfig() instanceof SeismicPlotConfig) {
            return (SeismicPlotConfig) getPlotConfig();
        }
        return null;
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

        try {
            if (getPhysicalEvents().size() == 0) {
                return;
            }

            Collection<IPhysicalEvent> phyEvents = getPhysicalEvents();

            double magnification = drawCapabilities
                    .getCapability(null, MagnificationCapability.class)
                    .getMagnification();

            SeismicPlotConfig seismicPlotConfig = getSeismicPlotConfig();

            // Progressive disclosure / density control
            if (seismicPlotConfig.isAutoDensityControl()) {
                double density = drawCapabilities
                        .getCapability(null, DensityCapability.class)
                        .getDensity();
                ProgressiveDisclosureStrategy<IPhysicalEvent> progDisc = new ProgressiveDisclosureStrategy<>(
                        paintProps, descriptor);
                progDisc.setDensity(density);
                progDisc.setMagnification(magnification);
                phyEvents = progDisc.progDisc(getPhysicalEvents(), target);
            }

            /*
             * Also make sure the currently SELECTED physical event is being
             * displayed (as it may have been removed by progressive disclosure)
             */
            Set<IPhysicalEvent> selectedEvents = PhysicalEventManager
                    .getInstance().getSelectedPhysicalEvents();
            phyEvents.addAll(selectedEvents);

            /*
             * TODO Other options could be to plot colored circles (filled or
             * unfilled), non-linear circles (ie: non-linear radiuses), colored
             * depths, etc
             */
            for (IPhysicalEvent event : phyEvents) {

                if (!(event.getData() instanceof SeismicEventData)) {
                    continue;
                }
                SeismicEventData smicData = (SeismicEventData) event.getData();
                boolean isEventSelected = PhysicalEventManager.getInstance()
                        .isSelected(event);

                /* Event location dot */
                DrawableCircle dot = new DrawableCircle();
                dot.screenRadius = LOCATION_DOT_RADIUS;
                double[] screenLocation = descriptor.worldToPixel(new double[] {
                        event.getLongitude(), event.getLatitude() });
                dot.setCoordinates(screenLocation[0], screenLocation[1]);
                dot.basics.color = GREEN;
                dot.filled = true;
                target.drawCircle(dot);

                /* Crosshairs if event is selected */
                if (isEventSelected) {
                    final RGB SELECTED_COLOR = new RGB(255, 0, 0);
                    double radius = MagnitudeCircleRenderer
                            .getEventScreenCircleRadius(descriptor,
                                    magnification, event)
                            + SELECT_EVENT_CIRCLE_SCREEN_RADIUS_DIFF;
                    DrawableCircle circle = new DrawableCircle();
                    circle.screenRadius = radius;
                    circle.setCoordinates(screenLocation[0], screenLocation[1]);
                    circle.basics.color = SELECTED_COLOR;
                    circle.filled = false;
                    circle.lineStyle = IGraphicsTarget.LineStyle.DEFAULT;
                    circle.lineWidth = 2f;
                    target.drawCircle(circle);
                    // Draw crosshairs / target. Comically, the circle radius
                    // is in screen coordinates, whereas the Lines are in grid
                    // coords. Also our limited # of columns java
                    // formatting is horrible. Add pixels, and then round.
                    final int crosshairLength = (int) (radius
                            + CROSSHAIR_ADDL_PIXELS + 0.5);
                    double[] realScreenLoc = target.getView()
                            .gridToScreen(screenLocation, target);
                    double[] north = { realScreenLoc[0],
                            realScreenLoc[1] + crosshairLength };
                    double[] south = { realScreenLoc[0],
                            realScreenLoc[1] - crosshairLength };
                    double[] west = { realScreenLoc[0] - crosshairLength,
                            realScreenLoc[1] };
                    double[] east = { realScreenLoc[0] + crosshairLength,
                            realScreenLoc[1] };
                    north = target.getView().screenToGrid(north[0], north[1], 0,
                            target);
                    south = target.getView().screenToGrid(south[0], south[1], 0,
                            target);
                    west = target.getView().screenToGrid(west[0], west[1], 0,
                            target);
                    east = target.getView().screenToGrid(east[0], east[1], 0,
                            target);
                    DrawableLine line1 = new DrawableLine();
                    line1.basics.color = SELECTED_COLOR;
                    line1.addPoint(north[0], north[1]);
                    line1.addPoint(south[0], south[1]);
                    line1.width = 2f;
                    DrawableLine line2 = new DrawableLine();
                    line2.basics.color = SELECTED_COLOR;
                    line2.addPoint(west[0], west[1]);
                    line2.addPoint(east[0], east[1]);
                    line2.width = 2f;
                    target.drawLine(line1, line2);
                }

                if (seismicPlotConfig.isShowCustomId()) {
                    /* Event Id */
                    DrawableString string = new DrawableString(
                            event.getCustomId() + " ", GREEN);
                    string.setCoordinates(screenLocation[0], screenLocation[1]);
                    string.verticallAlignment = VerticalAlignment.BOTTOM;
                    string.horizontalAlignment = HorizontalAlignment.RIGHT;
                    target.drawStrings(string);
                }
                if (seismicPlotConfig.isShowMagnitudeValue()) {
                    MagnitudeValueRenderer magRenderer = new MagnitudeValueRenderer(
                            smicData.getPrefMagnitude(), screenLocation);
                    magRenderer.plotMagnitude(target, descriptor, paintProps,
                            magnification, WHITE);
                }
                if (seismicPlotConfig.isShowMagnitudeCircle()) {
                    MagnitudeCircleRenderer magRenderer = new MagnitudeCircleRenderer(
                            smicData.getPrefMagnitude(), screenLocation);
                    magRenderer.plotMagnitude(target, descriptor, paintProps,
                            magnification, GREEN);
                }
                if (seismicPlotConfig.isShowDepthValue()) {
                    DepthRenderer depthRenderer = new DepthRenderer(
                            smicData.getDepth(), screenLocation);
                    depthRenderer.plot(target, descriptor, paintProps,
                            magnification, WHITE);
                }
                if (seismicPlotConfig.isShowPWave()
                        || seismicPlotConfig.isShowPWaveWithMinuteLines()) {
                    PWaveRenderer pWaveRenderer = new PWaveRenderer(event);
                    pWaveRenderer.setHistoricMinutesLine(
                            seismicPlotConfig.isShowPWaveWithMinuteLines());
                    pWaveRenderer.plot(target, paintProps, descriptor,
                            drawCapabilities, GREEN);
                }
                if (seismicPlotConfig.isShowRangeRing() && isEventSelected) {
                    RangeRingRenderer rangeRenderer = new RangeRingRenderer(
                            seismicPlotConfig.getRangeRingRadiusKm(),
                            screenLocation);
                    rangeRenderer.plot(target, descriptor, paintProps,
                            magnification, CYAN);
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

    @Override
    protected void clearConfigWidgets() {
        super.clearConfigWidgets();
        configMagValueCheckbox = null;
        configMagCircleCheckbox = null;
        configDepthCheckbox = null;
        configPWaveCheckbox = null;
        configPWaveMinLinesCheckbox = null;
        setBuildConfigWidgetsComplete(false);
    }

    @Override
    protected void reinitConfigWidgets() {
        if (!isBuildConfigWidgetsComplete() || isIdCheckboxDisposed()) {
            return;
        }
        super.reinitConfigWidgets();
        configMagValueCheckbox
                .setSelection(getSeismicPlotConfig().isShowMagnitudeValue());
        configMagCircleCheckbox
                .setSelection(getSeismicPlotConfig().isShowMagnitudeCircle());
        configDepthCheckbox
                .setSelection(getSeismicPlotConfig().isShowDepthValue());
        configPWaveCheckbox.setSelection(getSeismicPlotConfig().isShowPWave());
        configPWaveMinLinesCheckbox.setSelection(
                getSeismicPlotConfig().isShowPWaveWithMinuteLines());
    }

    @Override
    public void buildPlotterConfigTabItems(TabFolder tabFolder) {

        clearConfigWidgets();

        TabItem tabItem = new TabItem(tabFolder, SWT.BORDER);
        tabItem.setText("General");

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

        buildIdCheckbox(renderOptionsGroup);

        configMagValueCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configMagValueCheckbox.setText("Magnitude Value");
        configMagValueCheckbox
                .setSelection(getSeismicPlotConfig().isShowMagnitudeValue());
        configMagValueCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSeismicPlotConfig().setShowMagnitudeValue(
                        configMagValueCheckbox.getSelection());
            }
        });
        configMagCircleCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configMagCircleCheckbox.setText("Magnitude Circle");
        configMagCircleCheckbox
                .setSelection(getSeismicPlotConfig().isShowMagnitudeCircle());
        configMagCircleCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSeismicPlotConfig().setShowMagnitudeCircle(
                        configMagCircleCheckbox.getSelection());
            }
        });
        configDepthCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configDepthCheckbox.setText("Depth");
        configDepthCheckbox
                .setSelection(getSeismicPlotConfig().isShowDepthValue());
        configDepthCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSeismicPlotConfig()
                        .setShowDepthValue(configDepthCheckbox.getSelection());
            }
        });
        configPWaveCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configPWaveCheckbox.setText("P-Wave");
        configPWaveCheckbox.setSelection(getSeismicPlotConfig().isShowPWave());
        configPWaveCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSeismicPlotConfig()
                        .setShowPWave(configPWaveCheckbox.getSelection());
            }
        });
        configPWaveMinLinesCheckbox = new Button(renderOptionsGroup, SWT.CHECK);
        configPWaveMinLinesCheckbox.setText("P-Wave With Minute Lines");
        configPWaveMinLinesCheckbox.setSelection(
                getSeismicPlotConfig().isShowPWaveWithMinuteLines());
        configPWaveMinLinesCheckbox
                .addSelectionListener(new SelectionAdapter() {
                    @Override
                    public void widgetSelected(SelectionEvent e) {
                        getSeismicPlotConfig().setShowPWaveWithMinuteLines(
                                configPWaveMinLinesCheckbox.getSelection());
                    }
                });

        buildRangeRingGroup(renderOptionsGroup);

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
                getSeismicPlotConfig().setShowAll();
                reinitConfigWidgets();
            }
        });
        Button noneButton = new Button(allNoneComp, SWT.PUSH);
        noneButton.setText("Select None");
        noneButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getSeismicPlotConfig().setShowNone();
                reinitConfigWidgets();
            }
        });

        // Now for Auto Density Button
        buildAutoDensityGroup(mainComp);

        for (AbstractPlotter childPlotter : getChildPlotters()) {
            childPlotter.buildPlotterConfigTabItems(tabFolder);
        }

        setBuildConfigWidgetsComplete(true);
    }

}
