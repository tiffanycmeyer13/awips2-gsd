package gov.noaa.gsl.common.dataplugin.atomsImagery.request;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.serialization.comm.IServerRequest;

@DynamicSerialize
public class TfsImageryDescriptorsRequest implements IServerRequest {

    @DynamicSerializeElement
    private String physicalEventCustomId;

    public String getPhysicalEventCustomId() {
        return physicalEventCustomId;
    }

    public void setPhysicalEventCustomId(String physicalEventCustomId) {
        this.physicalEventCustomId = physicalEventCustomId;
    }
}
