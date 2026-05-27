/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.edex.atomsForecast.handlers;

import java.util.Date;
import java.util.List;

import com.raytheon.uf.common.serialization.comm.IRequestHandler;

import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecast;
import gov.noaa.gsl.common.dataplugin.atomsForecast.TsunamiForecastType;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.TsunamiForecastsRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.TsunamiForecastsResponse;
import gov.noaa.gsl.edex.atomsForecast.TsunamiForecastEdexDao;

/**
 *
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
public class TsunamiForecastsRequestHandler
        implements IRequestHandler<TsunamiForecastsRequest> {

    @Override
    public Object handleRequest(TsunamiForecastsRequest request)
            throws Exception {

        TsunamiForecastsResponse response = new TsunamiForecastsResponse();
        if (request == null) {
            return response;
        }

        String customId = request.getPhysicalEventCustomId();
        TsunamiForecastType type = request.getFcstType();
        Date refTime = request.getFcstRunTime();

        TsunamiForecastEdexDao dao = new TsunamiForecastEdexDao(
                TsunamiForecast.PLUGIN_NAME);

        List<TsunamiForecast> fcsts = dao.getTsunamiForecasts(customId, type,
                refTime);

        response.setFcsts(fcsts);

        return response;
    }

}
