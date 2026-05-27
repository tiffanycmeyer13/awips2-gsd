/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.pem;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;

/**
 * A type of IPhysicalEvent, such as a Seismic Event or Landslide event.
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
public enum PhysicalEventType {
    SEISMIC("Seismic"),
    VOLCANIC("Volcanic"),
    LANDSLIDE("Landslide"),
    UNKNOWN("Unknown");

    private final String label;

    private PhysicalEventType(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }

    public static PhysicalEventType fromString(String label) {
        return valueOf(label.toUpperCase());
    }

    public static String[] getValidValues() {

        List<String> validValuesList = new ArrayList<>();
        for (PhysicalEventType type : values()) {
            validValuesList.add(type.toString());
        }
        return validValuesList.toArray(new String[values().length]);
    }

    public static String[] getValidLabels() {

        List<String> validLabelsList = new ArrayList<>();
        for (PhysicalEventType type : values()) {
            validLabelsList.add(type.getLabel());
        }
        return validLabelsList.toArray(new String[values().length]);
    }
}
