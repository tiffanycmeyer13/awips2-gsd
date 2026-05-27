package gov.noaa.gsl.common.dataplugin.atoms;

import java.util.Objects;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * A class holding additional and optional seismic event data for a seismic
 * event, as received from the TFS. See the ATOMS project's ICD document for
 * better descriptions of the fields.
 *
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
@Table(name = "addl_seismic_event_data")
public class AdditionalSeismicEventData {

    @Id
    @GeneratedValue
    @Column(name = "add_seismic_event_data_id")
    protected int id;

    @DynamicSerializeElement
    @Column
    private Float faultWidth;

    @DynamicSerializeElement
    @Column
    private Float strike;

    @DynamicSerializeElement
    @Column
    private Float dip;

    @DynamicSerializeElement
    @Column
    private Float slip;

    @DynamicSerializeElement
    @Column
    private Float rigidity;

    @DynamicSerializeElement
    @Column
    private Float seismicMoment;

    @DynamicSerializeElement
    @Column
    private Float ruptureVelocity;

    @DynamicSerializeElement
    @Column
    private Float slipVelocity;

    @DynamicSerializeElement
    @Column
    private Float strikePercent;

    @DynamicSerializeElement
    @Column
    private Float dipPercent;

    @DynamicSerializeElement
    @Column
    private Float cmtLatitude;

    @DynamicSerializeElement
    @Column
    private Float cmtLongitude;

    @DynamicSerializeElement
    @Column
    private Float cmtDepth;

    @DynamicSerializeElement
    @Column
    private String cmtDepthType;

    @DynamicSerializeElement
    @Column
    private Float cmtMagnitude;

    @DynamicSerializeElement
    @Column
    private Integer cmtNSTA;

    @DynamicSerializeElement
    @Column
    private String cmtSRC;

    @DynamicSerializeElement
    @Column
    private String eid;

    @DynamicSerializeElement
    @Column
    private String vid;

    public AdditionalSeismicEventData() {
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getId() {
        return id;
    }

    public Float getFaultWidth() {
        return faultWidth;
    }

    public void setFaultWidth(Float faultWidth) {
        this.faultWidth = faultWidth;
    }

    public Float getStrike() {
        return strike;
    }

    public void setStrike(Float strike) {
        this.strike = strike;
    }

    public Float getDip() {
        return dip;
    }

    public void setDip(Float dip) {
        this.dip = dip;
    }

    public Float getSlip() {
        return slip;
    }

    public void setSlip(Float slip) {
        this.slip = slip;
    }

    public Float getRigidity() {
        return rigidity;
    }

    public void setRigidity(Float rigidity) {
        this.rigidity = rigidity;
    }

    public Float getSeismicMoment() {
        return seismicMoment;
    }

    public void setSeismicMoment(Float seismicMoment) {
        this.seismicMoment = seismicMoment;
    }

    public Float getRuptureVelocity() {
        return ruptureVelocity;
    }

    public void setRuptureVelocity(Float ruptureVelocity) {
        this.ruptureVelocity = ruptureVelocity;
    }

    public Float getSlipVelocity() {
        return slipVelocity;
    }

    public void setSlipVelocity(Float slipVelocity) {
        this.slipVelocity = slipVelocity;
    }

    public Float getStrikePercent() {
        return strikePercent;
    }

    public void setStrikePercent(Float strikePercent) {
        this.strikePercent = strikePercent;
    }

    public Float getDipPercent() {
        return dipPercent;
    }

    public void setDipPercent(Float dipPercent) {
        this.dipPercent = dipPercent;
    }

    public Float getCmtLatitude() {
        return cmtLatitude;
    }

    public void setCmtLatitude(Float cmtLatitude) {
        this.cmtLatitude = cmtLatitude;
    }

    public Float getCmtLongitude() {
        return cmtLongitude;
    }

    public void setCmtLongitude(Float cmtLongitude) {
        this.cmtLongitude = cmtLongitude;
    }

    public Float getCmtDepth() {
        return cmtDepth;
    }

    public void setCmtDepth(Float cmtDepth) {
        this.cmtDepth = cmtDepth;
    }

    public String getCmtDepthType() {
        return cmtDepthType;
    }

    public void setCmtDepthType(String cmtDepthType) {
        this.cmtDepthType = cmtDepthType;
    }

    public Float getCmtMagnitude() {
        return cmtMagnitude;
    }

    public void setCmtMagnitude(Float cmtMagnitude) {
        this.cmtMagnitude = cmtMagnitude;
    }

    public Integer getCmtNSTA() {
        return cmtNSTA;
    }

    public void setCmtNSTA(Integer cmtNSTA) {
        this.cmtNSTA = cmtNSTA;
    }

    public String getCmtSRC() {
        return cmtSRC;
    }

    public void setCmtSRC(String cmtSRC) {
        this.cmtSRC = cmtSRC;
    }

    public String getEid() {
        return eid;
    }

    public void setEid(String eid) {
        this.eid = eid;
    }

    public String getVid() {
        return vid;
    }

    public void setVid(String vid) {
        this.vid = vid;
    }

    @Override
    public int hashCode() {
        return Objects.hash(cmtDepth, cmtDepthType, cmtLatitude, cmtLongitude,
                cmtMagnitude, cmtNSTA, cmtSRC, dip, dipPercent, eid, faultWidth,
                rigidity, ruptureVelocity, seismicMoment, slip, slipVelocity,
                strike, strikePercent, vid);
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
        AdditionalSeismicEventData other = (AdditionalSeismicEventData) obj;
        return Objects.equals(cmtDepth, other.cmtDepth)
                && Objects.equals(cmtDepthType, other.cmtDepthType)
                && Objects.equals(cmtLatitude, other.cmtLatitude)
                && Objects.equals(cmtLongitude, other.cmtLongitude)
                && Objects.equals(cmtMagnitude, other.cmtMagnitude)
                && Objects.equals(cmtNSTA, other.cmtNSTA)
                && Objects.equals(cmtSRC, other.cmtSRC)
                && Objects.equals(dip, other.dip)
                && Objects.equals(dipPercent, other.dipPercent)
                && Objects.equals(eid, other.eid)
                && Objects.equals(faultWidth, other.faultWidth)
                && Objects.equals(rigidity, other.rigidity)
                && Objects.equals(ruptureVelocity, other.ruptureVelocity)
                && Objects.equals(seismicMoment, other.seismicMoment)
                && Objects.equals(slip, other.slip)
                && Objects.equals(slipVelocity, other.slipVelocity)
                && Objects.equals(strike, other.strike)
                && Objects.equals(strikePercent, other.strikePercent)
                && Objects.equals(vid, other.vid);
    }

}
