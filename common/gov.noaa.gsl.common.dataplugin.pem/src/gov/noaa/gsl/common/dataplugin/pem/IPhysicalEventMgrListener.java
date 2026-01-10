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
import java.util.Set;

import com.raytheon.uf.common.time.TimeRange;

/**
 * Sort of a marker interface for listening to changes on the
 * PhysicalEventManager.
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
public interface IPhysicalEventMgrListener extends IPhysicalEventDaoListener {

    void timeWindowChanged(TimeRange newTimeRange);

    void activeOptionChanged(ActiveOption newActiveOpt);

    void filtersChanged(List<PhysicalEventType> newFilters);

    void selectionsChanged(Set<String> newSelections);
}
