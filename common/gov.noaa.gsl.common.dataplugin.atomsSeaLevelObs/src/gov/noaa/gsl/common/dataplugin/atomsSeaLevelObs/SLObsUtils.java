package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class SLObsUtils {

    /**
     * Returns the most recent SLObs for any given station. Only the most recent
     * for each station will be included in the result.
     *
     * @param seaLevelObssList
     * @return
     */
    public static Collection<SeaLevelObs> getMostRecentSLObsSet(
            List<SeaLevelObservations> seaLevelObssList) {
        Map<String, SeaLevelObs> obsMap = new HashMap<>();
        for (SeaLevelObservations obsSet : seaLevelObssList) {
            for (SeaLevelObs thisObs : obsSet.getSeaLevelObs()) {
                String stnId = thisObs.getStation().getCustomId();
                if (!obsMap.containsKey(stnId)) {
                    obsMap.put(stnId, thisObs);
                } else {
                    SeaLevelObs existingObs = obsMap.get(stnId);
                    // If thisObs is more recent, then use it instead of an
                    // older one
                    if (thisObs.getStartTime().getTime() >= existingObs
                            .getStartTime().getTime()) {
                        obsMap.remove(stnId);
                        obsMap.put(stnId, thisObs);
                    }
                }
            }
        }

        List<SeaLevelObs> result = new ArrayList<>(obsMap.size());
        for (Map.Entry<String, SeaLevelObs> thisEntry : obsMap.entrySet()) {
            result.add(thisEntry.getValue());
        }
        return result;
    }
}
