/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.dialog;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.ControlAdapter;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;

import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.time.TimeRange;
import com.raytheon.viz.ui.dialogs.CaveSWTDialog;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEventMgrListener;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventManager;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;

/**
 * The dialog for displaying physical events.
 *
 * It includes the dropdowns for event type and display for filtering the events
 * to display, the event table for displaying and selecting event, and the data
 * tabs to show the data for a selected event.
 *
 * It interactively displays the physical event data from the database through
 * the physical event manager.
 *
 * It's synchronized with the physical event manager.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Dec 13, 2021        Robert.Weingruber     Initial Creation
 * Apr 19, 2922        Jing                  Initial implement physical event table
 *                                           and menus for control the display
 * May 13, 2022        Jing                  Connect the PemDialog to the PE Manager
 * May 16, 2022        Jing                  Implement physical event active status
 *                                           and operations
 * May 17, 2022        Jing                  Corrected the default display option
 * Sep 19, 2002        Rob Weingruber        Rewrite, with better design and enhancements,
 *                                           and no bugs or perf problems.
 *
 * </pre>
 *
 * @author robert.weingruber
 * @author Jing
 *
 * @version 1.0
 */
public class PEMDialog extends CaveSWTDialog {

    private static final transient IUFStatusHandler statusHandler = UFStatus
            .getHandler(PEMDialog.class);

    private static final String PEM_DLG_TITLE = "Physical Event Manager";

    private static final int MIN_SIZE_OF_PEM_DLG = 400;

    private static final String ALL = "ALL";

    private static final IPEMColumnSpecBuilder DEFAULT_COLUMN_BUILDER = new DefaultPEMColumnSpecBuilder();

    /* Store the data display tabs for each physical event type */
    private Map<PhysicalEventType, List<PEMDialogTab>> tabs = new HashMap<>();

    /*
     * The tab-folder to display the data of a selected event. How many tabs
     * depend on the event type
     */
    private TabFolder tabFolder;

    /*
     * Kinda like a splitpane
     */
    private SashForm sashForm;

    /* The menu to select a event type for display */
    private Combo phyEventTypeCombo;

    /*
     * the menu for display options, such as all events, inactive or active
     * events
     */
    private Combo activeOptionCombo;

    /*
     * The physical event table, display the event in general. The check box of
     * each event presents the event active status, and change the it.
     */
    private Table phyEventTable;

    private Map<PhysicalEventType, IPEMColumnSpecBuilder> columnBuilders = new HashMap<>();

    private IPEMColumnSpecBuilder currentColumnSpecBuilder = DEFAULT_COLUMN_BUILDER;

    private Comparator<IPhysicalEvent> phyEventComparator = Comparator
            .comparing(IPhysicalEvent::getCustomId);

    private IPhysicalEventMgrListener pemListener = new OurPEMListener();

    /*
     * The physical event type listener handles the event to select a physical
     * event type
     */
    private PhyEventTypeSelectionListener phyEventTypeListener = new PhyEventTypeSelectionListener();

    /*
     * The physical event display option listener handles the event to select a
     * display option
     */
    private ActiveOptionSelectionListener activeOptionSelectionListener = new ActiveOptionSelectionListener();

    /*
     * The physical event selection listener handles the event to select a
     * physical event to be currently displayed or change the active status
     */
    private PhyEventSelectionListener phyEventSelectionListener = new PhyEventSelectionListener();

    private PEMPlotterConfigDialog plotterConfigDialog = null;

    public PEMDialog(Shell parent) {

        /*
         * Pass the Display to the super constructor rather than the shell, so
         * that the PEMDialog can move forward and back in z-order! Yay!! But
         * NOOOO. Passing the Display keeps the PEMDialog open even when CAVE
         * closes. So use a DisposeListener on the parent, and close this dialog
         * when parent is disposed.
         */
        super(parent.getDisplay(),
                SWT.MIN | SWT.MAX | SWT.RESIZE | SWT.DIALOG_TRIM);

        parent.addDisposeListener(e -> close());

        for (Map.Entry<PhysicalEventType, IPEMColumnSpecBuilder> entry : PEMDialogConfigManager
                .getInstance().getPEMColumnSpecBuilders().entrySet()) {
            columnBuilders.put(entry.getKey(), entry.getValue());
        }
    }

