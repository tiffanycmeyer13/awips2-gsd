package gov.noaa.gsl.viz.atoms.ui;

import java.util.Calendar;
import java.util.Date;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.DateTime;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Spinner;

import gov.noaa.gsl.common.dataplugin.atoms.VolcanicEventData;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventData;
import gov.noaa.gsl.viz.pem.dialog.BasePEMDialogTab;

/**
 * Displays a volcanic event data in detail. It's not editable but keeps
 * editable option for future upload a event.
 *
 * It includes origin time and origin, the two data group.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Apr 19, 2922        Jing                  Initial implement volcanic data display tab
 *
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 *
 *
 */
public class VolcanicDataTab extends BasePEMDialogTab {
    private final static boolean IS_EDITABLE = true;

    public VolcanicDataTab() {
        super();
    }

    @Override
    protected void reinitializeTabContent() {

        if (getTabItem() == null || getTabFolder() == null) {
            return;
        }

        Composite comp = new Composite(getTabFolder(), SWT.NONE);
        comp.setLayout(new GridLayout());
        comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        comp.setBackground(new Color(250, 150, 100));
        setTabContentComposite(comp);
        getTabItem().setControl(getTabContentComposite());

        /* No event data, do noting */
        if (getPhysicalEvent() == null) {
            getTabContentComposite().setLayout(new GridLayout(2, false));
            Label noEventLabel = new Label(getTabContentComposite(), SWT.NONE);
            noEventLabel.setText("No Selected Physical Event");

        } else {
            /* Display the detail volcanic data of the event */
            PhysicalEventData data = getPhysicalEvent().getData();

            if (!(data instanceof VolcanicEventData)) {
                Label badDataLabel = new Label(getTabContentComposite(),
                        SWT.NONE);
                badDataLabel.setText(
                        "ERROR - Physical Event's Data is not a \"VolcanicEventData\"");
            } else {
                VolcanicEventData volcanicData = (VolcanicEventData) data;
                createVolcanicEventDataTab(volcanicData);
            }
        }
    }

    /**
     * Display the volcanic event data.
     *
     * @param volcanicicData
     *            The volcanic event data to be displayed.
     */
    private void createVolcanicEventDataTab(VolcanicEventData volcanicData) {

        /* The origin time group */
        Group originTimeGroup = new Group(getTabContentComposite(), SWT.NONE);
        RowLayout layoutOT = new RowLayout(SWT.HORIZONTAL);
        layoutOT.fill = true;
        originTimeGroup.setLayout(layoutOT);
        originTimeGroup.setText("Origin Time");

        initializeOriginTimeGroup(originTimeGroup);

        /* The origin group */
        Group originGroup = new Group(getTabContentComposite(), SWT.NONE);
        originGroup.setLayout(layoutOT);
        originGroup.setText("Origin");

        initializeOriginGroup(originGroup, volcanicData);
    }

    /**
     * Initializes the origin time data.
     *
     * The date and time format it TBD
     *
     * @param originTimeGroup
     *            The origin time group.
     */
    private void initializeOriginTimeGroup(Group originTimeGroup) {
        if (getPhysicalEvent() == null) {
            return;
        }

        /* Get the date for the current physical event */
        Date date = getPhysicalEvent().getRefTime();
        Calendar cal = Calendar.getInstance();
        cal.setTime(date);

        /* Display the date with a date editor */
        Label dateLabel = new Label(originTimeGroup, SWT.READ_ONLY);
        dateLabel.setText("Date:");

        DateTime theDate = new DateTime(originTimeGroup,
                SWT.DATE | SWT.DROP_DOWN | SWT.BORDER);
        theDate.setDate(cal.get(Calendar.YEAR), cal.get(Calendar.MONTH),
                cal.get(Calendar.DAY_OF_MONTH));

        /* Display the time with a time editor */
        Label timeLabel = new Label(originTimeGroup, SWT.READ_ONLY);
        timeLabel.setText("Time:");

        DateTime theTime = new DateTime(originTimeGroup,
                SWT.TIME | SWT.BORDER | SWT.SHORT);
        theTime.setTime(cal.get(Calendar.HOUR), cal.get(Calendar.MINUTE),
                cal.get(Calendar.SECOND));

        /* Determine if the date and time are editable */
        theDate.setEnabled(IS_EDITABLE);
        theTime.setEnabled(IS_EDITABLE);
    }

    /**
     * Initializes the origin data.
     *
     * @param originTimeGroup
     *            The origin group.
     */
    private void initializeOriginGroup(Group originGroup,
            VolcanicEventData volcanicData) {
        if (getPhysicalEvent() == null) {
            return;
        }

        /* Display the longitude */
        Label longitudeLabel = new Label(originGroup, SWT.READ_ONLY);
        longitudeLabel.setText("Longitude:");
        final Spinner longitudeSnipper = new Spinner(originGroup, 0);
        longitudeSnipper.setDigits(2);
        longitudeSnipper.setMinimum(-18000);
        longitudeSnipper.setMaximum(18000);
        longitudeSnipper
                .setSelection((int) (getPhysicalEvent().getLongitude() * 100));
        longitudeSnipper.setIncrement(1);
        longitudeSnipper.setPageIncrement(100);
        longitudeSnipper.setEnabled(false);
        longitudeSnipper.pack();

        /* Display the latitude */
        Label latitudeLabel = new Label(originGroup, SWT.READ_ONLY);
        latitudeLabel.setText("Latitude:");
        final Spinner latitudeSnipper = new Spinner(originGroup, 0);
        latitudeSnipper.setDigits(2);
        latitudeSnipper.setMinimum(-18000);
        latitudeSnipper.setMaximum(18000);
        latitudeSnipper
                .setSelection((int) (getPhysicalEvent().getLatitude() * 100));
        latitudeSnipper.setIncrement(1);
        latitudeSnipper.setPageIncrement(100);
        latitudeSnipper.pack();

        /* Determine if the date and time are editable */
        longitudeSnipper.setEnabled(IS_EDITABLE);
        latitudeSnipper.setEnabled(IS_EDITABLE);
    }
}
