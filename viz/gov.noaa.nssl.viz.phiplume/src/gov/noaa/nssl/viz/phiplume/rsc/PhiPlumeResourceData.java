package gov.noaa.nssl.viz.phiplume.rsc;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataquery.requests.RequestConstraint;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.rsc.AbstractRequestableResourceData;
import com.raytheon.uf.viz.core.rsc.AbstractVizResource;
import com.raytheon.uf.viz.core.rsc.LoadProperties;

import gov.noaa.nssl.common.dataplugin.phiplume.AbstractPhiPlumeRecord;
import jakarta.xml.bind.annotation.XmlAccessType;
import jakarta.xml.bind.annotation.XmlAccessorType;
import jakarta.xml.bind.annotation.XmlAttribute;

@XmlAccessorType(XmlAccessType.NONE)
public class PhiPlumeResourceData extends AbstractRequestableResourceData {

    @XmlAttribute
    private String displayName = "PHI Plume Tool";

    @XmlAttribute(required = false)
    protected String name;

    @XmlAttribute(required = false)
    protected boolean hideSampling;

    protected Collection<AbstractPhiPlumeRecord> records;

    @Override
    protected AbstractVizResource<?, ?> constructResource(
            LoadProperties loadProperties, PluginDataObject[] objects)
            throws VizException {

        PhiPlumeResource rsc = new PhiPlumeResource(this, loadProperties);
        records = new ArrayList<>(objects.length);
        if (objects.length > 0) {
            for (int i = 0; i < objects.length; i++) {
                records.add((AbstractPhiPlumeRecord) objects[i]);
            }
        }
        return new PhiPlumeResource(this, loadProperties);

    }

    @Override
    public boolean equals(Object obj) {

        if (!super.equals(obj)) {
            return false;
        }

        if (obj instanceof PhiPlumeResourceData == false) {
            return false;
        } else {
            return true;
        }

    }

    public String getDisplayName() {
        return displayName;
    }

    @Override
    public HashMap<String, RequestConstraint> getMetadataMap() {
        return metadataMap;
    }

}