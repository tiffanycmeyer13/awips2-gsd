package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs;

import java.util.ArrayList;
import java.util.Collection;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.annotations.DataURI;
import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atoms.TfsData;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToMany;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

@DynamicSerialize
@Entity
@SequenceGenerator(initialValue = 1, name = PluginDataObject.ID_GEN, sequenceName = "sealevel_observations_seq")
@Table(name = "sealevel_observations")
//@Table(name = "sealevel_observations", uniqueConstraints = {
//        @UniqueConstraint(columnNames = { "refTime", "phy_event_custom_id",
//                "fcst_type" }) })
// TODO Add Index for query performance
public class SeaLevelObservations extends PluginDataObject implements TfsData {

    public static final String PLUGIN_NAME = "atomsSeaLevelObs";

    /**
     * This is the custom id of the physical event that this set of observations
     * refers to. You can retrieve the PhysicalEvent via the appropriate DAO.
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
    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.EAGER)
    @JoinColumn(name = "sealevel_observations_id", nullable = false)
    private Collection<SeaLevelObs> seaLevelObs = new ArrayList<>();

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

    public String getPhyEventCustomId() {
        return phyEventCustomId;
    }

    public void setPhyEventCustomId(String phyEventCustomId) {
        this.phyEventCustomId = phyEventCustomId;
    }

    public Collection<SeaLevelObs> getSeaLevelObs() {
        /*
         * NOTE if you make this unmodifiable, deserialization dies!
         */
        return seaLevelObs;
    }

    public void setSeaLevelObs(Collection<SeaLevelObs> slobs) {
        if (slobs == null) {
            slobs = new ArrayList<>();
        }
        this.seaLevelObs = slobs;
    }

    @Override
    public String getPluginName() {
        return PLUGIN_NAME;
    }
}
