/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.atomsImagery;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
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
import com.raytheon.uf.common.datastorage.IDataStore;
import com.raytheon.uf.common.time.DataTime;
import com.raytheon.uf.edex.database.plugin.PluginDao;
import com.raytheon.uf.edex.database.query.DatabaseQuery;

import gov.noaa.gsl.common.dataplugin.atomsImagery.ITfsImageryDao;
import gov.noaa.gsl.common.dataplugin.atomsImagery.TfsImageryDescriptor;
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
* Aug 31, 2023        Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
public class TfsImageryEdexDao extends PluginDao implements ITfsImageryDao {

    private static final String OLD_EXT = ".old";

    private static final String IMAGERY_DIR = "imagery";

    public TfsImageryEdexDao(String pluginName) throws PluginException {
        super(pluginName);
        logger.info("TfsImageryEdexDao is being created.");
    }

    @Override
    public List<TfsImageryDescriptor> getImageryDescriptors(String eventId) {
        List<TfsImageryDescriptor> descs = new ArrayList<>();
        if (eventId == null || eventId.isEmpty()) {
            return descs;
        }

        String sql = "SELECT filename FROM tfs_imagery"
                + " WHERE phy_event_custom_id = :phy_event_custom_id";
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("phy_event_custom_id", eventId);

        try {
            Object[] qResult = executeSQLQuery(sql, paramMap);

            for (Object o : qResult) {
                TfsImageryDescriptor desc = new TfsImageryDescriptor();
                desc.setPhyEventCustomId(eventId);
                desc.setFilename((String) o);
                descs.add(desc);
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + " getImageryDescriptors(...) failed,  due to: "
                    + e.getMessage(), e);
        }
        return descs;
    }

