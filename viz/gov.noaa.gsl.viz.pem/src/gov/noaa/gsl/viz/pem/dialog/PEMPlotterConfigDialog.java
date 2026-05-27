package gov.noaa.gsl.viz.pem.dialog;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;

import com.raytheon.viz.ui.dialogs.CaveSWTDialog;

import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;

public class PEMPlotterConfigDialog extends CaveSWTDialog {

    private static final int MAX_WIDTH = 625;

    private static final int MAX_HEIGHT = 1000;

    private static final String DLG_TITLE = "PEM Display Options";

    private Map<PhysicalEventType, PEPlotter> plotters = new HashMap<>();

    /**
     * Remember this so that we can set the selected Tab if we can, as below.
     */
    private TabFolder mainTabFolder = null;

    /**
     * We'll try and select the appropriate Tab if you set this.
     */
    private PhysicalEventType selectedPhyEventType = null;

    public PEMPlotterConfigDialog(Shell parent,
            Map<PhysicalEventType, PEPlotter> plotters) {

        /*
         * Pass the Display to the super constructor rather than the shell, so
         * that the Dialog can move forward and back in z-order! Yay!! But
         * NOOOO. Passing the Display keeps the Dialog open even when CAVE
         * closes. So use a DisposeListener on the parent, and close this dialog
         * when parent is disposed.
         */
        super(parent.getDisplay(),
                SWT.MIN | SWT.MAX | SWT.RESIZE | SWT.DIALOG_TRIM);

        parent.addDisposeListener(e -> close());

        this.plotters = plotters;
        setText(DLG_TITLE);
    }

    public void setSelectedPhyEventType(PhysicalEventType phyEventType) {
        this.selectedPhyEventType = phyEventType;

        if (mainTabFolder != null) {
            for (TabItem tabItem : mainTabFolder.getItems()) {
                if (selectedPhyEventType != null) {
                    PhysicalEventType tabItemPhyEventType = PhysicalEventType
                            .fromString(tabItem.getText());
                    if (selectedPhyEventType.equals(tabItemPhyEventType)) {
                        mainTabFolder.setSelection(tabItem);
                    }
                }
            }
        }
    }

