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

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.serialization.comm.IServerRequest;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;

/**
 * A request to retrieve custom IDs for PhysicalEvents. Optionally provide the
 * PhysicalEventType and/or whether or not you want to restrict to active or
 * inactive events.
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
public class PhysicalEventIDsRequest implements IServerRequest {

    /**
     * Optional Parameter. Defaults to retrieving all IDs regardless of type.
     * Could be expensive.
     */
    @DynamicSerializeElement
    private PhysicalEventType physicalEventType;

    /**
     * Optional parameter. Defaults to retrieving IDs for active events.
     */
    @DynamicSerializeElement
    private ActiveOption activeOption = ActiveOption.ACTIVE_ONLY;

    /**
     * Optional parameter. Defaults to retrieving IDs for test events only.
     */
    @DynamicSerializeElement
    private boolean isTestOnly = false;

    public PhysicalEventIDsRequest() {

    }

    public PhysicalEventType getPhysicalEventType() {
        return physicalEventType;
    }

    public void setPhysicalEventType(PhysicalEventType physicalEventType) {
        this.physicalEventType = physicalEventType;
    }

    public ActiveOption getActiveOption() {
        return activeOption;
    }

    public void setActiveOption(ActiveOption activeOption) {
        this.activeOption = activeOption;
    }

    public boolean getIsTestOnly() {
        return isTestOnly;
    }

    public void setIsTestOnly(boolean isTestOnly) {
        this.isTestOnly = isTestOnly;
    }

}
