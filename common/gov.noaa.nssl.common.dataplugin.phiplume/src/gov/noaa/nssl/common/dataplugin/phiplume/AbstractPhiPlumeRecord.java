package gov.noaa.nssl.common.dataplugin.phiplume;

import java.util.Date;

import org.locationtech.jts.geom.Geometry;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.annotations.DataURI;
import com.raytheon.uf.common.dataplugin.annotations.NullString;
import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import jakarta.persistence.Column;
import jakarta.persistence.MappedSuperclass;

@MappedSuperclass
@DynamicSerialize
public abstract class AbstractPhiPlumeRecord extends PluginDataObject {

    private static final long serialVersionUID = 1L;

    @Column
    @DynamicSerializeElement
    private Date validStart;

    @Column
    @DynamicSerializeElement
    private Date validEnd;

    @Column
    @DataURI(position = 1)
    @DynamicSerializeElement
    private String IDnum;

    @Column
    @DataURI(position = 2)
    @DynamicSerializeElement
    private String objectType;

    @Column
    @DynamicSerializeElement
    private Integer probability;

    @Column
    @DynamicSerializeElement
    private Integer speed;

    @Column
    @DynamicSerializeElement
    private Integer direction;

    @Column
    @NullString
    @DynamicSerializeElement
    private String hazardType;

    @Column(columnDefinition = "text")
    @DynamicSerializeElement
    private String polygonWKT;

    @Column(name = "geomtry", columnDefinition = "Geometry")
    @DynamicSerializeElement
    private Geometry geometry;

    @Column
    @NullString
    @DynamicSerializeElement
    private String best_csi_threshold;

    @Column(columnDefinition = "text")
    @NullString
    @DynamicSerializeElement
    private String probsevereAttrs;

    private static final String[] DATA_NAMES = { "validStart", "validEnd",
            "IDnum", "probability", "best_csi_threshold", "speed", "direction",
            "hazardType", "polygonWKT", "geometry" };

    /**
     * Default empty constructor
     */
    public AbstractPhiPlumeRecord() {
    }

    public Date getValidStart() {
        return validStart;
    }

    public void setValidStart(Date validStart) {
        this.validStart = validStart;
    }

    public Date getValidEnd() {
        return validEnd;
    }

    public void setValidEnd(Date validEnd) {
        this.validEnd = validEnd;
    }

    public String getIDnum() {
        return IDnum;
    }

    public void setIDnum(String id) {
        this.IDnum = id;
    }

    public String getObjectType() {
        return objectType;
    }

    public void setObjectType(String objectType) {
        this.objectType = objectType;
    }

    public Integer getSpeed() {
        return speed;
    }

    public void setSpeed(Integer speed) {
        this.speed = speed;
    }

    public Integer getDirection() {
        return direction;
    }

    public void setDirection(Integer direction) {
        this.direction = direction;
    }

    public Integer getProbability() {
        return probability;
    }

    public void setProbability(Integer probability) {
        this.probability = probability;
    }

    public String getHazardType() {
        return hazardType;
    }

    public void setHazardType(String hazardType) {
        this.hazardType = hazardType;
    }

    public void setPolygonWKT(String polygonWKT) {
        this.polygonWKT = polygonWKT;
    }

    public String getPolygonWKT() {
        return polygonWKT;
    }

    public void setGeometry(Geometry polygon) {
        this.geometry = polygon;
    }

    public Geometry getGeometry() {
        return geometry;
    }

    public String getBest_csi_threshold() {
        return best_csi_threshold;
    }

    public void setBest_csi_threshold(String best_csi_threshold) {
        this.best_csi_threshold = best_csi_threshold;
    }

    public String getProbsevereAttrs() {
        return probsevereAttrs;
    }

    public void setProbsevereAttrs(String probsevereAttrs) {
        this.probsevereAttrs = probsevereAttrs;
    }

    public static String[] getDataNames() {
        return DATA_NAMES;
    }

    /**
     * Constructs a warning record from a dataURI
     *
     * @param uri
     *            The dataURI
     */
    public AbstractPhiPlumeRecord(String uri) {
        super(uri);
    }

}
