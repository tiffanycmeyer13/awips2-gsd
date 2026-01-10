package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs.request;

import java.util.Date;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.serialization.comm.IServerRequest;

@DynamicSerialize
public class SeaLevelObsRequest implements IServerRequest {
    /**
     * Required
     */
    @DynamicSerializeElement
    private String physicalEventCustomId;

    /**
     * Optional
     */
    @DynamicSerializeElement
    private Date refTime;

    public SeaLevelObsRequest() {
    }

    public String getPhysicalEventCustomId() {
        return physicalEventCustomId;
    }

    public void setPhysicalEventCustomId(String physicalEventCustomId) {
        this.physicalEventCustomId = physicalEventCustomId;
    }

    public Date getRefTime() {
        return refTime;
    }

    public void setRefTime(Date refTime) {
        this.refTime = refTime;
    }

}
