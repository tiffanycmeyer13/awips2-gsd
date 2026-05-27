package gov.noaa.gsl.edex.atomsSeaLevelObs.handlers;

import java.util.Date;
import java.util.List;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObservations;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.request.SeaLevelObsRequest;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.response.SeaLevelObsResponse;
import gov.noaa.gsl.edex.atomsSeaLevelObs.SeaLevelObsEdexDao;

public class SeaLevelObsRequestHandler
        implements IRequestHandler<SeaLevelObsRequest> {

    @Override
    public Object handleRequest(SeaLevelObsRequest request) throws Exception {

        SeaLevelObsResponse response = new SeaLevelObsResponse();
        if (request == null) {
            return response;
        }

        String customId = request.getPhysicalEventCustomId();
        Date refTime = request.getRefTime();

        SeaLevelObsEdexDao dao = new SeaLevelObsEdexDao(
                SeaLevelObservations.PLUGIN_NAME);

        List<SeaLevelObservations> slobs = dao.getSeaLevelObservations(customId,
                refTime);

        response.setSeaLevelObs(slobs);

        return response;
    }

}
