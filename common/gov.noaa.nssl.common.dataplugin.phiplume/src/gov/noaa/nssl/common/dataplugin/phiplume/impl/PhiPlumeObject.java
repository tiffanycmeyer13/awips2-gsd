package gov.noaa.nssl.common.dataplugin.phiplume.impl;

import com.raytheon.uf.common.dataplugin.PluginDataObject;

public class PhiPlumeObject extends PluginDataObject {

    private String validStart;

    private String validEnd;

    private String IDnum;

    private String speed;

    private String direction;

    private String probability;

    private String hazardType;

    // private String site;

    private String polygonWKT;

    private String best_csi_threshold;

    private String probsevereAttrs;

    private static final String[] DATA_NAMES = { "validStart", "validEnd",
            "IDnum", "probability", "best_csi_threshold", "speed", "direction",
            "hazardType", "polygonWKT" };

    public static final String PLUGIN_NAME = "phiplume";

    private static final long serialVersionUID = 1L;

    /**
     * Default empty constructor
     */
    public PhiPlumeObject() {
    }

    public String getValidStart() {
        return validStart;
    }

    public void setValidStart(String validStart) {
        this.validStart = validStart;
    }

    public String getValidEnd() {
        return validEnd;
    }

    public void setValidEnd(String validEnd) {
        this.validEnd = validEnd;
    }

    public String getIDnum() {
        return IDnum;
    }

    public void setIDnum(String id) {
        this.IDnum = id;
    }

    public String getSpeed() {
        return speed;
    }

    public void setSpeed(String speed) {
        this.speed = speed;
    }

    public String getDirection() {
        return direction;
    }

    public void setDirection(String direction) {
        this.direction = direction;
    }

    public String getHazardType() {
        return hazardType;
    }

    public void setHazardType(String hazardType) {
        this.hazardType = hazardType;
    }

    public String getProbability() {
        return probability;
    }

    public void setProbability(String probability) {
        this.probability = probability;
    }

//    public String getSite() {
//        return site;
//    }
//
//    public void setSite(String site) {
//        this.site = site;
//    }

    public String getPolygonWKT() {
        return polygonWKT;
    }

    public void setPolygonWKT(String polygonWKT) {
        this.polygonWKT = polygonWKT;
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

    @Override
    public String getPluginName() {
        return PLUGIN_NAME;
    }

    public static String[] getDataNames() {
        return DATA_NAMES;
    }

}
