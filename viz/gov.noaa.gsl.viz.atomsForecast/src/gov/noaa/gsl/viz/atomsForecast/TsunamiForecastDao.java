package gov.noaa.gsl.viz.atomsForecast;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.raytheon.uf.viz.core.alerts.AlertMessage;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.requests.ThriftClient;
import com.raytheon.viz.alerts.IAlertObserver;
import com.raytheon.viz.alerts.observers.ProductAlertObserver;

import gov.noaa.gsl.common.dataplugin.atomsForecast.ITsunamiForecastDao;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastInfo;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastType;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.MostRecentTsunamiForecastRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.PhyEventsWithForecastsRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.TsunamiForecastInfosRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.TsunamiForecastsRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.PhyEventsWithForecastsResponse;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.TsunamiForecastInfosResponse;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.TsunamiForecastsResponse;

public class TsunamiForecastDao implements IAlertObserver, ITsunamiForecastDao {

    private static final String ATOMS_FCST_PLUGIN_ID = "atomsForecast";

    private List<TsunamiForecastDaoListener> listeners = new ArrayList<>();

    private static TsunamiForecastDao instance = null;

    public static TsunamiForecastDao getInstance() {
        if (instance == null) {
            instance = new TsunamiForecastDao();
        }
        return instance;
    }

