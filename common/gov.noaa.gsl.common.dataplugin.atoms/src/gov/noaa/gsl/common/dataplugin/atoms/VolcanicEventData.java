/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atoms;

import java.util.Date;
import java.util.Objects;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEventData;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventData;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

/**
 * A class holding the data for a volcanic event, as received from the TFS.
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
@Table(name = "volcanic_event_data")
public class VolcanicEventData extends PhysicalEventData implements TfsData {

    @DynamicSerializeElement
    @Column
    private String tfsDataSource = "";

    @DynamicSerializeElement
    @Column
    private String tfsUser = "";

    /**
     * The timestamp denoting when the TFS record was created - this is part of
     * the ICD, and is provided as part of the XML record being uploaded via the
     * TFS. Note also that the PhysicalEvent (PluginDataObject really) already
     * has an insertTime, which is when the record got ingested and inserted
     * into the database.
     */
    @DynamicSerializeElement
    @Column
    private Date tfsCreationTime;

    public VolcanicEventData() {
    }

    /**
     * Copies everything except the id. other must be a VolcanicEventData
     */
    @Override
    public void copyFrom(IPhysicalEventData other) {

        if (!(other instanceof VolcanicEventData)) {
            throw new IllegalArgumentException(getClass().getName()
                    + ": copyFrom(other) received an other that is not a VolcanicEventData");
        }

        VolcanicEventData volcOther = (VolcanicEventData) other;
        super.copyFrom(volcOther);
        this.tfsDataSource = volcOther.getTfsDataSource();
        this.tfsUser = volcOther.getTfsUser();
    }

    @Override
    public String getTfsDataSource() {
        return tfsDataSource;
    }

    @Override
    public void setTfsDataSource(String source) {
        if (source == null) {
            source = "";
        }
        this.tfsDataSource = source;
    }

    @Override
    public String getTfsUser() {
        return tfsUser;
    }

    @Override
    public void setTfsUser(String user) {
        if (user == null) {
            user = "";
        }
        this.tfsUser = user;
    }

    public Date getTfsCreationTime() {
        return tfsCreationTime;
    }

    public void setTfsCreationTime(Date tfsCreationTime) {
        this.tfsCreationTime = tfsCreationTime;
    }

    @Override
    public PhysicalEventType getPhysicalEventType() {
        return PhysicalEventType.VOLCANIC;
    }

    @Override
    public int hashCode() {
        return Objects.hash(tfsDataSource, tfsUser);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        VolcanicEventData other = (VolcanicEventData) obj;
        if (!Objects.equals(tfsDataSource, other.tfsDataSource)) {
            return false;
        }
        if (!Objects.equals(tfsUser, other.tfsUser)) {
            return false;
        }
        return true;
    }

    @Override
    public String toString() {
        return "VolcanicEventData [tfsDataSource=" + tfsDataSource
                + ", tfsUser=" + tfsUser + "]";
    }

}
