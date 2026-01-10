package gov.noaa.gsl.edex.atomsForecast.utilities;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.raytheon.uf.common.dataaccess.util.DatabaseQueryUtil;
import com.raytheon.uf.common.dataaccess.util.DatabaseQueryUtil.QUERY_MODE;

import gov.noaa.gsl.common.dataplugin.atomsForecast.PtwcWarningPoint;

public class WarningPointsRetriever {

    private static final Logger logger = LoggerFactory
            .getLogger(WarningPointsRetriever.class);

    public Map<String, PtwcWarningPoint> getPtwcWarningPoints() {
        Map<String, PtwcWarningPoint> wngPts = new HashMap<>();
        // It seems we're limited to 4 query fields? Whuh?
        String queryString = "SELECT customid, name, country, domain FROM mapdata.ptwc_warning_points";
        try {
            List<Object[]> queryResults = DatabaseQueryUtil
                    .executeDatabaseQuery(QUERY_MODE.MODE_SQLQUERY, queryString,
                            "maps", "warning_points");
            if ((queryResults != null) && !queryResults.isEmpty()) {
                for (Object[] result : queryResults) {
                    PtwcWarningPoint wngPt = new PtwcWarningPoint();
                    wngPt.setCustomId(((String) result[0]).toUpperCase());
                    wngPt.setName((String) result[1]);
                    wngPt.setCountry((String) result[2]);
                    wngPt.setDomain(((String) result[3]).toUpperCase());

                    wngPts.put(wngPt.getCustomId(), wngPt);
                }
            }
        } catch (Exception e) {
            logger.error(getClass().getName()
                    + "::getPtwcWarningPoints() could not execute SQL query "
                    + " against maps.mapdata.ptwc_warning_points. Returning empty map.");
        }
        return wngPts;
    }
}
