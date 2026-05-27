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

import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;

/**
 * Tabs for the PEMDialog.
 *
 * See the notes on the top of PEMDialogConfigManager for a description.
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
public interface PEMDialogTab {

    void setPhysicalEvent(IPhysicalEvent evt);

    void setTitle(String title);

    String getTitle();

    TabItem buildTabItem(TabFolder tabFolder, int swtStyle,
            IPhysicalEvent phyEvent);

    TabItem getTabItem();

    void disposeTabItem();

    PEPlotter getPEPlotter();
}
