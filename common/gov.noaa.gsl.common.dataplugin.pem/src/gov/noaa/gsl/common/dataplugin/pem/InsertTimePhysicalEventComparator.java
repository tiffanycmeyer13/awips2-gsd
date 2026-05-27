package gov.noaa.gsl.common.dataplugin.pem;

import java.util.Comparator;

public class InsertTimePhysicalEventComparator
        implements Comparator<PhysicalEvent> {

    @Override
    public int compare(PhysicalEvent arg0, PhysicalEvent arg1) {
        return arg0.getInsertTime().compareTo(arg1.getInsertTime());
    }

}
