/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.ui;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtension;
import org.eclipse.core.runtime.IExtensionPoint;
import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.core.runtime.Platform;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.status.UFStatus.Priority;
import com.raytheon.viz.core.mode.CAVEMode;
import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEventDao;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventManager;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.viz.pem.dialog.IPEMColumnSpecBuilder;
import gov.noaa.gsl.viz.pem.dialog.PEMDialogConfigManager;
import gov.noaa.gsl.viz.pem.dialog.PEMDialogTab;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;

public class PEMVizBundleActivator extends AbstractUIPlugin {

    private static final String DAOS_EXTENSION_ID = "gov.noaa.gsl.viz.pem.pemDaos";

    private static final String TABS_EXTENSION_ID = "gov.noaa.gsl.viz.pem.pemDialogTabs";

    private static final String COLUMNS_EXTENSION_ID = "gov.noaa.gsl.viz.pem.pemDialogColumns";

    private static final String PLOTTERS_EXTENSION_ID = "gov.noaa.gsl.viz.pem.phyEvtPlotters";

    private static final String PHY_EVT_TYPE_ATTR = "physicalEventType";

    private static final String ORDER_INDEX_ATTR = "orderIndex";

    private static final String TITLE_ATTR = "title";

    private static class TabDescrip {
        public Integer orderIndex = -1;

        public PEMDialogTab tab;

        public PhysicalEventType type;

        public TabDescrip(Integer orderIndex, PEMDialogTab tab,
                PhysicalEventType type) {
            this.orderIndex = orderIndex;
            this.tab = tab;
            this.type = type;
        }

        @Override
        public String toString() {
            return "TabDescrip [orderIndex=" + orderIndex + ", tab="
                    + tab.getClass().getName() + ", type=" + type + "]";
        }
    }

    private void configureDAOs() {

        List<IConfigurationElement> configElems = new ArrayList<>();
        // Construct the resource mapping from Eclipse plugins
        IExtensionRegistry registry = Platform.getExtensionRegistry();
        IExtensionPoint point = registry.getExtensionPoint(DAOS_EXTENSION_ID);
        if (point != null) {
            IExtension[] extensions = point.getExtensions();
            for (IExtension extension : extensions) {
                IConfigurationElement[] config = extension
                        .getConfigurationElements();

                Collections.addAll(configElems, config);
            }
        }

        for (IConfigurationElement configElem : configElems) {
            try {
                /*
                 * Code copied from eclipse document online, and copied from
                 * TOPS too. Same same, but the TOPS version had a bug where
                 * createExecutableExtension was first called (whatever that
                 * does) and then newInstance. Both calls created a new instance
                 * In our case, creating the DAOs that listen on the
                 * ProductAlertObserver ended up with a memory leak of the first
                 * orphaned DAO created.
                 */
                IPhysicalEventDao dao = (IPhysicalEventDao) (configElem
                        .createExecutableExtension("class"));
                dao.setTestMode(CAVEMode.getMode().equals(CAVEMode.TEST));
                String phyEvtTypeString = configElem
                        .getAttribute(PHY_EVT_TYPE_ATTR);
                PhysicalEventType phyEvtType = PhysicalEventType
                        .valueOf(phyEvtTypeString);
                PhysicalEventManager.getInstance()
                        .addPhysicalEventDao(phyEvtType, dao);
            } catch (Exception e) {
                UFStatus.getHandler().handle(Priority.PROBLEM,
                        e.getLocalizedMessage(), e);
            }
        }
    }

