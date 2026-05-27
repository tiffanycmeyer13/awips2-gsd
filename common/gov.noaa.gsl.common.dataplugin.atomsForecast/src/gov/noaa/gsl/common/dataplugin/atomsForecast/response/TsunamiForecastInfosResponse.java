package gov.noaa.gsl.common.dataplugin.atomsForecast.response;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastInfo;

@DynamicSerialize
public class TsunamiForecastInfosResponse {

    @DynamicSerializeElement
    private List<TsunamiForecastInfo> fcstInfos = new ArrayList<>();

    public TsunamiForecastInfosResponse() {

    }

    public List<TsunamiForecastInfo> getFcstInfos() {
        return fcstInfos;
    }

    public void setFcstInfos(List<TsunamiForecastInfo> fcstInfos) {
        if (fcstInfos == null) {
            fcstInfos = new ArrayList<>();
        }
        this.fcstInfos = fcstInfos;
    }

}
