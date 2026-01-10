package gov.noaa.gsl.viz.atoms.plot;

import java.math.RoundingMode;
import java.text.DecimalFormat;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Text;

import gov.noaa.gsl.viz.pem.plot.PEPlotter;

public abstract class GeneralPEPlotter extends PEPlotter {

    protected static final RGB CYAN = new RGB(0, 255, 255);

    private static DecimalFormat RANGE_FORMATTER = new DecimalFormat("0.0");

    static {
        RANGE_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    private Button configIdCheckbox;

    private Button configRangeRingCheckbox;

    private Text configRangeRingRadiusTextfield;

    private Button configAutoDensityCheckbox;

    public GeneralPEPlotter(GeneralPlotConfig plotConfig) {
        super(plotConfig);
    }

    protected GeneralPlotConfig getGeneralPlotConfig() {
        if (getPlotConfig() instanceof GeneralPlotConfig) {
            return (GeneralPlotConfig) getPlotConfig();
        }
        return null;
    }

    protected void clearConfigWidgets() {
        configIdCheckbox = null;
        configAutoDensityCheckbox = null;
        configRangeRingCheckbox = null;
        configRangeRingRadiusTextfield = null;
        setBuildConfigWidgetsComplete(false);
    }

    protected boolean isIdCheckboxDisposed() {
        return (configIdCheckbox == null || configIdCheckbox.isDisposed());
    }

    @Override
    protected void reinitConfigWidgets() {
        if (!isBuildConfigWidgetsComplete() || isIdCheckboxDisposed()) {
            return;
        }
        configIdCheckbox.setSelection(getGeneralPlotConfig().isShowCustomId());
        configRangeRingCheckbox
                .setSelection(getGeneralPlotConfig().isShowRangeRing());
        configRangeRingRadiusTextfield.setText(RANGE_FORMATTER
                .format(getGeneralPlotConfig().getRangeRingRadiusKm()));
        configAutoDensityCheckbox
                .setSelection(getGeneralPlotConfig().isAutoDensityControl());
    }

    protected void buildIdCheckbox(Composite parent) {
        configIdCheckbox = new Button(parent, SWT.CHECK);
        configIdCheckbox.setText("Custom ID");
        configIdCheckbox.setSelection(getGeneralPlotConfig().isShowCustomId());
        configIdCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getGeneralPlotConfig()
                        .setShowCustomId(configIdCheckbox.getSelection());
            }
        });
    }

    protected void buildRangeRingGroup(Composite parent) {
        Composite rowComp = new Composite(parent, SWT.NONE);
        GridLayout rowGridLayout = new GridLayout();
        rowGridLayout.numColumns = 2;
        rowComp.setLayout(rowGridLayout);
        rowComp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

        configRangeRingCheckbox = new Button(rowComp, SWT.CHECK);
        configRangeRingCheckbox.setText("Range Ring with Km Radius = ");
        configRangeRingCheckbox
                .setSelection(getGeneralPlotConfig().isShowRangeRing());
        configRangeRingCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getGeneralPlotConfig().setShowRangeRing(
                        configRangeRingCheckbox.getSelection());
            }
        });

        configRangeRingRadiusTextfield = new Text(rowComp,
                SWT.SINGLE | SWT.BORDER);
        configRangeRingRadiusTextfield.setText(RANGE_FORMATTER
                .format(getGeneralPlotConfig().getRangeRingRadiusKm()));
        configRangeRingRadiusTextfield.addModifyListener(e -> {
            String newValue = ((Text) e.widget).getText();
            try {
                float newFloat1 = Float.parseFloat(newValue);
                getGeneralPlotConfig().setRangeRingRadiusKm(newFloat1);
            } catch (Exception exception) {
                try {
                    float newFloat2 = Integer.parseInt(newValue);
                    getGeneralPlotConfig().setRangeRingRadiusKm(newFloat2);
                } catch (Exception exception2) {
                }
            }
        });
    }

    protected void buildAutoDensityGroup(Composite parent) {
        Group otherOptionsGroup = new Group(parent, SWT.NONE);
        otherOptionsGroup.setLayout(new GridLayout());
        otherOptionsGroup
                .setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        otherOptionsGroup.setText("Other options:");

        configAutoDensityCheckbox = new Button(otherOptionsGroup, SWT.CHECK);
        configAutoDensityCheckbox.setText("Auto Density Control");
        configAutoDensityCheckbox
                .setSelection(getGeneralPlotConfig().isAutoDensityControl());
        configAutoDensityCheckbox.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                getGeneralPlotConfig().setAutoDensityControl(
                        configAutoDensityCheckbox.getSelection());
            }
        });

    }
}
