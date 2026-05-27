package gov.noaa.gsl.common.dataplugin.pem;

/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
import java.util.ArrayList;
import java.util.List;

/**
 * A basic implementation of IPhysicalEventDao
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
public abstract class BasePhysicalEventDao implements IPhysicalEventDao {

    private PhysicalEventType phyEventType = PhysicalEventType.UNKNOWN;

    private List<IPhysicalEventDaoListener> daoListeners = new ArrayList<>();

    private boolean isTest = false;

    @Override
    public void setPhysicalEventType(PhysicalEventType type) {
        if (type == null) {
            type = PhysicalEventType.UNKNOWN;
        }
        phyEventType = type;
    }

    @Override
    public PhysicalEventType getPhysicalEventType() {
        return phyEventType;
    }

    @Override
    public boolean isTestMode() {
        return isTest;
    }

    @Override
    public void setTestMode(boolean isTest) {
        this.isTest = isTest;
    }

    @Override
    public void addPhysicalEventDaoListener(IPhysicalEventDaoListener lister) {
        if (lister == null) {
            return;
        }
        daoListeners.add(lister);
    }

    @Override
    public boolean removePhysicalEventDaoListener(
            IPhysicalEventDaoListener lister) {
        if (lister == null) {
            return false;
        }
        return daoListeners.remove(lister);
    }

    @Override
    public void clearPhysicalEventDaoListeners() {
        daoListeners.clear();
    }

    protected void firePhysicalEventAdded(String id) {
        if (id == null) {
            return;
        }

        for (IPhysicalEventDaoListener lister : daoListeners) {
            lister.physicalEventAdded(id, getPhysicalEventType());
        }
    }

    protected void firePhysicalEventRemoved(String id) {
        if (id == null) {
            return;
        }

        for (IPhysicalEventDaoListener lister : daoListeners) {
            lister.physicalEventRemoved(id, getPhysicalEventType());
        }
    }

    protected void firePhysicalEventChanged(String id) {
        if (id == null) {
            return;
        }

        for (IPhysicalEventDaoListener lister : daoListeners) {
            lister.physicalEventChanged(id, getPhysicalEventType());
        }
    }
}
