/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atomsForecast.request;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.serialization.comm.IServerRequest;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastType;

/**
 *
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
public class MostRecentTsunamiForecastRequest implements IServerRequest {

    /**
     * Required
     */
    @DynamicSerializeElement
    private String physicalEventCustomId;

    @DynamicSerializeElement
    private TsunamiForecastType tsunamiForecastType;

    public MostRecentTsunamiForecastRequest() {
    }

    public String getPhysicalEventCustomId() {
        return physicalEventCustomId;
    }

    public void setPhysicalEventCustomId(String physicalEventCustomId) {
        this.physicalEventCustomId = physicalEventCustomId;
    }

    public TsunamiForecastType getTsunamiForecastType() {
        return tsunamiForecastType;
    }

    public void setTsunamiForecastType(
            TsunamiForecastType tsunamiForecastType) {
        this.tsunamiForecastType = tsunamiForecastType;
    }

}
