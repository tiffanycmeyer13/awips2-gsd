/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atomsForecast;

import java.util.Date;
import java.util.List;
import java.util.Set;

/**
 *
 *
 * <pre>
*
* SOFTWARE HISTORY
* Date         Ticket#    Engineer          Description
* ------------ ---------- ----------------- --------------------------
*                       Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
public interface ITsunamiForecastDao {

    /**
     * Returns a list of TsunamiForecastType that are available for the given
     * customEventId.
     *
     * @param customEvtId
     * @return
     */
    List<TsunamiForecastType> getForecastTypes(String customEvtId);

    /**
     * Returns a List of reference times (ie forecast run times) that are
     * available for the given customEventId and of the given
     * TsunamiForecastType.
     *
     * @param customEventId
     * @param type
     * @return
     */
    List<Date> getForecastRunTimes(String customEventId,
            TsunamiForecastType type);

    /**
     * Returns the forecast specified by the given info. May return null if the
     * forecast does not exist.
     *
     * @param info
     * @return
     */
    TsunamiForecast getTsunamiForecast(TsunamiForecastInfo info);

    /**
     * Returns zero or more {@link TsunamiForecast}. Typically you would supply
     * the customEventId, forecast type, and refTime to get a single
     * TsunamiForecast. Remember that retrieving a TsunamiForecast may be
     * expensive, since it comes with a slew of TsunamiStationForecasts, and so
     * I would recommend just retrieving one TsunamiForecast at a time. But, you
     * can retrieve multiple if you want, by making type and/or refTime null.
     *
     * @param customEventId
     *            required
     * @param type
     *            optional
     * @param refTime
     *            optional
     * @return
     */
    List<TsunamiForecast> getTsunamiForecasts(String customEventId,
            TsunamiForecastType type, Date refTime);

    /**
     * Retrieves all of the TsunamiForecasts for the given customEventId and
     * forecast type. Remember, retrieving multiple TsunamiForecasts could be
     * expensive.
     *
     * @param customEventId
     * @param type
     * @return
     */
    List<TsunamiForecast> getTsunamiForecasts(String customEventId,
            TsunamiForecastType type);

    /**
     * Retrieves all of the TsunamiForecasts for the given customEventId.
     * Remember, retrieving multiple TsunamiForecasts could be expensive.
     *
     * @param customEventId
     * @return
     */
    List<TsunamiForecast> getTsunamiForecasts(String customEventId);

    /**
     * Returns the most recent TsunamiForecast for the given customEventId. If
     * there are more than one Forecasts of different types with the same most
     * recent forecast run time (ie refTime) for the given customEventId, then
     * more than one forecast will be returned. Otherwise only one forecast will
     * be returned, with the most recent refTime. An empty list is returned if
     * the customEventId is invalid.
     *
     * @param customEventId
     * @return
     */
    List<TsunamiForecast> getMostRecentTsunamiForecast(String customEventId);

    /**
     * Returns the most recent TsunamiForecast for the given customEventId and
     * (optional) type. An empty list is returned if the customEventId is
     * invalid.
     *
     * @param customEventId
     * @return
     */
    List<TsunamiForecast> getMostRecentTsunamiForecast(String customEventId,
            TsunamiForecastType type);

    /**
     * And finally a more generalize accessor
     */
    List<TsunamiForecastInfo> getTsunamiForecastInfos(String customEventId);

    Set<String> getPhyEventIDsWithForecasts();
}