    /**
     * Initials the physical event dialog.
     */
    @Override
    protected void initializeComponents(Shell shell) {

        // shell.setLocation(100, 100); // Does nothing
        // this.shell.setLocation(100, 100); // Does nothing
        // shell.setSize(500, 500); // Does nothing
        // shell.pack(); // Does nothing
        // All does nothing cuz the final super.open() does some
        // parent centering (and setLocation). Annoying for sure.
        // shell.setMaximumSize(500, 500); // Does soemthing but we dont want
        // this

        /*
         * NOTE that this method is called each time the window is opened, and
         * hence may be called more than once on the same instance.
         *
         * Putting the registration of the PEMListener in the constructor
         * doesn't work because unregistering the listener is done in the
         * disposed() method. So a new dialog (hence registers) has this method
         * called, then disposed (hence unregisters), then this method called
         * again. And so we need to re-register.
         */
        /*
         * Unregister the listener here just in case so that we dont have
         * duplicates, and also when disposing.
         */
        PhysicalEventManager.getInstance().removePEMListener(pemListener);
        PhysicalEventManager.getInstance().addPEMListener(pemListener);

        /*
         * Create the data tab entries for each event type. And remember that
         * they may already exist, and hence we need to clear em first.
         */
        clearTabs();
        for (Map.Entry<PhysicalEventType, List<PEMDialogTab>> entry : PEMDialogConfigManager
                .getInstance().getPEMDialogTabs().entrySet()) {
            for (PEMDialogTab tab : entry.getValue()) {
                statusHandler.info("    PEMDialog adding tab for "
                        + entry.getKey() + ": " + tab.getTitle());
                addPEMDialogTab(entry.getKey(), tab);
            }
        }

        /* Set the dialog properties */
        shell.setText(PEM_DLG_TITLE);
        shell.setMinimumSize(MIN_SIZE_OF_PEM_DLG, MIN_SIZE_OF_PEM_DLG);
        shell.setLayout(new GridLayout());
        shell.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        /* Create the physical event type and active combos */
        if (phyEventTypeCombo == null || activeOptionCombo == null) {
            /*
             * Composite for physical event types combo and active option combo
             */
            Composite eventTypeAndActiveComposite = new Composite(shell,
                    SWT.NONE);
            eventTypeAndActiveComposite
                    .setLayout(new RowLayout(SWT.HORIZONTAL));

            createEventTypeCombo(eventTypeAndActiveComposite);
            createActiveOptionCombo(eventTypeAndActiveComposite);
            createUnselectAllButton(eventTypeAndActiveComposite);
            createPlotOptionsButton(eventTypeAndActiveComposite, shell);

            eventTypeAndActiveComposite.pack();
        }

        sashForm = new SashForm(shell, SWT.VERTICAL);
        sashForm.setLayout(new GridLayout());
        /*
         * Setting the FILL to true for the SashForm is critical. Without that,
         * the UI doesnt work at all!
         */
        sashForm.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        /* Creates the physical event table */
        if (phyEventTable == null) {
            createEventTable(sashForm);
        }

        /* Creates the physical event data tabs */
        if (tabFolder == null) {
            tabFolder = new TabFolder(sashForm,
                    SWT.BORDER | SWT.V_SCROLL | SWT.H_SCROLL);
            tabFolder.setLayout(new GridLayout());
            tabFolder.setLayoutData(
                    new GridData(SWT.FILL, SWT.FILL, true, true));
        }

        /*
         * phyEventTypeCombo.select(0) doesnt fire the listener for some lame
         * SWT reason. So do it manually.
         */
        phyEventTypeListener.widgetSelected(null);
        reinitPhysicalEventsTable();
    }

    private void clearTabs() {
        disposeTabItems();
        tabs.clear();
    }

