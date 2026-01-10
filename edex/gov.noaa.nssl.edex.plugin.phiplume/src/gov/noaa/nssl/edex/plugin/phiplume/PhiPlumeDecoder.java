package gov.noaa.nssl.edex.plugin.phiplume;

import java.io.File;
import java.util.List;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;

import gov.noaa.nssl.common.dataplugin.phiplume.AbstractPhiPlumeRecord;
//import gov.noaa.nssl.common.dataplugin.phiplume.PhiPlumeRecord;
import gov.noaa.nssl.edex.plugin.phiplume.impl.PhiPlumeParser;

public class PhiPlumeDecoder {
    private final IUFStatusHandler statusHandler = UFStatus
            .getHandler(PhiPlumeDecoder.class);

//    private String traceId = null;

    /**
     * Default empty constructor
     */
    public PhiPlumeDecoder() {
    }

    /**
     * Creates the data object that will be persisted to the database and hdf5
     * repository
     *
     * @param File
     *            object passed by EDEX
     * @return PluginDataObject[] object of shape data
     * @throws Throwable
     */
    public PluginDataObject[] decode(File file) throws Throwable {

        PhiPlumeParser parser = new PhiPlumeParser(file);
        List<AbstractPhiPlumeRecord> records = parser.getRecords();

        AbstractPhiPlumeRecord[] debugRecords = records
                .toArray(new AbstractPhiPlumeRecord[0]);
        System.out.println("The Decode STANDARD Method Is Returning "
                + String.valueOf(debugRecords.length) + " Records");

        return records.toArray(new PluginDataObject[records.size()]);
    }
}
