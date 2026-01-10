/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.dialog;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;

/**
 * The PEMDialogConfigManager contains dynamic configuration options as defined
 * in XML, for use by the PEMDialog etc. This includes PEMDialogTabs, PEMDialog
 * columns, and Physical Event PLotters.
 * 
 * The PEMDialogTabs are created via extension points and XML in the
 * PEMVizBundleActivator. From the Activator, the Tabs need to be plugged into
 * the PEMDialog. Since I have no idea how to access the instance of the
 * PEMDialog from the Activator, I thought I would have to make the PEMDialog a
 * singleton (yuck) so that I could access it and plug in the Tabs. However, the
 * constructor for the PEMDialog requires the Shell (and so would the
 * getInstance() call), but the Shell is not accessible, nor would it likely
 * even exist at that point, from the Activator. So making the PEMDialog a
 * singleton probably doesn't solve the problem.
 *
 * And so, we are going to put all of the Tabs here in this class, which will be
 * a singleton. The PEMDialog will have to get its Tabs from here.
 *
 * Also, the TabItems in SWT are not meant to be subclassed. And so instead of
 * making a PEMDialogTab class, which isA TabItem, we'll use a Builder type of
 * notion instead.
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
public class PEMDialogConfigManager {

    private static PEMDialogConfigManager instance;

    private Map<PhysicalEventType, List<PEMDialogTab>> tabs = new HashMap<>();

    private Map<PhysicalEventType, IPEMColumnSpecBuilder> columnBuilders = new HashMap<>();

    private Map<PhysicalEventType, PEPlotter> plotters = new HashMap<>();

    public static PEMDialogConfigManager getInstance() {
        if (instance == null) {
            instance = new PEMDialogConfigManager();
        }
        return instance;
    }

    private PEMDialogConfigManager() {

    }

    public void setPEMDialogTabs(
            Map<PhysicalEventType, List<PEMDialogTab>> tabs) {
        if (tabs != null) {
            this.tabs = tabs;
        }
    }

    public Map<PhysicalEventType, List<PEMDialogTab>> getPEMDialogTabs() {
        return tabs;
    }

    public void setPEMColumnSpecBuilders(
            Map<PhysicalEventType, IPEMColumnSpecBuilder> map) {
        columnBuilders = map;
    }

    public Map<PhysicalEventType, IPEMColumnSpecBuilder> getPEMColumnSpecBuilders() {
        return columnBuilders;
    }

    public Map<PhysicalEventType, PEPlotter> getPlotters() {
        return plotters;
    }

    public void setPlotters(Map<PhysicalEventType, PEPlotter> plotters) {
        this.plotters = plotters;
    }

}
