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

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.serialization.comm.IServerRequest;
import com.raytheon.uf.common.time.TimeRange;

import gov.noaa.gsl.common.dataplugin.pem.ActiveOption;
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
public class PhysicalEventsRequest implements IServerRequest {

    /**
     * Optional parameter specifying the type of the PhysicalEvents to retrieve.
     */
    @DynamicSerializeElement
    private PhysicalEventType physicalEventType;

    /**
     * Optional parameter. Defaults to retrieving active events.
     */
    @DynamicSerializeElement
    private ActiveOption activeOption = ActiveOption.ACTIVE_ONLY;

    /**
     * Optional parameter specifying the timeRange (start and end inclusive) for
     * the refTime of the events to include. Defaults to null, meaning all time.
     */
    @DynamicSerializeElement
    private TimeRange timeRange = null;

    /**
     * Optional parameter. Defaults to retrieving test events only.
     */
    @DynamicSerializeElement
    private boolean isTestOnly = false;

    /**
     * Optional, restricting results to events with a customId contained in the
     * List. If an event identified by an Id does not satisfy the additional
     * constraints above, then it will not be retrieved.
     */
    @DynamicSerializeElement
    private List<String> customIds = new ArrayList<>();

    public PhysicalEventsRequest() {

    }

    public List<String> getCustomIds() {
        return customIds;
    }

    public void setCustomIds(List<String> customIds) {
        if (customIds == null) {
            customIds = new ArrayList<>();
        }
        this.customIds = customIds;
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
        if (activeOption == null) {
            activeOption = ActiveOption.ACTIVE_ONLY;
        }
        this.activeOption = activeOption;
    }

    public TimeRange getTimeRange() {
        return timeRange;
    }

    public void setTimeRange(TimeRange timeRange) {
        this.timeRange = timeRange;
    }

    public boolean getIsTestOnly() {
        return isTestOnly;
    }

    public void setIsTestOnly(boolean isTestOnly) {
        this.isTestOnly = isTestOnly;
    }
}
