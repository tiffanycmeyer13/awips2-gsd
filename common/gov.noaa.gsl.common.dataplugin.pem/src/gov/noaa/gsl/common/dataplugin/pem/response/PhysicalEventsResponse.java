/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.pem.response;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

/**
 * A container for the PhysicalEvents retrieved from the database.
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
public class PhysicalEventsResponse {

    @DynamicSerializeElement
    private List<IPhysicalEvent> physicalEvents = new ArrayList<>();

    public PhysicalEventsResponse() {

    }

    public List<IPhysicalEvent> getPhysicalEvents() {
        return physicalEvents;
    }

    public void setPhysicalEvents(List<IPhysicalEvent> physicalEvents) {
        if (physicalEvents == null) {
            physicalEvents = new ArrayList<>();
        }
        this.physicalEvents = physicalEvents;
    }

}
