package gov.noaa.gsl.edex.atomsForecast.handlers;

import java.util.List;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastType;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.MostRecentTsunamiForecastRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.TsunamiForecastsResponse;
import gov.noaa.gsl.edex.atomsForecast.TsunamiForecastEdexDao;

public class MostRecentTsunamiForecastRequestHandler
        implements IRequestHandler<MostRecentTsunamiForecastRequest> {

    @Override
    public Object handleRequest(MostRecentTsunamiForecastRequest request)
            throws Exception {
        TsunamiForecastsResponse response = new TsunamiForecastsResponse();
        if (request == null) {
            return response;
        }

        String customId = request.getPhysicalEventCustomId();
        TsunamiForecastType type = request.getTsunamiForecastType();

        TsunamiForecastEdexDao dao = new TsunamiForecastEdexDao(
                TsunamiForecast.PLUGIN_NAME);

        List<TsunamiForecast> fcsts = dao.getMostRecentTsunamiForecast(customId,
                type);

        response.setFcsts(fcsts);

        return response;

    }

}
