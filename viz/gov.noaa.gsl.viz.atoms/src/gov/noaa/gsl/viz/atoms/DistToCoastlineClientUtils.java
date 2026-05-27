package gov.noaa.gsl.viz.atoms;

import com.raytheon.uf.viz.core.requests.ThriftClient;

import gov.noaa.gsl.common.dataplugin.atoms.request.DistToCoastlineRequest;
import gov.noaa.gsl.common.dataplugin.atoms.response.DistToCoastlineResponse;

public class DistToCoastlineClientUtils {

    /**
     * Allowed ranges show below.
     * 
     * Returns the distance to the nearest coastline, in km. The return value is
     * a negative number if the lon/lat is over land / onshore, and a positive
     * number if the lon/lat is over the ocean / offshore.
     * 
     * @param lon
     *            -180 =< lon < 180
     * @param lat
     *            -90 < lat <= 90
     * @return null if out of bounds or if there's a problem.
     */
    public static Integer getDistToCoastKm(float lon, float lat) {

        DistToCoastlineRequest request = new DistToCoastlineRequest(lon, lat);

        try {
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof DistToCoastlineResponse) {
                DistToCoastlineResponse distResponse = (DistToCoastlineResponse) response;
                if (distResponse.getDistanceInKm() != null) {
                    return distResponse.getDistanceInKm();
                }
            }
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }
        return null;
    }
}
