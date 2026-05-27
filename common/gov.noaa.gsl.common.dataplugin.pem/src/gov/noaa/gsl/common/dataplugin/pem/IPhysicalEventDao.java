/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.pem;

import java.util.List;

import com.raytheon.uf.common.time.TimeRange;

/**
 * The interface for DAO-type of thing that retrieves and saves PhysicalEvents.
 * Note that this is a CAVE-side DAO interface, and not an EDEX DAO @TODO though
 * we could/should come up with a common interface.
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
public interface IPhysicalEventDao {

    /*
     ******************** Save/Update methods below ******************************
     */

    void savePhysicalEvent(IPhysicalEvent event) throws Exception;

    /*
     ******************** Retrieval methods below ******************************
     */

    /**
     * Returns the list of customIds for the active PhysicalEvents of the DAO's
     * PhysicalEventType.
     *
     * @return
     */
    List<String> getPhysicalEventIds();

    /**
     * Returns the list of customIds for the PhysicalEvents of the DAO's
     * PhysicalEventType with the given activeOption.
     *
     * @return
     */
    List<String> getPhysicalEventIds(ActiveOption activeOption);

    /**
     * Returns the PhysicalEvent with the given customId and DAO's
     * PhysicalEventType.
     *
     * @param customId
     * @return
     */
    IPhysicalEvent getPhysicalEvent(String customId);

    /**
     * Returns the PhysicalEvents with the given customIds and DAO's
     * PhysicalEventType.
     *
     * @param customId
     * @return
     */
    List<IPhysicalEvent> getPhysicalEvents(List<String> customIds);

    /**
     * Returns the PhysicalEvents of the DAO's PhysicalEventType that are active
     * (or not) and that have a refTime within the timeRange (start and end
     * times inclusive).
     *
     * @param activeOption
     *            if null, it is assumed ActiveOption.ACTIVE_ONLY
     * @param timeRange
     *            may be null meaning all time, otherwise start/end of time
     *            range is inclusive
     * @return
     */
    List<IPhysicalEvent> getPhysicalEvents(ActiveOption activeOption,
            TimeRange timeRange);

    /**
     * Returns the PhysicalEvents of the DAO's PhysicalEventType that are active
     * (or not) and that have a refTime within the timeRange (start and end
     * times inclusive). Optionally, you can provide a list of customIds
     * identifying the physical events that you want to retrieve, that satisfy
     * the activeOption and timeRange constraints. If those physical events do
     * not satisfy the constraints, they will not be returned as part of the
     * List. This method exists so that database queries can be made to
     * determine if an event(s) satisfies the constraints rather than putting
     * the burden on the client such that the client has to retrieve the
     * event(s) and then check that it conforms to the constraints.
     *
     * @param activeOption
     * @param timeRange
     * @param customIds
     *            optional
     * @return
     */
    List<IPhysicalEvent> getPhysicalEvents(ActiveOption activeOption,
            TimeRange timeRange, List<String> customIds);
    /*
     ******************** DAO Properties below ******************************
     */

    /**
     * Sets the DAO's PhysicalEventType.
     *
     * @param type
     */
    void setPhysicalEventType(PhysicalEventType type);

    void setTestMode(boolean isTest);

    boolean isTestMode();

    /**
     * Returns the DAO's PhysicalEventType.
     *
     * @param type
     */
    PhysicalEventType getPhysicalEventType();

    /*
     ******************** Listener methods below ******************************
     */
    void addPhysicalEventDaoListener(IPhysicalEventDaoListener lister);

    boolean removePhysicalEventDaoListener(IPhysicalEventDaoListener lister);

    void clearPhysicalEventDaoListeners();

}