    @Override
    protected void disposed() {

        super.disposed();

        if (phyEventTypeCombo != null && !phyEventTypeCombo.isDisposed()) {
            phyEventTypeCombo.removeSelectionListener(phyEventTypeListener);
            phyEventTypeCombo.dispose();
        }

        phyEventTypeCombo = null;

        if (activeOptionCombo != null && !activeOptionCombo.isDisposed()) {
            activeOptionCombo
                    .removeSelectionListener(activeOptionSelectionListener);
            activeOptionCombo.dispose();
        }
        activeOptionCombo = null;

        if (phyEventTable != null && !phyEventTable.isDisposed()) {
            phyEventTable.removeSelectionListener(phyEventSelectionListener);
            phyEventTable.removeAll();
            phyEventTable.dispose();
        }
        phyEventTable = null;

        if (tabFolder != null) {
            disposeTabItems();
            if (!tabFolder.isDisposed()) {
                tabFolder.dispose();
            }
            tabFolder = null;
        }

        if (plotterConfigDialog != null && !plotterConfigDialog.isDisposed()) {
            plotterConfigDialog.close();
            plotterConfigDialog = null;
        }
        PhysicalEventManager.getInstance().removePEMListener(pemListener);
    }

    /**
     * Creates the event type combo.
     *
     * @param parent
     *            The base composite to contain the combo
     */
    private void createEventTypeCombo(Composite parent) {

        /* Physical event types, a label and a menu */
        Label typeLabel = new Label(parent, SWT.NONE);
        typeLabel.setText("Event Type: ");
        phyEventTypeCombo = new Combo(parent, SWT.READ_ONLY);
        phyEventTypeCombo.addSelectionListener(phyEventTypeListener);

        Set<PhysicalEventType> types = PhysicalEventManager.getInstance()
                .getPhysicalEventTypes();
        for (PhysicalEventType type : types) {
            phyEventTypeCombo.add(type.toString());
        }
        phyEventTypeCombo.add(ALL);
        phyEventTypeCombo.select(0);
    }

    /**
     * Creates the Active Option combo.
     *
     * @param parent
     *            The base composite to contain the combo
     */
    private void createActiveOptionCombo(Composite parent) {

        /* Display options, a label and a menu */
        Label displayLabel = new Label(parent, SWT.NONE);
        displayLabel.setText("Display: ");

        activeOptionCombo = new Combo(parent, SWT.READ_ONLY);
        activeOptionCombo.add(ActiveOption.ACTIVE_ONLY.toString());
        activeOptionCombo.add(ActiveOption.INACTIVE_ONLY.toString());
        activeOptionCombo.add(ActiveOption.ALL.toString());
        int x = PhysicalEventManager.getInstance().getActiveOption().ordinal();
        activeOptionCombo.select(x);
        activeOptionCombo.addSelectionListener(activeOptionSelectionListener);
    }

    private void createPlotOptionsButton(Composite parent, Shell shell) {
        Button plotOptionButton = new Button(parent, SWT.FLAT);
        plotOptionButton.setText("Display Options...");
        plotOptionButton.addSelectionListener(new SelectionListener() {

            @Override
            public void widgetSelected(SelectionEvent e) {

                if (plotterConfigDialog == null
                        || plotterConfigDialog.isDisposed()) {
                    plotterConfigDialog = new PEMPlotterConfigDialog(shell,
                            PEMDialogConfigManager.getInstance().getPlotters());
                }
                String selectedPhyTypeText = phyEventTypeCombo.getText();
                /*
                 * null means ALL
                 */
                PhysicalEventType selectedType = null;
                if (!ALL.equals(selectedPhyTypeText)) {
                    selectedType = PhysicalEventType
                            .valueOf(selectedPhyTypeText);
                } else {
                    /*
                     * If we selected ALL in the dropdown, then what's the type
                     * of the selected row?
                     */
                    TableItem[] items = phyEventTable.getSelection();
                    if (items != null && items.length == 1 && items[0] != null
                            && items[0].getData() instanceof IPhysicalEvent) {
                        IPhysicalEvent selectedPhyEvent = (IPhysicalEvent) items[0]
                                .getData();
                        selectedType = selectedPhyEvent.getEventType();
                    }
                }
                plotterConfigDialog.setSelectedPhyEventType(selectedType);
                plotterConfigDialog.open();
            }

            @Override
            public void widgetDefaultSelected(SelectionEvent e) {
            }
        });
    }

