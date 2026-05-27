package gov.noaa.gsl.viz.atomsImagery;

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import com.raytheon.uf.viz.core.alerts.AlertMessage;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.requests.ThriftClient;
import com.raytheon.viz.alerts.IAlertObserver;
import com.raytheon.viz.alerts.observers.ProductAlertObserver;

import gov.noaa.gsl.common.dataplugin.atomsImagery.ITfsImageryDao;
import gov.noaa.gsl.common.dataplugin.atomsImagery.TfsImageryDescriptor;
import gov.noaa.gsl.common.dataplugin.atomsImagery.request.TfsImageryDescriptorsRequest;
import gov.noaa.gsl.common.dataplugin.atomsImagery.response.TfsImageryDescriptorsResponse;

// Stuff
public class TfsImageryDao implements IAlertObserver, ITfsImageryDao {

    private static final String ATOMS_IMAGERY_PLUGIN_ID = "atomsImagery";

    private static TfsImageryDao instance = null;

    public static TfsImageryDao getInstance() {
        if (instance == null) {
            instance = new TfsImageryDao();
        }
        return instance;
    }

    private List<TfsImageryDaoListener> listeners = new ArrayList<>();

    private TfsImageryDao() {
        ProductAlertObserver.addObserver(ATOMS_IMAGERY_PLUGIN_ID, this);
    }

    /*
     * =========================================================================
     * IAlertObserver methods
     * =========================================================================
     */

    /**
     * Called when EDEX gets new data, and hence a Notification of new/changed
     * server side data.
     */
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
                fireTfsImageryChanged(customId);
            }
        }
    }

    /*
     * =========================================================================
     * ITfsImageryDao methods
     * =========================================================================
     */
    @Override
    public List<TfsImageryDescriptor> getImageryDescriptors(String eventId) {
        List<TfsImageryDescriptor> result = new ArrayList<>();
        try {
            TfsImageryDescriptorsRequest request = new TfsImageryDescriptorsRequest();
            request.setPhysicalEventCustomId(eventId);
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof TfsImageryDescriptorsResponse) {
                TfsImageryDescriptorsResponse descsResponse = (TfsImageryDescriptorsResponse) response;
                result = descsResponse.getDescriptors();
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return result;
    }

    @Override
    public List<File> getImageryFiles(List<TfsImageryDescriptor> descs) {
        // TODO Auto-generated method stub
        return new ArrayList<>();
    }

    /*
     * =========================================================================
     * Listener methods
     * =========================================================================
     */

    public void addTfsImageryDaoListener(TfsImageryDaoListener lister) {
        if (lister == null) {
            return;
        }
        listeners.add(lister);
    }

    public boolean removeTfsImageryDaoListener(TfsImageryDaoListener lister) {
        if (lister == null) {
            return false;
        }
        return listeners.remove(lister);
    }

    public void clearTfsImageryDaoListeners() {
        listeners.clear();
    }

    protected void fireTfsImageryChanged(String phyEventCustomId) {
        if (phyEventCustomId == null) {
            return;
        }

        for (TfsImageryDaoListener lister : listeners) {
            lister.tfsImageryChanged(phyEventCustomId);
        }
    }

}
