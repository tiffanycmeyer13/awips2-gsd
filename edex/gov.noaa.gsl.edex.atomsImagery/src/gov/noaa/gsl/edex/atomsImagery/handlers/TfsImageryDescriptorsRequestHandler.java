package gov.noaa.gsl.edex.atomsImagery.handlers;

import java.util.List;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atomsImagery.TfsImageryDescriptor;
import gov.noaa.gsl.common.dataplugin.atomsImagery.request.TfsImageryDescriptorsRequest;
import gov.noaa.gsl.common.dataplugin.atomsImagery.response.TfsImageryDescriptorsResponse;
import gov.noaa.gsl.edex.atomsImagery.TfsImageryEdexDao;

public class TfsImageryDescriptorsRequestHandler
        implements IRequestHandler<TfsImageryDescriptorsRequest> {

    @Override
    public Object handleRequest(TfsImageryDescriptorsRequest request)
            throws Exception {
        TfsImageryDescriptorsResponse response = new TfsImageryDescriptorsResponse();
        if (request == null) {
            return response;
        }

        String customId = request.getPhysicalEventCustomId();

        TfsImageryEdexDao dao = new TfsImageryEdexDao(
                TfsImageryDescriptor.PLUGIN_NAME);

        List<TfsImageryDescriptor> descs = dao.getImageryDescriptors(customId);

        response.setDescriptors(descs);

        return response;

    }

}
