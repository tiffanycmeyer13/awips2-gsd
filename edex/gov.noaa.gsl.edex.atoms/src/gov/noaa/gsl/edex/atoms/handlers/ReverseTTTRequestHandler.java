package gov.noaa.gsl.edex.atoms.handlers;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atoms.ReverseTTTRegion;
import gov.noaa.gsl.common.dataplugin.atoms.request.ReverseTTTRequest;
import gov.noaa.gsl.common.dataplugin.atoms.response.ReverseTTTResponse;
import gov.noaa.gsl.edex.atoms.utilities.ReverseTTTUtilities;

public class ReverseTTTRequestHandler
        implements IRequestHandler<ReverseTTTRequest> {

    @Override
    public Object handleRequest(ReverseTTTRequest request) throws Exception {

        if (request == null) {
            return null;
        }

        ReverseTTTResponse response = new ReverseTTTResponse();

        float lon = request.getLongitude();
        float lat = request.getLatitude();
        for (ReverseTTTRegion region : request.getRequestedRegions()) {
            float numHours = ReverseTTTUtilities.getTravelTime(lon, lat,
                    region);
            if (!Float.isNaN(numHours)) {
                response.setTravelTimeHours(region, numHours);
            }
        }

        return response;
    }
}