    private void configurePEMDialogTabs() {

        List<IConfigurationElement> configElems = new ArrayList<>();
        // Construct the resource mapping from Eclipse plugins
        IExtensionRegistry registry = Platform.getExtensionRegistry();
        IExtensionPoint point = registry.getExtensionPoint(TABS_EXTENSION_ID);
        if (point != null) {
            IExtension[] extensions = point.getExtensions();
            for (IExtension extension : extensions) {
                IConfigurationElement[] config = extension
                        .getConfigurationElements();

                Collections.addAll(configElems, config);
            }
        }

        Map<PhysicalEventType, Map<Integer, TabDescrip>> tabDescripsMaps = new HashMap<>();
        Map<PhysicalEventType, List<TabDescrip>> badDescripsLists = new HashMap<>();

        /*
         * <extension point="gov.noaa.gsl.viz.pem.pemDialogTabs"> <pemDialogTab
         * physicalEventType="SEISMIC" orderIndex = "1" title =
         * "Tsunami Forecast Runs" class=
         * "gov.noaa.gsl.viz.atomsForecast.ui.TsunamiForecastsTab"/>
         * </extension>
         *
         */
        for (IConfigurationElement configElem : configElems) {
            try {
                PhysicalEventType phyEvtType = PhysicalEventType
                        .valueOf(configElem.getAttribute(PHY_EVT_TYPE_ATTR));
                if (tabDescripsMaps.get(phyEvtType) == null) {
                    tabDescripsMaps.put(phyEvtType, new HashMap<>());
                }
                if (badDescripsLists.get(phyEvtType) == null) {
                    badDescripsLists.put(phyEvtType, new ArrayList<>());
                }

                PEMDialogTab tab = (PEMDialogTab) (configElem
                        .createExecutableExtension("class"));
                tab.setTitle((configElem.getAttribute(TITLE_ATTR) == null
                        ? "No Title"
                        : configElem.getAttribute(TITLE_ATTR)));

                Integer orderIndex = -1;
                if (configElem.getAttribute(ORDER_INDEX_ATTR) != null) {
                    try {
                        orderIndex = Integer.valueOf(
                                configElem.getAttribute(ORDER_INDEX_ATTR));
                    } catch (NumberFormatException e) {
                        UFStatus.getHandler().handle(Priority.WARN, getClass()
                                .getName() + " found a \"" + ORDER_INDEX_ATTR
                                + "\" attribute in a plugin extension (extension-point id=\""
                                + TABS_EXTENSION_ID
                                + "\") that was not an integer. Adding the PEMDialogTab to the end of the list.");
                        throw e;
                    }
                }

                /*
                 * Create a TabDescrip for this configuration, and add it to our
                 * Map by orderIndex. Later, we will order these by that
                 * orderIndex. If now we find a duplicate order index, then add
                 * the TabEntry to our duplicate/BadList, and later, we will
                 * just add these left overs to the end of our TabEntry list.
                 */
                TabDescrip tabDescrip = new TabDescrip(orderIndex, tab,
                        phyEvtType);
                if (tabDescripsMaps.get(phyEvtType).containsKey(orderIndex)
                        || orderIndex < 0) {
                    badDescripsLists.get(phyEvtType).add(tabDescrip);
                } else {
                    tabDescripsMaps.get(phyEvtType).put(orderIndex, tabDescrip);
                }
            } catch (Exception e) {
                UFStatus.getHandler().handle(Priority.PROBLEM,
                        e.getLocalizedMessage(), e);
                e.printStackTrace(System.err);
            }
        }

        /*
         * Order the tabEntriesList for each PhysicalEventType
         */
        Map<PhysicalEventType, List<TabDescrip>> sortedDescripsMap = new HashMap<>();
        for (Map.Entry<PhysicalEventType, Map<Integer, TabDescrip>> mapEntry : tabDescripsMaps
                .entrySet()) {
            List<TabDescrip> tabDescripsList = new ArrayList<>(
                    mapEntry.getValue().values());
            tabDescripsList.sort((arg0, arg1) -> {
                if (arg0.orderIndex < arg1.orderIndex) {
                    return -1;
                } else if (arg0.orderIndex > arg1.orderIndex) {
                    return 1;
                } else {
                    return 0;
                }
            });
            sortedDescripsMap.put(mapEntry.getKey(), tabDescripsList);
        }

        /*
         * Add the -1 / Bad or Duplicate orderIndex entries at the end. Sorry
         * this is all so confusing. Wow. Very confusing.
         */
        for (Map.Entry<PhysicalEventType, List<TabDescrip>> sortedDescrips : sortedDescripsMap
                .entrySet()) {
            sortedDescrips.getValue()
                    .addAll(badDescripsLists.get(sortedDescrips.getKey()));
        }

        /*
         * Now here I wanted to add each Tab to the PEMDialog. But I have no
         * idea how to get the instance of the PEMDialog here, and so I wanted
         * to make the PEMDialog a singleton (yuck). But the constructor for the
         * PEMDialog (and the getInstance() method would too) requires the
         * SHell. And here we don't have the SHell, which probably doesn't yet
         * exist in the first place.
         *
         * And so. We are going to put all of the Tabs in a PEMDialogTabManager,
         * which will be a singleton that the PEMDialog will access to acquire
         * its Tabs. Oh the horror.
         */
        Map<PhysicalEventType, List<PEMDialogTab>> finalTabsMap = new HashMap<>();
        for (Map.Entry<PhysicalEventType, List<TabDescrip>> sortedDescrips : sortedDescripsMap
                .entrySet()) {
            List<PEMDialogTab> listOfTabs = new ArrayList<>(
                    sortedDescrips.getValue().size());
            for (TabDescrip tabDescrip : sortedDescrips.getValue()) {
                listOfTabs.add(tabDescrip.tab);
            }
            finalTabsMap.put(sortedDescrips.getKey(), listOfTabs);
        }

        PEMDialogConfigManager.getInstance().setPEMDialogTabs(finalTabsMap);
    }

