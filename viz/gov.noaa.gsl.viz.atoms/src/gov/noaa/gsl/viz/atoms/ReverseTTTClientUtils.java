package gov.noaa.gsl.viz.atoms;

import java.util.HashMap;
import java.util.Map;

import com.raytheon.uf.viz.core.requests.ThriftClient;

import gov.noaa.gsl.common.dataplugin.atoms.ReverseTTTRegion;
import gov.noaa.gsl.common.dataplugin.atoms.request.ReverseTTTRequest;
import gov.noaa.gsl.common.dataplugin.atoms.response.ReverseTTTResponse;

public class ReverseTTTClientUtils {

    public static Map<ReverseTTTRegion, Float> getAllTravelTimeHours(float lon,
            float lat) {
        return ReverseTTTClientUtils.getTravelTimeHours(lon, lat,
                ReverseTTTRegion.values());
    }

    /**
     * Allowed ranges show below.
     *
     * Returns the reverse TTT time in hours from the given lon/lat to the given
     * region.
     *
     * @param lon
     *            -180 =< lon < 180
     * @param lat
     *            -90 < lat <= 90
     * @return null if out of bounds or if there's a problem.
     */
    public static Float getTravelTimeHours(float lon, float lat,
            ReverseTTTRegion region) {

        ReverseTTTRequest request = new ReverseTTTRequest(lon, lat);
        request.addRequestedRegion(region);

        try {
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof ReverseTTTResponse) {
                ReverseTTTResponse tttResponse = (ReverseTTTResponse) response;
                return tttResponse.getTravelTimeHours(region);
            }
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }
        return null;
    }

    public static Map<ReverseTTTRegion, Float> getTravelTimeHours(float lon,
            float lat, ReverseTTTRegion[] regions) {
        Map<ReverseTTTRegion, Float> result = new HashMap<>();
        if (regions != null) {
            ReverseTTTRequest request = new ReverseTTTRequest(lon, lat);
            for (ReverseTTTRegion region : regions) {
                request.addRequestedRegion(region);
            }
            try {
                Object response = ThriftClient.sendRequest(request);
                if (response instanceof ReverseTTTResponse) {
                    ReverseTTTResponse tttResponse = (ReverseTTTResponse) response;
                    for (ReverseTTTRegion region : regions) {
                        Float hrsForRegion = tttResponse
                                .getTravelTimeHours(region);
                        if (hrsForRegion != null) {
                            result.put(region, hrsForRegion);
                        }
                    }
                }
            } catch (Exception e) {
                e.printStackTrace(System.err);
            }
        }
        return result;
    }
}
