package gov.noaa.gsl.viz.pem.dialog;

import java.util.Comparator;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

public class PEMColumnSpec {

    private String header = "";

    private int width;

    private ColumnStringBuilder stringBuilder;

    private Comparator<IPhysicalEvent> comparator;

    public PEMColumnSpec(String hdr, int width, ColumnStringBuilder thing,
            Comparator<IPhysicalEvent> comp) {
        this.header = hdr;
        this.width = width;
        this.stringBuilder = thing;
        this.comparator = comp;
    }

    public String getHeader() {
        return header;
    }

    public int getWidth() {
        return width;
    }

    public void setWidth(int newWidth) {
        this.width = newWidth;
    }

    public ColumnStringBuilder getStringBuilder() {
        return stringBuilder;
    }

    public Comparator<IPhysicalEvent> getComparator() {
        return comparator;
    }

    ////////////////////// ColumnStringBuilder ////////////////////////////////

    public interface ColumnStringBuilder {
        String run(IPhysicalEvent evt);
    }

}