    /**
     * Initials the physical event dialog.
     */
    @Override
    protected void initializeComponents(Shell shell) {

        // shell.setLocation(100, 100); // Does nothing
        // shell.setSize(500, 500); // Does nothing
        // shell.pack(); // Does nothing
        shell.setMaximumSize(MAX_WIDTH, MAX_HEIGHT);

        Composite dlgComp = new Composite(shell, SWT.VERTICAL);
        GridLayout dlgLayout = new GridLayout();
        dlgLayout.numColumns = 1;
        dlgComp.setLayout(dlgLayout);
        dlgComp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        mainTabFolder = new TabFolder(dlgComp,
                SWT.BORDER | SWT.V_SCROLL | SWT.H_SCROLL);
        mainTabFolder.setLayout(new GridLayout());
        mainTabFolder
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        for (PhysicalEventType peType : PhysicalEventType.values()) {

            PEPlotter plotter = plotters.get(peType);
            if (plotter == null) {
                continue;
            }

            TabItem topTabItem = new TabItem(mainTabFolder, SWT.BORDER);
            topTabItem.setText(peType.getLabel());
            if (selectedPhyEventType != null
                    && selectedPhyEventType.equals(peType)) {
                mainTabFolder.setSelection(topTabItem);
            }

            Composite topComp = new Composite(mainTabFolder, SWT.NONE);
            topComp.setLayout(new GridLayout());
            topComp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
            topTabItem.setControl(topComp);

            TabFolder subTabFolder = new TabFolder(topComp,
                    SWT.BORDER | SWT.V_SCROLL | SWT.H_SCROLL);
            subTabFolder.setLayout(new GridLayout());
            subTabFolder.setLayoutData(
                    new GridData(SWT.FILL, SWT.FILL, true, true));

            plotter.buildPlotterConfigTabItems(subTabFolder);
        }

        Button closeButton = new Button(dlgComp, SWT.PUSH);
        GridData closeBtnGridData = new GridData();
        closeBtnGridData.horizontalAlignment = GridData.CENTER;
        closeBtnGridData.verticalAlignment = GridData.CENTER;
        closeBtnGridData.grabExcessHorizontalSpace = false;
        closeBtnGridData.grabExcessVerticalSpace = false;
        closeButton.setLayoutData(closeBtnGridData);
        closeButton.setText("Close");
        closeButton.addSelectionListener(new SelectionListener() {

            @Override
            public void widgetSelected(SelectionEvent e) {
                close();
            }

            @Override
            public void widgetDefaultSelected(SelectionEvent e) {
                // close();
            }
        });

//        dlgComp.setSize(1000, 500);
        dlgComp.pack();

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
//        PhysicalEventManager.getInstance().removePEMListener(pemListener);
//        PhysicalEventManager.getInstance().addPEMListener(pemListener);
//
//        /*
//         * Create the data tab entries for each event type. And remember that
//         * they may already exist, and hence we need to clear em first.
//         */
//        clearTabs();
//        for (Map.Entry<PhysicalEventType, List<PEMDialogTab>> entry : PEMDialogConfigManager
//                .getInstance().getPEMDialogTabs().entrySet()) {
//            for (PEMDialogTab tab : entry.getValue()) {
//                statusHandler.info("    PEMDialog adding tab for "
//                        + entry.getKey() + ": " + tab.getTitle());
//                addPEMDialogTab(entry.getKey(), tab);
//            }
//        }
//
//        /* Set the dialog properties */
//        shell.setText(PEM_DLG_TITLE);
//        shell.setMinimumSize(MIN_SIZE_OF_PEM_DLG, MIN_SIZE_OF_PEM_DLG);
//        shell.setLayout(new GridLayout());
//        shell.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
//
//        /* Create the physical event type and active combos */
//        if (phyEventTypeCombo == null || activeOptionCombo == null) {
//            /*
//             * Composite for physical event types combo and active option combo
//             */
//            Composite eventTypeAndActiveComposite = new Composite(shell,
//                    SWT.NONE);
//            eventTypeAndActiveComposite
//                    .setLayout(new RowLayout(SWT.HORIZONTAL));
//
//            createEventTypeCombo(eventTypeAndActiveComposite);
//            createActiveOptionCombo(eventTypeAndActiveComposite);
//            createPlotOptionMenus(eventTypeAndActiveComposite, shell);
//
//            eventTypeAndActiveComposite.pack();
//        }
//
//        sashForm = new SashForm(shell, SWT.VERTICAL);
//        sashForm.setLayout(new GridLayout());
//        /*
//         * Setting the FILL to true for the SashForm is critical. Without that,
//         * the UI doesnt work at all!
//         */
//        sashForm.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
//
//        /* The composite for the event table */
//        final ScrolledComposite phyEventTableComposite = new ScrolledComposite(
//                sashForm, SWT.V_SCROLL | SWT.H_SCROLL);
//
//        /* Creates the physical event table */
//        if (phyEventTable == null) {
//            createEventTable(phyEventTableComposite);
//        }
//
//        /* Creates the physical event data tabs */
//        if (tabFolder == null) {
//            tabFolder = new TabFolder(sashForm,
//                    SWT.BORDER | SWT.V_SCROLL | SWT.H_SCROLL);
//            tabFolder.setLayout(new GridLayout());
//            tabFolder.setLayoutData(
//                    new GridData(SWT.FILL, SWT.FILL, true, true));
//        }
//
//        /*
//         * phyEventTypeCombo.select(0) doesnt fire the listener for some lame
//         * SWT reason. So do it manually.
//         */
//        phyEventTypeListener.widgetSelected(null);
//        reinitPhysicalEventsTable();
    }

    @Override
    protected void disposed() {

        super.disposed();

//        if (phyEventTypeCombo != null && !phyEventTypeCombo.isDisposed()) {
//            phyEventTypeCombo.removeSelectionListener(phyEventTypeListener);
//            phyEventTypeCombo.dispose();
//        }
//
//        phyEventTypeCombo = null;
//
//        if (activeOptionCombo != null && !activeOptionCombo.isDisposed()) {
//            activeOptionCombo
//                    .removeSelectionListener(activeOptionSelectionListener);
//            activeOptionCombo.dispose();
//        }
//        activeOptionCombo = null;
//
//        if (phyEventTable != null && !phyEventTable.isDisposed()) {
//            phyEventTable.removeSelectionListener(phyEventSelectionListener);
//            phyEventTable.removeAll();
//            phyEventTable.dispose();
//        }
//        phyEventTable = null;
//
//        if (tabFolder != null) {
//            disposeTabItems();
//            if (!tabFolder.isDisposed()) {
//                tabFolder.dispose();
//            }
//            tabFolder = null;
//        }
//
//        PhysicalEventManager.getInstance().removePEMListener(pemListener);
    }

}
