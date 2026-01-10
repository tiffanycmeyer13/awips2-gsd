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

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

/**
 * A request to save or update a PhysicalEvent.
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
public class SavePhysicalEventRequest implements IServerRequest {

    /**
     * Non-null event
     */
    @DynamicSerializeElement
    private IPhysicalEvent physicalEvent;

    public SavePhysicalEventRequest() {

    }

    public IPhysicalEvent getPhysicalEvent() {
        return physicalEvent;
    }

    public void setPhysicalEvent(IPhysicalEvent physicalEvent) {
        if (physicalEvent == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + ": setPhysicalEvent(e) received a null physicalEvent.");
        }
        this.physicalEvent = physicalEvent;
    }

}
