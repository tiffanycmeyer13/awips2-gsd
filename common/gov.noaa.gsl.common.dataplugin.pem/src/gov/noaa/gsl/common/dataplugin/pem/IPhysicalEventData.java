/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.pem;

/**
 * A marker interface to represent the data for a IPhysicalEvent. This data is
 * specific to the type of IPhysicalEvent, such as data representing a Seismic
 * Event or Landslide event.
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
public interface IPhysicalEventData {

    /**
     * Though the PhysicalEvent has a PhysicalEventType, it would also be good
     * to be able to get the type from the PhyEventData itself, rather than
     * switching on the instanceof specific PhysicalEventData class when
     * determining the type to use for the PhysicalEvent.
     *
     * @return
     */
    PhysicalEventType getPhysicalEventType();

    void copyFrom(IPhysicalEventData other);

}