    private TsunamiForecastDao() {
        ProductAlertObserver.addObserver(ATOMS_FCST_PLUGIN_ID, this);
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
                fireTsunamiForecastChanged(customId);
            }
        }
    }

    /*
     * =========================================================================
     * ITsunamiForecastDao methods
     * =========================================================================
     */
    @Override
    public List<TsunamiForecastType> getForecastTypes(String customEvtId) {
        List<TsunamiForecastType> result = new ArrayList<>();
        try {
            TsunamiForecastInfosRequest request = new TsunamiForecastInfosRequest();
            request.setPhysicalEventCustomId(customEvtId);
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof TsunamiForecastInfosResponse) {
                TsunamiForecastInfosResponse fcstInfosResponse = (TsunamiForecastInfosResponse) response;
                List<TsunamiForecastInfo> fcstInfos = fcstInfosResponse
                        .getFcstInfos();
                result = TsunamiForecastInfo.getFcstTypes(fcstInfos);
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return result;
    }

    @Override
    public List<Date> getForecastRunTimes(String customEvtId,
            TsunamiForecastType type) {
        List<Date> result = new ArrayList<>();
        try {
            TsunamiForecastInfosRequest request = new TsunamiForecastInfosRequest();
            request.setPhysicalEventCustomId(customEvtId);
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof TsunamiForecastInfosResponse) {
                TsunamiForecastInfosResponse infosResponse = (TsunamiForecastInfosResponse) response;
                List<TsunamiForecastInfo> fcstInfos = infosResponse
                        .getFcstInfos();
                result = TsunamiForecastInfo.getFcstRunTimes(fcstInfos, type);
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return result;
    }

    @Override
    public TsunamiForecast getTsunamiForecast(TsunamiForecastInfo info) {
        if (info == null) {
            return null;
        }
        List<TsunamiForecast> fcsts = getTsunamiForecasts(
                info.getPhysicalEventCustomId(), info.getForecastType(),
                info.getRunTime());

        if (fcsts.size() == 0) {
            return null;
        }

        if (fcsts.size() == 1) {
            return fcsts.get(0);
        } else {
            throw new IllegalStateException(getClass().getName()
                    + " getTsunamiForecast(TsunamiForecastInfo info) retrieved greater than ONE forecast!");
        }
    }

    @Override
    public List<TsunamiForecast> getTsunamiForecasts(
            String physicalEventCustomId) {

        return getTsunamiForecasts(physicalEventCustomId, null, null);
    }

    @Override
    public List<TsunamiForecast> getTsunamiForecasts(String customEventId,
            TsunamiForecastType type) {

        return getTsunamiForecasts(customEventId, type, null);
    }

    @Override
    public List<TsunamiForecast> getTsunamiForecasts(String customEventId,
            TsunamiForecastType type, Date refTime) {
        List<TsunamiForecast> result = new ArrayList<>();
        try {
            TsunamiForecastsRequest request = new TsunamiForecastsRequest();
            request.setPhysicalEventCustomId(customEventId);
            if (type != null) {
                request.setFcstType(type);
            }
            if (refTime != null) {
                request.setFcstRunTime(refTime);
            }
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof TsunamiForecastsResponse) {
                TsunamiForecastsResponse fcstRunsResponse = (TsunamiForecastsResponse) response;
                result = fcstRunsResponse.getFcsts();
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return result;
    }

    @Override
    public List<TsunamiForecast> getMostRecentTsunamiForecast(
            String customEventId) {

        return getMostRecentTsunamiForecast(customEventId, null);
    }

    @Override
    public List<TsunamiForecast> getMostRecentTsunamiForecast(
            String customEventId, TsunamiForecastType type) {
        List<TsunamiForecast> result = new ArrayList<>();
        try {
            MostRecentTsunamiForecastRequest request = new MostRecentTsunamiForecastRequest();
            request.setPhysicalEventCustomId(customEventId);
            request.setTsunamiForecastType(type);
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof TsunamiForecastsResponse) {
                TsunamiForecastsResponse fcstRunsResponse = (TsunamiForecastsResponse) response;
                result = fcstRunsResponse.getFcsts();
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return result;

    }

    @Override
    public List<TsunamiForecastInfo> getTsunamiForecastInfos(
            String customEventId) {
        List<TsunamiForecastInfo> result = new ArrayList<>();
        try {
            TsunamiForecastInfosRequest request = new TsunamiForecastInfosRequest();
            request.setPhysicalEventCustomId(customEventId);
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof TsunamiForecastInfosResponse) {
                TsunamiForecastInfosResponse infosResponse = (TsunamiForecastInfosResponse) response;
                result = infosResponse.getFcstInfos();
            }
        } catch (VizException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        return result;
    }

    @Override
    public Set<String> getPhyEventIDsWithForecasts() {
        Set<String> result = new HashSet<>();
        try {
            PhyEventsWithForecastsRequest request = new PhyEventsWithForecastsRequest();
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof PhyEventsWithForecastsResponse) {
                PhyEventsWithForecastsResponse infosResponse = (PhyEventsWithForecastsResponse) response;
                result = infosResponse.getPhyEventIDs();
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

    public void addTsunamiForecastDaoListener(
            TsunamiForecastDaoListener lister) {
        if (lister == null) {
            return;
        }
        listeners.add(lister);
    }

    public boolean removeTsunamiForecastDaoListener(
            TsunamiForecastDaoListener lister) {
        if (lister == null) {
            return false;
        }
        return listeners.remove(lister);
    }

    public void clearTsunamiForecastDaoListeners() {
        listeners.clear();
    }

    protected void fireTsunamiForecastAdded(String phyEventCustomId) {
        if (phyEventCustomId == null) {
            return;
        }

        for (TsunamiForecastDaoListener lister : listeners) {
            lister.tsunamiForecastAdded(phyEventCustomId);
        }
    }

    protected void fireTsunamiForecastRemoved(String phyEventCustomId) {
        if (phyEventCustomId == null) {
            return;
        }

        for (TsunamiForecastDaoListener lister : listeners) {
            lister.tsunamiForecastRemoved(phyEventCustomId);
        }
    }

    protected void fireTsunamiForecastChanged(String phyEventCustomId) {
        if (phyEventCustomId == null) {
            return;
        }

        for (TsunamiForecastDaoListener lister : listeners) {
            lister.tsunamiForecastChanged(phyEventCustomId);
        }
    }
}
