package gov.noaa.gsd.viz.ensemble.display.control.contour;

import java.util.List;

import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.FocusAdapter;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;

import com.raytheon.uf.common.style.StyleException;
import com.raytheon.uf.viz.core.grid.rsc.AbstractGridResource;
import com.raytheon.viz.ui.dialogs.CaveJFACEDialog;

/**
 *
 * A dialog to interactively control the contour display of one or multiple grid
 * resources. It can be popped up by selecting "Contour Control" on the legend
 * right clicking menu of a loaded product, generated product or a ensemble
 * product.
 *
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Feb 28, 2017   19598      jing     Initial creation
 * Jun 27, 2017   19325      jing     Upgrade to 17.3.1
 * Oct 28, 2021   97771      srussell Updated createDialogArea()
 *                                    Updated addThresholdValueModifyBehavior()
 *                                    Added addFocusListenersForInputFields()
 * Dec 28, 2021   99596      thuggins Fixing functionality of the contour control
 *                                    so that users can enter negative values.
 *                                    Changes made to the modifyText() method
 * Feb 18, 2022   99598      srussell Updated increaseContour(), createButtonsForButtonBar()
 * </pre>
 *
 * @author jing
 */

public class ContourControlDialog extends CaveJFACEDialog {

    private Composite mainPanelComposite = null;

    /*
     * For inputing the specified contour value. It should be same unit as the
     * displayed grid contour. The initial value comes from the resource style
     * preference. If it is empty(NaN), the grid will be displayed as default
     * contours with the increment only. The up and down arrow buttons can
     * increase or decrease this value with the increment.
     */
    private Text contourValueEntryTxt = null;

    /*
     * For inputing the specified contour increment. It should be same unit as
     * the displayed grid contour. The initial value comes from the resource
     * style preference.
     */
    private Text contourIncrementEntryTxt = null;

    private Label ensembleProductNameLbl = null;

    private String ensembleProductName = null;

    /*
     * Saves the specified contour value.
     */
    private float value = Float.NaN;

    /*
     * Saves the specified contour increment.
     */
    private float increment = Float.NaN;

    /*
     * The ContourControl object to control the contours of the resource(s).
     */
    private ContourControl contourControl;

    /*
     * The grid resource(s) to be controlled.
     */
    private List<AbstractGridResource<?>> rscList;

    private ContourControlDialog(Shell parentShell) {
        super(parentShell);
    }

    /**
     * Constructor.
     *
     * @param parentShell
     *            The parent shell.
     * @param name
     *            Product name
     * @param rscs
     *            Grid resource list
     * @throws StyleException
     */
    public ContourControlDialog(Shell parentShell, String name,
            List<AbstractGridResource<?>> rscs) throws StyleException {

        super(parentShell);
        rscList = rscs;

        // Use labeling preference of first resource to do single or group
        // contour control
        contourControl = new ContourControl(rscs.get(0));
        value = contourControl.getDefaultValue();
        increment = contourControl.getIncrementOrig();

        ensembleProductName = name;

    }

    /*
     *
     * @see org.eclipse.jface.dialogs.Dialog#isResizable()
     */
    @Override
    protected boolean isResizable() {
        return false;
    }

    /**
     * Create contents of the dialog.
     *
     * @param parent
     * @return A Control
     */
    @Override
    protected Control createDialogArea(Composite parent) {

        setBlockOnOpen(true);

        createRootArea(parent);

        createTitleWidget();

        createVerticalSeparator();

        createContourArea();

        Label dummySpacerLbl_1 = new Label(mainPanelComposite, SWT.NONE);
        GridData dummySpacerLbl_gd_1 = new GridData(SWT.LEFT, SWT.CENTER, true,
                false, 2, 1);
        dummySpacerLbl_1.setLayoutData(dummySpacerLbl_gd_1);

        contourValueEntryTxt.setEnabled(true);
        contourIncrementEntryTxt.setEnabled(true);

        addThresholdValueModifyBehavior();

        addFocusListenersForInputFields();

        return parent;

    }

