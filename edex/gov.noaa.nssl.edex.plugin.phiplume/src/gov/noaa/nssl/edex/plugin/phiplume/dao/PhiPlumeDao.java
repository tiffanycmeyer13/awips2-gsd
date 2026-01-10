package gov.noaa.nssl.edex.plugin.phiplume.dao;

import com.raytheon.edex.db.dao.DefaultPluginDao;
import com.raytheon.uf.common.dataplugin.PluginException;

/**
 * NOAA/CIMSS Prob Tornado Model Data Acquisition Object
 *
 * Defines access to persisted data from NOAA/CIMMS Prob Tornado Model
 *
 * <pre>
 * SOFTWARE HISTORY Date Ticket# Engineer Description ------------ ----------
 * ----------- -------------------------- Mar 27, 2014 DCS 15298 jgerth Initial
 * Creation. Oct 26, 2018 tmeyer Update for probTornado
 *
 * </pre
 *
 * @author Tiffany Meyer
 * @version 1.0
 *
 */

public class PhiPlumeDao extends DefaultPluginDao {

    /**
     * PhiPlumeDao constructor
     *
     * @param Plugin
     *            name
     * @throws PluginException
     */
    public PhiPlumeDao(String pluginName) throws PluginException {
        super(pluginName);
    }

    /**
     * Copy data from a Persistable object into a given DataStore container.
     *
     * @param dataStore
     *            DataStore instance to receive the Persistable data.
     * @param obj
     *            The Persistable object to be stored.
     * @throws Exception
     *             Any general exception thrown in this method.
     */
//    @Override
//    protected boolean populateDataStore(IDataStore dataStore, IPersistable obj)
//            throws Exception {
//        PhiPlumeRecord phiRec = (PhiPlumeRecord) obj;
//        String[] phiRecDataNames = PhiPlumeRecord.getDataNames();
//
//        for (int i = 0; i < phiRecDataNames.length; i++) {
//            IDataRecord record = DataStoreFactory.createStorageRecord(
//                    phiRecDataNames[i], phiRec.getDataURI(),
//                    phiRecDataNames[i]);
//            record.setCorrelationObject(phiRec);
//            IMetadataIdentifier metaId = new DataUriMetadataIdentifier(phiRec);
//            dataStore.addDataRecord(record, metaId);
//        }
//
//        return true;
//    }

}