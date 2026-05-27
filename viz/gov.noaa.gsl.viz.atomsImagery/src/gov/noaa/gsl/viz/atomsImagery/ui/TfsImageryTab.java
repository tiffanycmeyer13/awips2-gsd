package gov.noaa.gsl.viz.atomsImagery.ui;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;

import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;

import gov.noaa.gsl.common.dataplugin.atomsImagery.TfsImageryDescriptor;
import gov.noaa.gsl.viz.atomsImagery.TfsImageryDao;
import gov.noaa.gsl.viz.atomsImagery.TfsImageryDaoListener;
import gov.noaa.gsl.viz.pem.dialog.BasePEMDialogTab;

public class TfsImageryTab extends BasePEMDialogTab
        implements TfsImageryDaoListener {

    private static final transient IUFStatusHandler statusHandler = UFStatus
            .getHandler(TfsImageryTab.class);

    private List<TfsImageryDescriptor> imageryDescs = new ArrayList<>();

    private org.eclipse.swt.widgets.List swtList;

    public TfsImageryTab() {
        super();
        TfsImageryDao.getInstance().addTfsImageryDaoListener(this);
        setPEPlotter(null);
    }

    @Override
    protected void reinitializeTabContent() {

        if (getTabItem() == null || getTabFolder() == null) {
            return;
        }

        /*
         * Dispose the imagery tab if it's existing, and create one then
         */
        if (getTabContentComposite() != null) {
            getTabContentComposite().dispose();
        }

        setTabContentComposite(new Composite(getTabFolder(), SWT.NONE));
        getTabContentComposite().setLayout(new FillLayout(SWT.VERTICAL));
        getTabItem().setControl(getTabContentComposite());

        /* No data, do nothing */
        if (getPhysicalEvent() == null) {
            Label noEventLabel = new Label(getTabContentComposite(), SWT.NONE);
            noEventLabel.setText("No Selected Physical Event");
        } else {
            /* Display the list of imagery descriptors in the tab */
            imageryDescs = TfsImageryDao.getInstance()
                    .getImageryDescriptors(getPhysicalEvent().getCustomId());
        }

        getTabContentComposite().setBackground(new Color(250, 150, 100));

        if (swtList != null) {
            swtList.dispose();
        }

        /* Builds the list */
        swtList = new org.eclipse.swt.widgets.List(getTabContentComposite(),
                SWT.BORDER | SWT.FULL_SELECTION | SWT.V_SCROLL);
        for (TfsImageryDescriptor desc : imageryDescs) {
            swtList.add(desc.getFilename());
        }
        swtList.setRedraw(true);
    }

    @Override
    public void tfsImageryChanged(String customEventId) {
        /*
         * Check if the customEventId == physicalEvent.getCustomId(). otherwise
         * ignore.
         */
        if (customEventId == null || getPhysicalEvent() == null
                || !customEventId.equals(getPhysicalEvent().getCustomId())) {
            statusHandler.info("TfsImageryTab ignoring eventId = "
                    + customEventId
                    + " because it's null or it doesn't match the customId of the TfsImageryTab's physicalEvent ("
                    + (getPhysicalEvent() == null ? null
                            : getPhysicalEvent().getCustomId())
                    + "). ");

            return;
        }
        Display.getDefault().syncExec(() -> {
            reinitializeTabContent();
        });
    }

}