    @Override
    public List<File> getImageryFiles(List<TfsImageryDescriptor> descs) {
        List<File> result = new ArrayList<>();
        if (descs == null) {
            return result;
        }

        for (TfsImageryDescriptor desc : descs) {
            // TODO
        }

        return result;
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
                TfsImageryDescriptor decodedPDO = null;
                try {
                    decodedPDO = (TfsImageryDescriptor) pdos.get(i);
                    TfsImageryDescriptor pdoToSave = decodedPDO;

                    /*
                     * Verify the PhysicalEvent exists.
                     */
                    DatabaseQuery query = new DatabaseQuery(
                            PhysicalEvent.class);
                    query.addQueryParam("customId",
                            decodedPDO.getPhyEventCustomId());
                    List<PluginDataObject> existingEvents = (List<PluginDataObject>) super.queryByCriteria(
                            query);
                    if (existingEvents == null || existingEvents.size() != 1) {
                        // TODO Somehow move imagery file to rejected directory
                        logger.error(getClass().getName()
                                + " could not find a PhysicalEvent customId = "
                                + decodedPDO.getPhyEventCustomId()
                                + ". Ignoring decoding and persisting. Fix the Filename to include a correct event ID.");
                        return new PluginDataObject[] {};
                    }

                    /*
                     * Query for an already-existing TfsImageryDescriptor in DB.
                     */
                    query = new DatabaseQuery(TfsImageryDescriptor.class);
                    query.addQueryParam("phyEventCustomId",
                            decodedPDO.getPhyEventCustomId());
                    query.addQueryParam("filename", decodedPDO.getFilename());
                    List<PluginDataObject> existingDescs = (List<PluginDataObject>) super.queryByCriteria(
                            query);

                    File pdoFile = decodedPDO.getFile();

                    /*
                     * If we already have this TfsImageryDescriptor in the
                     * database, then just use it.
                     */
                    if (existingDescs.size() == 1) {
                        TfsImageryDescriptor existingPDO = (TfsImageryDescriptor) existingDescs
                                .get(0);
                        pdoToSave = existingPDO;
                    }
                    /*
                     * Otherwise it's a brand new TfsImageryDescriptor and
                     * nothing to update.
                     */
                    else if (existingDescs.size() == 0) {
                        pdoToSave = decodedPDO;
                    }
                    /*
                     * More than one is an error
                     */
                    else {
                        throw new Exception(
                                "TFSImageryEdexDao found MORE THAN ONE (BAD!!!) existing TfsImageryDescriptor with phyEventId = "
                                        + decodedPDO.getPhyEventCustomId()
                                        + " and filename = "
                                        + decodedPDO.getFilename());
                    }

                    /**
                     * Now save the file as something like TFSEnergyMap.123.jpg,
                     * while shuffling the older existing files to something
                     * like TFSEnergyMap.123.jpg.3.old
                     */
                    Path pdoFilePath = pdoFile.toPath();
                    File eventDataDir = getEventDataDir(
                            pdoToSave.getPhyEventCustomId());

                    shuffleOlderFiles(eventDataDir, pdoFile.getName());
                    Path newFilePath = null;
                    boolean copySuccess = false;
                    try {
                        newFilePath = Paths.get(eventDataDir.getAbsolutePath(),
                                pdoToSave.getFilename());
                        Files.copy(pdoFilePath, newFilePath,
                                StandardCopyOption.REPLACE_EXISTING);
                        copySuccess = true;
                    } catch (Exception e) {
                        logger.error(getClass().getName()
                                + " had trouble saving the tfsImagery file to \""
                                + newFilePath.toAbsolutePath() + "\"", e);
                    }

                    if (copySuccess) {
                        try {
                            String[] disseminateCommand = { "python",
                                    TfsImageryDescriptor.getDissemScriptsDir()
                                            + File.separator
                                            + "compressAndSendFiles.py",
                                    "-f", eventDataDir.getAbsolutePath(),
                                    "-i" };
                            // Let's wait for it to complete and log errors
                            Process process = Runtime.getRuntime()
                                    .exec(disseminateCommand);
                            process.waitFor();
                            logger.info(getClass().getName()
                                    + " successfully invoked compressAndSendFiles.py when ingesting "
                                    + newFilePath.toString());
                        } catch (IOException | InterruptedException e) {
                            logger.error(getClass().getName()
                                    + " had trouble invoking compressAndSendFiles.py when ingesting "
                                    + newFilePath.toString(), e);
                        }
                    }
                    /*
                     * Set the DataTime to be nowish
                     */
                    pdoToSave.setDataTime(new DataTime(new Date()));

                    tx = session.beginTransaction();
                    session.saveOrUpdate(pdoToSave);
                    session.flush();
                    tx.commit();
                    persisted.add(pdoToSave);
                } catch (PersistenceException e) {
                    logger.error(
                            "Query failed here: Unable to insert or update "
                                    + decodedPDO.getIdentifier(),
                            e);
                    if (e.getCause() instanceof ConstraintViolationException) {
                        tx.rollback();
                        session.clear();
                    } else {
                        throw e;
                    }
                } catch (Exception e) {
                    logger.error("Query failed: Unable to insert or update "
                            + decodedPDO.getIdentifier(), e);
                    tx.rollback();
                }
            }

        } finally {
            if (session != null) {
                session.close();
            }
        }

        return persisted.toArray(new PluginDataObject[persisted.size()]);
    }

    /**
     * Given the baseFileName, shuffles filenames to OLD_EXT files
     *
     * @param eventDataDir
     * @param baseFileName
     *            such as TFSEnergyMap.123.jpg
     */
    private void shuffleOlderFiles(File eventDataDir, String baseFileName) {
        shuffleOlderFiles(eventDataDir, baseFileName, 1);
    }

    /**
     * Given the baseFileName, shuffles filenames to OLD_EXT files
     *
     * @param eventDataDir
     * @param baseFileName
     *            such as TFSEnergyMap.123.jpg
     * @param index
     */
    private void shuffleOlderFiles(File eventDataDir, String baseFileName,
            int index) {

        /*
         * Shuffle Blah.eventid.jpg.2.old to Blah.eventid.jpg.3.old, etc
         */
        StringBuilder dataFilePath = new StringBuilder()
                .append(eventDataDir.getAbsolutePath()).append(File.separator)
                .append(baseFileName);
        if (index > 1) {
            dataFilePath.append(".").append(index).append(OLD_EXT);
        }
        File dataFile = new File(dataFilePath.toString());
        if (dataFile.exists()) {
            shuffleOlderFiles(eventDataDir, baseFileName, index + 1);
            String newName = eventDataDir.getAbsolutePath() + File.separator
                    + baseFileName + "." + (index + 1) + OLD_EXT;
            dataFile.renameTo(new File(newName));
        }
    }

    private File getEventDataDir(String eventID) {

        String edexDataDir = TfsImageryDescriptor.getParentDataDir();
        String eventDataDirPath = edexDataDir + File.separator + eventID
                + File.separator + IMAGERY_DIR;
        File eventDataDir = new File(eventDataDirPath);
        try {
            if (!eventDataDir.exists()) {
                eventDataDir.mkdirs();
            }
        } catch (Exception e) {
            logger.error(getClass().getName() + " could not mkdir (\""
                    + eventDataDirPath + "\")!!!", e);
        }
        return eventDataDir;
    }
}
