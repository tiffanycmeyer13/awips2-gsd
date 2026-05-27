package gov.noaa.gsl.viz.pem.dialog;

import java.text.DecimalFormat;
import java.util.List;

import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;

public interface IPEMColumnSpecBuilder {

    static DecimalFormat DIST_FORMATTER = new DecimalFormat("#####.#");

    public List<PEMColumnSpec> getColumnSpecs();

    public int getNumColumns();

    public PEMColumnSpec getColumnSpec(int colIndex);

    /*
     * What will we do for ALL? Return null for ALL? yes.
     */
    public PhysicalEventType getPhysicalEventType();
}
