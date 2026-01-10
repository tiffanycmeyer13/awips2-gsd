package gov.noaa.gsl.viz.atoms.trecs;

import org.eclipse.jface.dialogs.MessageDialog;

import com.raytheon.uf.viz.core.VizApp;

public class MessageDialogUtils {

    public static int openConfirm(final String title, final String message,
            String[] buttonLabels, int defaultIndex) {
        final int[] status = new int[1];
        VizApp.runSync(() -> {
            MessageDialog dialog = new MessageDialog(null, title, null, message,
                    MessageDialog.INFORMATION, buttonLabels, defaultIndex);
            status[0] = dialog.open();
        });
        return status[0];
    }

}
