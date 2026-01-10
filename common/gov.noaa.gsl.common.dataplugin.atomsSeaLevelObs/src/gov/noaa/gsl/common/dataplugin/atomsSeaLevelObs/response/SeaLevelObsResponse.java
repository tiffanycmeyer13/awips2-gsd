package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.response;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObservations;

@DynamicSerialize
public class SeaLevelObsResponse {

    @DynamicSerializeElement
    private List<SeaLevelObservations> seaLevelObs = new ArrayList<>();

    public SeaLevelObsResponse() {
    }

    public List<SeaLevelObservations> getSeaLevelObs() {
        return seaLevelObs;
    }

    public void setSeaLevelObs(List<SeaLevelObservations> seaLevelObs) {
        if (seaLevelObs == null) {
            seaLevelObs = new ArrayList<>();
        }
        this.seaLevelObs = seaLevelObs;
    }

}