    private String dumpPEMDialogTabConfigElem(
            IConfigurationElement configElem) {
        if (configElem == null) {
            return "null";
        }
        StringBuilder dump = new StringBuilder(
                "<" + configElem.getName() + " ");
        dump.append(PHY_EVT_TYPE_ATTR + "=\""
                + configElem.getAttribute(PHY_EVT_TYPE_ATTR) + "\" ");
        dump.append(ORDER_INDEX_ATTR + "=\""
                + configElem.getAttribute(ORDER_INDEX_ATTR) + "\" ");
        dump.append(TITLE_ATTR + "=\"" + configElem.getAttribute(TITLE_ATTR)
                + "\" ");
        dump.append("class=\"" + configElem.getAttribute("class") + "\"/>");
        return dump.toString();
    }

    private void configurePEMDialogColumns() {

        List<IConfigurationElement> configElems = new ArrayList<>();
        // Construct the resource mapping from Eclipse plugins
        IExtensionRegistry registry = Platform.getExtensionRegistry();
        IExtensionPoint point = registry
                .getExtensionPoint(COLUMNS_EXTENSION_ID);
        if (point != null) {
            IExtension[] extensions = point.getExtensions();
            for (IExtension extension : extensions) {
                IConfigurationElement[] config = extension
                        .getConfigurationElements();

                Collections.addAll(configElems, config);
            }
        }

        Map<PhysicalEventType, IPEMColumnSpecBuilder> columnSpecBuilders = new HashMap<>();

        /*
         * <extension point="gov.noaa.gsl.viz.pem.pemDialogColumns">
         * <pemDialogColumn physicalEventType="SEISMIC" class=
         * "gov.noaa.gsl.viz.atoms.ui.SeismicDataColumnSpecBuilder"/>
         * </extension>
         *
         */
        for (IConfigurationElement configElem : configElems) {
            try {
                PhysicalEventType phyEvtType = PhysicalEventType
                        .valueOf(configElem.getAttribute(PHY_EVT_TYPE_ATTR));

                IPEMColumnSpecBuilder builder = (IPEMColumnSpecBuilder) (configElem
                        .createExecutableExtension("class"));

                columnSpecBuilders.put(phyEvtType, builder);
            } catch (Exception e) {
                UFStatus.getHandler().handle(Priority.PROBLEM,
                        e.getLocalizedMessage(), e);
                e.printStackTrace(System.err);
            }
        }

        PEMDialogConfigManager.getInstance()
                .setPEMColumnSpecBuilders(columnSpecBuilders);
    }

