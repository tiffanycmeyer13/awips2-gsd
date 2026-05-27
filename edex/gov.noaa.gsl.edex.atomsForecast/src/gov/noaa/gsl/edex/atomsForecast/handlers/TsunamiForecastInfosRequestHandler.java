package gov.noaa.gsl.edex.atomsForecast.handlers;

import java.util.List;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastInfo;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.TsunamiForecastInfosRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.TsunamiForecastInfosResponse;
import gov.noaa.gsl.edex.atomsForecast.TsunamiForecastEdexDao;

public class TsunamiForecastInfosRequestHandler
        implements IRequestHandler<TsunamiForecastInfosRequest> {

    @Override
    public Object handleRequest(TsunamiForecastInfosRequest request)
            throws Exception {
        TsunamiForecastInfosResponse response = new TsunamiForecastInfosResponse();
        if (request == null) {
            return response;
        }

        String customId = request.getPhysicalEventCustomId();

        TsunamiForecastEdexDao dao = new TsunamiForecastEdexDao(
                TsunamiForecast.PLUGIN_NAME);

        List<TsunamiForecastInfo> fcstInfos = dao
                .getTsunamiForecastInfos(customId);

        response.setFcstInfos(fcstInfos);

        return response;

    }

}
