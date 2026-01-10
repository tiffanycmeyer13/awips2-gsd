package gov.noaa.gsl.common.dataplugin.atoms;

import java.util.ArrayList;
import java.util.List;

public enum PrefMagnitudeType {

    DURATION("Duration", "Md"),
    LOCAL("Local", "ML"),
    SURFACE_WAVE("Surface_Wave", "Ms"),
    MOMENT("Moment", "Mw"),
    ENERGY("Energy", "Me"),
    MOMENT_P("Moment_P", "Mwp"),
    BODY("Body", "Mb"),
    UNKNOWN("Unknown", "");

    private final String label;

    private final String abbreviation;

    PrefMagnitudeType(String label, String abbrev) {
        this.label = label;
        this.abbreviation = abbrev;
    }

    public String getLabel() {
        return label;
    }

    public String getAbbreviation() {
        return abbreviation;
    }

    public static PrefMagnitudeType fromString(String label) {
        return valueOf(label.toUpperCase());
    }

    public static PrefMagnitudeType fromAbbrev(String abbrev) {
        if (abbrev == null) {
            return null;
        }

        for (PrefMagnitudeType type : values()) {
            if (type.getAbbreviation().toUpperCase()
                    .equals(abbrev.toUpperCase())) {
                return type;
            }
        }
        return null;
    }

    public static String[] getValidValues() {

        List<String> validValuesList = new ArrayList<>();
        for (PrefMagnitudeType type : values()) {
            validValuesList.add(type.toString());
        }
        return validValuesList.toArray(new String[values().length]);
    }

    public static String[] getValidLabels() {

        List<String> validLabelsList = new ArrayList<>();
        for (PrefMagnitudeType type : values()) {
            validLabelsList.add(type.getLabel());
        }
        return validLabelsList.toArray(new String[values().length]);
    }

}
