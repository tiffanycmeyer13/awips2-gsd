/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Weather Informatics and Decision Support Division (WIDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atoms.trecs;

import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;
import org.eclipse.ui.PlatformUI;

import com.raytheon.uf.viz.core.VizApp;

import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

/**
 * Class to open a dialog displaying tabs for product regions, with procedures
 * used by the TRECS
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jul 31, 2023   100405    Robert Weingruber Initial creation.
 * </pre>
 *
 * @author Robert Weingruber
 * @version 1.0
 */
public class TrecsExecDialog extends Dialog {

    private static DecimalFormat FLOAT_FORMATTER = new DecimalFormat("0.0");

    private static final String NONE_PROCEDURE = "None";

    private Font boldFont = null;
    static {
        FLOAT_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    /**
     * The info to base the dialog on
     */
    private TrecsExecInfo info;

    public TrecsExecDialog(Shell parent, TrecsExecInfo info) {
        super(parent);

        if (info == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + " constructor received a null TrecsExecDialogInfo.");
        }
        this.info = info;
    }

    @Override
    protected boolean isResizable() {
        return true;
    }

    @Override
    public boolean close() {
        if (boldFont != null && !boldFont.isDisposed()) {
            boldFont.dispose();
            boldFont = null;
        }
        return super.close();
    }

    public TrecsExecInfo getInfo() {
        return info;
    }

    public void setInfo(TrecsExecInfo info) {
        this.info = info;
    }

    @Override
    protected Control createDialogArea(Composite parent) {

        GridData griddyData;

        /*
         * I think we need to create our own Composite child (with GridLayout)
         * of this hosedParentContainer. Otherwise, if we use the
         * hosedParentContainer directly, then our Groups get smushed up near
         * the top sometimes.
         */
        Composite hosedParentContainer = (Composite) super.createDialogArea(
                parent);

        /*
         * NOTE: Remember that GridData is set for each widget WITHIN a
         * Composite, and not for the Composite itself!!! Ea GridData tells the
         * Composite's GridLayout what to do with this child widget.
         */
        Composite container = new Composite(hosedParentContainer, SWT.FILL);
        container.setLayout(new GridLayout());
        container.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
        /*
         * Physical Event Attributes Group
         */
        Group phyEventAttrsGroup = new Group(container, SWT.NONE);
        phyEventAttrsGroup.setLayout(new GridLayout());
        phyEventAttrsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
        phyEventAttrsGroup.setText("Physical Event Attributes");

        Composite peComposite = new Composite(phyEventAttrsGroup, SWT.FILL);
        GridLayout peCompGridLayout = new GridLayout();
        peCompGridLayout.numColumns = 2;
        peComposite.setLayout(peCompGridLayout);
        peComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        if (info.getPhyEvent() == null) {
            return container;
        }

        IPhysicalEvent phyEvent = info.getPhyEvent();

        /*
         * Left side of PhyEvent Attributes
         */
        Composite leftComposite = new Composite(peComposite, SWT.FILL);
        GridLayout leftCompGridLayout = new GridLayout();
        leftCompGridLayout.numColumns = 1;
        leftComposite.setLayout(leftCompGridLayout);
        leftComposite
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        new Label(leftComposite, SWT.NONE)
                .setText("Type: " + phyEvent.getEventType().getLabel());
        new Label(leftComposite, SWT.NONE)
                .setText("ID: " + phyEvent.getCustomId());
        if (phyEvent.getData() instanceof SeismicEventData) {
            SeismicEventData seismicData = (SeismicEventData) phyEvent
                    .getData();
            new Label(leftComposite, SWT.NONE)
                    .setText("Magnitude: " + seismicData.getPrefMagnitude());
        }

        /*
         * Right side of PhyEvent Attributes
         */
        Composite rightComposite = new Composite(peComposite, SWT.FILL);
        GridLayout rightCompGridLayout = new GridLayout();
        rightCompGridLayout.numColumns = 1;
        rightComposite.setLayout(rightCompGridLayout);
        rightComposite
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        String lon = FLOAT_FORMATTER.format(phyEvent.getLongitude());
        String lat = FLOAT_FORMATTER.format(phyEvent.getLatitude());

        new Label(rightComposite, SWT.NONE)
                .setText("Lon/Lat: " + lon + "/" + lat);
        if (phyEvent.getData() instanceof SeismicEventData) {
            SeismicEventData seismicData = (SeismicEventData) phyEvent
                    .getData();
            new Label(rightComposite, SWT.NONE).setText("Depth: "
                    + FLOAT_FORMATTER.format(seismicData.getDepth()) + " mi / "
                    + FLOAT_FORMATTER.format(seismicData.getDepthKm()) + " km");
            new Label(rightComposite, SWT.NONE).setText("Dist To Coast: "
                    + FLOAT_FORMATTER.format(phyEvent.getDistanceToCoastKm())
                    + " km "
                    + (phyEvent.getDistanceToCoastKm() >= 0 ? "(OFFshore)"
                            : "(ONshore)"));
        }

        /*
         * Trace Group
         */
        griddyData = new GridData(SWT.FILL, SWT.FILL, true, false);
        griddyData.heightHint = 100; // Min height would be nice?
        Group traceGroup = new Group(container, SWT.FILL);
        traceGroup.setLayout(new GridLayout());
        traceGroup.setLayoutData(griddyData);
        traceGroup.setText("T-RECS Execution Progress");

        Composite preambComposite = new Composite(traceGroup, SWT.FILL);
        preambComposite.setLayout(new GridLayout());
        preambComposite
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        for (String s : info.getTrace()) {
            new Label(preambComposite, SWT.NONE).setText(s);
        }

        /*
         * Procedures Group
         */
        Group proceduresGroup = new Group(container, SWT.FILL);
        proceduresGroup.setLayout(new GridLayout());
        proceduresGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        proceduresGroup.setText("T-RECS Procedures");
        List<String> enabledProductRegions = info.getEnabledProductRegions();

        /*
         * Procedures Tabs, some of which may omitted if not in the
         * enabledProductRegions.
         */
        TabFolder tabFolder = new TabFolder(proceduresGroup, SWT.FILL);
        tabFolder.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        int currentTabIndex = 0;
        int selectedTabIndex = 0;
        // Loop over each product region, with a tab for each product region
        for (Map.Entry<String, List<TrecsExecProcedure>> entry : info
                .getProcedures().entrySet()) {

            if (!enabledProductRegions.isEmpty()
                    && !enabledProductRegions.contains(entry.getKey())) {
                continue;
            }

            Composite tabComposite = new Composite(tabFolder, SWT.FILL);
            tabComposite.setLayout(new GridLayout());
            tabComposite.setLayoutData(
                    new GridData(SWT.FILL, SWT.FILL, true, true));

            TabItem tabItem = new TabItem(tabFolder, SWT.NULL);
            tabItem.setText(entry.getKey());
            tabItem.setControl(tabComposite);

            if (entry.getKey().equals(info.getSelectedProductRegion())) {
                selectedTabIndex = currentTabIndex;
            }
            currentTabIndex++;

            /*
             * Top of procedures
             */
            Composite procsTopComposite = new Composite(tabComposite, SWT.FILL);
            RowLayout procsTopRowLayout = new RowLayout();
            procsTopRowLayout.wrap = false;
            procsTopRowLayout.justify = false;
            procsTopComposite.setLayout(procsTopRowLayout);
            procsTopComposite.setLayoutData(
                    new GridData(SWT.FILL, SWT.FILL, true, false));

            new Label(procsTopComposite, SWT.NONE)
                    .setText("T-RECS will recommend using the ");
            Combo proceduresCombo = new Combo(procsTopComposite, SWT.READ_ONLY);
            List<String> procNames = new ArrayList<>(
                    info.getProcedures().size());
            procNames.add(NONE_PROCEDURE);
            TrecsExecProcedure selectedProc = null;
            int selectedProcIndex = 0;
            int index = 1;
            for (TrecsExecProcedure proc : entry.getValue()) {
                procNames.add(proc.getName());
                if (proc.isSelected()) {
                    selectedProc = proc;
                    selectedProcIndex = index;
                }
                index++;
            }
            proceduresCombo.setItems(procNames.toArray(new String[0]));
            proceduresCombo.select(selectedProcIndex);
            proceduresCombo.addSelectionListener(new SelectionAdapter() {

                @Override
                public void widgetSelected(SelectionEvent e) {
                    String selectedProcName = proceduresCombo.getText();
                    TrecsExecProcedure selectedProc = null;
                    for (TrecsExecProcedure proc : entry.getValue()) {
                        if (proc.getName().equals(selectedProcName)) {
                            proc.setSelected(true);
                            selectedProc = proc;
                            break;
                        } else {
                            proc.setSelected(false);
                        }
                    }
                    TabItem[] selectedTabItems = tabFolder.getSelection();
                    if (selectedTabItems.length != 1) {
                        // Heck if i know
                        return;
                    }
                    TabItem selectedTabItem = selectedTabItems[0];
                    Group categoriesGroup = (Group) selectedTabItem.getData();
                    reinitCategoriesGroup(selectedProc, categoriesGroup);

                }

            });

            new Label(procsTopComposite, SWT.NONE).setText(" procedures.");

            /*
             * Bottom of procedures group
             */
            Composite procsBottomComposite = new Composite(tabComposite,
                    SWT.FILL);
            GridLayout procsBottomGridLayout = new GridLayout();
            procsBottomGridLayout.numColumns = 2;
            procsBottomComposite.setLayout(procsBottomGridLayout);
            procsBottomComposite.setLayoutData(
                    new GridData(SWT.FILL, SWT.FILL, true, true));

            /*
             * Categories group and composite
             */
            griddyData = new GridData(SWT.FILL, SWT.FILL, false, true);
            Group categoriesGroup = new Group(procsBottomComposite, SWT.FILL);
            categoriesGroup.setLayout(new GridLayout());
            categoriesGroup.setLayoutData(griddyData);
            categoriesGroup.setText("With selected category:");

            /*
             * Keep the categoriesGroup on the TabItem for later use. Crazy.
             */
            tabItem.setData(categoriesGroup);

            /*
             * Conditions/Actions Composite
             */
            griddyData = new GridData(SWT.FILL, SWT.FILL, true, true);
            Group condActionsGroup = new Group(procsBottomComposite, SWT.FILL);
            condActionsGroup.setLayout(new GridLayout());
            condActionsGroup.setLayoutData(griddyData);
            condActionsGroup.setText("Conditions/Actions:");

            /*
             * Set the condActionsGroup on the categoriesGroup for later use.
             * Crazy.
             */
            categoriesGroup.setData(condActionsGroup);

            reinitCategoriesGroup(selectedProc, categoriesGroup);
            // reinitConditionsActionsComposite(condActionsGroup);
        }

        tabFolder.setSelection(selectedTabIndex);

        container.requestLayout();
        return container;
    }

    protected void reinitCategoriesGroup(TrecsExecProcedure selectedProc,
            Group categoriesGroup) {

        if (categoriesGroup == null) {
            return;
        }

        for (Control child : categoriesGroup.getChildren()) {
            child.dispose();
        }

        Composite categoriesComposite = new Composite(categoriesGroup,
                SWT.V_SCROLL | SWT.H_SCROLL);
        // Making the vertical BEGINNING and false has no effect below.
        categoriesComposite
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        categoriesComposite.setLayout(new GridLayout());
        if (selectedProc != null) {
            for (TrecsExecCategory categ : selectedProc.getCategories()) {
                Button radioBtn = new Button(categoriesComposite, SWT.RADIO);
                radioBtn.setText(categ.getName());
                radioBtn.setData(categoriesGroup);
                boolean selected = false;
                if (selectedProc.getSelectedCategory() != null
                        && categ.getName().equals(
                                selectedProc.getSelectedCategory().getName())) {
                    selected = true;
                }
                radioBtn.setSelection(selected);
                if (selectedProc.isDefault()
                        && categ.equals(selectedProc.getDefaultCategory())) {
                    FontData[] data = radioBtn.getFont().getFontData();

                    for (FontData datum : data) {
                        datum.setStyle(SWT.BOLD);
                    }

                    if (boldFont != null && !boldFont.isDisposed()) {
                        // Is this C++ or do we just love SWT?
                        boldFont.dispose();
                        boldFont = null;
                    }
                    boldFont = new Font(radioBtn.getDisplay(), data);
                    radioBtn.setFont(boldFont);
                }
                radioBtn.addSelectionListener(new SelectionAdapter() {

                    @Override
                    public void widgetSelected(SelectionEvent e) {
                        String selectedCategName = radioBtn.getText();
                        TrecsExecCategory selectedCateg = null;
                        if (selectedProc != null) {
                            for (TrecsExecCategory categ : selectedProc
                                    .getCategories()) {
                                if (categ.getName().equals(selectedCategName)) {
                                    selectedCateg = categ;
                                    break;
                                }
                            }
                            /*
                             * I think there is a bug in SWT such that unselect
                             * doesn't work well. So if we get a selection event
                             * for the already-selected category, then unselect
                             * the category.
                             */
                            if (selectedProc.getSelectedCategory() != null
                                    && selectedProc.getSelectedCategory()
                                            .equals(selectedCateg)) {
                                selectedCateg = null;
                                radioBtn.setSelection(false);
                            }
                            selectedProc.setSelectedCategory(selectedCateg);
                        }
                        Group condActionsGroup = (Group) categoriesGroup
                                .getData();
                        reinitConditionsActionsComposite(selectedCateg,
                                condActionsGroup);
                    }
                });
            }
        }
        // categoriesGroup.layout();
        categoriesGroup.requestLayout();

        Group condActionsGroup = (Group) categoriesGroup.getData();
        reinitConditionsActionsComposite(
                (selectedProc != null ? selectedProc.getSelectedCategory()
                        : null),
                condActionsGroup);
    }

    protected void reinitConditionsActionsComposite(
            TrecsExecCategory selectedCateg, Group condActionsGroup) {

        if (condActionsGroup == null) {
            return;
        }

        for (Control child : condActionsGroup.getChildren()) {
            child.dispose();
        }

        Composite condActionsComposite = new Composite(condActionsGroup,
                SWT.FILL);
        condActionsComposite.setLayout(new GridLayout());
        condActionsComposite
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        if (selectedCateg != null) {
            List<String> conditions = selectedCateg.getConditions();
            List<String> actions = selectedCateg.getActions();

            for (String cond : conditions) {
                new Label(condActionsComposite, SWT.NONE).setText(cond);
            }
            new Label(condActionsComposite, SWT.SEPARATOR | SWT.HORIZONTAL);
            for (String action : actions) {
                new Label(condActionsComposite, SWT.NONE).setText(action);
            }
        }

        condActionsGroup.requestLayout();
    }

    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("T-RECS Execution Dialog");
    }

//    @Override
//    protected Point getInitialSize() {
//        return new Point(450, 300);
//    }

    ///////////////////////////////////////////////////////////////////////////

    public static TrecsExecInfo open(TrecsExecInfo info) {
        int status[] = new int[1];
        VizApp.runSync(() -> {
            // Note that PlatformUI.getWorkbench() return null if NOT
            // on the UI thread!
            TrecsExecDialog trecsDlg = new TrecsExecDialog(PlatformUI
                    .getWorkbench().getActiveWorkbenchWindow().getShell(),
                    info);
            // System.out.println(info.toString());
            int result = trecsDlg.open();
            status[0] = result;
        });
        // OK == 0
        if (status[0] == 0) {
            return info;
        }
        // Cancel == 1
        else {
            return null;
        }
    }

}
