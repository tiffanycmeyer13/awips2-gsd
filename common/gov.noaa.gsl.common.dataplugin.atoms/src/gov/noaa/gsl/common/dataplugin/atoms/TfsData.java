/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atoms;

/**
 * A interface for data received from the TFS.
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
public interface TfsData {

    /**
     * The source organization that uploaded this data record, which may be
     * different than the organization that created the PhysicalEvent in the
     * first place.
     *
     * @return the tfsDataSource, may be empty
     */
    String getTfsDataSource();

    void setTfsDataSource(String source);

    /**
     * The TFS user who uploaded the data
     *
     * @return the user, may be empty
     */
    String getTfsUser();

    void setTfsUser(String user);
}
