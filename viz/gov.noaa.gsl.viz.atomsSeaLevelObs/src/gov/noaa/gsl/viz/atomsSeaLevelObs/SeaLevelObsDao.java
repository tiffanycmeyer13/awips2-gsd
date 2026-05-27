package gov.noaa.gsl.viz.atomsSeaLevelObs;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.List;

import com.raytheon.uf.viz.core.alerts.AlertMessage;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.requests.ThriftClient;
import com.raytheon.viz.alerts.IAlertObserver;
import com.raytheon.viz.alerts.observers.ProductAlertObserver;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.ISeaLevelObsDao;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObservations;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.request.SeaLevelObsRequest;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.response.SeaLevelObsResponse;

public class SeaLevelObsDao implements IAlertObserver, ISeaLevelObsDao {

    private static final String SLOBS_PLUGIN_ID = "atomsSeaLevelObs";

    private List<SeaLevelObsDaoListener> listeners = new ArrayList<>();

    private static SeaLevelObsDao instance = null;

    public static SeaLevelObsDao getInstance() {
        if (instance == null) {
            instance = new SeaLevelObsDao();
        }
        return instance;
    }

    private SeaLevelObsDao() {
        ProductAlertObserver.addObserver(SLOBS_PLUGIN_ID, this);
    }

    @Override
    public void alertArrived(Collection<AlertMessage> alertMessages) {
        /*
         * Go thru each AlertMessage, and fire notifications if the alert is of
         * the correct something or other
         */
        for (AlertMessage msg : alertMessages) {
            if (msg.decodedAlert != null) {
                String customId = msg.decodedAlert.get("phyEventCustomId")
                        .toString();
                fireSeaLevelObsChanged(customId);
            }
        }
    }

    @Override
    public List<SeaLevelObservations> getSeaLevelObservations(
            String customEventId, Date refTime) {
        List<SeaLevelObservations> result = new ArrayList<>();
        try {
            SeaLevelObsRequest request = new SeaLevelObsRequest();
            request.setPhysicalEventCustomId(customEventId);
            request.setRefTime(refTime);
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof SeaLevelObsResponse) {
                SeaLevelObsResponse slobsResponse = (SeaLevelObsResponse) response;
                result = slobsResponse.getSeaLevelObs();
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return result;
    }

    /*
     * =========================================================================
     * Listener methods
     * =========================================================================
     */

    public void addSeaLevelObsDaoListener(SeaLevelObsDaoListener lister) {
        if (lister == null) {
            return;
        }
        listeners.add(lister);
    }

    public boolean removeSeaLevelObsDaoListener(SeaLevelObsDaoListener lister) {
        if (lister == null) {
            return false;
        }
        return listeners.remove(lister);
    }

    public void clearSeaLevelObsDaoListeners() {
        listeners.clear();
    }

    protected void fireSeaLevelObsAdded(String phyEventCustomId) {
        if (phyEventCustomId == null) {
            return;
        }

        for (SeaLevelObsDaoListener lister : listeners) {
            lister.seaLevelObsAdded(phyEventCustomId);
        }
    }

    protected void fireSeaLevelObsRemoved(String phyEventCustomId) {
        if (phyEventCustomId == null) {
            return;
        }

        for (SeaLevelObsDaoListener lister : listeners) {
            lister.seaLevelObsRemoved(phyEventCustomId);
        }
    }

    protected void fireSeaLevelObsChanged(String phyEventCustomId) {
        if (phyEventCustomId == null) {
            return;
        }

        for (SeaLevelObsDaoListener lister : listeners) {
            lister.seaLevelObsChanged(phyEventCustomId);
        }
    }
}
