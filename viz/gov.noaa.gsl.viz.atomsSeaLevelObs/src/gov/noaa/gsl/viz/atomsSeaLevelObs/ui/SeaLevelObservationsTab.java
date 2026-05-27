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
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;

import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SLOObsType;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SLOSensorType;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObs;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObservations;
import gov.noaa.gsl.pem.utils.PemUtils;
import gov.noaa.gsl.viz.atomsSeaLevelObs.SeaLevelObsDao;
import gov.noaa.gsl.viz.atomsSeaLevelObs.SeaLevelObsDaoListener;
import gov.noaa.gsl.viz.pem.dialog.BasePEMDialogTab;

/**
 * Displays the sea level observations for current physical event. The
 * implementation is with the table.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Apr 19, 2022        Jing                  Initial implement the sea level observations display
 * Aug 10, 2022        Jing                  Added name, state, country and obs-type
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 */

public class SeaLevelObservationsTab extends BasePEMDialogTab
        implements SeaLevelObsDaoListener {
    private static final transient IUFStatusHandler statusHandler = UFStatus
            .getHandler(SeaLevelObservationsTab.class);

    private final static String[] COLUMN_HEADERS = { "Id", "Name", "State",
            "Country", "Sensor", "Obs Type", "Start Time", "End Time",
            "Amplitude (m)" };

    private final static int[] COLUMN_WIDTHS = { 50, 140, 140, 115, 65, 120,
            160, 160, 60 };

    private static final ColumnStringBuilder[] COLUMN_STRING_BUILDERS = {
            (obs) -> obs.getStation().getCustomId(),
            (obs) -> obs.getStation().getName(),
            (obs) -> obs.getStation().getState(),
            (obs) -> obs.getStation().getCountry(),
            (obs) -> (obs.getSensorType() == null ? ""
                    : obs.getSensorType().toString()),
            (obs) -> (obs.getObsType() == null ? ""
                    : obs.getObsType().toString()),
            (obs) -> (obs.getStartTime() != null ? PemUtils
                    .getSecondTimeFormatter().format(obs.getStartTime()) : ""),
            (obs) -> (obs.getEndTime() != null
                    ? PemUtils.getSecondTimeFormatter().format(obs.getEndTime())
                    : ""),
            (obs) -> (obs.getAmplitude() != null ? obs.getAmplitude().toString()
                    : "") };

    /*
     * This is horrible looking code
     */
    private static final Comparator[] COLUMN_COMPARATORS = {
            (Object e1, Object e2) -> ((SeaLevelObs) e1).getStation()
                    .getCustomId()
                    .compareTo(((SeaLevelObs) e2).getStation().getCustomId()),
            (Object e1, Object e2) -> ((SeaLevelObs) e1).getStation().getName()
                    .compareTo(((SeaLevelObs) e2).getStation().getName()),
            (Object e1, Object e2) -> ((SeaLevelObs) e1).getStation().getState()
                    .compareTo(((SeaLevelObs) e2).getStation().getState()),
            (Object e1, Object e2) -> ((SeaLevelObs) e1).getStation()
                    .getCountry()
                    .compareTo(((SeaLevelObs) e2).getStation().getCountry()),
            (Object e1,
                    Object e2) -> (((SeaLevelObs) e1).getSensorType() == null
                            || ((SeaLevelObs) e2).getSensorType() == null
                                    ? 0
                                    : ((SeaLevelObs) e1).getSensorType()
                                            .compareTo(((SeaLevelObs) e2)
                                                    .getSensorType())),
            (Object e1,
                    Object e2) -> (((SeaLevelObs) e1).getObsType() == null
                            || ((SeaLevelObs) e2).getObsType() == null
                                    ? 0
                                    : ((SeaLevelObs) e1).getObsType().compareTo(
                                            ((SeaLevelObs) e2).getObsType())),
            (Object e1,
                    Object e2) -> (((SeaLevelObs) e1).getStartTime() == null
                            || ((SeaLevelObs) e2).getStartTime() == null
                                    ? 0
                                    : ((SeaLevelObs) e1).getStartTime()
                                            .compareTo(((SeaLevelObs) e2)
                                                    .getStartTime())),
            (Object e1,
                    Object e2) -> (((SeaLevelObs) e1).getEndTime() == null
                            || ((SeaLevelObs) e2).getEndTime() == null
                                    ? 0
                                    : ((SeaLevelObs) e1).getEndTime().compareTo(
                                            ((SeaLevelObs) e2).getEndTime())),
            (Object e1, Object e2) -> (((SeaLevelObs) e1).getAmplitude() == null
                    || ((SeaLevelObs) e2).getAmplitude() == null ? 0
                            : ((SeaLevelObs) e1).getAmplitude().compareTo(
                                    ((SeaLevelObs) e2).getAmplitude())), };

    public interface ColumnStringBuilder {
        String run(SeaLevelObs obs);
    }

    private static class ColumnSpec {
        String header = "";

        int width;

        ColumnStringBuilder stringBuilderThing;

        Comparator<SeaLevelObs> comparator;

        public ColumnSpec(String hdr, int width, ColumnStringBuilder thing,
                Comparator<SeaLevelObs> comp) {
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

    private Comparator<SeaLevelObs> obsComparator = null;

    /* The sea level observation table */
    private Table sealevelObsTable;

    /* All sea level observation data */
    private List<SeaLevelObs> allSlobs = new ArrayList<>();

    private Composite typeTimeComposite = null;

    public SeaLevelObservationsTab() {
        super();
        SeaLevelObsDao.getInstance().addSeaLevelObsDaoListener(this);
        setPEPlotter(new SeaLevelObsPlotter());
    }

    private SeaLevelObsPlotter getSeaLevelObsPlotter() {
        return (SeaLevelObsPlotter) getPEPlotter();
    }

    @Override
    protected void reinitializeTabContent() {
        if (getTabItem() == null || getTabFolder() == null) {
            return;
        }

        if (getTabContentComposite() != null) {
            getTabContentComposite().dispose();
        }
        setTabContentComposite(new Composite(getTabFolder(), SWT.NONE));
        getTabContentComposite().setLayout(new GridLayout(2, false));
        getTabItem().setControl(getTabContentComposite());

        /* No event data, do noting */
        if (getPhysicalEvent() == null) {
            getTabContentComposite().setLayout(new GridLayout(2, false));
            Label noEventLabel = new Label(getTabContentComposite(), SWT.NONE);
            noEventLabel.setText("No Selected Physical Event");

            getTabContentComposite().pack();
            getTabItem().setControl(getTabContentComposite());
        } else {
            /* Display the detail sea level observations of the event */
//            getTabContentComposite()
//                    .setLayout(new GridLayout(COLUMN_HEADERS.length, false));

            /*
             * Get all SLObs Runs, and sort them oldest to newest
             */
            allSlobs.clear();
            List<SeaLevelObservations> slobsRunList = SeaLevelObsDao
                    .getInstance().getSeaLevelObservations(
                            getPhysicalEvent().getCustomId(), null);
            Collections.sort(slobsRunList,
                    new Comparator<SeaLevelObservations>() {

                        @Override
                        public int compare(SeaLevelObservations arg0,
                                SeaLevelObservations arg1) {
                            if (arg0 == null || arg1 == null
                                    || arg0.getDataTime() == null
                                    || arg1.getDataTime() == null
                                    || arg0.getDataTime().getRefTime() == null
                                    || arg1.getDataTime()
                                            .getRefTime() == null) {
                                return 0;
                            }

                            return arg0.getDataTime().getRefTime()
                                    .compareTo(arg1.getDataTime().getRefTime());
                        }
                    });

            /*
             * Remove duplicates - do so by adding each SLObs to a map, via a
             * key, and overwriting the duplicates with the same key but newer
             * values. We go thru the slobsRuns, from oldest to newest. We "put"
             * each time, and if the key already exists, it will be overwritten
             * with the newest values. Note the Key's equals and hashcode
             * methods, such that two Keys with different startTimes will be
             * different (for example), allowing for history. Or note that
             * different SLOSensorTypes make different keys too.
             */
            Map<SlobsKey, SeaLevelObs> slobsMap = new HashMap<>();
            for (SeaLevelObservations slobsRun : slobsRunList) {
                for (SeaLevelObs obs : slobsRun.getSeaLevelObs()) {
                    SlobsKey key = new SlobsKey(obs);
                    slobsMap.put(key, obs);
                }
            }

            /*
             * Now put all of those SLObs in a List, to be sorted later. I dont
             * much like this whole algorithm. Hhhmpf.
             */
            for (Map.Entry<SlobsKey, SeaLevelObs> entry : slobsMap.entrySet()) {
                allSlobs.add(entry.getValue());
            }

            typeTimeComposite = new Composite(getTabContentComposite(),
                    SWT.NONE);
            typeTimeComposite.setLayout(new RowLayout(SWT.HORIZONTAL));

            createSeaLevelObsTable();
            updateTable();
        }
    }

    /**
     * Create the sea level observation table.
     */
    private void createSeaLevelObsTable() {
        getTabContentComposite().setBackground(new Color(250, 150, 100));

        if (sealevelObsTable != null) {
            sealevelObsTable.dispose();
        }

        /* Builds the table */
        sealevelObsTable = new Table(getTabContentComposite(),
                SWT.BORDER | SWT.FULL_SELECTION | SWT.V_SCROLL);
        final GridData gd = new GridData(GridData.FILL_BOTH);
        gd.horizontalAlignment = GridData.FILL;
        gd.grabExcessHorizontalSpace = true;
        gd.horizontalSpan = 2;
        sealevelObsTable.setLayoutData(gd);
        sealevelObsTable.setHeaderVisible(true);
        sealevelObsTable.setVisible(true);
        sealevelObsTable.setBackground(new Color(0, 200, 0));

        /* Set column headers, widths, resizeable */
        int i = 0;
        for (ColumnSpec spec : COLUMN_SPECS) {

            final TableColumn tc = new TableColumn(sealevelObsTable, SWT.LEFT);
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
                    Comparator<SeaLevelObs> comparator = null;
                    if (spec != null && spec.comparator != null) {
                        obsComparator = spec.comparator;
                        /*
                         * Clicked on current sort column? If so, reverse the
                         * sort
                         */
                        if (column.equals(sealevelObsTable.getSortColumn())) {
                            sealevelObsTable.setSortDirection(sealevelObsTable
                                    .getSortDirection() == SWT.UP ? SWT.DOWN
                                            : SWT.UP);
                            int newSortDirection = sealevelObsTable
                                    .getSortDirection();
                            if (newSortDirection == SWT.DOWN) {
                                obsComparator = obsComparator.reversed();
                            }
                        }
                        /* Otherwise new sort column */
                        else {
                            sealevelObsTable.setSortColumn(column);
                            sealevelObsTable.setSortDirection(SWT.UP);
                        }
                    }

                    updateTable();
                }
            });

            if (i == 0) {
                obsComparator = spec.comparator;
                sealevelObsTable.setSortColumn(tc);
                i++;
            }
        }

        sealevelObsTable.pack();
    }

    /**
     * Update the sea level observation display in the table.
     */
    private void updateTable() {

        sealevelObsTable.removeAll();

        getSeaLevelObsPlotter().setSeaLevelObs(allSlobs);
        if (allSlobs == null || allSlobs.size() == 0) {
            return;
        }

        Collections.sort(allSlobs, obsComparator);

        for (SeaLevelObs obs : allSlobs) {
            String[] tableItemStrs = getTableItemStrings(obs);
            final TableItem item = new TableItem(sealevelObsTable, SWT.NONE);
            item.setBackground(
                    SeaLevelObsPlotter.getAmplitudeColor(obs.getAmplitude()));
            item.setText(tableItemStrs);
        }
    }

    private String[] getTableItemStrings(SeaLevelObs slob) {

        String[] slobsStrings = new String[COLUMN_SPECS.size()];

        for (int i = 0; i < COLUMN_SPECS.size(); i++) {
            ColumnSpec spec = COLUMN_SPECS.get(i);
            slobsStrings[i] = spec.stringBuilderThing.run(slob);
        }
        return slobsStrings;
    }

    @Override
    public void disposeTabItem() {
        super.disposeTabItem();
    }

    @Override
    public void seaLevelObsAdded(String customEventId) {
        updateTable();
    }

    @Override
    public void seaLevelObsRemoved(String customEventId) {
        updateTable();
    }

    @Override
    public void seaLevelObsChanged(String customEventId) {
        /*
         * Check if the customEventId == physicalEvent.getCustomId(). otherwise
         * ignore.
         */
        if (customEventId == null || getPhysicalEvent() == null
                || !customEventId.equals(getPhysicalEvent().getCustomId())) {
            statusHandler.info("SeaLevelObservationsTab ignoring eventId = "
                    + customEventId
                    + " because it's null or it doesn't match the customId of the SeaLevelObservationsTab's physicalEvent ("
                    + (getPhysicalEvent() == null ? null
                            : getPhysicalEvent().getCustomId())
                    + "). ");

            return;
        }

        Display.getDefault().syncExec(() -> {
            reinitializeTabContent();
        });
    }

    private class SlobsKey {
        private SeaLevelObs obs;

        private String stnId;

        private SLOSensorType sensorType;

        private SLOObsType obsType;

        private Date startTime;

        private Date endTime;

        public SlobsKey(SeaLevelObs obs) {
            this.obs = obs;
            stnId = obs.getStation().getCustomId();
            sensorType = obs.getSensorType();
            obsType = obs.getObsType();
            startTime = obs.getStartTime();
            endTime = obs.getEndTime();
        }

        public SeaLevelObs getObs() {
            return obs;
        }

        @Override
        public int hashCode() {
            final int prime = 31;
            int result = 1;
            result = prime * result + Objects.hash(endTime, obsType, sensorType,
                    startTime, stnId);
            return result;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) {
                return true;
            }
            if (obj == null) {
                return false;
            }
            if (getClass() != obj.getClass()) {
                return false;
            }
            SlobsKey other = (SlobsKey) obj;
            return Objects.equals(endTime, other.endTime)
                    && obsType == other.obsType
                    && sensorType == other.sensorType
                    && Objects.equals(startTime, other.startTime)
                    && Objects.equals(stnId, other.stnId);
        }
    }
}