    private void createUnselectAllButton(Composite parent) {
        Button unselectAllButton = new Button(parent, SWT.FLAT);
        unselectAllButton.setText("Unselect All");
        unselectAllButton.addSelectionListener(new SelectionListener() {

            @Override
            public void widgetSelected(SelectionEvent e) {
                PhysicalEventManager.getInstance().clearSelected();
            }

            @Override
            public void widgetDefaultSelected(SelectionEvent e) {
            }
        });
    }

    /**
     * Creates the physical event table.
     *
     * Checkbox is event visibility status. Only a single event can be selected
     */
    private void createEventTable(Composite phyEventTableComposite) {

        phyEventTableComposite.setLayout(new GridLayout());
        phyEventTableComposite
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        /*
         * The event table
         */
        phyEventTable = new Table(phyEventTableComposite,
                SWT.BORDER | SWT.V_SCROLL | SWT.H_SCROLL | SWT.SINGLE
                        | SWT.FULL_SELECTION);
        phyEventTable.setSize(600, 500);

        /*
         * Right click context menu
         */
        Menu menu = new Menu(shell, SWT.POP_UP);
        phyEventTable.setMenu(menu);
        MenuItem item = new MenuItem(menu, SWT.PUSH);
        item.setText("Make Selected In/Active");
        item.addSelectionListener(new SelectionAdapter() {

            @Override
            public void widgetSelected(SelectionEvent e) {
                TableItem[] selectedItems = phyEventTable.getSelection();
                if (selectedItems == null || selectedItems.length != 1
                        || selectedItems[0].getData() == null) {
                    return;
                }
                IPhysicalEvent selectedEvent = (IPhysicalEvent) selectedItems[0]
                        .getData();
                selectedEvent.setIsActive(!selectedEvent.getIsActive());
                PhysicalEventManager.getInstance()
                        .savePhysicalEvent(selectedEvent);
                reinitPhysicalEventsTable();
            }
        });

        phyEventTable.setHeaderVisible(true);
        phyEventTable.setVisible(true);
        phyEventTable.setLinesVisible(true);
        phyEventTable.addSelectionListener(phyEventSelectionListener);

//        reinitTableColums();

        phyEventTable.removeAll();
        phyEventTable.pack();
    }

    private void reinitTableColumns(IPEMColumnSpecBuilder currentBuilder) {

        /*
         * Undo drawing so the user doesnt see it happening
         */
        phyEventTable.setRedraw(false);

        String oldSortColumnHeader = "";
        if (phyEventTable.getSortColumn() != null) {
            oldSortColumnHeader = phyEventTable.getSortColumn().getText();
        }

        /*
         * Remove all of the old columns
         */
        while (phyEventTable.getColumnCount() > 0) {
            phyEventTable.getColumns()[0].dispose();
        }

        /*
         * And now add the new ones. Set column headers, widths, resizeable
         */
        int i = 0;
        for (PEMColumnSpec spec : currentBuilder.getColumnSpecs()) {

            final TableColumn tc = new TableColumn(phyEventTable, SWT.LEFT);
            tc.setText(spec.getHeader());
            tc.setWidth(spec.getWidth());
            // tc.setMoveable(true);
            tc.setResizable(true);
            tc.setData(spec);

            tc.addControlListener(new ControlAdapter() {
                @Override
                public void controlResized(ControlEvent e) {
                    TableColumn column = (TableColumn) e.widget;
                    int newWidth = column.getWidth();

                    PEMColumnSpec spec = (PEMColumnSpec) column.getData();
                    spec.setWidth(newWidth);
                }
            });

            tc.addSelectionListener(new SelectionAdapter() {
                @Override
                public void widgetSelected(SelectionEvent e) {
                    TableColumn column = (TableColumn) e.widget;
                    PEMColumnSpec spec = (PEMColumnSpec) column.getData();
                    Comparator<IPhysicalEvent> comparator = null;
                    if (spec != null && spec.getComparator() != null) {
                        phyEventComparator = spec.getComparator();
                        /*
                         * Clicked on current sort column? If so, reverse the
                         * sort. And since we redo all of the columns in the
                         * reinitPhysicalEventsTable() method, then we need to
                         * check column 'equality' by header name.
                         */
                        if (phyEventTable.getSortColumn() != null
                                && phyEventTable.getSortColumn()
                                        .getText() != null
                                && phyEventTable.getSortColumn().getText()
                                        .equals(column.getText())) {
                            // if (column.equals(phyEventTable.getSortColumn()))
                            // {
                            phyEventTable.setSortDirection(
                                    phyEventTable.getSortDirection() == SWT.UP
                                            ? SWT.DOWN
                                            : SWT.UP);
                            int newSortDirection = phyEventTable
                                    .getSortDirection();
                            if (newSortDirection == SWT.DOWN) {
                                phyEventComparator = phyEventComparator
                                        .reversed();
                            }
                        }
                        /* Otherwise new sort column */
                        else {
                            phyEventTable.setSortColumn(column);
                            phyEventTable.setSortDirection(SWT.UP);
                        }
                    }

                    reinitPhysicalEventsTable();
                }
            });

            if (i == 0 || tc.getText().equals(oldSortColumnHeader)) {
                phyEventTable.setSortColumn(tc);
                i++;
            }
        }

        /*
         * Turn drawing back on
         */
        phyEventTable.setRedraw(true);
    }

