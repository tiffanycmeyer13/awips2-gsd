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
import java.util.HashSet;
import java.util.Set;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.annotations.DataURI;
import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.time.DataTime;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToOne;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

/**
 * A default implementation of IPhysicalEvent.
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
@Entity
@SequenceGenerator(initialValue = 1, name = PluginDataObject.ID_GEN, sequenceName = "phyevent_seq")
@Table(name = "phy_event", uniqueConstraints = {
        @UniqueConstraint(columnNames = { "customId" }) })
public class PhysicalEvent extends PluginDataObject implements IPhysicalEvent {

    private static final Set<String> PRODUCT_REGIONS;
    static {
        PRODUCT_REGIONS = new HashSet<>();
        PRODUCT_REGIONS.add("AkBcWc");
        PRODUCT_REGIONS.add("EcGc");
        PRODUCT_REGIONS.add("Hi");
        PRODUCT_REGIONS.add("As");
        PRODUCT_REGIONS.add("Gu");
        PRODUCT_REGIONS.add("Pr");
        PRODUCT_REGIONS.add("Pac");
        PRODUCT_REGIONS.add("Car");
    }

    public static final String PLUGIN_NAME = "pem";

    /*
     * NOTE Remember that PluginDataObject hasA dataTime which is a DataTime,
     * which is embeddable (!!!) and has a refTime, forecastTime, and embedded
     * validPeriod TimeRange! This means that we will have these too, in our
     * physical_event table, i think.
     */

    /*
     * @TODO: We probably need a reasonable @Index on this class!!!!
     */

    /*
     * @TODO: Verify the @UniqueConstraint and the @DataURI annotations are
     * reasonable. Our superclass PluginDataObject already includes the refTime
     * as position 0 in the DataURI, which is not great (consider that an
     * initial sensor reading might indicate 12:04 Z but then they legitimately
     * change it to 12:06 Z).
     */

    @DynamicSerializeElement
    @DataURI(position = 1)
    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private PhysicalEventType eventType = PhysicalEventType.UNKNOWN;

    @DataURI(position = 2)
    @DynamicSerializeElement
    @Column
    private String customId = "";

    @DynamicSerializeElement
    @Column
    private String name = "";

    @DynamicSerializeElement
    @Column
    private String source = "";

    @DynamicSerializeElement
    @Column
    private boolean isTestEvent = false;

    @DynamicSerializeElement
    @Column
    private boolean isKnownEvent = false;

    @DynamicSerializeElement
    @Column
    private boolean isActive = true;

    @DynamicSerializeElement
    @Column
    private float latitude;

    @DynamicSerializeElement
    @Column
    private float longitude;

    @DynamicSerializeElement
    @Column
    private float distanceToCoastKm = 0.0f;

    /*
     * @TODO Fix the orphans that are left behind.
     */
    @DynamicSerializeElement
    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "phy_event_data_id", nullable = false, referencedColumnName = "phy_event_data_id")
    private PhysicalEventData data = null;

    public PhysicalEvent() {
        setOverwriteAllowed(true);
    }

    /**
     * If other is null, nothing is copied.
     *
     * Copies everything from 'other' EXCEPT for the stuff listed below. If
     * other's type is different than this' type/data, then a new Data will be
     * created (whos data fields will be copied from other).
     *
     * NOT copied: id, insertTime, messageData, dataURI, identifier, processId,
     * traceId, overwriteAllowed
     *
     */
    @Override
    public void copyFrom(IPhysicalEvent other) {
        if (other == null) {
        }
        this.customId = other.getCustomId();
        this.source = other.getSource();
        this.name = other.getName();
        this.isTestEvent = other.getIsTestEvent();
        this.isKnownEvent = other.getIsKnownEvent();
        this.isActive = other.getIsActive();
        this.latitude = other.getLatitude();
        this.longitude = other.getLongitude();
        this.distanceToCoastKm = other.getDistanceToCoastKm();

        setDataTime(new DataTime(other.getRefTime()));

        // If we're the same type and data, just copy other's data
        if (this.eventType.equals(other.getEventType())
                && this.data.getClass().equals(other.getData().getClass())) {

            this.eventType = other.getEventType();
            this.data.copyFrom(other.getData());
        }
        // If we're different types or data, we need a new data
        else {
            this.eventType = other.getEventType();
            IPhysicalEventData newData = null;
            try {
                newData = other.getData().getClass().getDeclaredConstructor()
                        .newInstance();
            } catch (Exception e) {
                throw new RuntimeException(getClass().getName()
                        + ": copyFrom(other) received an Exception calling "
                        + "the Data's default constructor.");
            }
            newData.copyFrom(other.getData());

            // Ugh. Cast.
            setData((PhysicalEventData) newData);
        }
    }

    @Override
    public String getPluginName() {
        return PLUGIN_NAME;
    }

    @Override
    public String getSource() {
        return source;
    }

    @Override
    public void setSource(String source) {
        if (source == null) {
            source = "";
        }
        this.source = source;
    }

    @Override
    public String getCustomId() {
        return customId;
    }

    @Override
    public void setCustomId(String customId) {
        if (customId == null) {
            customId = "";
        }
        this.customId = customId;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public void setName(String name) {
        this.name = name;
    }

    @Override
    public boolean getIsTestEvent() {
        return isTestEvent;
    }

    @Override
    public void setIsTestEvent(boolean isTest) {
        this.isTestEvent = isTest;
    }

    @Override
    public boolean getIsKnownEvent() {
        return isKnownEvent;
    }

    @Override
    public void setIsKnownEvent(boolean isKnown) {
        this.isKnownEvent = isKnown;
    }

    @Override
    public boolean getIsActive() {
        return isActive;
    }

    @Override
    public void setIsActive(boolean isActive) {
        this.isActive = isActive;
    }

    @Override
    public PhysicalEventType getEventType() {
        return eventType;
    }

    @Override
    public void setEventType(PhysicalEventType type) {
        if (type == null) {
            type = PhysicalEventType.UNKNOWN;
        }
        this.eventType = type;
    }

    @Override
    public float getLatitude() {
        return latitude;
    }

    @Override
    public void setLatitude(float latitude) {
        this.latitude = latitude;
    }

    @Override
    public float getLongitude() {
        return longitude;
    }

    @Override
    public void setLongitude(float longitude) {
        this.longitude = longitude;
    }

    @Override
    public PhysicalEventData getData() {
        return data;
    }

    @Override
    public void setData(PhysicalEventData data) {
        if (data != null) {
            setEventType(data.getPhysicalEventType());
        }
        this.data = data;
    }

    @Override
    public String toString() {
        return "PhysicalEvent [eventType=" + eventType + ", customId="
                + customId + ", name=" + name + ", source=" + source
                + ", isTestEvent=" + isTestEvent + ", isKnownEvent="
                + isKnownEvent + ", isActive=" + isActive + ", latitude="
                + latitude + ", longitude=" + longitude + ", distanceToCoastKm="
                + distanceToCoastKm + ", data=" + data + "]";
    }

    @Override
    public Date getRefTime() {
        if (getDataTime() == null) {
            return null;
        }
        return getDataTime().getRefTime();
    }

    @Override
    public float getDistanceToCoastKm() {
        return distanceToCoastKm;
    }

    @Override
    public void setDistanceToCoastKm(float distanceToCoastKm) {
        this.distanceToCoastKm = distanceToCoastKm;
    }
}
