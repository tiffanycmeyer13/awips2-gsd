/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.pem.request;

import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.serialization.comm.IServerRequest;

import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;

/**
 * A request to retrieve PhysicalEvents. You must provide the customIds of the
 * events, and optionally the PhysicalEventType applied to each PhysicalEvent
 * (meaning you might retrieve several SEISMIC events, for example). The most
 * recent PhysicalEvents will be retrieved, meaning the ones with the most
 * recent inserttime if there are multiple rows.
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
@DynamicSerialize
public class PhysicalEventsByIDsRequest implements IServerRequest {

    /**
     * Required.
     */
    @DynamicSerializeElement
    private List<String> customIds;

    /**
     * Optional parameter specifying the type of the PhysicalEvents to retrieve.
     */
    @DynamicSerializeElement
    private PhysicalEventType physicalEventType;

    public PhysicalEventsByIDsRequest() {

    }

    public List<String> getCustomIds() {
        return customIds;
    }

    public void setCustomIds(List<String> customIds) {
        this.customIds = customIds;
    }

    public PhysicalEventType getPhysicalEventType() {
        return physicalEventType;
    }

    public void setPhysicalEventType(PhysicalEventType physicalEventType) {
        this.physicalEventType = physicalEventType;
    }

}
