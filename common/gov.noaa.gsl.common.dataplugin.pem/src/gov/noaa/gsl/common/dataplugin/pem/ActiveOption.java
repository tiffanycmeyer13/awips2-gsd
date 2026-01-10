package gov.noaa.gsl.common.dataplugin.pem;

import java.util.ArrayList;
import java.util.List;

public enum ActiveOption {
    ACTIVE_ONLY("ActiveOnly"),
    INACTIVE_ONLY("InactiveOnly"),
    ALL("All");

    private final String label;

    private ActiveOption(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }

    public static ActiveOption fromString(String label) {
        return valueOf(label.toUpperCase());
    }

    public static String[] getValidValues() {

        List<String> validValuesList = new ArrayList<>();
        for (ActiveOption type : values()) {
            validValuesList.add(type.toString());
        }
        return validValuesList.toArray(new String[values().length]);
    }

    public static String[] getValidLabels() {

        List<String> validLabelsList = new ArrayList<>();
        for (ActiveOption type : values()) {
            validLabelsList.add(type.getLabel());
        }
        return validLabelsList.toArray(new String[values().length]);
    }

}
