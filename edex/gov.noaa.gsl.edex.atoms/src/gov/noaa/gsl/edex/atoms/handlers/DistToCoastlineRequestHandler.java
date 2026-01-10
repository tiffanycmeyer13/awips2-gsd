/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.atoms.handlers;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atoms.request.DistToCoastlineRequest;
import gov.noaa.gsl.common.dataplugin.atoms.response.DistToCoastlineResponse;
import gov.noaa.gsl.edex.atoms.utilities.SeismicEventUtilities;

public class DistToCoastlineRequestHandler
        implements IRequestHandler<DistToCoastlineRequest> {

    @Override
    public Object handleRequest(DistToCoastlineRequest request)
            throws Exception {

        if (request == null) {
            return null;
        }

        float lon = request.getLongitude();
        float lat = request.getLatitude();

        Integer distance = SeismicEventUtilities.getDistanceToCoastline(lon,
                lat);

        DistToCoastlineResponse response = new DistToCoastlineResponse();
        response.setDistanceInKm(distance);

        return response;
    }

}
