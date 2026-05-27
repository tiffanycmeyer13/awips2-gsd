package gov.noaa.gsl.common.dataplugin.atoms.request;

import java.util.HashSet;
import java.util.Set;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;
import com.raytheon.uf.common.serialization.comm.IServerRequest;

import gov.noaa.gsl.common.dataplugin.atoms.ReverseTTTRegion;

@DynamicSerialize
public class ReverseTTTRequest implements IServerRequest {

    @DynamicSerializeElement
    private Set<ReverseTTTRegion> requestedRegions = new HashSet<>();

    @DynamicSerializeElement
    private Float longitude;

    @DynamicSerializeElement
    private Float latitude;

    /**
     * If you don't have a default constructor, the server fails silently. No
     * surprise there.
     */
    public ReverseTTTRequest() {
    }

    public ReverseTTTRequest(Float lon, Float lat) {
        this.longitude = lon;
        this.latitude = lat;
    }

    public void addRequestedRegion(ReverseTTTRegion requestedRegion) {
        if (requestedRegion != null) {
            requestedRegions.add(requestedRegion);
        }
    }

    public void setRequestedRegions(Set<ReverseTTTRegion> requestedRegions) {
        if (requestedRegions != null) {
            this.requestedRegions = requestedRegions;
        }
    }

    public Set<ReverseTTTRegion> getRequestedRegions() {
        return requestedRegions;
    }

    public Float getLongitude() {
        return longitude;
    }

    public void setLongitude(Float longitude) {
        this.longitude = longitude;
    }

    public Float getLatitude() {
        return latitude;
    }

    public void setLatitude(Float latitude) {
        this.latitude = latitude;
    }

    public void setLonLat(Float lon, Float lat) {
        this.longitude = lon;
        this.latitude = lat;
    }
}
