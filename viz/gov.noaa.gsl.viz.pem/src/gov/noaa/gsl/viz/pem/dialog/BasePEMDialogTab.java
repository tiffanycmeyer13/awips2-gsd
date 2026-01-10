package gov.noaa.gsl.viz.pem.dialog;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventManager;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventMgrAdapter;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEventType;
import gov.noaa.gsl.viz.pem.plot.PEPlotter;

public abstract class BasePEMDialogTab implements PEMDialogTab {

    /**
     * May be null
     */
    private IPhysicalEvent physicalEvent;

    private String title = "";

    private TabFolder tabFolder = null;

    private TabItem tabItem = null;

    private Composite tabContentComposite = null;

    /*
     * Optional plotter for rendering attributes from this tab on a map
     */
    private PEPlotter pePlotter;

    private PhysicalEventMgrListener pemListener = new PhysicalEventMgrListener();

    public BasePEMDialogTab() {
        PhysicalEventManager.getInstance().addPEMListener(pemListener);
    }

    @Override
    public void setPhysicalEvent(IPhysicalEvent evt) {

        IPhysicalEvent oldEvent = this.physicalEvent;
        this.physicalEvent = evt;

        reinitializeTabContent();
    }

    protected IPhysicalEvent getPhysicalEvent() {
        return physicalEvent;
    }

    @Override
    public void setTitle(String title) {
        if (title == null) {
            title = "";
        }
        this.title = title;
    }

    @Override
    public String getTitle() {
        return title;
    }

    protected TabFolder getTabFolder() {
        return tabFolder;
    }

    protected Composite getTabContentComposite() {
        return tabContentComposite;
    }

    protected void setTabContentComposite(Composite comp) {
        tabContentComposite = comp;
    }

    protected abstract void reinitializeTabContent();

    @Override
    public TabItem buildTabItem(TabFolder tabFolder, int swtStyle,
            IPhysicalEvent phyEvent) {

        disposeTabItem();

        this.tabFolder = tabFolder;
        tabItem = new TabItem(tabFolder, swtStyle);
        tabItem.setText(title);

        setPhysicalEvent(phyEvent);

        // reinitializeTabContent();
        return tabItem;
    }

    @Override
    public TabItem getTabItem() {
        return tabItem;
    }

    @Override
    public PEPlotter getPEPlotter() {
        return pePlotter;
    }

    protected void setPEPlotter(PEPlotter plotter) {
        this.pePlotter = plotter;
    }

    @Override
    public void disposeTabItem() {
        if (tabItem != null && !tabItem.isDisposed()) {
            tabItem.dispose();
        }
        tabItem = null;
    }

    private class PhysicalEventMgrListener extends PhysicalEventMgrAdapter {

        @Override
        public void physicalEventChanged(String id, PhysicalEventType type) {
            Display.getDefault().syncExec(() -> {
                if (physicalEvent != null
                        && physicalEvent.getCustomId().equals(id)) {
                    reinitializeTabContent();
                }
            });
        }
    }
}
