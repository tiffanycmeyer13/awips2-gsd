/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.pem;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.hibernate.Session;
import org.hibernate.Transaction;
import org.hibernate.exception.ConstraintViolationException;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.PluginException;
import com.raytheon.uf.common.dataplugin.persist.IPersistable;
import com.raytheon.uf.common.dataquery.db.OrderField.ResultOrder;
import com.raytheon.uf.common.dataquery.db.QueryParam.QueryOperand;
import com.raytheon.uf.common.datastorage.IDataStore;
import com.raytheon.uf.common.time.TimeRange;
import com.raytheon.uf.common.time.util.TimeUtil;
import com.raytheon.uf.edex.database.plugin.PluginDao;
import com.raytheon.uf.edex.database.query.DatabaseQuery;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.InsertTimePhysicalEventComparator;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import jakarta.persistence.PersistenceException;

public class PhysicalEventEdexDao extends PluginDao {

    /**
     * Creates a new PhysicalEventEdexDao
     *
     * @throws PluginException
     */
    public PhysicalEventEdexDao(String pluginName) throws PluginException {
        super(pluginName);
        logger.info("PhysicalEventEdexDao is being created.");
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
        List<PluginDataObject> persistedPDOs = new ArrayList<>(records.length);

        Session session = null;
        try {
            session = getSession();
            for (int i = 0; i < pdos.size(); i++) {
                Transaction tx = null;
                PhysicalEvent decodedPDO = null;
                try {
                    decodedPDO = (PhysicalEvent) pdos.get(i);
                    PhysicalEvent pdoToSave = null;
                    PhysicalEvent existingPDO = null;

                    /*
                     * Query for an already-existing physical event in the DB
                     */
                    DatabaseQuery query = new DatabaseQuery(
                            PhysicalEvent.class);
                    query.addQueryParam("customId", decodedPDO.getCustomId());
                    /*
                     * Since there is a unique constraint on eventType /
                     * customId (see PhysicalEvent.java), then this query will
                     * only return at most ONE PhysicalEvent. So we dont need:
                     * query.addOrder("insertTime", false);
                     */
                    List<PluginDataObject> existingEvents = (List<PluginDataObject>) super.queryByCriteria(
                            query);

                    /*
                     * If none already exist, then it's a brand new
                     * PhysicalEvent and nothing to update
                     */
                    if (existingEvents.size() == 0) {
                        pdoToSave = decodedPDO;
                    }
                    /*
                     * If we have one existing event, then we update rather than
                     * create. So set the properties.
                     */
                    else if (existingEvents.size() == 1) {
                        existingPDO = (PhysicalEvent) existingEvents.get(0);
                        existingPDO.setSource(decodedPDO.getSource());
                        existingPDO.setName(decodedPDO.getName());
                        existingPDO.setIsTestEvent(decodedPDO.getIsTestEvent());
                        existingPDO
                                .setIsKnownEvent(decodedPDO.getIsKnownEvent());
                        existingPDO.setDataTime(decodedPDO.getDataTime());
                        existingPDO.setLatitude(decodedPDO.getLatitude());
                        existingPDO.setLongitude(decodedPDO.getLongitude());
                        existingPDO.setDistanceToCoastKm(
                                decodedPDO.getDistanceToCoastKm());

                        // TODO This gives us a new Data every time, whereas we
                        // probably want to update an existing one if it's of
                        // the same type.
                        existingPDO.setData(decodedPDO.getData());
                        pdoToSave = existingPDO;
                    } else {
                        throw new Exception(getClass().getName()
                                + " found MORE THAN ONE PhysicalEvent with customId = "
                                + decodedPDO.getCustomId());
                    }

                    pdoToSave.setInsertTime(TimeUtil.newGmtCalendar());
                    tx = session.beginTransaction();
                    session.saveOrUpdate(pdoToSave);
                    tx.commit();
                    persistedPDOs.add(pdoToSave);
                } catch (PersistenceException e) {
                    if (e.getCause() instanceof ConstraintViolationException) {
                        tx.rollback();
                        session.clear();
                    } else {
                        throw e;
                    }
                } catch (Exception e) {
                    tx.rollback();
                    logger.error(getClass().getName()
                            + " Query failed: Unable to insert or update "
                            + decodedPDO.getIdentifier(), e);
                }
            }

        } finally {
            if (session != null) {
                session.close();
            }
        }

        return persistedPDOs
                .toArray(new PluginDataObject[persistedPDOs.size()]);
    }

    /**
     * Returns the IDs of the active events for the given type
     *
     * @param type
     * @return
     */
    public List<String> getPhysicalEventIds(PhysicalEventType type,
            boolean testOnly) {
        return getPhysicalEventIds(type, null, testOnly);
    }

