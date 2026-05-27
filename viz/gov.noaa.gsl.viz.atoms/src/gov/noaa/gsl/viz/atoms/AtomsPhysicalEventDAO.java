/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atoms;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import com.raytheon.uf.common.time.TimeRange;
import com.raytheon.uf.viz.core.alerts.AlertMessage;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.requests.ThriftClient;
import com.raytheon.viz.alerts.IAlertObserver;
import com.raytheon.viz.alerts.observers.ProductAlertObserver;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
import gov.noaa.gsl.common.dataplugin.pem.BasePhysicalEventDao;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEventDao;
import gov.noaa.gsl.common.dataplugin.pem.request.PhysicalEventIDsRequest;
import gov.noaa.gsl.common.dataplugin.pem.request.PhysicalEventsRequest;
import gov.noaa.gsl.common.dataplugin.pem.request.SavePhysicalEventRequest;
import gov.noaa.gsl.common.dataplugin.pem.response.PhysicalEventIDsResponse;
import gov.noaa.gsl.common.dataplugin.pem.response.PhysicalEventsResponse;
import gov.noaa.gsl.common.dataplugin.pem.response.SavePhysicalEventResponse;

public class AtomsPhysicalEventDAO extends BasePhysicalEventDao
        implements IPhysicalEventDao, IAlertObserver {

    private static final String PEM_PLUGIN_ID = "pem";

    public AtomsPhysicalEventDAO() {
        ProductAlertObserver.addObserver(PEM_PLUGIN_ID, this);
    }

    @Override
    public void savePhysicalEvent(IPhysicalEvent event) throws Exception {

        if (event == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + " savePhysicalEvent(e) received a null event.");
        }

        SavePhysicalEventRequest request = new SavePhysicalEventRequest();
        request.setPhysicalEvent(event);
        Object response = ThriftClient.sendRequest(request);
        if (response instanceof SavePhysicalEventResponse) {
            SavePhysicalEventResponse saveResponse = (SavePhysicalEventResponse) response;
            if (saveResponse.getError() != null) {
                throw new Exception(getClass().getName()
                        + " savePhysicalEvent(e) failed. Exception follows.",
                        saveResponse.getError());
            }
        }
    }

    @Override
    public List<String> getPhysicalEventIds() {

        return getPhysicalEventIds(ActiveOption.ACTIVE_ONLY);
    }

    @Override
    public List<String> getPhysicalEventIds(ActiveOption activeOption) {

        List<String> customIds = new ArrayList<>();
        try {
            PhysicalEventIDsRequest rqst = new PhysicalEventIDsRequest();
            rqst.setPhysicalEventType(getPhysicalEventType());
            rqst.setActiveOption(activeOption);
            rqst.setIsTestOnly(isTestMode());
            Object response = ThriftClient.sendRequest(rqst);
            if (response instanceof PhysicalEventIDsResponse) {
                PhysicalEventIDsResponse idsResponse = (PhysicalEventIDsResponse) response;
                customIds = idsResponse.getIds();
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return customIds;
    }

    @Override
    public IPhysicalEvent getPhysicalEvent(String customId) {

        if (customId == null || customId.isEmpty()) {
            return null;
        }

        List<String> customIds = new ArrayList<>();
        customIds.add(customId);
        List<IPhysicalEvent> events = getPhysicalEvents(customIds);
        if (events.size() != 1) {
            return null;
        }
        return events.get(0);
    }

    @Override
    public List<IPhysicalEvent> getPhysicalEvents(List<String> customIds) {

        return getPhysicalEvents(ActiveOption.ALL, null, customIds);
    }

    @Override
    public List<IPhysicalEvent> getPhysicalEvents(ActiveOption activeOption,
            TimeRange timeRange) {

        return getPhysicalEvents(activeOption, timeRange, null);
    }

    @Override
    public List<IPhysicalEvent> getPhysicalEvents(ActiveOption activeOption,
            TimeRange timeRange, List<String> customIds) {

        List<IPhysicalEvent> events = new ArrayList<>();
        try {
            PhysicalEventsRequest evtsRqst = new PhysicalEventsRequest();
            evtsRqst.setPhysicalEventType(getPhysicalEventType());
            evtsRqst.setActiveOption(activeOption);
            evtsRqst.setTimeRange(timeRange);
            evtsRqst.setCustomIds(customIds);
            evtsRqst.setIsTestOnly(isTestMode());
            Object response = ThriftClient.sendRequest(evtsRqst);
            if (response instanceof PhysicalEventsResponse) {
                PhysicalEventsResponse evtsResponse = (PhysicalEventsResponse) response;
                events = evtsResponse.getPhysicalEvents();
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return events;
    }

    @Override
    public void alertArrived(Collection<AlertMessage> alertMessages) {

        /*
         * Go thru each AlertMessage, and fire notifications if the alert is of
         * the correct PhysicalEventType
         */
        for (AlertMessage msg : alertMessages) {
            if (msg.decodedAlert != null
                    && msg.decodedAlert.containsKey("eventType")
                    && msg.decodedAlert.get("eventType")
                            .equals(getPhysicalEventType())) {
                String id = msg.decodedAlert.get("customId").toString();
                firePhysicalEventChanged(id);
            }
        }
    }
}
