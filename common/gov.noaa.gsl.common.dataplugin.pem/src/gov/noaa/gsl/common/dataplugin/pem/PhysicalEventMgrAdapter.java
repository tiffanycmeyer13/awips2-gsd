package gov.noaa.gsl.common.dataplugin.pem;

import java.util.List;
import java.util.Set;

import com.raytheon.uf.common.time.TimeRange;

public class PhysicalEventMgrAdapter implements IPhysicalEventMgrListener {

    @Override
    public void physicalEventAdded(String id, PhysicalEventType type) {
        // TODO Auto-generated method stub

    }

    @Override
    public void physicalEventChanged(String id, PhysicalEventType type) {
        // TODO Auto-generated method stub

    }

    @Override
    public void physicalEventRemoved(String id, PhysicalEventType type) {
        // TODO Auto-generated method stub

    }

    @Override
    public void timeWindowChanged(TimeRange newTimeRange) {
        // TODO Auto-generated method stub

    }

    @Override
    public void activeOptionChanged(ActiveOption newActiveOpt) {
        // TODO Auto-generated method stub

    }

    @Override
    public void filtersChanged(List<PhysicalEventType> newFilters) {
        // TODO Auto-generated method stub

    }

    @Override
    public void selectionsChanged(Set<String> newSelections) {
        // TODO Auto-generated method stub

    }

}