    /**
     * Refresh the physical event table according to what's in the PEM
     *
     */
    private void reinitPhysicalEventsTable() {

        final PhysicalEventManager pem = PhysicalEventManager.getInstance();

        currentColumnSpecBuilder = DEFAULT_COLUMN_BUILDER;
        List<PhysicalEventType> currentFilters = pem.getFilters();
        if (currentFilters.size() == 1) {
            PhysicalEventType filterType = currentFilters.get(0);
            if (columnBuilders.get(filterType) != null) {
                currentColumnSpecBuilder = columnBuilders.get(filterType);
            }
        }

        TableItem[] oldSelectedItems = phyEventTable.getSelection();
        String oldSelectedId = ((oldSelectedItems == null
                || oldSelectedItems.length != 1) ? ""
                        : oldSelectedItems[0].getText(0));
        boolean selectionChanged = true;

        /*
         * Remove all physical events and columns etc from the table.
         */
        phyEventTable.removeAll();
        phyEventTable.clearAll();

        reinitTableColumns(currentColumnSpecBuilder);

        List<IPhysicalEvent> events = pem.getPhysicalEventsList();
        Collections.sort(events, phyEventComparator);

        if (events.size() == 0) {
            /*
             * No event.
             *
             * TODO May do something here later, such as says no event
             * available,...
             */

        } else {
            int index = 0;
            for (IPhysicalEvent event : events) {

                TableItem tableItem = new TableItem(phyEventTable, SWT.NONE);
                tableItem.setText(getTableItemStrings(event));
                tableItem.setData(event);

                /* Initial the check box with the event active status */
                if (event.getIsActive()) {
                    tableItem.setBackground(Display.getDefault()
                            .getSystemColor(SWT.COLOR_WHITE));
                } else {
                    tableItem.setBackground(Display.getDefault()
                            .getSystemColor(SWT.COLOR_GRAY));
                }

                /* Recover the selected event if there is one */
                if (oldSelectedId.equals(event.getCustomId())) {
                    phyEventTable.select(index);
                    selectionChanged = false;
                }
                index++;
            }

            /*
             * For some stupid SWT reason, the listener is not notified. So
             * let's do it ourselves.
             *
             * TODO re-check this late
             */
            if (selectionChanged) {
                phyEventSelectionListener.widgetSelected(null);
            }
        }
    }

    /**
     * Convert an event into the strings for display in the event table..
     *
     * @param event
     *            The event to be converted into strings.
     * @return The event strings.
     */
    private String[] getTableItemStrings(IPhysicalEvent event) {

        String[] eventStrings = new String[currentColumnSpecBuilder
                .getNumColumns()];

        for (int i = 0; i < currentColumnSpecBuilder.getNumColumns(); i++) {
            PEMColumnSpec spec = currentColumnSpecBuilder.getColumnSpec(i);
            eventStrings[i] = spec.getStringBuilder().run(event);
        }
        return eventStrings;
    }