    private void createVerticalSeparator() {
        new Label(mainPanelComposite, SWT.NONE).setLayoutData(
                new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 2));

    }

    private void createRootArea(Composite parent) {
        mainPanelComposite = new Composite(parent, SWT.BORDER);

        GridData rootCalculatorPanel_gd = new GridData(SWT.FILL, SWT.FILL, true,
                true, 1, 1);
        mainPanelComposite.setLayoutData(rootCalculatorPanel_gd);
        mainPanelComposite.setLayout(new GridLayout(1, false));
    }

    private void createTitleWidget() {

        Composite titleContainerComposite = new Composite(mainPanelComposite,
                SWT.BORDER);
        titleContainerComposite.setLayoutData(
                new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
        titleContainerComposite.setLayout(new GridLayout(1, true));

        ensembleProductNameLbl = new Label(titleContainerComposite,
                SWT.CENTER | SWT.BORDER);

        GridData frameTimeUsingBasisLbl_gd = new GridData(SWT.FILL, SWT.CENTER,
                true, true, 1, 1);
        ensembleProductNameLbl.setLayoutData(frameTimeUsingBasisLbl_gd);

    }

    /**
     * Create the interactive contour specify area.
     */
    private void createContourArea() {

        Composite contourRootComposite = new Composite(mainPanelComposite,
                // SWT.BORDER);
                SWT.NONE);

        GridData contourRootComposite_gd = new GridData(SWT.FILL, SWT.CENTER,
                true, true, 1, 1);
        contourRootComposite.setLayoutData(contourRootComposite_gd);
        contourRootComposite.setLayout(new GridLayout(2, false));

        Label contourLabel = new Label(contourRootComposite,
                SWT.SINGLE | SWT.CENTER);
        contourLabel.setText("Contour");
        GridData contourLabel_gd = new GridData(SWT.FILL, SWT.CENTER, true,
                false, 1, 1);
        contourLabel.setLayoutData(contourLabel_gd);

        Label incrementLabel = new Label(contourRootComposite,
                SWT.SINGLE | SWT.CENTER);
        incrementLabel.setText("Increment");
        GridData incrementLabel_gd = new GridData(SWT.FILL, SWT.CENTER, true,
                false, 1, 1);
        incrementLabel.setLayoutData(incrementLabel_gd);

        Composite contourControllerComposite = new Composite(
                contourRootComposite, SWT.BORDER);
        GridData contourControllerComposite_gd = new GridData(SWT.FILL,
                SWT.CENTER, true, true, 1, 1);
        contourControllerComposite.setLayoutData(contourControllerComposite_gd);
        contourControllerComposite.setLayout(new GridLayout(2, false));

        /*
         * Text entry for specifying contour value
         */
        contourValueEntryTxt = new Text(contourControllerComposite,
                SWT.BORDER | SWT.SINGLE | SWT.CENTER);

        setValueEntryTxt(value);
        contourValueEntryTxt.setToolTipText("A contour label value");
        contourValueEntryTxt.selectAll();

        GridData contourValueEntryTxt_gd = new GridData(SWT.FILL, SWT.CENTER,
                true, false, 1, 1);
        contourValueEntryTxt.setLayoutData(contourValueEntryTxt_gd);

        Composite contourControllerUpDownComposite = new Composite(
                contourControllerComposite, SWT.BORDER);
        FillLayout contourControllerUpDownComposite_fl = new FillLayout();
        contourControllerUpDownComposite_fl.type = SWT.HORIZONTAL;
        contourControllerUpDownComposite
                .setLayout(contourControllerUpDownComposite_fl);

        /*
         * Arrow button for increasing contour value
         */
        final Button contourIncreaseButton = new Button(
                contourControllerUpDownComposite, SWT.ARROW | SWT.UP);
        contourIncreaseButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                increaseContour(true);
            }
        });

        /*
         * Arrow button for decreasing contour value
         */
        final Button contourDecreaseButton = new Button(
                contourControllerUpDownComposite, SWT.ARROW | SWT.DOWN);
        contourDecreaseButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                increaseContour(false);
            }
        });

        /*
         * Text entry for specifying contour increment
         */
        contourIncrementEntryTxt = new Text(contourRootComposite,
                SWT.BORDER | SWT.SINGLE | SWT.CENTER);
        GridData contourIncrementEntryTxt_gd = new GridData(SWT.FILL,
                SWT.CENTER, true, false, 1, 1);
        contourIncrementEntryTxt.setLayoutData(contourIncrementEntryTxt_gd);
        setIncrementEntryTxt(increment);
        contourIncrementEntryTxt.setToolTipText("The contour increment");

    }

    /**
     * Increase/Decrease the contour base on the flag passed in
     *
     * @param increase
     *            If it is true then increase the contour value and display it
     *            Otherwise decrease the contour.
     */
    private void increaseContour(boolean increase) {

        if (Float.isNaN(increment) || Float.isNaN(value) || increment == 0) {
            return;
        }
        if (increase) {
            value += increment;
        } else {
            value -= increment;
        }
        setValueEntryTxt(value);

        contourControl.changeContourValues(value);
        if (rscList.size() > 1) {
            contourControl.changeContourGroup(rscList, increment, value);
        }
    }

    private void setValueEntryTxt(float value) {

        String valueString = "";
        if (!Float.isNaN(value)) {
            valueString = String.valueOf(value);
        }

        contourValueEntryTxt.setText(valueString);
    }

    private void setIncrementEntryTxt(float increment) {
        String incrementString = "";
        if (!Float.isNaN(increment)) {
            incrementString = String.valueOf(increment);
        }

        contourIncrementEntryTxt.setText(incrementString);
    }

    private void addThresholdValueModifyBehavior() {

        contourValueEntryTxt.addModifyListener(new ModifyListener() {

            @Override
            public void modifyText(ModifyEvent e) {

                // Prevent the user from entering any character that is not
                // a digit or a decimal point.
                Text text = (Text) e.widget;
                String contourValue = text.getText();
                int length = 0;
                length = (contourValue == null) ? 0 : contourValue.length();
                value = handleTextEntry(contourValue);
                if (length == 0) {
                    return;
                }
                if (length == 1 && "-".contentEquals(contourValue)) {
                    return;

                }
                if (Float.isNaN(value) && length == 1) {
                    contourValueEntryTxt.setText("");
                } else if (Float.isNaN(value) && length > 1) {
                    contourValue = contourValue.substring(0, (length - 1));
                    contourValueEntryTxt.setText(contourValue);
                    contourValueEntryTxt.setSelection(length);
                }
            }
        });

        contourIncrementEntryTxt.addModifyListener(new ModifyListener() {

            @Override
            public void modifyText(ModifyEvent e) {

                // Prevent the user from entering anything other than a digit
                // or a decimal point into the field.
                Text text = (Text) e.widget;
                String incrementValue = text.getText();
                int length = 0;
                length = (incrementValue == null) ? 0 : incrementValue.length();
                increment = handleTextEntry(incrementValue);
                if (length == 0) {
                    return;
                }
                if (Float.isNaN(increment) && length == 1) {
                    contourIncrementEntryTxt.setText("");
                } else if (Float.isNaN(increment) && length > 1) {
                    incrementValue = incrementValue.substring(0, (length - 1));
                    contourIncrementEntryTxt.setText(incrementValue);
                    contourIncrementEntryTxt.setSelection(length);
                }

            }
        });

    }

    private void addFocusListenersForInputFields() {

        contourValueEntryTxt.addFocusListener(new FocusAdapter() {
            @Override
            public void focusLost(FocusEvent fe) {
                // If it ends with a decimal point, add a zero after that
                String incrementValue = contourValueEntryTxt.getText();
                incrementValue = (incrementValue == null) ? ""
                        : incrementValue.trim();
                if (incrementValue.endsWith(".")) {
                    incrementValue += "0";
                    contourValueEntryTxt.setText(incrementValue);
                }
            }
        });

        contourIncrementEntryTxt.addFocusListener(new FocusAdapter() {
            @Override
            public void focusLost(FocusEvent fe) {
                // If it ends with a decimal point, add a zero after that
                String incrementValue = contourIncrementEntryTxt.getText();
                incrementValue = (incrementValue == null) ? ""
                        : incrementValue.trim();
                if (incrementValue.endsWith(".")) {
                    incrementValue += "0";
                    contourIncrementEntryTxt.setText(incrementValue);
                }
            }
        });

    }

    protected float handleTextEntry(String entry) {

        if ((entry == null) || (entry.length() == 0)) {
            return Float.NaN;
        }

        if (!entry.matches("[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)")) {
            return Float.NaN;
        }
        float value = Float.NaN;
        try {
            value = Float.parseFloat(entry);

        } catch (NumberFormatException nfe) {

            return Float.NaN;
        }
        return value;
    }

    /**
     * enable the widgets default state
     */
    protected void enableDefaultContourWidgetState() {

        ensembleProductNameLbl.setText(ensembleProductName);

        contourValueEntryTxt.setEnabled(true);

        contourIncrementEntryTxt.setEnabled(true);

        setValueEntryTxt(value);

        contourValueEntryTxt.forceFocus();
        setIncrementEntryTxt(increment);

        mainPanelComposite.getShell().pack();
        mainPanelComposite.getShell()
                .setMinimumSize(mainPanelComposite.getShell().getSize());

    }

    /**
     *
     * Create contents of the button bar.
     *
     * @param parent
     */

    @Override
    protected void createButtonsForButtonBar(Composite parent) {

        Button updateButton = createButton(parent, SWT.PUSH, "Apply", true);

        updateButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                contourControl.changeContourValues(value);
                if (rscList.size() > 1) {
                    contourControl.changeContourGroup(rscList, increment,
                            value);
                }
            }
        });

        Button closeButton = createButton(parent, IDialogConstants.CLOSE_ID,
                IDialogConstants.CLOSE_LABEL, false);
        closeButton.addSelectionListener(new SelectionAdapter() {

            @Override
            public void widgetSelected(SelectionEvent e) {
                close();
            }

        });

    }

    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("Contour Control");
    }

    @Override
    protected Control createContents(Composite parent) {
        Control contents = super.createContents(parent);
        enableDefaultContourWidgetState();
        return contents;
    }

    @Override
    public boolean close() {
        contourControl = null;
        rscList.clear();
        return super.close();
    }

}
