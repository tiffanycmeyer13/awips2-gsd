package gov.noaa.gsl.edex.pem;

import java.io.File;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;

public class PhysicalEventDecoder {

    private static final IUFStatusHandler logger = UFStatus
            .getHandler(PhysicalEventDecoder.class);

    public PluginDataObject[] decode(File file) {
        logger.info("Starting and finishing PhysicalEventDecoder");
        return new PluginDataObject[] {};
    }
}
