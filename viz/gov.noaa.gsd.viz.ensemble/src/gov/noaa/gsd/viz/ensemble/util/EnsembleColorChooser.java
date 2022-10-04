package gov.noaa.gsd.viz.ensemble.util;

import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.ColorDialog;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Shell;

import com.raytheon.viz.ui.dialogs.CaveJFACEDialog;

/**
 * This class is a Dialog which allows users to change the colors of the GFS
 * ensemble perturbation members. It is used as a convenience feature to make it
 * easy to create a gradient of colors given a base color.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date          Ticket#  Engineer  Description
 * ------------- -------- --------- --------------------------------------------
 * Oct 08, 2014  5056     polster   Initial creation
 * Apr 18, 2022  103658   smanoj    Remove data source name in the Color
 *                                  Gradient “Choose Color Range” dialog
 * May 03, 2022  103658   tjensen   Make EnsembleGFESColorChooser generic for
 *                                  any Ensemble models
 *
 * </pre>
 *
 * @author polster
 */
public class EnsembleColorChooser extends CaveJFACEDialog {

    /**
     * Create the dialog.
     *
     * @param parentShell
     */
    public EnsembleColorChooser(Shell parentShell) {
        super(parentShell);
    }

    /**
     * Create contents of the dialog.
     *
     * @param parent
     */
    @Override
    protected Control createDialogArea(Composite parent) {

        Composite container = (Composite) super.createDialogArea(parent);
        GridLayout gridLayout = (GridLayout) container.getLayout();
        gridLayout.numColumns = 5;
        gridLayout.makeColumnsEqualWidth = false;

        final Composite label_color = new Composite(container, SWT.BORDER);
        label_color.setForeground(ChosenColors.getInstance().getColor());
        label_color.setBackground(GlobalColor.get(GlobalColor.WHITE));
        GridData gd_label_color = new GridData(SWT.LEFT, SWT.CENTER, false,
                false, 3, 1);
        gd_label_color.heightHint = 24;
        gd_label_color.widthHint = 116;
        gd_label_color.minimumWidth = 116;
        gd_label_color.minimumHeight = 24;
        label_color.setLayoutData(gd_label_color);
        label_color.setSize(116, 24);
        applyGradientBG(label_color);
        label_color.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseDown(MouseEvent e) {

                ColorDialog cd = new ColorDialog(getShell());
                cd.setRGB(ChosenColors.getInstance().getColor().getRGB());
                cd.setText("Choose lower color");
                RGB result = cd.open();
                if (result != null) {
                    Color nc = SWTResourceManager.getColor(result);
                    ChosenColors.getInstance().setColor(nc);
                    label_color.setForeground(nc);
                    applyGradientBG(label_color);
                }
            }
        });

        container.pack();
        return container;

    }

    public static void applyGradientBG(Composite c) {

        Rectangle rect = c.getClientArea();
        Image image = new Image(c.getDisplay(), rect.width, rect.height);
        GC gc = new GC(image);
        gc.setForeground(c.getForeground());
        gc.setBackground(c.getBackground());
        gc.fillGradientRectangle(0, 0, rect.width, rect.height, false);
        c.setBackgroundImage(image);
        gc.dispose();
        image.dispose();
    }

    /**
     * Create contents of the button bar.
     *
     * @param parent
     */
    @Override
    protected void createButtonsForButtonBar(Composite parent) {

        createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL,
                true);
        createButton(parent, IDialogConstants.CANCEL_ID,
                IDialogConstants.CANCEL_LABEL, false);
    }

    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("Choose Color Range");
    }

}
