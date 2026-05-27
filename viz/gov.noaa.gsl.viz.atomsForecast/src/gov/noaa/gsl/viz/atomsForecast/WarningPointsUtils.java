package gov.noaa.gsl.viz.atomsForecast;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import com.raytheon.uf.viz.core.requests.ThriftClient;

import gov.noaa.gsl.common.dataplugin.atomsForecast.PtwcWarningPoint;
import gov.noaa.gsl.common.dataplugin.atomsForecast.request.WarningPointsRequest;
import gov.noaa.gsl.common.dataplugin.atomsForecast.response.WarningPointsResponse;

public class WarningPointsUtils {

    private static Map<String, PtwcWarningPoint> wngPointsMap = null;

    /**
     * Returns a map containing keys, or really customIDs, for all PTWC warning
     * points.
     *
     * @return
     */
    private static Map<String, PtwcWarningPoint> getWarningPoints() {

        if (wngPointsMap != null) {
            return wngPointsMap;
        }

        try {
            WarningPointsRequest request = new WarningPointsRequest();
            Object response = ThriftClient.sendRequest(request);
            if (response instanceof WarningPointsResponse) {
                WarningPointsResponse warningPointsResponse = (WarningPointsResponse) response;
                wngPointsMap = warningPointsResponse.getWarningPoints();
                wngPointsMap = Collections.unmodifiableMap(wngPointsMap);
            }
        } catch (Exception e) {
            System.err.print(e);
            return new HashMap<>();
        }

        return wngPointsMap;
    }

    public static boolean isWarningPoint(String customID) {
        Map<String, PtwcWarningPoint> warningPoints = getWarningPoints();
        if (warningPoints != null && warningPoints.containsKey(customID)) {
            return true;
        }
        return false;
    }

    public static boolean isWarningPoint(String customID, String domain) {
        if (domain == null) {
            domain = "";
        }
        Map<String, PtwcWarningPoint> warningPoints = getWarningPoints();
        if (warningPoints != null && warningPoints.containsKey(customID)) {
            return warningPoints.get(customID).getDomain().equals(domain);
        }
        return false;
    }

    public static PtwcWarningPoint getWarningPoint(String customID) {
        Map<String, PtwcWarningPoint> warningPoints = getWarningPoints();
        return warningPoints.get(customID);
    }

}