    private void configurePhyEvtPlotters() {
        List<IConfigurationElement> configElems = new ArrayList<>();
        // Construct the resource mapping from Eclipse plugins
        IExtensionRegistry registry = Platform.getExtensionRegistry();
        IExtensionPoint point = registry
                .getExtensionPoint(PLOTTERS_EXTENSION_ID);
        if (point != null) {
            IExtension[] extensions = point.getExtensions();
            for (IExtension extension : extensions) {
                IConfigurationElement[] config = extension
                        .getConfigurationElements();

                Collections.addAll(configElems, config);
            }
        }

        Map<PhysicalEventType, PEPlotter> plotters = new HashMap<>();

        /*
         * <extension point="gov.noaa.gsl.viz.pem.phyEvtPlotters"> <pePlotter
         * physicalEventType="SEISMIC"
         * class="gov.noaa.gsl.viz.atoms.plot.SeismicPlotter"/> </extension>
         *
         */
        for (IConfigurationElement configElem : configElems) {
            try {
                PhysicalEventType phyEvtType = PhysicalEventType
                        .valueOf(configElem.getAttribute(PHY_EVT_TYPE_ATTR));

                PEPlotter plotter = (PEPlotter) (configElem
                        .createExecutableExtension("class"));

                plotters.put(phyEvtType, plotter);
            } catch (Exception e) {
                UFStatus.getHandler().handle(Priority.PROBLEM,
                        e.getLocalizedMessage(), e);
                e.printStackTrace(System.err);
            }
        }

        PEMDialogConfigManager.getInstance().setPlotters(plotters);
    }

    @Override
    public void start(BundleContext context) throws Exception {
        super.start(context);

        // DAOs
        configureDAOs();

        // PEPlotters
        try {
            configurePhyEvtPlotters();
        } catch (Exception e) {
            System.err.println(getClass().getName()
                    + " received an Exception when configurePhyEvtPlotters. Exception follows: ");
            e.printStackTrace(System.err);
        }

        // PEMDialogTabs (and child PEPlotters)
        try {
            configurePEMDialogTabs();

            Map<PhysicalEventType, PEPlotter> plotters = PEMDialogConfigManager
                    .getInstance().getPlotters();
            Map<PhysicalEventType, List<PEMDialogTab>> tabsMap = PEMDialogConfigManager
                    .getInstance().getPEMDialogTabs();
            /*
             * For each parent plotter of a type, eg seismic, add a child
             * plotter for each tab under seismic.
             */
            for (Map.Entry<PhysicalEventType, PEPlotter> plotterEntry : plotters
                    .entrySet()) {
                PhysicalEventType peType = plotterEntry.getKey();
                PEPlotter parentPlotter = plotterEntry.getValue();
                List<PEMDialogTab> tabs = tabsMap.get(peType);
                if (tabs == null || parentPlotter == null) {
                    continue;
                }
                // Add child plotters to the parent plotter
                for (PEMDialogTab tab : tabs) {
                    parentPlotter.addChildPlotter(tab.getPEPlotter());
                }
            }
        } catch (Exception e) {
            System.err.println(getClass().getName()
                    + " received an Exception when configurePEMDialogTabs. Exception follows: ");
            e.printStackTrace(System.err);
        }

        // PEMDialogColumns
        try {
            configurePEMDialogColumns();
        } catch (Exception e) {
            System.err.println(getClass().getName()
                    + " received an Exception when configurePEMDialogColumns. Exception follows: ");
            e.printStackTrace(System.err);
        }
    }

    @Override
    public void stop(BundleContext context) throws Exception {
        super.stop(context);
        // TODO unregister things
    }

}
