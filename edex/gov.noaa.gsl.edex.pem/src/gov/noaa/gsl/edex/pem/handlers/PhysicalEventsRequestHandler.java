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
import com.raytheon.uf.common.time.TimeRange;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.common.dataplugin.pem.request.PhysicalEventsRequest;
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
public class PhysicalEventsRequestHandler
        implements IRequestHandler<PhysicalEventsRequest> {

    @Override
    public Object handleRequest(PhysicalEventsRequest request)
            throws Exception {

        PhysicalEventsResponse response = new PhysicalEventsResponse();
        if (request == null) {
            return response;
        }

        List<String> customIds = request.getCustomIds();
        PhysicalEventType type = request.getPhysicalEventType();
        TimeRange timeRange = request.getTimeRange();
        ActiveOption activeOption = request.getActiveOption();

        /*
         * TODO Given the billions of different access / code patterns used by
         * EDEX coders, I have no idea what is the best way to do any of this.
         * So unfort I will make it up.
         */
        PhysicalEventEdexDao dao = new PhysicalEventEdexDao(
                PhysicalEvent.PLUGIN_NAME);
        List<IPhysicalEvent> events = dao.getPhysicalEvents(type, activeOption,
                timeRange, customIds, request.getIsTestOnly());

        response.setPhysicalEvents(events);

        return response;
    }

}
