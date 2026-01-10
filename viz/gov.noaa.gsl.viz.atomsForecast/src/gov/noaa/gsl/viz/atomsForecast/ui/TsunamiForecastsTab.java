package gov.noaa.gsl.viz.atomsForecast.ui;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;

import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastInfo;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastType;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiStationForecast;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.pem.utils.PemUtils;
import gov.noaa.gsl.viz.atomsForecast.TsunamiForecastDao;
import gov.noaa.gsl.viz.atomsForecast.TsunamiForecastDaoListener;
import gov.noaa.gsl.viz.pem.dialog.BasePEMDialogTab;

/**
 * Displays the forecast run data for current physical event. It includes the
 * menus of forecast type and forecast run time, and forecast event data.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Apr 19, 2022        Jing                  Initial implement the tsunami  forecast run display
 * Aug 10, 2022        Jing                  Added Station ID and duration
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 */
public class TsunamiForecastsTab extends BasePEMDialogTab
        implements TsunamiForecastDaoListener {
    private static final transient IUFStatusHandler statusHandler = UFStatus
            .getHandler(TsunamiForecastsTab.class);

    private static final String NONE = "<None>";

    private final static String[] COLUMN_HEADERS = { "Id", "Station", "State",
            "Country", "Arrival Time", "Travel Time", "Amplitude (m)",
            "Duration" };

    private final static int[] COLUMN_WIDTHS = { 50, 140, 140, 115, 160, 105,
            100, 80 };

    private static final ColumnStringBuilder[] COLUMN_STRING_BUILDERS = {
            (e, stnFcst) -> stnFcst.getStation().getCustomId(),
            (e, stnFcst) -> stnFcst.getStation().getName(),
            (e, stnFcst) -> stnFcst.getStation().getState(),
            (e, stnFcst) -> stnFcst.getStation().getCountry(),
            (e, stnFcst) -> (stnFcst.getArrivalTime() == null ? "--"
                    : PemUtils.getSecondTimeFormatter()
                            .format(stnFcst.getArrivalTime())),
            (e, stnFcst) -> (stnFcst.getArrivalTime() == null || e == null
                    || e.getRefTime() == null
                            ? "--"
                            : PemUtils.formatElapsedTime(e.getRefTime(),
                                    stnFcst.getArrivalTime())),
            (e, stnFcst) -> (Float.isNaN(stnFcst.getAmplitude()) ? "--"
                    : Float.toString(stnFcst.getAmplitude())),
            (e, stnFcst) -> Integer.toString(stnFcst.getDuration()) };

    /*
     * This is horrible looking code
     */
    private static final Comparator[] COLUMN_COMPARATORS = {
            (Object e1, Object e2) -> ((TsunamiStationForecast) e1).getStation()
                    .getCustomId()
                    .compareTo(((TsunamiStationForecast) e2).getStation()
                            .getCustomId()),
            (Object e1, Object e2) -> ((TsunamiStationForecast) e1).getStation()
                    .getName()
                    .compareTo(((TsunamiStationForecast) e2).getStation()
                            .getName()),
            (Object e1, Object e2) -> ((TsunamiStationForecast) e1).getStation()
                    .getState()
                    .compareTo(((TsunamiStationForecast) e2).getStation()
                            .getState()),
            (Object e1, Object e2) -> ((TsunamiStationForecast) e1).getStation()
                    .getCountry()
                    .compareTo(((TsunamiStationForecast) e2).getStation()
                            .getCountry()),
            (Object e1, Object e2) -> (((TsunamiStationForecast) e1)
                    .getArrivalTime() == null
                    || ((TsunamiStationForecast) e2).getArrivalTime() == null
                            ? 0
                            : ((TsunamiStationForecast) e1).getArrivalTime()
                                    .compareTo(((TsunamiStationForecast) e2)
                                            .getArrivalTime())),
            (Object e1, Object e2) -> (((TsunamiStationForecast) e1)
                    .getArrivalTime() == null
                    || ((TsunamiStationForecast) e2).getArrivalTime() == null
                            ? 0
                            : ((TsunamiStationForecast) e1).getArrivalTime()
                                    .compareTo(((TsunamiStationForecast) e2)
                                            .getArrivalTime())),
            (Object e1, Object e2) -> (Float
                    .isNaN(((TsunamiStationForecast) e1).getAmplitude())
                    || Float.isNaN(((TsunamiStationForecast) e2).getAmplitude())
                            ? 0
                            : Float.compare(
                                    ((TsunamiStationForecast) e1)
                                            .getAmplitude(),
                                    ((TsunamiStationForecast) e2)
                                            .getAmplitude())),
            (Object e1, Object e2) -> Integer.compare(
                    ((TsunamiStationForecast) e1).getDuration(),
                    ((TsunamiStationForecast) e2).getDuration()) };

    public interface ColumnStringBuilder {
        String run(IPhysicalEvent e, TsunamiStationForecast stnFcst);
    }

    private static class ColumnSpec {
        String header = "";

        int width;

        ColumnStringBuilder stringBuilderThing;

        Comparator<TsunamiStationForecast> comparator;

        public ColumnSpec(String hdr, int width, ColumnStringBuilder thing,
                Comparator<TsunamiStationForecast> comp) {
            this.header = hdr;
            this.width = width;
            this.stringBuilderThing = thing;
            this.comparator = comp;
        }
    }

    private static List<ColumnSpec> COLUMN_SPECS = new ArrayList<>();

    static {
        /*
         * The tsu fcst station table column specs, including header, width, and
         * lambda to use to get the string for the value of the cell.
         */
        for (int i = 0; i < COLUMN_HEADERS.length; i++) {
            ColumnSpec spec = new ColumnSpec(COLUMN_HEADERS[i],
                    COLUMN_WIDTHS[i], COLUMN_STRING_BUILDERS[i],
                    COLUMN_COMPARATORS[i]);
            COLUMN_SPECS.add(spec);
        }
    }

    private Comparator<TsunamiStationForecast> tsuStnFcstComparator = null;

    private Composite typeTimeComposite = null;

    /**
     * The menu to select a forecast type. The values depend on all available
     * forecasts for current event
     */
    private Label typeLabel;

    private Combo typeCombo;

    private FcstTypeComboSelectionListener typeComboSelectionListener = new FcstTypeComboSelectionListener();

    /**
     * The menu to select a forecast run time. The values depend on all
     * available forecasts for current event
     */
    private Label runTimeLabel;

    private Combo runTimeCombo;

    private Label descLabel;

    private Text description;

    private RunTimeComboSelectionListener runTimeComboSelectionListener = new RunTimeComboSelectionListener();

    /**
     * The table to display the selected tsunami station forecast data
     */
    private Table forecastTable;

    private List<TsunamiForecastInfo> fcstInfos = new ArrayList<>();

    public TsunamiForecastsTab() {
        super();
        TsunamiForecastDao.getInstance().addTsunamiForecastDaoListener(this);
        setPEPlotter(new TsunamiForecastPlotter());
    }

    private TsunamiForecastPlotter getTsuFcstPlotter() {
        return (TsunamiForecastPlotter) getPEPlotter();
    }

    @Override
    protected void reinitializeTabContent() {

        if (getTabItem() == null || getTabFolder() == null) {
            return;
        }

        /*
         * Dispose the tsunami forecast tab if it's existing, and create one
         * then
         */
        if (getTabContentComposite() != null) {
            getTabContentComposite().dispose();
        }

        setTabContentComposite(new Composite(getTabFolder(), SWT.NONE));
        getTabContentComposite().setLayout(new GridLayout(2, false));
        getTabItem().setControl(getTabContentComposite());

        /* No data, do nothing */
        if (getPhysicalEvent() == null) {
            Label noEventLabel = new Label(getTabContentComposite(), SWT.NONE);
            noEventLabel.setText("No Selected Physical Event");
            getTsuFcstPlotter().setPhysicalEvents(new ArrayList<>());
            getTsuFcstPlotter().setTsunamiForecast(null);
        } else {
            /* Display the tsunami forecast data in the tab */
            fcstInfos = TsunamiForecastDao.getInstance()
                    .getTsunamiForecastInfos(getPhysicalEvent().getCustomId());

            if (fcstInfos.size() == 0) {
                getTsuFcstPlotter().setPhysicalEvents(new ArrayList<>());
                getTsuFcstPlotter().setTsunamiForecast(null);
            }

            typeTimeComposite = new Composite(getTabContentComposite(),
                    SWT.NONE);
            typeTimeComposite
                    .setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
            // typeTimeComposite.setLayout(new RowLayout(SWT.HORIZONTAL));
            typeTimeComposite.setLayout(new GridLayout(6, false));

            // Table has to be created before a RunTime is selected
            createForecastTable();
            createFcstTypeDropdown(typeTimeComposite);
            createRunTimesDropdown(typeTimeComposite);
            createDescTextField(typeTimeComposite);
            typeTimeComposite.pack();
        }
    }

    /**
     * Create the menus of the forecast type
     *
     * @param parent
     *            The parent composite holding the menus.
     */
    private void createFcstTypeDropdown(Composite parent) {

        /* The forecast type menu */
        if (typeLabel == null || typeLabel.isDisposed()) {
            typeLabel = new Label(parent, SWT.NONE);
            typeLabel.setText(" Forecast Type: ");
        }

        if (typeCombo == null || typeCombo.isDisposed()) {
            typeCombo = new Combo(parent, SWT.READ_ONLY | SWT.SINGLE);
        }
        typeCombo.removeAll();

        List<TsunamiForecastType> fcstTypes = TsunamiForecastInfo
                .getFcstTypes(fcstInfos);
        for (TsunamiForecastType type : fcstTypes) {
            typeCombo.add(type.toString());
        }

        /* The selection listener for the forecast type menu */
        typeCombo.addSelectionListener(typeComboSelectionListener);
        if (fcstTypes.size() > 0) {
            typeCombo.setSelection(new Point(0, 0));
            typeCombo.setText(fcstTypes.get(0).toString());
            // Lame SWT doesn't notify the SelectionListener. Do it manually.
            typeComboSelectionListener.widgetSelected(null);
        }
    }

    /**
     * Create the menus of the run time.
     *
     * @param parent
     *            The parent composite holding the menus.
     */
    private void createRunTimesDropdown(Composite parent) {

        TsunamiForecastType selectedFcstType = getSelectedForecastType();
        if (selectedFcstType == null) {
            return;
        }
        /* The forecast run time menu */
        if (runTimeLabel == null || runTimeLabel.isDisposed()) {
            runTimeLabel = new Label(parent, SWT.NONE);
            runTimeLabel.setText("  Forecast Run Time: ");
        }

        if (runTimeCombo == null || runTimeCombo.isDisposed()) {
            runTimeCombo = new Combo(parent, SWT.READ_ONLY | SWT.SINGLE);
        }
        runTimeCombo.removeAll();

        List<Date> runTimes = TsunamiForecastInfo.getFcstRunTimes(fcstInfos,
                selectedFcstType);

        for (Date runTime : runTimes) {
            runTimeCombo.add(PemUtils.getSecondTimeFormatter().format(runTime));
        }
        /* The selection listener for the forecast run time menu */
        runTimeCombo.addSelectionListener(runTimeComboSelectionListener);

        if (runTimes.size() > 0) {
            runTimeCombo.setSelection(new Point(0, 0));
            runTimeCombo.setText(
                    PemUtils.getSecondTimeFormatter().format(runTimes.get(0)));
            // Lame SWT doesn't notify the SelectionListener. Do it manually.
            runTimeComboSelectionListener.widgetSelected(null);
        }
    }

    private void createDescTextField(Composite parent) {

        /* The description label */
        if (descLabel == null || descLabel.isDisposed()) {
            descLabel = new Label(parent, SWT.NONE);
            descLabel.setText("  Description: ");
        }

        if (description == null || description.isDisposed()) {
            description = new Text(parent, SWT.MULTI | SWT.READ_ONLY | SWT.WRAP
                    | SWT.H_SCROLL | SWT.V_SCROLL);
            description.setText(NONE);
            description.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
        }
    }

    /**
     * Create the tsunami station forecast table.
     */
    private void createForecastTable() {
        getTabContentComposite().setBackground(new Color(250, 150, 100));

        if (forecastTable != null) {
            forecastTable.dispose();
        }

        forecastTable = new Table(getTabContentComposite(),
                SWT.BORDER | SWT.FULL_SELECTION | SWT.V_SCROLL | SWT.FILL);
        final GridData gd = new GridData(SWT.FILL, SWT.FILL, true, true);
        gd.horizontalSpan = 2;
        gd.heightHint = 200;
        forecastTable.setLayoutData(gd);
        forecastTable.setHeaderVisible(true);
        forecastTable.setVisible(true);
        forecastTable.setBackground(new Color(0, 200, 0));
        forecastTable.getVerticalBar().isVisible();
        forecastTable.getVerticalBar().setEnabled(true);
        // forecastTable.computeSize(SWT.DEFAULT, SWT.DEFAULT);

        /* Set column headers, widths, resizeable */
        int i = 0;
        for (ColumnSpec spec : COLUMN_SPECS) {

            final TableColumn tc = new TableColumn(forecastTable, SWT.LEFT);
            tc.setText(spec.header);
            tc.setWidth(spec.width);
            // tc.setMoveable(true);
            tc.setResizable(true);
            tc.setData(spec);

            tc.addSelectionListener(new SelectionAdapter() {
                @Override
                public void widgetSelected(SelectionEvent e) {
                    TableColumn column = (TableColumn) e.widget;
                    ColumnSpec spec = (ColumnSpec) column.getData();
                    Comparator<TsunamiStationForecast> comparator = null;
                    if (spec != null && spec.comparator != null) {
                        tsuStnFcstComparator = spec.comparator;
                        /*
                         * Clicked on current sort column? If so, reverse the
                         * sort
                         */
                        if (column.equals(forecastTable.getSortColumn())) {
                            forecastTable.setSortDirection(
                                    forecastTable.getSortDirection() == SWT.UP
                                            ? SWT.DOWN
                                            : SWT.UP);
                            int newSortDirection = forecastTable
                                    .getSortDirection();
                            if (newSortDirection == SWT.DOWN) {
                                tsuStnFcstComparator = tsuStnFcstComparator
                                        .reversed();
                            }
                        }
                        /* Otherwise new sort column */
                        else {
                            forecastTable.setSortColumn(column);
                            forecastTable.setSortDirection(SWT.UP);
                        }
                    }

                    updateTable();
                }
            });

            if (i == 0) {
                tsuStnFcstComparator = spec.comparator;
                forecastTable.setSortColumn(tc);
                i++;
            }
        }
        forecastTable.pack();
    }

    private TsunamiForecastType getSelectedForecastType() {
        if (typeCombo == null || typeCombo.isDisposed()
                || typeCombo.getText() == null
                || typeCombo.getText().isEmpty()) {
            return null;
        }

        return TsunamiForecastType.valueOf(typeCombo.getText());
    }

    private Date getSelectedRunTime() {
        if (runTimeCombo == null || runTimeCombo.isDisposed()
                || runTimeCombo.getText() == null
                || runTimeCombo.getText().isEmpty()) {
            return null;
        }

        Date date = null;
        try {
            date = PemUtils.getSecondTimeFormatter()
                    .parse(runTimeCombo.getText());
        } catch (Exception e) {
            throw new IllegalStateException(getClass().getName()
                    + " getSelectedRunTime() has an incorrectly formatted date in the runTimeCombo.");
        }
        return date;
    }

    /**
     * Update the tsunami station forecast table.
     */
    private void updateTable() {

        forecastTable.removeAll();

        if (getPhysicalEvent() == null) {
            getTsuFcstPlotter().setPhysicalEvents(new ArrayList<>());
            getTsuFcstPlotter().setTsunamiForecast(null);
            return;
        }

        /*
         * Display tsunami station forecast for the selected forecast type and
         * run time
         */
        TsunamiForecastType selectedFcstType = getSelectedForecastType();
        Date selectedRunTime = getSelectedRunTime();
        if (selectedFcstType == null || selectedRunTime == null) {
            getTsuFcstPlotter().setPhysicalEvents(new ArrayList<>());
            getTsuFcstPlotter().setTsunamiForecast(null);
            return;
        }

        List<TsunamiForecast> fcsts = TsunamiForecastDao.getInstance()
                .getTsunamiForecasts(getPhysicalEvent().getCustomId(),
                        selectedFcstType, selectedRunTime);
        if (fcsts.size() != 1) {
            throw new IllegalStateException(getClass().getName()
                    + " tried to get a TsunamiForecast for customEventId = "
                    + getPhysicalEvent().getCustomId() + ", selectedFcstType = "
                    + selectedFcstType.toString() + ", selectedRunTime = "
                    + PemUtils.getSecondTimeFormatter().format(selectedRunTime)
                    + " but received != 1 forecasts!");
        }

        TsunamiForecast fcst = fcsts.get(0);
        description.setText(("".equals(fcst.getDescription()) ? NONE
                : fcst.getDescription()));
        typeTimeComposite.pack(true);
        List<IPhysicalEvent> phyEvents = new ArrayList<>();
        phyEvents.add(getPhysicalEvent());
        getTsuFcstPlotter().setPhysicalEvents(phyEvents);
        getTsuFcstPlotter().setTsunamiForecast(fcst);

        Collection<TsunamiStationForecast> stnFcstsCollection = fcst
                .getStationFcsts();
        List<TsunamiStationForecast> stnFcstsList = new ArrayList<>(
                stnFcstsCollection);
        Collections.sort(stnFcstsList, tsuStnFcstComparator);

        for (TsunamiStationForecast stnFcst : stnFcstsList) {
            String[] tableItemStrings = getTableItemStrings(stnFcst);

            final TableItem item = new TableItem(forecastTable, SWT.NONE);
            Color rowColor = TsunamiForecastPlotter
                    .getAmplitudeColor(stnFcst.getAmplitude());
            item.setBackground(rowColor);
            item.setText(tableItemStrings);
        }

        forecastTable.computeSize(SWT.DEFAULT, SWT.DEFAULT);
        forecastTable.getVerticalBar().getEnabled();
        forecastTable.getVerticalBar().setVisible(true);
    }

    private String[] getTableItemStrings(TsunamiStationForecast stnFcst) {

        String[] stnFcstStrings = new String[COLUMN_SPECS.size()];

        for (int i = 0; i < COLUMN_SPECS.size(); i++) {
            ColumnSpec spec = COLUMN_SPECS.get(i);
            stnFcstStrings[i] = spec.stringBuilderThing.run(getPhysicalEvent(),
                    stnFcst);
        }
        return stnFcstStrings;
    }

    @Override
    public void disposeTabItem() {
        if (typeCombo != null) {
            try {
                typeCombo.removeSelectionListener(typeComboSelectionListener);
            } catch (Exception e) {
                /* Do nothing */
            }
            if (!typeCombo.isDisposed()) {
                typeCombo.dispose();
            }
            typeCombo = null;
        }

        if (runTimeCombo != null) {
            try {
                runTimeCombo
                        .removeSelectionListener(runTimeComboSelectionListener);
            } catch (Exception e) {
                /* Do nothing */
            }

            if (!runTimeCombo.isDisposed()) {
                runTimeCombo.dispose();
            }
            runTimeCombo = null;
        }

        super.disposeTabItem();

    }

    /////////////////////////////////////////////////////////////////////////////////////////
    @Override
    public void tsunamiForecastAdded(String customEventId) {
        updateTable();
    }

    @Override
    public void tsunamiForecastRemoved(String customEventId) {
        updateTable();
    }

    @Override
    public void tsunamiForecastChanged(String customEventId) {

        /*
         * Check if the customEventId == physicalEvent.getCustomId(). otherwise
         * ignore.
         */
        if (customEventId == null || getPhysicalEvent() == null
                || !customEventId.equals(getPhysicalEvent().getCustomId())) {
            return;
        }
        Display.getDefault().syncExec(() -> {
            reinitializeTabContent();
        });
    }

    /////////////////////////////////////////////////////////////////////////////////////////
    private class FcstTypeComboSelectionListener extends SelectionAdapter {

        @Override
        public void widgetSelected(SelectionEvent e) {
            createRunTimesDropdown(typeTimeComposite);
            createDescTextField(typeTimeComposite);
            typeTimeComposite.pack();
        }
    }

    private class RunTimeComboSelectionListener extends SelectionAdapter {

        @Override
        public void widgetSelected(SelectionEvent e) {
            createDescTextField(typeTimeComposite);
            updateTable();
        }
    }
}
