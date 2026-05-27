package gov.noaa.gsl.viz.atoms.ui;

import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.pem.utils.PemUtils;
import gov.noaa.gsl.viz.pem.dialog.IPEMColumnSpecBuilder;
import gov.noaa.gsl.viz.pem.dialog.PEMColumnSpec;

public class SeismicDataColumnSpecBuilder implements IPEMColumnSpecBuilder {

    private static final String ERROR = "ERROR";

    private static DecimalFormat LAT_LON_FORMATTER = new DecimalFormat("0.00");

    private static DecimalFormat DEPTH_FORMATTER = new DecimalFormat("0.0");

    static {
        LAT_LON_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
        DEPTH_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }

    /*
     * COLUMN_HEADER, COLUMN_WIDTHS, and COLUMN_STRING_BUILDERS should all have
     * the same length. They are used in the ColumnSpec(ifications).
     */
    private final String[] COLUMN_HEADERS = { "ID", "Date", "Time (UTC)",
            "Magnitude", "Lon", "Lat", "Depth (mi/km)", "Km to Coast",
            "Source" };

    /*
     * COLUMN_HEADER, COLUMN_WIDTHS, and COLUMN_STRING_BUILDERS should all have
     * the same length. They are used in the ColumnSpec(ifications).
     */
    private final int[] COLUMN_WIDTHS = { 165, 100, 85, 100, 80, 80, 100, 120,
            65 };

    /*
     * COLUMN_HEADER, COLUMN_WIDTHS, and COLUMN_STRING_BUILDERS should all have
     * the same length. They are used in the ColumnSpec(ifications).
     *
     * Also, if our auto-code formatting was normal, the following would be
     * readable, ie an (e) per line would be nice.
     */
    private final PEMColumnSpec.ColumnStringBuilder[] COLUMN_STRING_BUILDERS = {
            (e) -> e.getCustomId(),
            (e) -> PemUtils.getDateFormatter().format(e.getRefTime()),
            (e) -> PemUtils.getHourMinuteFormatter().format(e.getRefTime()),
            new PEMColumnSpec.ColumnStringBuilder() {
                @Override
                public String run(IPhysicalEvent e) {
                    if (!(e.getData() instanceof SeismicEventData)) {
                        return ERROR;
                    } else {
                        SeismicEventData seismicData = (SeismicEventData) e
                                .getData();
                        return LAT_LON_FORMATTER
                                .format(seismicData.getPrefMagnitude());
                    }
                }
            },
            (e) -> (e.getLongitude() >= 0 ? " " : "")
                    + LAT_LON_FORMATTER.format(e.getLongitude()),
            (e) -> (e.getLatitude() >= 0 ? " " : "")
                    + LAT_LON_FORMATTER.format(e.getLatitude()),
            new PEMColumnSpec.ColumnStringBuilder() {
                @Override
                public String run(IPhysicalEvent e) {
                    if (!(e.getData() instanceof SeismicEventData)) {
                        return ERROR;
                    } else {
                        SeismicEventData seismicData = (SeismicEventData) e
                                .getData();
                        return DEPTH_FORMATTER.format(seismicData.getDepth())
                                + "/" + DEPTH_FORMATTER
                                        .format(seismicData.getDepthKm());
                    }
                }
            },
            (e) -> (e.getDistanceToCoastKm() >= 0 ? " " : "")
                    + DIST_FORMATTER.format(e.getDistanceToCoastKm()),
            new PEMColumnSpec.ColumnStringBuilder() {
                @Override
                public String run(IPhysicalEvent e) {
                    return e.getSource();
                }
            } };

    private final Comparator[] COLUMN_COMPARATORS = {
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getCustomId()
                    .compareTo(((IPhysicalEvent) e2).getCustomId()),
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getRefTime()
                    .compareTo(((IPhysicalEvent) e2).getRefTime()),
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getRefTime()
                    .compareTo(((IPhysicalEvent) e2).getRefTime()),
            new Comparator() {
                @Override
                public int compare(Object arg0, Object arg1) {
                    IPhysicalEvent e1 = (IPhysicalEvent) arg0;
                    IPhysicalEvent e2 = (IPhysicalEvent) arg1;
                    if (!(e1.getData() instanceof SeismicEventData)
                            || !(e2.getData() instanceof SeismicEventData)) {
                        return 0;
                    }

                    SeismicEventData d1 = (SeismicEventData) e1.getData();
                    SeismicEventData d2 = (SeismicEventData) e2.getData();

                    return Float.compare(d1.getPrefMagnitude(),
                            d2.getPrefMagnitude());
                }
            },
            (Object e1,
                    Object e2) -> (Float.compare(
                            ((IPhysicalEvent) e1).getLongitude(),
                            ((IPhysicalEvent) e2).getLongitude())),
            (Object e1,
                    Object e2) -> (Float.compare(
                            ((IPhysicalEvent) e1).getLatitude(),
                            ((IPhysicalEvent) e2).getLatitude())),
            new Comparator() {
                @Override
                public int compare(Object arg0, Object arg1) {
                    IPhysicalEvent e1 = (IPhysicalEvent) arg0;
                    IPhysicalEvent e2 = (IPhysicalEvent) arg1;
                    if (!(e1.getData() instanceof SeismicEventData)
                            || !(e2.getData() instanceof SeismicEventData)) {
                        return 0;
                    }

                    SeismicEventData d1 = (SeismicEventData) e1.getData();
                    SeismicEventData d2 = (SeismicEventData) e2.getData();

                    return Float.compare(d1.getDepth(), d2.getDepth());
                }
            },
            (Object e1,
                    Object e2) -> (Float.compare(
                            ((IPhysicalEvent) e1).getDistanceToCoastKm(),
                            ((IPhysicalEvent) e2).getDistanceToCoastKm())),
            (Object e1, Object e2) -> ((IPhysicalEvent) e1).getSource()
                    .compareTo(((IPhysicalEvent) e2).getSource()) };

    private List<PEMColumnSpec> columnSpecs = new ArrayList<>();

    public SeismicDataColumnSpecBuilder() {
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
        return PhysicalEventType.SEISMIC;
    }

}
