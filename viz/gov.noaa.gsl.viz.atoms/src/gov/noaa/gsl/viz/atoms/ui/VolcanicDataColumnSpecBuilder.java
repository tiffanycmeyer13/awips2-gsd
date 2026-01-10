package gov.noaa.gsl.viz.atoms.ui;

import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.pem.utils.PemUtils;
import gov.noaa.gsl.viz.pem.dialog.IPEMColumnSpecBuilder;
import gov.noaa.gsl.viz.pem.dialog.PEMColumnSpec;

public class VolcanicDataColumnSpecBuilder implements IPEMColumnSpecBuilder {

    private static final String ERROR = "ERROR";

    private static DecimalFormat LAT_LON_FORMATTER = new DecimalFormat("0.00");

    static {
        LAT_LON_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    /*
     * COLUMN_HEADER, COLUMN_WIDTHS, and COLUMN_STRING_BUILDERS should all have
     * the same length. They are used in the ColumnSpec(ifications).
     */
    private final String[] COLUMN_HEADERS = { "ID", "Name", "Date",
            "Time (UTC)", "Lon", "Lat", "Km to Coast", "Known", "Source" };

    /*
     * COLUMN_HEADER, COLUMN_WIDTHS, and COLUMN_STRING_BUILDERS should all have
     * the same length. They are used in the ColumnSpec(ifications).
     */
    private final int[] COLUMN_WIDTHS = { 160, 120, 95, 83, 80, 80, 120, 55,
            65 };

    /*
     * COLUMN_HEADER, COLUMN_WIDTHS, and COLUMN_STRING_BUILDERS should all have
     * the same length. They are used in the ColumnSpec(ifications).
     *
     * Also, if our auto-code formatting was normal, the following would be
     * readable, ie an (e) per line would be nice.
     */
    private final PEMColumnSpec.ColumnStringBuilder[] COLUMN_STRING_BUILDERS = {
            (e) -> e.getCustomId(), (e) -> e.getName(),
            (e) -> PemUtils.getDateFormatter().format(e.getRefTime()),
            (e) -> PemUtils.getHourMinuteFormatter().format(e.getRefTime()),
            (e) -> (e.getLongitude() >= 0 ? " " : "")
                    + LAT_LON_FORMATTER.format(e.getLongitude()),
            (e) -> (e.getLatitude() >= 0 ? " " : "")
                    + LAT_LON_FORMATTER.format(e.getLatitude()),
            (e) -> (e.getDistanceToCoastKm() >= 0 ? " " : "")
                    + DIST_FORMATTER.format(e.getDistanceToCoastKm()),
            new PEMColumnSpec.ColumnStringBuilder() {
                @Override
                public String run(IPhysicalEvent e) {
                    if (e.getIsKnownEvent()) {
                        return "Y";
                    } else {
                        return "N";
                    }
                }
            }, new PEMColumnSpec.ColumnStringBuilder() {
                @Override
                public String run(IPhysicalEvent e) {
                    return e.getSource();
                }
            } };

    private final Comparator[] COLUMN_COMPARATORS = {
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getCustomId()
                    .compareTo(((IPhysicalEvent) e2).getCustomId()),
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getName()
                    .compareTo(((IPhysicalEvent) e2).getName()),
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getRefTime()
                    .compareTo(((IPhysicalEvent) e2).getRefTime()),
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getRefTime()
                    .compareTo(((IPhysicalEvent) e2).getRefTime()),
            (Object e1,
                    Object e2) -> (Float.compare(
                            ((IPhysicalEvent) e1).getLongitude(),
                            ((IPhysicalEvent) e2).getLongitude())),
            (Object e1,
                    Object e2) -> (Float.compare(
                            ((IPhysicalEvent) e1).getLatitude(),
                            ((IPhysicalEvent) e2).getLatitude())),
            (Object e1,
                    Object e2) -> (Float.compare(
                            ((IPhysicalEvent) e1).getDistanceToCoastKm(),
                            ((IPhysicalEvent) e2).getDistanceToCoastKm())),
            (Object e1,
                    Object e2) -> (Boolean.compare(
                            ((IPhysicalEvent) e1).getIsKnownEvent(),
                            ((IPhysicalEvent) e2).getIsKnownEvent())),
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getSource()
                    .compareTo(((IPhysicalEvent) e2).getSource()) };

    private List<PEMColumnSpec> columnSpecs = new ArrayList<>();

    public VolcanicDataColumnSpecBuilder() {
        /*
         * The event table column specs, including header, width, and lambda to
         * use to get the string for the value of the cell.
         */
        for (int i = 0; i < COLUMN_HEADERS.length; i++) {
            PEMColumnSpec spec = new PEMColumnSpec(COLUMN_HEADERS[i],
                    COLUMN_WIDTHS[i], COLUMN_STRING_BUILDERS[i],
                    COLUMN_COMPARATORS[i]);
            columnSpecs.add(spec);
        }
    }

    @Override
    public List<PEMColumnSpec> getColumnSpecs() {
        return columnSpecs;
    }

    @Override
    public int getNumColumns() {
        return columnSpecs.size();
    }

    @Override
    public PEMColumnSpec getColumnSpec(int colIndex) {
        if (colIndex < 0 || colIndex >= columnSpecs.size()) {
            return null;
        }

        return columnSpecs.get(colIndex);
    }

    @Override
    public PhysicalEventType getPhysicalEventType() {
        return PhysicalEventType.VOLCANIC;
    }

}
