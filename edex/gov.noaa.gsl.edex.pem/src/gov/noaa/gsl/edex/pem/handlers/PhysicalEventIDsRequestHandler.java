/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.pem.handlers;

import java.util.List;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.common.dataplugin.pem.request.PhysicalEventIDsRequest;
import gov.noaa.gsl.common.dataplugin.pem.response.PhysicalEventIDsResponse;
import gov.noaa.gsl.edex.pem.PhysicalEventEdexDao;

public class PhysicalEventIDsRequestHandler
        implements IRequestHandler<PhysicalEventIDsRequest> {

    @Override
    public Object handleRequest(PhysicalEventIDsRequest request)
            throws Exception {

        if (request == null) {
            return null;
        }

        PhysicalEventType type = request.getPhysicalEventType();
        ActiveOption activeOption = request.getActiveOption();

        /*
         * TODO Given the billions of different access / code patterns used by
         * EDEX coders, I have no idea what is the best way to do any of this.
         * So unfort I will make it up.
         */
        PhysicalEventEdexDao dao = new PhysicalEventEdexDao(
                PhysicalEvent.PLUGIN_NAME);
        List<String> customIds = dao.getPhysicalEventIds(
                request.getPhysicalEventType(), activeOption,
                request.getIsTestOnly());

        PhysicalEventIDsResponse response = new PhysicalEventIDsResponse();
        response.setIds(customIds);

        return response;
    }

}
