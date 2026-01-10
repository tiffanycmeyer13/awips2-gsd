package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;

@DynamicSerialize
public enum SLOSensorType {
    BTR("BTR"),
    PR("PR"),
    PRS("PRS"),
    PTR("PTR"),
    PWL("PWL"),
    RAD("RAD"),
    WEB("WEB"),
    UNK("UNK");

    private final String label;

    SLOSensorType(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }

    public static SLOSensorType fromString(String label) {
        return valueOf(label.toUpperCase());
    }

    public static String[] getValidValues() {

        List<String> validValuesList = new ArrayList<>();
        for (SLOSensorType type : values()) {
            validValuesList.add(type.toString());
        }
        return validValuesList.toArray(new String[values().length]);
    }

    public static String[] getValidLabels() {

        List<String> validLabelsList = new ArrayList<>();
        for (SLOSensorType type : values()) {
            validLabelsList.add(type.getLabel());
        }
        return validLabelsList.toArray(new String[values().length]);
    }

}