    /**
     * Clean the tab folder by disposing all tabs.
     */
    private void disposeTabItems() {

        for (Map.Entry<PhysicalEventType, List<PEMDialogTab>> entry : tabs
                .entrySet()) {
            for (PEMDialogTab tab : entry.getValue()) {
                tab.disposeTabItem();
            }
        }
    }

    private void createTabItems(IPhysicalEvent selectedEvent) {
        if (selectedEvent == null || selectedEvent.getEventType() == null) {
            return;
        }

        List<PEMDialogTab> pemTabs = tabs.get(selectedEvent.getEventType());
        if (pemTabs != null) {
            for (PEMDialogTab tab : pemTabs) {
                TabItem tabItem = tab.buildTabItem(tabFolder, SWT.NULL,
                        selectedEvent);
            }
        }
    }

    private void reinitTabItems(IPhysicalEvent selectedEvent) {

        disposeTabItems();
        createTabItems(selectedEvent);
        tabFolder.setSelection(0);
        tabFolder.pack(true);
        /*
         * LOVE TO get rid of this pack line, if possible, since it resizes the
         * window when an event is selected. But without, the tab doesnt
         * refresh. Ah, but it does if the correct GridLayout and GridDatas are
         * used, with FILL options. So all works fine with the following line
         * commented out, and the window thankfully does not resize.
         *
         * shell.pack();
         */
    }

    /**
     * Adds the Tab to the end of the list for the given type.
     *
     * @param type
     *            The selected event type.
     * @param tab
     *            The tab to be added into the tab folder.
     */
    private void addPEMDialogTab(PhysicalEventType type, PEMDialogTab tab) {
        if (type == null || tab == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + " addPEMDialogTab(...) received a null type and/or tab.");
        }

