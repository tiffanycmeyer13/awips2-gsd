package gov.noaa.gsl.edex.atomsForecast.handlers;

import java.util.Map;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atomsForecast.PtwcWarningPoint;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.WarningPointsRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.WarningPointsResponse;
import gov.noaa.gsl.edex.atomsForecast.utilities.WarningPointsRetriever;

public class WarningPointsRequestHandler
        implements IRequestHandler<WarningPointsRequest> {

    @Override
    public Object handleRequest(WarningPointsRequest request) throws Exception {
        WarningPointsResponse response = new WarningPointsResponse();
        if (request == null) {
            return response;
        }

        WarningPointsRetriever retriever = new WarningPointsRetriever();
        Map<String, PtwcWarningPoint> wngPts = retriever.getPtwcWarningPoints();
        response.setWarningPoints(wngPts);

        return response;

    }

}
