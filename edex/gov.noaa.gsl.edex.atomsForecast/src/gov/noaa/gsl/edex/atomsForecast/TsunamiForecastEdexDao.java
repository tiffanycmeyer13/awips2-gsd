/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.atomsForecast;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.hibernate.Session;
import org.hibernate.Transaction;
import org.hibernate.exception.ConstraintViolationException;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.PluginException;
import com.raytheon.uf.common.dataplugin.persist.IPersistable;
import com.raytheon.uf.common.datastorage.IDataStore;
import com.raytheon.uf.edex.database.plugin.PluginDao;
import com.raytheon.uf.edex.database.query.DatabaseQuery;

import gov.noaa.gsl.common.dataplugin.atomsForecast.ForecastStation;
import gov.noaa.gsl.common.dataplugin.atomsForecast.ITsunamiForecastDao;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastInfo;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastType;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiStationForecast;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import jakarta.persistence.PersistenceException;

/**
 *
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
public class TsunamiForecastEdexDao extends PluginDao
        implements ITsunamiForecastDao {

    public TsunamiForecastEdexDao(String pluginName) throws PluginException {
        super(pluginName);
        logger.info("TsunamiForecastEdexDao is being created.");
    }

    @Override
    protected boolean populateDataStore(IDataStore dataStore, IPersistable obj)
            throws Exception {
        return false;
    }

    @Override
    public PluginDataObject[] persistToDatabase(PluginDataObject... records) {
        if (records == null || records.length == 0) {
            return records;
        }
        List<PluginDataObject> pdos = Arrays.asList(records);
        List<PluginDataObject> persisted = new ArrayList<>(records.length);

        Session session = null;
        try {
            session = getSession();
            for (int i = 0; i < pdos.size(); i++) {
                Transaction tx = null;
                TsunamiForecast decodedPDO = null;
                try {
                    decodedPDO = (TsunamiForecast) pdos.get(i);
                    TsunamiForecast pdoToSave = null;
                    TsunamiForecast existingPDO = null;
                    Collection<TsunamiStationForecast> existingStationFcsts = null;

                    /*
                     * Verify the PhysicalEvent exists. TODO Hardcoding property
                     * names for the query is bad!
                     */
                    DatabaseQuery query = new DatabaseQuery(
                            PhysicalEvent.class);
                    // query.addQueryParam("source",
                    // decodedPDO.getPhyEventSource());
                    query.addQueryParam("customId",
                            decodedPDO.getPhyEventCustomId());
                    List<PluginDataObject> existingEvents = (List<PluginDataObject>) super.queryByCriteria(
                            query);
                    if (existingEvents == null || existingEvents.size() != 1) {
                        // TODO Somehow move XML file to rejected directory
                        logger.error(getClass().getName()
                                + " could not find a PhysicalEvent customId = "
                                + decodedPDO.getPhyEventCustomId()
                                + ". Ignoring decoding and persisting. Fix the XML.");
                        return new PluginDataObject[] {};
                    }

                    /*
                     * Verify the Station. Throw out bad ones, and log em.
                     */
                    Iterator<TsunamiStationForecast> stnFcstIter = decodedPDO
                            .getStationFcsts().iterator();
                    while (stnFcstIter.hasNext()) {
                        TsunamiStationForecast decodedStationFcst = stnFcstIter
                                .next();
                        String decodedStnId = decodedStationFcst.getStation()
                                .getCustomId();
                        /*
                         * TODO Hardcoding property names for the query is bad!
                         */
                        query = new DatabaseQuery(ForecastStation.class);
                        query.addQueryParam("customId", decodedStnId);
                        List<ForecastStation> existingStations = (List<ForecastStation>) super.queryByCriteria(
                                query);
                        if (existingStations == null
                                || existingStations.size() != 1) {
                            logger.error(getClass().getName()
                                    + ": For PhyEventId = "
                                    + decodedPDO.getPhyEventCustomId()
                                    + ", could not find a Station with customId = "
                                    + decodedStnId
                                    + ". Skipping decoding of this single TsunamiStationForecast. Fix the XML or database.");
                            decodedPDO.removeStationFcst(decodedStnId);
                        } else {
                            /*
                             * We need to set the database's station on the
                             * fcst, otherwise it's transient
                             */
                            ForecastStation dbStation = existingStations.get(0);
                            decodedStationFcst.setStation(dbStation);
                        }
                    }

                    /*
                     * Query for an already-existing TsunamiForecast in the DB.
                     *
                     * TODO Hardcoding property names for the query is bad!
                     */
                    query = new DatabaseQuery(TsunamiForecast.class);
                    // query.addQueryParam("phyEventSource",
                    // decodedPDO.getPhyEventSource());
                    query.addQueryParam("phyEventCustomId",
                            decodedPDO.getPhyEventCustomId());
                    query.addQueryParam("dataTime.refTime",
                            decodedPDO.getDataTime().getRefTime());
                    query.addQueryParam("fcstType", decodedPDO.getFcstType());
                    List<PluginDataObject> existingRuns = (List<PluginDataObject>) super.queryByCriteria(
                            query);

                    /*
                     * If we already have this TsunamiForecast in the database,
                     * then update it's properties
                     */
                    if (existingRuns.size() == 1) {
                        existingPDO = (TsunamiForecast) existingRuns.get(0);
                        existingPDO.setDataTime(decodedPDO.getDataTime());
                        existingStationFcsts = existingPDO.getStationFcsts();
                        existingPDO
                                .setStationFcsts(decodedPDO.getStationFcsts());
                        existingPDO.setDescription(decodedPDO.getDescription());
                        pdoToSave = existingPDO;
                    }
                    /*
                     * Otherwise it's a brand new TsunamiForecast and nothing to
                     * update
                     */
                    else if (existingRuns.size() == 0) {
                        pdoToSave = decodedPDO;
                    }
                    /*
                     * More than one is an error
                     */
                    else {
                        throw new Exception(
                                "TsunamiForecastEdexDao found MORE THAN ONE (BAD!!!) existing TsunamiForecasts with phyEventId = "
                                        + decodedPDO.getPhyEventCustomId()
                                        + ", reftime = "
                                        + decodedPDO.getDataTime().getRefTime()
                                        + ", fcst_type = "
                                        + decodedPDO.getFcstType());
                    }

                    tx = session.beginTransaction();
                    if (existingStationFcsts != null) {
                        for (TsunamiStationForecast oldStnFcst : existingStationFcsts) {
                            session.delete(oldStnFcst);
                        }
                    }
                    session.saveOrUpdate(pdoToSave);
                    session.flush();
                    tx.commit();
                    persisted.add(pdoToSave);
                } catch (PersistenceException e) {
                    if (e.getCause() instanceof ConstraintViolationException) {
                        tx.rollback();
                        session.clear();
                    } else {
                        throw e;
                    }
                } catch (Exception e) {
                    tx.rollback();
                    logger.error("Query failed: Unable to insert or update "
                            + decodedPDO.getIdentifier(), e);
                }
            }

        } finally {
            if (session != null) {
                session.close();
            }
        }

        return persisted.toArray(new PluginDataObject[persisted.size()]);
    }

    @Override
    public List<TsunamiForecastType> getForecastTypes(String customEvtId) {

        List<TsunamiForecastType> types = new ArrayList<>();
        if (customEvtId == null || customEvtId.isEmpty()) {
            return types;
        }

        String sql = "SELECT DISTINCT fcst_type FROM tsunami_fcst"
                + " WHERE phy_event_custom_id = :phy_event_custom_id";
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("phy_event_custom_id", customEvtId);

        try {
            Object[] qResult = executeSQLQuery(sql, paramMap);

            for (Object o : qResult) {
                types.add(TsunamiForecastType.valueOf((String) o));
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getForecastTypes(...) failed, due to: "
                    + e.getMessage(), e);
        }
        return types;
    }

    @Override
    public List<Date> getForecastRunTimes(String customEventId,
            TsunamiForecastType type) {

        List<Date> refTimes = new ArrayList<>();
        if (customEventId == null || customEventId.isEmpty()) {
            return refTimes;
        }

        StringBuilder sqlStringBuffer = new StringBuilder(
                "SELECT DISTINCT refTime FROM tsunami_fcst"
                        + " WHERE phy_event_custom_id = :phy_event_custom_id");

        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("phy_event_custom_id", customEventId);

        if (type != null) {
            sqlStringBuffer.append(" AND fcst_type = :fcst_type");
            if (type != null) {
                paramMap.put("fcst_type", type);
            }
        }

        try {
            Object[] qResult = executeSQLQuery(sqlStringBuffer.toString(),
                    paramMap);

            for (Object o : qResult) {
                refTimes.add((Date) o);
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getForecastRunTimes(id, type) failed, due to: "
                    + e.getMessage(), e);
        }
        return refTimes;
    }

    @Override
    public List<TsunamiForecast> getMostRecentTsunamiForecast(
            String customEventId) {

        return getMostRecentTsunamiForecast(customEventId, null);
    }

    @Override
    public List<TsunamiForecast> getMostRecentTsunamiForecast(
            String customEventId, TsunamiForecastType type) {

        List<TsunamiForecast> fcstResults = new ArrayList<>();

        if (customEventId == null || customEventId.isEmpty()) {
            return fcstResults;
        }

        List<String> fields = new ArrayList<>();
        List<Object> values = new ArrayList<>();
        List<String> operands = new ArrayList<>();

        // where customId = customId
        fields.add("phyEventCustomId");
        values.add(customEventId);
        operands.add("=");

        if (type != null) {
            fields.add("fcstType");
            values.add(type);
            operands.add("=");
        }

        try {
            // OrderBy refTime. TODO I think this is very very expensive. We
            // should figure out how to get the most recent via SQL. Look at
            // this for a decent looking example:
            // https://stackoverflow.com/questions/8523374/get-most-recent-row-for-given-id
            List<?> questionableResults = queryByCriteria(fields, values,
                    operands, "dataTime.refTime", false);

            if (questionableResults.size() == 0) {
                return fcstResults;
            }

            TsunamiForecast bestFcst = (TsunamiForecast) questionableResults
                    .get(0);
            fcstResults.add(bestFcst);

            // Unlikely, but we might have more than one forecast for the same
            // refTime but different forecast type. Remember the
            // questionableResults are already ordered descending by refTime
            long bestRefTimeMillis = bestFcst.getDataTime().getRefTime()
                    .getTime();

            for (int index = 1; index < questionableResults.size(); index++) {
                TsunamiForecast nextFcst = (TsunamiForecast) questionableResults
                        .get(index);
                if (nextFcst.getDataTime().getRefTime()
                        .getTime() == bestRefTimeMillis) {
                    fcstResults.add(nextFcst);
                } else {
                    break;
                }
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getMostRecentTsunamiForecast(...) failed, due to: "
                    + e.getMessage(), e);
        }
        return fcstResults;
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
    public List<TsunamiForecast> getTsunamiForecasts(String customEventId,
            TsunamiForecastType type, Date refTime) {

        List<TsunamiForecast> fcstResults = new ArrayList<>();

        if (customEventId == null || customEventId.isEmpty()) {
            return fcstResults;
        }

        List<String> fields = new ArrayList<>();
        List<Object> values = new ArrayList<>();
        List<String> operands = new ArrayList<>();

        // where phyEventCustomId = phyEventCustomId
        fields.add("phyEventCustomId");
        values.add(customEventId);
        operands.add("=");

        if (type != null) {
            fields.add("fcstType");
            values.add(type);
            operands.add("=");
        }

        if (refTime != null) {
            fields.add("dataTime.refTime");
            values.add(refTime);
            operands.add("=");
        }
        try {
            List<?> questionableResults = queryByCriteria(fields, values,
                    operands);

            if (questionableResults.size() == 0) {
                return fcstResults;
            }

            for (Object o : questionableResults) {
                fcstResults.add((TsunamiForecast) o);
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getTsunamiForecasts(...) failed, due to: "
                    + e.getMessage(), e);
        }
        return fcstResults;
    }

    @Override
    public List<TsunamiForecast> getTsunamiForecasts(String customEventId,
            TsunamiForecastType type) {
        return getTsunamiForecasts(customEventId, type, null);
    }

    @Override
    public List<TsunamiForecast> getTsunamiForecasts(String customEventId) {
        return getTsunamiForecasts(customEventId, null, null);
    }

    @Override
    public List<TsunamiForecastInfo> getTsunamiForecastInfos(
            String customEventId) {

        List<TsunamiForecastInfo> infos = new ArrayList<>();
        if (customEventId == null || customEventId.isEmpty()) {
            return infos;
        }

        String sql = "SELECT fcst_type, reftime FROM tsunami_fcst"
                + " WHERE phy_event_custom_id = :phy_event_custom_id";
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("phy_event_custom_id", customEventId);

        try {
            Object[] qResult = executeSQLQuery(sql, paramMap);

            for (Object o : qResult) {
                Object[] row = (Object[]) o;
                TsunamiForecastType type = TsunamiForecastType
                        .valueOf(row[0].toString());
                Date refTime = (Date) row[1];
                infos.add(
                        new TsunamiForecastInfo(customEventId, type, refTime));
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getTsunamiForecastInfos(...) failed, due to: "
                    + e.getMessage(), e);
        }
        return infos;
    }

    @Override
    public Set<String> getPhyEventIDsWithForecasts() {
        String sql = "SELECT distinct phy_event_custom_id FROM tsunami_fcst";
        Set<String> ids = new HashSet<>();
        try {
            Object[] qResult = executeSQLQuery(sql);

            for (Object o : qResult) {
                Object[] row = (Object[]) o;
                ids.add(row.toString());
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getPhyEventIDsWithForecasts(...) failed, due to: "
                    + e.getMessage(), e);
        }
        return ids;
    }
}
