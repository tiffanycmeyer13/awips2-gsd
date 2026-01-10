/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Weather Informatics and Decision Support Division (WIDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atoms.trecs;

import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;
import java.util.TreeMap;

import gov.noaa.gsl.common.dataplugin.atoms.SeismicEventData;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

/**
 * Class to represent stuff to be shown in the TrecsExecDialog
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jul 31, 2023   100405    Robert Weingruber Initial creation.
 * </pre>
 *
 * @author Robert Weingruber
 * @version 1.0
 */

public class TrecsExecInfo {

    private static DecimalFormat FLOAT_FORMATTER = new DecimalFormat("0.0");

    private static SimpleDateFormat DATE_FORMATTER = new SimpleDateFormat(
            "yyyy-MM-dd' 'HH:mm:ss'Z'");
    static {
        DATE_FORMATTER.setTimeZone(TimeZone.getTimeZone("UTC"));
    }

    static DecimalFormat DIST_FORMATTER = new DecimalFormat("#####.#");

    private IPhysicalEvent phyEvent = null;

    /**
     * Trace is meant for telling the user what the TRECS has done so far.
     */
    private List<String> trace = new ArrayList();

    /**
     * Ordered Map of productRegion (eg AkBcWc, or Hawaii) to List of
     * procedures. Ordered by Pacific / Atlantic product regions.
     */
    private Map<String, List<TrecsExecProcedure>> procedures = new TreeMap<>(
            new ProductRegionComparator());

    /**
     * A list of product region (tabs) that should be enabled, and all others,
     * disabled. All are enabled by default.
     *
     */
    private List<String> enabledProductRegions = new ArrayList<>();

    private String selectedProductRegion = "";

    /**
     * Informational just to record whether or not there was a ThreatDB hit for
     * the productRegion key.
     */
    private Map<String, Boolean> threatDBHitInfo = new HashMap<>();

    public TrecsExecInfo(IPhysicalEvent pEvent) {
        setPhyEvent(pEvent);
    }

    public IPhysicalEvent getPhyEvent() {
        return phyEvent;
    }

    public void setPhyEvent(IPhysicalEvent phyEvent) {
        if (phyEvent == null) {
            throw new IllegalArgumentException(
                    "TrecsExecDialog()::setPhyEvent requires a non-null IPhysicalEvent!");
        }
        this.phyEvent = phyEvent;
    }

    public List<String> getTrace() {
        return trace;
    }

    public void setTrace(List<String> trace) {
        if (trace == null) {
            trace = new ArrayList();
        }
        this.trace = trace;
    }

    public void clearTrace() {
        trace.clear();
    }

    /**
     * Summary returns a list of user messages, starting with a summary of the
     * physical event's attributes, then the trace list. If you don't like the
     * summary of the attributes, then just call getTrace() and add your own
     * summary.
     */
    public List<String> getExecSummary() {
        List<String> summary = new ArrayList();

        IPhysicalEvent phyEvent = getPhyEvent();
        if (phyEvent != null) {
            summary.add("Type: " + phyEvent.getEventType().getLabel());
            summary.add("ID: " + phyEvent.getCustomId());
            if (phyEvent.getName() != null && !phyEvent.getName().isEmpty()) {
                summary.add("Name: " + phyEvent.getName());
            }
            String lon = FLOAT_FORMATTER.format(phyEvent.getLongitude());
            String lat = FLOAT_FORMATTER.format(phyEvent.getLatitude());
            summary.add("Lon/Lat: " + lon + "/" + lat);
            summary.add("Origin Time: "
                    + DATE_FORMATTER.format(phyEvent.getRefTime()));
            summary.add("Dist To Coast: "
                    + FLOAT_FORMATTER.format(phyEvent.getDistanceToCoastKm())
                    + " km "
                    + (phyEvent.getDistanceToCoastKm() >= 0 ? "(OFFshore)"
                            : "(ONshore)"));
            if (phyEvent.getData() instanceof SeismicEventData) {
                SeismicEventData sed = (SeismicEventData) phyEvent.getData();
                summary.add("Magnitude: " + sed.getPrefMagnitude());
                summary.add("Depth: " + DIST_FORMATTER.format(sed.getDepth())
                        + " mi / " + DIST_FORMATTER.format(sed.getDepthKm())
                        + " km");
            }
        }
        summary.add("===================================");
        summary.addAll(getTrace());
        return summary;
    }

    public void appendToTrace(String string) {
        if (string == null || string.isBlank() || string.isEmpty()) {
            return;
        }
        trace.add(string);
    }

    public void appendToTrace(String linePrefix, String string) {
        if (string == null || string.isBlank() || string.isEmpty()) {
            return;
        }
        if (linePrefix == null) {
            linePrefix = "";
        }
        trace.add(linePrefix + string);
    }

    public void appendToTrace(List<String> strings) {
        if (strings == null) {
            return;
        }
        for (String s : strings) {
            appendToTrace(s);
        }
    }

    public void appendToTrace(String linePrefix, List<String> strings) {
        if (strings == null) {
            return;
        }
        if (linePrefix == null) {
            linePrefix = "";
        }
        for (String s : strings) {
            appendToTrace(linePrefix + s);
        }
    }

    public List<String> getProductRegions() {
        return new ArrayList(procedures.keySet());
    }

    public Map<String, List<TrecsExecProcedure>> getProcedures() {
        return procedures;
    }

    public List<TrecsExecProcedure> getProcedures(String prodRegionName) {
        if (procedures.get(prodRegionName) == null) {
            return new ArrayList<>();
        } else {
            return procedures.get(prodRegionName);
        }
    }

    /**
     *
     * @param procedures
     *            Map of productRegion string identifier to the list of
     *            procedures pertinent to that productRegion
     */
    public void setProcedures(
            Map<String, List<TrecsExecProcedure>> procedures) {
        if (procedures == null) {
            procedures = new TreeMap(new ProductRegionComparator());
            selectedProductRegion = "";
        }
        this.procedures = new TreeMap(new ProductRegionComparator());
        this.procedures.putAll(procedures);

        // Select first productRegion as default for now
        for (String productRegion : procedures.keySet()) {
            selectedProductRegion = productRegion;
            break;
        }
    }

    public void deselectAllProcedures() {
        for (Map.Entry<String, List<TrecsExecProcedure>> entry : procedures
                .entrySet()) {
            for (TrecsExecProcedure proc : entry.getValue()) {
                proc.setSelected(false);
                proc.setDefault(false);
                proc.setSelectedCategory(null);
                proc.setDefaultCategory(null);
            }
        }

        selectedProductRegion = "";
    }

    /**
     * A list of product region (tabs) that should be enabled, and all others,
     * disabled. All are enabled by default.
     *
     * @param enabledProductRegions
     */
    public void setEnabledProductRegions(List<String> enabledProductRegions) {
        if (enabledProductRegions == null) {
            enabledProductRegions = new ArrayList<>();
        }

        this.enabledProductRegions = enabledProductRegions;
    }

    public List<String> getEnabledProductRegions() {
        return enabledProductRegions;
    }

    /**
     * Sets selected to true for the first procedure belonging to the prodRegion
     * as well as the procedure's first category
     *
     * @param name
     */
    public void selectFirstProcedureAndCategoryForProductRegion(
            String prodRegionName) {
        List<TrecsExecProcedure> procs = procedures.get(prodRegionName);
        if (procs == null || procs.size() == 0) {
            return;
        }
        TrecsExecProcedure firstProc = procs.get(0);
        firstProc.setSelected(true);
        if (firstProc.getCategories().size() > 0) {
            firstProc.setSelectedCategory(firstProc.getCategories().get(0));
        }
    }

    /**
     * Sets selected to true for the procedure identified by the given name.
     * Hopefully just one procedure has that name, but checks em all.
     *
     * @param name
     */
    public void selectProcedureByName(String name) {
        for (Map.Entry<String, List<TrecsExecProcedure>> entry : procedures
                .entrySet()) {
            for (TrecsExecProcedure proc : entry.getValue()) {
                if (proc.getName().equals(name)) {
                    proc.setSelected(true);
                    selectedProductRegion = entry.getKey();
                }
            }
        }
    }

    /**
     * Returns the first procedure found with the given name (or null if not
     * found). Hopefully this name is unique if you were smart when defining the
     * procedures.
     *
     * @param name
     */
    public TrecsExecProcedure getProcedureByName(String name) {
        for (Map.Entry<String, List<TrecsExecProcedure>> entry : procedures
                .entrySet()) {
            for (TrecsExecProcedure proc : entry.getValue()) {
                if (proc.getName().equals(name)) {
                    return proc;
                }
            }
        }
        return null;
    }

    /**
     * Returns a list of categories including those that are selected AND the
     * parent procedure is selected.
     *
     * @return
     */
    public List<TrecsExecCategory> getSelectedCategories() {
        List<TrecsExecCategory> result = new ArrayList<>();
        for (Map.Entry<String, List<TrecsExecProcedure>> entry : procedures
                .entrySet()) {
            for (TrecsExecProcedure proc : entry.getValue()) {
                if (proc.isSelected() && proc.getSelectedCategory() != null) {
                    result.add(proc.getSelectedCategory());
                }
            }
        }
        return result;
    }

    public String getSelectedProductRegion() {
        return selectedProductRegion;
    }

    public void setSelectedProductRegion(String productRegion) {
        if (productRegion != null && !productRegion.isEmpty()) {
            selectedProductRegion = productRegion;
        }
    }

    public TrecsExecProcedure getDefaultProcedure(String productRegion) {
        List<TrecsExecProcedure> procs = procedures.get(productRegion);
        if (procs == null) {
            return null;
        }
        for (TrecsExecProcedure proc : procs) {
            if (proc.isDefault()) {
                return proc;
            }
        }
        return null;
    }

    @Override
    public String toString() {
        return "TrecsExecDialogInfo [phyEvent=" + phyEvent + ", trace=" + trace
                + ", procedures=" + procedures + "]";
    }

    private static class ProductRegionComparator implements Comparator<String> {

        private static final List<String> PRODUCT_REGIONS = Arrays
                .asList("AkBcWc", "EcGc", "Hi", "As", "Gu", "Pac", "Pr", "Car");

        @Override
        public int compare(String arg0, String arg1) {
            return PRODUCT_REGIONS.indexOf(arg0)
                    - PRODUCT_REGIONS.indexOf(arg1);
        }

    }

    public void setThreatDBHit(String productRegion, boolean hit) {
        if (productRegion != null && !productRegion.isEmpty()) {
            threatDBHitInfo.put(productRegion, hit);
        }
    }

    public boolean wasThreatDBHit(String productRegion) {
        return (threatDBHitInfo.containsKey(productRegion)
                && threatDBHitInfo.get(productRegion) == true);
    }
}
