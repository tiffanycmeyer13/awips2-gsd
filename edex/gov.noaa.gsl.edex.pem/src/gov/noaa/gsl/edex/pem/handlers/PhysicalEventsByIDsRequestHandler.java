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

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.common.dataplugin.pem.request.PhysicalEventsByIDsRequest;
import gov.noaa.gsl.common.dataplugin.pem.response.PhysicalEventsResponse;
import gov.noaa.gsl.edex.pem.PhysicalEventEdexDao;

/**
 * Self explanatory
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Dec 13, 2021        Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
public class PhysicalEventsByIDsRequestHandler
        implements IRequestHandler<PhysicalEventsByIDsRequest> {

    @Override
    public Object handleRequest(PhysicalEventsByIDsRequest request)
            throws Exception {

        PhysicalEventsResponse response = new PhysicalEventsResponse();
        if (request == null) {
            return response;
        }

        List<String> customIds = request.getCustomIds();
        PhysicalEventType type = request.getPhysicalEventType();

        if (customIds == null || customIds.isEmpty()) {
            return response;
        }

        /*
         * TODO Given the billions of different access / code patterns used by
         * EDEX coders, I have no idea what is the best way to do any of this.
         * So unfort I will make it up.
         */
        PhysicalEventEdexDao dao = new PhysicalEventEdexDao(
                PhysicalEvent.PLUGIN_NAME);
        List<IPhysicalEvent> events = dao.getPhysicalEvents(customIds, type,
                null);

        response.setPhysicalEvents(events);

        return response;
    }

}