        List<PEMDialogTab> listOfTabs = tabs.get(type);
        if (listOfTabs == null) {
            listOfTabs = new ArrayList<>();
            tabs.put(type, listOfTabs);
        }
        listOfTabs.add(tab);
    }

    //////////////////////////////////////////////////////////////////////////
    // =============================== OurPEMListener =========================
    //////////////////////////////////////////////////////////////////////////

    private class OurPEMListener implements IPhysicalEventMgrListener {
        @Override
        public void physicalEventAdded(String id, PhysicalEventType type) {
            statusHandler
                    .info("PEMDialog got a PhysicalEvent added notification");
            physicalEventChanged(id, type);
        }

        @Override
        public void physicalEventChanged(String id, PhysicalEventType type) {

            Display.getDefault().syncExec(() -> {
                reinitPhysicalEventsTable();
            });

        }

        @Override
        public void physicalEventRemoved(String id, PhysicalEventType type) {
            statusHandler
                    .info("PEMDialog got a PhysicalEvent removed notification");
            physicalEventChanged(id, type);
        }

        @Override
        public void timeWindowChanged(TimeRange newTimeRange) {
            physicalEventChanged(null, null);
        }

        @Override
        public void activeOptionChanged(ActiveOption newActiveOption) {
            /*
             * THis may be called on the PEM/DAO threads. So make sure we sync
             * up to the SWT thread to exec anything.
             */
            Display.getDefault().syncExec(() -> {
                phyEventTypeListener.widgetSelected(null);
                int x = PhysicalEventManager.getInstance().getActiveOption()
                        .ordinal();

                activeOptionCombo.setSelection(new Point(x, x));
                physicalEventChanged(null, null);
            });
        }

        @Override
        public void filtersChanged(List<PhysicalEventType> newFilters) {
            physicalEventChanged(null, null);
        }

        @Override
        public void selectionsChanged(Set<String> newSelections) {

            /*
             * THis may be called on the PEM/DAO threads. So make sure we sync
             * up to the SWT thread to exec anything.
             */
            Display.getDefault().syncExec(() -> {

                IPhysicalEvent selectedEvent = null;
                Set<String> pemSelectedIds = PhysicalEventManager.getInstance()
                        .getSelected();
                if (pemSelectedIds.size() != 1) {
                    phyEventTable.deselectAll();
                } else {
                    String pemSelectedEventId = pemSelectedIds.iterator()
                            .next();
                    // If it's already selected, great
                    TableItem[] selectedItems = phyEventTable.getSelection();
                    if (selectedItems != null && selectedItems.length == 1
                            && selectedItems[0] != null
                            && selectedItems[0].getData() != null) {
                        IPhysicalEvent selectedData = (IPhysicalEvent) selectedItems[0]
                                .getData();
                        if (selectedData.getCustomId()
                                .equals(pemSelectedEventId)) {
                            selectedEvent = selectedData;
                        }
                    }

                    if (selectedEvent == null) {
                        // Otherwise, deselect all and then go select the
                        // appropriate one
                        phyEventTable.deselectAll();
                        TableItem[] tableItems = phyEventTable.getItems();
                        for (TableItem item : tableItems) {
                            if (item.getData() != null) {
                                IPhysicalEvent itemData = (IPhysicalEvent) item
                                        .getData();
                                if (itemData.getCustomId()
                                        .equals(pemSelectedEventId)) {
                                    phyEventTable.setSelection(item);
                                    phyEventTable.showSelection();
                                    phyEventTable.showItem(item);
                                    selectedEvent = itemData;
                                    break;
                                }
                            }
                        }
                    }
                }

                reinitTabItems(selectedEvent);
            });
        }
    }

    //////////////////////////////////////////////////////////////////////////
    // ======================== Event Type Filter Listener ==================
    //////////////////////////////////////////////////////////////////////////

    /**
     * Handles the event for the physical event type selection.
     */
    private class PhyEventTypeSelectionListener extends SelectionAdapter {
        @Override
        public void widgetSelected(SelectionEvent e) {

            /*
             * Which physical event type is selected in the menu?
             */
            String selectedPhyTypeText = phyEventTypeCombo.getText();

            /*
             * null means ALL
             */
            PhysicalEventType selectedType = null;
            if (!ALL.equals(selectedPhyTypeText)) {
                selectedType = PhysicalEventType.valueOf(selectedPhyTypeText);
            }

            /*
             * Setting null means no filter
             */
            PhysicalEventManager.getInstance().setFilter(selectedType);
        }
    }

    //////////////////////////////////////////////////////////////////////////
    // ======================== Active option Listener ==================
    //////////////////////////////////////////////////////////////////////////

    /**
     *
     * Display option selection listener
     *
     */
    private class ActiveOptionSelectionListener extends SelectionAdapter {
        @Override
        public void widgetSelected(SelectionEvent e) {

            ActiveOption displayOption = ActiveOption
                    .valueOf(activeOptionCombo.getText());
            PhysicalEventManager.getInstance().setActiveOption(displayOption);
        }
    }

    //////////////////////////////////////////////////////////////////////////
    // ======================== Event Selection Listener ==================
    //////////////////////////////////////////////////////////////////////////

    /**
     * Physical event selection listener for the event table. This is the key
     * method to keep the dialog collaboratively works, and synchronous with the
     * physical event manager. Ensure to understand the algorithm before any
     * change.
     */
    private class PhyEventSelectionListener extends SelectionAdapter {
        @Override
        public void widgetSelected(SelectionEvent e) {
            if (e == null) {
                return;
            }

            TableItem[] items = phyEventTable.getSelection();
            if (items == null || items.length != 1 || items[0] == null) {
                PhysicalEventManager.getInstance().clearSelected();
            } else {
                IPhysicalEvent selectedPhyEvent = (IPhysicalEvent) items[0]
                        .getData();
                /*
                 * I think there is a bug in SWT such that unselect doesn't work
                 * well. So if we get a selection event for the already-selected
                 * phyEvent, then unselect the phyEvent.
                 */
                if (PhysicalEventManager.getInstance()
                        .isSelected(selectedPhyEvent)) {
                    PhysicalEventManager.getInstance().clearSelected();
                } else {
                    EventZoom eventZoom = new EventZoom(selectedPhyEvent);
                    eventZoom.zoomToEventLocation();
                    PhysicalEventManager.getInstance()
                            .setSelected(selectedPhyEvent);
                }
            }

        }
    }
}
