/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atomsForecast;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.Iterator;
import java.util.Objects;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.annotations.DataURI;
import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atoms.TfsData;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToMany;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import jakarta.persistence.Transient;
import jakarta.persistence.UniqueConstraint;

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
@Entity
@SequenceGenerator(initialValue = 1, name = PluginDataObject.ID_GEN, sequenceName = "tsunami_fcst_seq")
@Table(name = "tsunami_fcst", uniqueConstraints = {
        @UniqueConstraint(columnNames = { "refTime", "phy_event_custom_id",
                "fcst_type" }) })
// TODO Add Index for query performance
public class TsunamiForecast extends PluginDataObject implements TfsData {

    public static final String PLUGIN_NAME = "atomsForecast";

    /*
     * NOTE: @DataURI(position = 0) is for dataTime from superclass! We will use
     * the refTime for the tsunami forecast run's forecastRunTime.
     */

    /**
     * This is the custom id of the physical event that this forecast run refers
     * to. You can retrieve the PhysicalEvent via the appropriate DAO.
     */
    @DynamicSerializeElement
    @DataURI(position = 1)
    @Column(name = "phy_event_custom_id")
    private String phyEventCustomId;

    /**
     * This is the source / organization that uploaded the XML for this
     * TsunamiForecast
     */
    @DynamicSerializeElement
    @Column
    private String tfsDataSource = "";

    @DynamicSerializeElement
    @Column
    private String tfsUser = "";

    @DynamicSerializeElement
    @Column
    private String description = "";

    @DataURI(position = 2)
    @DynamicSerializeElement
    @Column(name = "fcst_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private TsunamiForecastType fcstType;

    /**
     * TODO Add annotations when ready to do a database drop/reinstall
     */
    @Transient
    @DynamicSerializeElement
    private Date creationTime;

    /**
     * Lazy loading might be useful here, because this can be expensive to load
     * all of the TsunamiStationForecasts. However, if it's lazy, then dynamic
     * serializing this Collection to return TsunamiForecasts within EDEX server
     * Responses ends up throwing No-Hibernate-Session exceptions. Im not sure
     * if lazy is even useful, since this collection needs to be returned as
     * part of the TsunamiForecast anyway, and hence you might as well just
     * retrieve the collection eagerly, since the dynamic serializing happens
     * almost immediately thereafter. I think. TODO Alternatively, we could
     * separate the TsunamiStationForecast from the TsunamiForecast itself, and
     * instead have a DAO that retrieves them for you, given the ID of the
     * TsunamiForecast they belong to. THis could be a good option if the eager
     * performance is bad. TODO Doesnt seem like cascade is working for deleting
     * orphans.
     */
    @DynamicSerializeElement
    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.EAGER)
    @JoinColumn(name = "tsunami_fcst_id", nullable = false)
    Collection<TsunamiStationForecast> stationFcsts = new ArrayList<>();

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

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        if (description == null) {
            description = "";
        }
        this.description = description;
    }

    public TsunamiForecastType getFcstType() {
        return fcstType;
    }

    public void setFcstType(TsunamiForecastType fcstType) {
        this.fcstType = fcstType;
    }

    public Date getForecastRunTime() {
        return getDataTime().getRefTime();
    }

    public Collection<TsunamiStationForecast> getStationFcsts() {
        /*
         * NOTE if you make this unmodifiable, deserialization dies!
         */
        return new ArrayList<TsunamiStationForecast>(stationFcsts);
    }

    public boolean removeStationFcst(TsunamiStationForecast fcstToRemove) {
        if (fcstToRemove == null || fcstToRemove.getStation() == null) {
            return false;
        }

        return removeStationFcst(fcstToRemove.getStation().getCustomId());
    }

    public boolean removeStationFcst(String stnCustomId) {
        if (stnCustomId == null || stnCustomId.isEmpty()) {
            return false;
        }

        Iterator<TsunamiStationForecast> fcstIter = stationFcsts.iterator();
        while (fcstIter.hasNext()) {
            TsunamiStationForecast fcst = fcstIter.next();
            if (fcst.getStation().getCustomId().equals(stnCustomId)) {
                fcstIter.remove();
                return true;
            }
        }

        return false;
    }

    public void setStationFcsts(
            Collection<TsunamiStationForecast> stationFcsts) {
        if (stationFcsts == null) {
            stationFcsts = new ArrayList<>();
        }
        this.stationFcsts = stationFcsts;
    }

    public String getPhyEventCustomId() {
        return phyEventCustomId;
    }

    public void setPhyEventCustomId(String phyEventCustomId) {
        this.phyEventCustomId = phyEventCustomId;
    }

    public Date getCreationTime() {
        return creationTime;
    }

    public void setCreationTime(Date creationTime) {
        this.creationTime = creationTime;
    }

    @Override
    public String getPluginName() {
        return PLUGIN_NAME;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = super.hashCode();
        result = prime * result
                + Objects.hash(creationTime, fcstType, phyEventCustomId,
                        stationFcsts, tfsDataSource, tfsUser, description);
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (!super.equals(obj)) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        TsunamiForecast other = (TsunamiForecast) obj;
        return Objects.equals(creationTime, other.creationTime)
                && fcstType == other.fcstType
                && Objects.equals(phyEventCustomId, other.phyEventCustomId)
                && Objects.equals(stationFcsts, other.stationFcsts)
                && Objects.equals(tfsDataSource, other.tfsDataSource)
                && Objects.equals(description, other.description)
                && Objects.equals(tfsUser, other.tfsUser);
    }

    @Override
    public String toString() {
        return "TsunamiForecast [phyEventCustomId=" + phyEventCustomId
                + ", tfsDataSource=" + tfsDataSource + ", tfsUser=" + tfsUser
                + ", fcstType=" + fcstType + ", creationTime=" + creationTime
                + ", dataTime=" + dataTime + ", stationFcsts=" + stationFcsts
                + ", description=" + description + "]";
    }

}
