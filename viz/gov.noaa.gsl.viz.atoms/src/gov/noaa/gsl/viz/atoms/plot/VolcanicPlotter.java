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
import com.raytheon.uf.viz.core.IGraphicsTarget.VerticalAlignment;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.capabilities.Capabilities;
import com.raytheon.uf.viz.core.rsc.capabilities.MagnificationCapability;

import gov.noaa.gsl.common.dataplugin.atoms.VolcanicEventData;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventManager;
import gov.noaa.gsl.viz.pem.plot.AbstractPlotter;

/**
 * Plot / Rendering for volcanic physical events.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023            weingruber             Initial Creation
 *
 * </pre>
 *
 * @author awips
 *
 */
public class VolcanicPlotter extends GeneralPEPlotter {

    private static final RGB WHITE = new RGB(255, 255, 255);

    private static final double LOCATION_INNER_DOT_RADIUS = 2d;

    private static final double LOCATION_OUTER_DOT_RADIUS = 6d;

    private static final double SELECTED_RADIUS = 15d;

    private static final RGB DOT_COLOR = new RGB(255, 0, 0);

    private static final double SELECT_EVENT_CIRCLE_SCREEN_RADIUS_DIFF = 4d;

    private static final int CROSSHAIR_ADDL_PIXELS = 7;

    public VolcanicPlotter() {
        super(new VolcanicPlotConfig());
    }

    private VolcanicPlotConfig getVolcPlotConfig() {
        return (VolcanicPlotConfig) getPlotConfig();
    }

    /**
     * Plots a volcanic event data.
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

            double magnification = drawCapabilities
                    .getCapability(null, MagnificationCapability.class)
                    .getMagnification();

            /*
             * TODO Other options could be to plot colored circles (filled or
             * unfilled), non-linear circles (ie: non-linear radiuses), colored
             * depths, etc
             */
            VolcanicPlotConfig volcPlotConfig = getVolcPlotConfig();
            for (IPhysicalEvent event : getPhysicalEvents()) {

                if (!(event.getData() instanceof VolcanicEventData)) {
                    continue;
                }
                VolcanicEventData volcData = (VolcanicEventData) event
                        .getData();
                boolean isEventSelected = PhysicalEventManager.getInstance()
                        .isSelected(event);

                double[] screenLoc = descriptor.worldToPixel(new double[] {
                        event.getLongitude(), event.getLatitude() });

                /* Event location dot */
                DrawableCircle dot = new DrawableCircle();
                dot.screenRadius = LOCATION_INNER_DOT_RADIUS;
                dot.setCoordinates(screenLoc[0], screenLoc[1]);
                dot.basics.color = DOT_COLOR;
                dot.filled = true;
                target.drawCircle(dot);
                dot.filled = false;
                dot.screenRadius = LOCATION_OUTER_DOT_RADIUS;
                target.drawCircle(dot);

                /* Crosshairs if event is selected */
                if (isEventSelected) {
                    final RGB SELECTED_COLOR = new RGB(255, 0, 0);
                    double radius = SELECTED_RADIUS;
                    DrawableCircle circle = new DrawableCircle();
                    circle.screenRadius = radius;
                    circle.setCoordinates(screenLoc[0], screenLoc[1]);
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
                            .gridToScreen(screenLoc, target);
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

                if (volcPlotConfig.isShowCustomId()) {
                    /* Event Id */
                    DrawableString string = new DrawableString(
                            event.getCustomId(), WHITE);
                    string.setCoordinates(screenLoc[0], screenLoc[1]);
                    string.verticallAlignment = VerticalAlignment.BOTTOM;
                    target.drawStrings(string);
                }

                if (getVolcPlotConfig().isShowRangeRing() && isEventSelected) {
                    RangeRingRenderer rangeRenderer = new RangeRingRenderer(
                            getVolcPlotConfig().getRangeRingRadiusKm(),
                            screenLoc);
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
        setBuildConfigWidgetsComplete(false);
    }

    @Override
    protected void reinitConfigWidgets() {
        if (!isBuildConfigWidgetsComplete() || isIdCheckboxDisposed()) {
            return;
        }
        super.reinitConfigWidgets();
    }

    @Override
    public void buildPlotterConfigTabItems(TabFolder tabFolder) {

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
                getVolcPlotConfig().setShowAll();
                reinitConfigWidgets();
            }
        });
        Button noneButton = new Button(allNoneComp, SWT.PUSH);
        noneButton.setText("Select None");
        noneButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getVolcPlotConfig().setShowNone();
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
