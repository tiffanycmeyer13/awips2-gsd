package gov.noaa.gsl.common.dataplugin.atomsForecast.response;

import java.util.HashMap;
import java.util.Map;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atomsForecast.PtwcWarningPoint;

@DynamicSerialize
public class WarningPointsResponse {

    @DynamicSerializeElement
    private Map<String, PtwcWarningPoint> warningPoints = new HashMap<>();

    public Map<String, PtwcWarningPoint> getWarningPoints() {
        return warningPoints;
    }

    public void setWarningPoints(Map<String, PtwcWarningPoint> wngPts) {
        if (wngPts == null) {
            wngPts = new HashMap<>();
        }
        this.warningPoints = wngPts;
    }
}
