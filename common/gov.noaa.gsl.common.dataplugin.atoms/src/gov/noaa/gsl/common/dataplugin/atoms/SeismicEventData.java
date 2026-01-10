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

import javax.measure.MetricPrefix;
import javax.measure.UnitConverter;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEventData;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventData;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;
import si.uom.SI;
import systems.uom.common.USCustomary;

/**
 * A class holding the data for a seismic event, as received from the TFS. See
 * the ICD document for better descriptions of the fields.
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
@Table(name = "seismic_event_data")
public class SeismicEventData extends PhysicalEventData implements TfsData {

    private static final UnitConverter MILES_TO_KM = USCustomary.MILE
            .getConverterTo(MetricPrefix.KILO(SI.METRE));

    private static final UnitConverter KM_TO_MILES = USCustomary.MILE
            .getConverterTo(MetricPrefix.KILO(SI.METRE)).inverse();

    /**
     * Originator or tfsDataSource is different than the source field. The
     * source field describes who uploaded the physical event, whereas the
     * originator/tfsDataSource is who generated the seismic event solution.
     * They're probably the same, but not necessarily.
     */
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

    /**
     * Preferred Magnitude
     */
    @DynamicSerializeElement
    @Column
    private float prefMagnitude = 0.0f;

    /**
     * Preferred magnitude type
     */
    @DynamicSerializeElement
    @Column(nullable = true)
    private PrefMagnitudeType prefMagnitudeType = PrefMagnitudeType.UNKNOWN;

    /**
     * Depth in miles
     */
    @DynamicSerializeElement
    @Column
    private float depth = 0.0f;

    /**
     * In degrees
     */
    @DynamicSerializeElement
    @Column
    private int azimuthalCoverage = 0;

    /**
     * Number of stations used to compute preferred magnitude
     */
    @DynamicSerializeElement
    @Column
    private int numStations = 0;

    /**
     * Energy/moment ratio
     */
    @DynamicSerializeElement
    @Column
    private float theta = 0.0f;

    /**
     * Optional, additional TFS-supplied seismic event data
     */
    @DynamicSerializeElement
    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "addl_seismic_event_data_id", nullable = true, referencedColumnName = "add_seismic_event_data_id")
    private AdditionalSeismicEventData addlSeismicEventData = null;

    public SeismicEventData() {
    }

    /**
     * Copies everything except the id. other must be a SeismicEventData
     */
    @Override
    public void copyFrom(IPhysicalEventData other) {

        if (!(other instanceof SeismicEventData)) {
            throw new IllegalArgumentException(getClass().getName()
                    + ": copyFrom(other) received an other that is not a SeismicEventData");
        }

        SeismicEventData seismicOther = (SeismicEventData) other;
        super.copyFrom(seismicOther);
        this.tfsDataSource = seismicOther.getTfsDataSource();
        this.tfsUser = seismicOther.getTfsUser();
        this.tfsCreationTime = seismicOther.getTfsCreationTime();
        this.prefMagnitude = seismicOther.getPrefMagnitude();
        this.prefMagnitudeType = seismicOther.getPrefMagnitudeType();
        this.depth = seismicOther.getDepth();
        this.azimuthalCoverage = seismicOther.getAzimuthalCoverage();
        this.numStations = seismicOther.getNumStations();
        this.theta = seismicOther.getTheta();
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

    public float getPrefMagnitude() {
        return prefMagnitude;
    }

    public void setPrefMagnitude(float prefMagnitude) {
        this.prefMagnitude = prefMagnitude;
    }

    @Override
    public PhysicalEventType getPhysicalEventType() {
        return PhysicalEventType.SEISMIC;
    }

    public PrefMagnitudeType getPrefMagnitudeType() {
        return prefMagnitudeType;
    }

    public void setPrefMagnitudeType(PrefMagnitudeType prefMagnitudeType) {
        this.prefMagnitudeType = prefMagnitudeType;
    }

    /**
     * In miles
     *
     * @return
     */
    public float getDepth() {
        return depth;
    }

    public void setDepth(float depth) {
        this.depth = depth;
    }

    public float getDepthKm() {
        return (float) MILES_TO_KM.convert(getDepth());
    }

    public void setDepthKm(float depthKm) {
        setDepth((float) KM_TO_MILES.convert(depthKm));
    }

    public int getAzimuthalCoverage() {
        return azimuthalCoverage;
    }

    public void setAzimuthalCoverage(int azimuthalCoverage) {
        this.azimuthalCoverage = azimuthalCoverage;
    }

    public int getNumStations() {
        return numStations;
    }

    public void setNumStations(int numStations) {
        this.numStations = numStations;
    }

    public float getTheta() {
        return theta;
    }

    public void setTheta(float theta) {
        this.theta = theta;
    }

    public Date getTfsCreationTime() {
        return tfsCreationTime;
    }

    public void setTfsCreationTime(Date tfsCreationTime) {
        this.tfsCreationTime = tfsCreationTime;
    }

    public AdditionalSeismicEventData getAddlSeismicEventData() {
        return addlSeismicEventData;
    }

    public void setAddlSeismicEventData(
            AdditionalSeismicEventData addlSeismicEventData) {
        this.addlSeismicEventData = addlSeismicEventData;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = super.hashCode();
        result = prime * result
                + Objects.hash(addlSeismicEventData, azimuthalCoverage, depth,
                        numStations, prefMagnitude, prefMagnitudeType,
                        tfsCreationTime, tfsDataSource, tfsUser, theta);
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
        SeismicEventData other = (SeismicEventData) obj;
        return Objects.equals(addlSeismicEventData, other.addlSeismicEventData)
                && azimuthalCoverage == other.azimuthalCoverage
                && Float.floatToIntBits(depth) == Float
                        .floatToIntBits(other.depth)
                && numStations == other.numStations
                && Float.floatToIntBits(prefMagnitude) == Float
                        .floatToIntBits(other.prefMagnitude)
                && Objects.equals(prefMagnitudeType, other.prefMagnitudeType)
                && Objects.equals(tfsCreationTime, other.tfsCreationTime)
                && Objects.equals(tfsDataSource, other.tfsDataSource)
                && Objects.equals(tfsUser, other.tfsUser)
                && Float.floatToIntBits(theta) == Float
                        .floatToIntBits(other.theta);
    }

    @Override
    public String toString() {
        return "SeismicEventData [tfsDataSource=" + tfsDataSource + ", tfsUser="
                + tfsUser + ", tfsCreationTime=" + tfsCreationTime
                + ", prefMagnitude=" + prefMagnitude + ", prefMagnitudeType="
                + prefMagnitudeType + ", depth=" + depth
                + ", azimuthalCoverage=" + azimuthalCoverage + ", numStations="
                + numStations + ", theta=" + theta + ", addlSeismicEventData="
                + addlSeismicEventData + "]";
    }

}
