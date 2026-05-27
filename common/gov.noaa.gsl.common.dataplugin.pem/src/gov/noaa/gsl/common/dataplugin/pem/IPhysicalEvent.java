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

import java.util.Date;

/**
 * An interface representing a PhysicalEvent, such as a Seismic event or
 * Landslide event.
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
public interface IPhysicalEvent extends ILonLat {

    /**
     * Unfort, PluginDataObject that implementations of IPhysicalEvent will
     * possibly extend, already has an Integer Id. And so I am hoping we will be
     * using that and therefore we will make the ID on this IPhysicalEvent
     * interface be an Integer as well.
     *
     * @return the id, may be empty
     */
    int getId();

    void setId(int id);

    /**
     * The source organization that created this physical event. e.g. PTWC
     *
     * @return the source, may be empty
     */
    String getSource();

    void setSource(String source);

    /**
     * A custom id that may have some domain specific meaning or customization
     * specific to the organization who created the physical event.
     *
     * @return the custom id, may be empty
     */
    String getCustomId();

    void setCustomId(String customId);

    /**
     * A name, optional
     *
     * @return
     */
    String getName();

    void setName(String name);

    /**
     * Returns the type of IPhysicalEvent
     *
     * @return the type
     */
    PhysicalEventType getEventType();

    void setEventType(PhysicalEventType type);

    /**
     * A boolean specifying whether or not this is real vs test data
     *
     * @return true if test data, false by default
     */
    boolean getIsTestEvent();

    void setIsTestEvent(boolean isTest);

    /**
     * An optional boolean specifying whether or not it is known apriori that
     * this is a well known event or special procedure. In ATOMS, the UI will
     * ask the user if the event is 'special' if the event falls within a threat
     * database source region. However, if it is known apriori that this is a
     * well known event, then we can set the flag here, in which case the UI
     * does not have to ask the user.
     *
     * @return true if well known event, false by default
     */
    boolean getIsKnownEvent();

    void setIsKnownEvent(boolean isKnown);

    /**
     * The latitude for the event
     *
     * @return
     */
    @Override
    float getLatitude();

    void setLatitude(float latitude);

    /**
     * The longitude for the event
     *
     * @return
     */
    @Override
    float getLongitude();

    void setLongitude(float longitude);

    /**
     * The distance to coast km for the event. Positive is offshore, negative is
     * onshore.
     *
     * @return
     */
    float getDistanceToCoastKm();

    void setDistanceToCoastKm(float distToCoastKm);

    /**
     * The origin time for the event - when the event occurred.
     *
     * @return
     */
    Date getRefTime();

    /**
     * Returns the data for this physical event. NOTE: Ideally we would return
     * an IPhysicalEventData interface, but we can't specify a JPA mapping with
     * an interface.
     *
     * @return the data, may be null if it hasn't been established yet.
     */
    PhysicalEventData getData();

    void setData(PhysicalEventData data);

    /**
     * Whether or not the event is active, meaning someone still cares about it.
     *
     * @return
     */
    boolean getIsActive();

    void setIsActive(boolean isActive);

    /**
     *
     * @param other
     * @throws Exception
     */
    void copyFrom(IPhysicalEvent other);
}
