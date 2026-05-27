package gov.noaa.gsl.common.dataplugin.atomsImagery.response;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atomsImagery.TfsImageryDescriptor;

@DynamicSerialize
public class TfsImageryDescriptorsResponse {

    @DynamicSerializeElement
    private List<TfsImageryDescriptor> descriptors = new ArrayList<>();

    public TfsImageryDescriptorsResponse() {
    }

    public List<TfsImageryDescriptor> getDescriptors() {
        return descriptors;
    }

    public void setDescriptors(List<TfsImageryDescriptor> descs) {
        if (descs == null) {
            descs = new ArrayList<>();
        }

        this.descriptors = descs;
    }
}
