/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atomsImagery;

import java.io.File;
import java.util.List;

/**
 *
 *
 * <pre>
*
* SOFTWARE HISTORY
* Date         Ticket#    Engineer          Description
* ------------ ---------- ----------------- --------------------------
*  8/30/23                Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
public interface ITfsImageryDao {

    /**
     * Get a list of imagery descriptors associated with the eventId
     * 
     * @param eventId
     * @return
     */
    List<TfsImageryDescriptor> getImageryDescriptors(String eventId);

    /**
     * @TODO I surely do not know what to return!? These need to end up as
     *       attachments to the outgoing threat messages.
     * @param descs
     * @return
     */
    List<File> getImageryFiles(List<TfsImageryDescriptor> descs);
}
