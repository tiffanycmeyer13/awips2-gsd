package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;

@DynamicSerialize
public enum SLOObsType {
    TROUGH_TO_PEAK("Trough_To_Peak"),
    TROUGH_TO_ZERO("Trough_To_Zero"),
    PEAK_TO_PEAK("Peak_To_Peak"),
    ZERO_TO_PEAK("Zero_To_Peak"),
    FIRST_ARRIVAL("First_Arrival"),
    GAUGE_STOPPED_REPORTING("Gauge_Stopped_Reporting");

    private final String label;

    SLOObsType(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }

    public static SLOObsType fromString(String label) {
        return valueOf(label.toUpperCase());
    }

    public static String[] getValidValues() {

        List<String> validValuesList = new ArrayList<>();
        for (SLOObsType type : values()) {
            validValuesList.add(type.toString());
        }
        return validValuesList.toArray(new String[values().length]);
    }

    public static String[] getValidLabels() {

        List<String> validLabelsList = new ArrayList<>();
        for (SLOObsType type : values()) {
            validLabelsList.add(type.getLabel());
        }
        return validLabelsList.toArray(new String[values().length]);
    }

}
