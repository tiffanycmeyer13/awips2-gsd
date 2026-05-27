/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.menu;

import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;

import com.raytheon.viz.ui.cmenu.AbstractRightClickAction;

import gov.noaa.gsl.viz.pem.dialog.PEMDialog;
import gov.noaa.gsl.viz.pem.rsc.PEMMapDisplay;

public class PEMProductMenuAction extends AbstractRightClickAction {

    private PEMDialog pemDialog;

    @Override
    public String getText() {
        return "Open Physical Event Manager Dialog...";
    }

    /**
     * @TODO dispose and cleanup n stuff
     */

    @Override
    public void run() {
        Shell shell = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
                .getShell();
        if (pemDialog == null) {
            pemDialog = new PEMDialog(shell);
        }
        pemDialog.open();
    }

    @Override
    public boolean isHidden() {
        if (getSelectedRsc() instanceof PEMMapDisplay) {
            return false;
        }
        return true;
    }
}
