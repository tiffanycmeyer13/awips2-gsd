package gov.noaa.gsl.common.dataplugin.atoms.response;

import java.util.HashMap;
import java.util.Map;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atoms.ReverseTTTRegion;

@DynamicSerialize
public class ReverseTTTResponse {

    @DynamicSerializeElement
    private Map<ReverseTTTRegion, Float> allTravelTimesHours = new HashMap<>();

    /**
     * If you don't have a default constructor, the server fails silently. No
     * surprise there.
     */
    public ReverseTTTResponse() {
    }

    public void setTravelTimeHours(ReverseTTTRegion region, float hours) {
        if (region != null) {
            allTravelTimesHours.put(region, hours);
        }
    }

    public void setAllTravelTimesHours(Map<ReverseTTTRegion, Float> tttHours) {
        if (tttHours != null) {
            this.allTravelTimesHours = tttHours;
        }
    }

    /**
     * May return NULL if the region isnt included in this response.
     *
     * @param region
     * @return
     */
    public Float getTravelTimeHours(ReverseTTTRegion region) {
        return allTravelTimesHours.get(region);
    }

    public Map<ReverseTTTRegion, Float> getAllTravelTimesHours() {
        return this.allTravelTimesHours;
    }
}