    public List<String> getPhysicalEventIds(PhysicalEventType type,
            ActiveOption option, boolean testOnly) {

        if (option == null) {
            option = ActiveOption.ALL;
        }

        /*
         * TODO Yuck. Straight SQL aint so pretty. Alternatives?
         */
        StringBuilder sqlStringBuffer = new StringBuilder(
                "SELECT DISTINCT customId FROM phy_event");
        Map<String, Object> paramMap = new HashMap<>();
        if (type != null || !ActiveOption.ALL.equals(option)) {
            sqlStringBuffer.append(" WHERE ");
            if (type != null) {
                sqlStringBuffer.append("eventType = :eventType");
                paramMap.put("eventType", type.toString());
                if (option != ActiveOption.ALL) {
                    sqlStringBuffer.append(" AND ");
                }
            }
            if (!ActiveOption.ALL.equals(option)) {
                sqlStringBuffer.append("isActive = :isActive");
                paramMap.put("isActive",
                        (ActiveOption.ACTIVE_ONLY.equals(option) ? Boolean.TRUE
                                : Boolean.FALSE));
            }
            sqlStringBuffer.append(" AND ");
            sqlStringBuffer.append("isTestEvent = :testOnly");
            paramMap.put("testOnly", testOnly);
        }
        Object[] qResult = executeSQLQuery(sqlStringBuffer.toString(),
                paramMap);

        List<String> ids = new ArrayList<>(qResult.length);
        for (Object o : qResult) {
            ids.add(o.toString());
        }
        return ids;
    }

    public IPhysicalEvent getPhysicalEvent(String customId) {
        return getPhysicalEvent(customId, null);
    }

    public IPhysicalEvent getPhysicalEvent(String customId,
            PhysicalEventType type) {

        if (customId == null || customId.isEmpty()) {
            return null;
        }

        List<String> fields = new ArrayList<>();
        List<Object> values = new ArrayList<>();
        List<String> operands = new ArrayList<>();

        // where customId = customId
        fields.add("customId");
        values.add(customId);
        operands.add("=");

        // where eventtype = type
        if (type != null) {
            fields.add("eventType");
            values.add(type.toString());
            operands.add("=");
        }

        try {
            // OrderBy inserttime for handling updated / duplicate rows
            List<?> questionableResults = queryByCriteria(fields, values,
                    operands, "insertTime", false);

            // Just get the first most recent one
            IPhysicalEvent event = null;
            if (questionableResults.size() > 0) {
                event = (IPhysicalEvent) questionableResults.get(0);
            }
            return event;
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getPhysicalEvent(...) failed, due to: "
                    + e.getMessage(), e);
            return null;
        }
    }

    /**
     * Retrieves a list of PhysicalEvents for the given customIds, all of the
     * singular PhysicalEventType. If there are more than one rows with a
     * specific customId, the most recent (according to inserttime) is
     * retrieved.
     *
     * @param customIds
     * @param type
     * @param testOnly
     *            May be null. If this is null, then the boolean is NOT added to
     *            the query, and results may be test or non-test physical
     *            events. If it's non null, we restrict the query appropriately.
     * @return
     */
    public List<IPhysicalEvent> getPhysicalEvents(List<String> customIds,
            PhysicalEventType type, Boolean testOnly) {

        if (customIds == null || customIds.isEmpty()) {
            return new ArrayList<>();
        }

        return getPhysicalEvents(type, ActiveOption.ALL, null, customIds,
                testOnly);
    }

    /**
     *
     * @param type
     * @param activeOption
     * @param timeRange
     * @param customIds
     * @param testOnly
     *            May be null. If this is null, then the boolean is NOT added to
     *            the query, and results may be test or non-test physical
     *            events. If it's non null, we restrict the query appropriately.
     * @return
     */
    public List<IPhysicalEvent> getPhysicalEvents(PhysicalEventType type,
            ActiveOption activeOption, TimeRange timeRange,
            List<String> customIds, Boolean testOnly) {

        List<IPhysicalEvent> resultEvents = new ArrayList<>();

        try {

            DatabaseQuery query = new DatabaseQuery(
                    PhysicalEvent.class.getName());
            if (type != null) {
                query.addQueryParam("eventType", type.toString());
            }
            if (activeOption != null
                    && !ActiveOption.ALL.equals(activeOption)) {
                query.addQueryParam("isActive",
                        (ActiveOption.ACTIVE_ONLY.equals(activeOption)
                                ? Boolean.TRUE
                                : Boolean.FALSE));
            }
            if (timeRange != null) {
                query.addQueryParam("dataTime.refTime",
                        new Date[] { timeRange.getStart(), timeRange.getEnd() },
                        QueryOperand.BETWEEN);

            }
            if (customIds != null && !customIds.isEmpty()) {
                query.addQueryParam("customId", customIds, QueryOperand.IN);
            }

            if (testOnly != null) {
                query.addQueryParam("isTestEvent", testOnly);
            }

            // We could have historical records for the same event custom ID. So
            // group em by customId.
            query.addOrder("customId", ResultOrder.DESC);

            // Do the query
            List<PhysicalEvent> records = (List<PhysicalEvent>) queryByCriteria(
                    query);

            // Now for each event with the same customId, add it to a list for
            // sorting later. (Though we should probably due this via SQL in the
            // database instead.)
            Map<String, List<PhysicalEvent>> eventsByCustomId = new HashMap<>();
            for (PhysicalEvent event : records) {
                List<PhysicalEvent> list = eventsByCustomId
                        .get(event.getCustomId());
                if (list == null) {
                    list = new ArrayList<>();
                    eventsByCustomId.put(event.getCustomId(), list);
                }
                list.add(event);
            }

            // Sort by inserttime, and add the most recent to our results
            for (List<PhysicalEvent> listOfSameIdEvents : eventsByCustomId
                    .values()) {
                listOfSameIdEvents
                        .sort(new InsertTimePhysicalEventComparator());
                resultEvents.add(
                        listOfSameIdEvents.get(listOfSameIdEvents.size() - 1));
            }

            return resultEvents;
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getPhysicalEvents(...) failed, due to: "
                    + e.getMessage(), e);
            return new ArrayList<>();
        }
    }

}
