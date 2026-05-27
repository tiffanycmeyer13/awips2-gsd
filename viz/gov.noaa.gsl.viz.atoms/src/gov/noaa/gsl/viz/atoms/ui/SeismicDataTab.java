package gov.noaa.gsl.viz.atoms.ui;

import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.util.Calendar;
import java.util.Date;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.DateTime;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;

import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventData;
import gov.noaa.gsl.viz.pem.dialog.BasePEMDialogTab;

/**
 * Displays a seismic event data in detail. It's not editable but keeps editable
 * option for future upload an event.
 *
 * It includes origin time, origin and magnitude, the three data group.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Apr 19, 2022        Jing                  Initial implement seismic
 *                                           data display tab
 * Aug 10, 2022        Jing                  Display the Depth and Type
 *                                           in the from SeismicEventData
 * Aug 15, 2022        Jing                  Add the azimuth coverage, number
 *                                           of stations and theta.
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 *
 *
 */

public class SeismicDataTab extends BasePEMDialogTab {
    private final static boolean IS_EDITABLE = false;

    private static DecimalFormat DEPTH_FORMATTER = new DecimalFormat("0.0");
    static {
        DEPTH_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    public SeismicDataTab() {
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
        setTabContentComposite(comp);
        getTabItem().setControl(getTabContentComposite());

        /* No event data, do noting */
        if (getPhysicalEvent() == null) {
            getTabContentComposite().setLayout(new GridLayout(2, false));
            Label noEventLabel = new Label(getTabContentComposite(), SWT.NONE);
            noEventLabel.setText("No Selected Physical Event");

        } else {
            /* Display the detail seismic data of the current event */
            PhysicalEventData data = getPhysicalEvent().getData();
            if (!(data instanceof SeismicEventData)) {
                Label badDataLabel = new Label(getTabContentComposite(),
                        SWT.NONE);
                badDataLabel.setText(
                        "ERROR - Physical Event's Data is not a \"SeismicEventData\"");
            } else {

                SeismicEventData seismicData = (SeismicEventData) data;
                createSeismicDataTab(seismicData);
            }
        }
    }

    /**
     * Display the seismic event data.
     *
     * @param seismicData
     *            The seismic event data to be displayed.
     */
    private void createSeismicDataTab(SeismicEventData seismicData) {

        getTabContentComposite().setBackground(new Color(250, 150, 100));

        /* The origin time group */
        Group originTimeGroup = new Group(getTabContentComposite(), SWT.NONE);
        RowLayout layoutOT = new RowLayout(SWT.HORIZONTAL);
        originTimeGroup.setLayout(layoutOT);
        originTimeGroup.setText("Origin Time");
        initializeOriginTimeGroup(originTimeGroup);
        originTimeGroup.pack();

        /* The origin group */
        Group originGroup = new Group(getTabContentComposite(), SWT.NONE);
        originGroup.setLayout(layoutOT);
        originGroup.setText("Origin");
        initializeOriginGroup(originGroup, seismicData);
        originGroup.pack();

        /* The magnitude group */
        Group magnitudeGroup = new Group(getTabContentComposite(), SWT.NONE);
        magnitudeGroup.setLayout(layoutOT);
        magnitudeGroup.setText("Magnitude");
        initializeMagnitudeGroup(magnitudeGroup, seismicData);
        magnitudeGroup.pack();

        /* The other group */
        Group otherGroup = new Group(getTabContentComposite(), SWT.NONE);
        otherGroup.setLayout(layoutOT);
        otherGroup.setText("Other");
        initializeOtherGroup(otherGroup, seismicData);
        otherGroup.pack();
    }

    /**
     * Initializes the origin time data.
     *
     * The date and time format is TBD
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
     * @param originGroup
     *            The origin group.
     * @param seismicData
     *            The seismic data to be displayed
     */
    private void initializeOriginGroup(Group originGroup,
            SeismicEventData seismicData) {
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
        if (getPhysicalEvent().getLongitude() >= 0) {
            longitudeSnipper.setSelection(
                    (int) (getPhysicalEvent().getLongitude() * 100 + 0.5));
        } else {
            longitudeSnipper.setSelection(
                    (int) (getPhysicalEvent().getLongitude() * 100 - 0.5));
        }
        longitudeSnipper.setIncrement(1);
        longitudeSnipper.setPageIncrement(100);
        longitudeSnipper.pack();

        /* Display the latitude */
        Label latitudeLabel = new Label(originGroup, SWT.READ_ONLY);
        latitudeLabel.setText("Latitude:");

        final Spinner latitudeSnipper = new Spinner(originGroup, 0);
        latitudeSnipper.setDigits(2);
        latitudeSnipper.setMinimum(-18000);
        latitudeSnipper.setMaximum(18000);
        if (getPhysicalEvent().getLatitude() >= 0) {
            latitudeSnipper.setSelection(
                    (int) (getPhysicalEvent().getLatitude() * 100 + 0.5));
        } else {
            latitudeSnipper.setSelection(
                    (int) (getPhysicalEvent().getLatitude() * 100 - 0.5));
        }
        latitudeSnipper.setIncrement(1);
        latitudeSnipper.setPageIncrement(100);
        latitudeSnipper.pack();

        /* Displays the depth */
        Label depthLabel = new Label(originGroup, SWT.READ_ONLY);
        depthLabel.setText("Depth (km):");

        final Text depthText = new Text(originGroup, SWT.READ_ONLY);
        depthText.setText(DEPTH_FORMATTER.format(seismicData.getDepthKm()));

        /* Displays the depth */
        Label distLabel = new Label(originGroup, SWT.READ_ONLY);
        distLabel.setText("KM to Coast:");

        final Text distText = new Text(originGroup, SWT.READ_ONLY);
        distText.setText(DEPTH_FORMATTER
                .format(getPhysicalEvent().getDistanceToCoastKm()));

        /* Determine if the date and time are editable */
        longitudeSnipper.setEnabled(IS_EDITABLE);
        latitudeSnipper.setEnabled(IS_EDITABLE);
        depthText.setEnabled(IS_EDITABLE);
        distText.setEnabled(IS_EDITABLE);
    }

    /**
     * Initializes the other data.
     *
     * @param originGroup
     *            The origin group.
     * @param seismicData
     *            The seismic data to be displayed
     */
    private void initializeOtherGroup(Group otherGroup,
            SeismicEventData seismicData) {
        if (getPhysicalEvent() == null) {
            return;
        }

        /* Display the azimuth coverage */
        Label azimCoverLabel = new Label(otherGroup, SWT.READ_ONLY);
        azimCoverLabel.setText("Azim Cover:");

        final Spinner azimuthalCoverageSnipper = new Spinner(otherGroup, 0);
        azimuthalCoverageSnipper.setDigits(2);
        azimuthalCoverageSnipper.setMinimum(-18000);
        azimuthalCoverageSnipper.setMaximum(18000);
        azimuthalCoverageSnipper
                .setSelection(seismicData.getAzimuthalCoverage() * 100);
        azimuthalCoverageSnipper.setIncrement(1);
        azimuthalCoverageSnipper.setPageIncrement(100);
        azimuthalCoverageSnipper.pack();

        /* Display the Number of stations */
        Label numStationsLabel = new Label(otherGroup, SWT.READ_ONLY);
        numStationsLabel.setText("Num Stations:");

        final Spinner numStationsSnipper = new Spinner(otherGroup, 0);
        numStationsSnipper.setMinimum(0);
        numStationsSnipper.setMaximum(1000);
        numStationsSnipper.setSelection(seismicData.getNumStations());
        numStationsSnipper.setIncrement(1);
        numStationsSnipper.setPageIncrement(10);
        numStationsSnipper.pack();

        /* Displays the theta */
        Label thetaLabel = new Label(otherGroup, SWT.READ_ONLY);
        thetaLabel.setText("Theta:");

        final Spinner thetaSnipper = new Spinner(otherGroup, 0);
        thetaSnipper.setDigits(1);
        thetaSnipper.setMinimum(0);
        thetaSnipper.setMaximum(1000);
        thetaSnipper.setSelection((int) (seismicData.getTheta() * 10));
        /*
         * TODO: final Spinner depthSnipper = new Spinner(originGroup,
         * seismicData.getDepth());
         */

        /* Determine if the date and time are editable */
        azimuthalCoverageSnipper.setEnabled(IS_EDITABLE);
        numStationsSnipper.setEnabled(IS_EDITABLE);
        thetaSnipper.setEnabled(IS_EDITABLE);
    }

    /**
     * Initializes the magnitude data.
     *
     * @param originTimeGroup
     *            The origin group.
     */
    private void initializeMagnitudeGroup(Group magnitudeGroup,
            SeismicEventData seismicData) {
        if (seismicData == null) {
            return;
        }

        /* Display the magnitude */
        Label magnitudeLabel = new Label(magnitudeGroup, SWT.READ_ONLY);
        magnitudeLabel.setText("Magnitude:");
        final Spinner magnitudeSnipper = new Spinner(magnitudeGroup,
                (int) (seismicData.getPrefMagnitude() * 10));

        magnitudeSnipper.setDigits(1);
        magnitudeSnipper.setMinimum(0);
        magnitudeSnipper.setMaximum(1000);
        magnitudeSnipper
                .setSelection((int) (seismicData.getPrefMagnitude() * 10));

        /* Display the magnitude type menu */
        Label TypeLabel = new Label(magnitudeGroup, SWT.READ_ONLY);
        TypeLabel.setText("Type:");
        Combo typeCombo = new Combo(magnitudeGroup, SWT.READ_ONLY);

        if (seismicData.getPrefMagnitudeType() != null) {
            typeCombo.add(seismicData.getPrefMagnitudeType().toString());
        }

        typeCombo.select(0);

        /* Determine if the date and time are editable */
        magnitudeSnipper.setEnabled(IS_EDITABLE);
        typeCombo.setEnabled(IS_EDITABLE);

    }
}
