package gov.noaa.gsl.edex.atomsSeaLevelObs;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.Iterator;
import java.util.List;

import org.hibernate.Session;
import org.hibernate.Transaction;
import org.hibernate.exception.ConstraintViolationException;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.PluginException;
import com.raytheon.uf.common.dataplugin.persist.IPersistable;
import com.raytheon.uf.common.datastorage.IDataStore;
import com.raytheon.uf.edex.database.plugin.PluginDao;
import com.raytheon.uf.edex.database.query.DatabaseQuery;

import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.ISeaLevelObsDao;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObs;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelObservations;
import gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.SeaLevelStation;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import jakarta.persistence.PersistenceException;

public class SeaLevelObsEdexDao extends PluginDao implements ISeaLevelObsDao {

    public SeaLevelObsEdexDao(String pluginName) throws PluginException {
        super(pluginName);
        logger.info("SeaLevelObsEdexDao is being created.");
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
                SeaLevelObservations decodedPDO = null;
                try {
                    /*
                     * SeaLevelObservations are always new. No need to update.
                     */
                    decodedPDO = (SeaLevelObservations) pdos.get(i);

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
                    Iterator<SeaLevelObs> slobsIter = decodedPDO
                            .getSeaLevelObs().iterator();
                    while (slobsIter.hasNext()) {
                        SeaLevelObs decodedSlob = slobsIter.next();
                        String decodedStnId = decodedSlob.getStation()
                                .getCustomId();
                        /*
                         * TODO Hardcoding property names for the query is bad!
                         */
                        query = new DatabaseQuery(SeaLevelStation.class);
                        query.addQueryParam("customId", decodedStnId);
                        List<SeaLevelStation> existingStations = (List<SeaLevelStation>) super.queryByCriteria(
                                query);
                        if (existingStations == null
                                || existingStations.size() != 1) {
                            // TODO Somehow move XML file to rejected directory
                            logger.error(getClass().getName()
                                    + " could not find a Station with customId = "
                                    + decodedStnId
                                    + ". Skipping decoding of this single SLObs. Fix the XML or database.");
                            slobsIter.remove();
                        } else {
                            /*
                             * We need to set the database's station on the
                             * fcst, otherwise it's transient
                             */
                            SeaLevelStation dbStation = existingStations.get(0);
                            decodedSlob.setStation(dbStation);
                        }
                    }

                    /*
                     * No need to query for an already-existing
                     * SeaLevelObservations, since any decoded
                     * SeaLevelObservations is always new.
                     */

                    tx = session.beginTransaction();
                    session.saveOrUpdate(decodedPDO);
                    tx.commit();
                    persisted.add(decodedPDO);
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
    public List<SeaLevelObservations> getSeaLevelObservations(
            String customEventId, Date refTime) {
        List<SeaLevelObservations> slobsResults = new ArrayList<>();

        if (customEventId == null || customEventId.isEmpty()) {
            return slobsResults;
        }

        List<String> fields = new ArrayList<>();
        List<Object> values = new ArrayList<>();
        List<String> operands = new ArrayList<>();

        // where phyEventCustomId = phyEventCustomId
        fields.add("phyEventCustomId");
        values.add(customEventId);
        operands.add("=");

        if (refTime != null) {
            fields.add("dataTime.refTime");
            values.add(refTime);
            operands.add("=");
        }
        try {
            List<?> questionableResults = queryByCriteria(fields, values,
                    operands);

            if (questionableResults.size() == 0) {
                return slobsResults;
            }

            for (Object o : questionableResults) {
                slobsResults.add((SeaLevelObservations) o);
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getSeaLevelObservations(...) failed, due to: "
                    + e.getMessage(), e);
        }
        return slobsResults;
    }

}
