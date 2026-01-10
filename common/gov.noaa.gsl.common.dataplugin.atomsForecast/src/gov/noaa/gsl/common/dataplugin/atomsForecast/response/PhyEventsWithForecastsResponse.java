package gov.noaa.gsl.common.dataplugin.atomsForecast.response;

import java.util.HashSet;
import java.util.Set;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

@DynamicSerialize
public class PhyEventsWithForecastsResponse {

    @DynamicSerializeElement
    private Set<String> phyEventIDs = new HashSet<>();

    public PhyEventsWithForecastsResponse() {

    }

    public Set<String> getPhyEventIDs() {
        return phyEventIDs;
    }

    public void setPhyEventIDs(Set<String> ids) {
        if (ids == null) {
            ids = new HashSet<>();
        }
        this.phyEventIDs = ids;
    }

}
