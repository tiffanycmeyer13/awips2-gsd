/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */

package gov.noaa.gsl.common.dataplugin.pem.response;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

/**
 * A success / failure response for saving a Physical Event
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
@DynamicSerialize
public class SavePhysicalEventResponse {

    @DynamicSerializeElement
    private Exception error;

    public SavePhysicalEventResponse() {

    }

    /**
     * If the error is null, then the Request was successful.
     *
     * @return
     */
    public Exception getError() {
        return error;
    }

    public void setError(Exception error) {
        this.error = error;
    }

}
