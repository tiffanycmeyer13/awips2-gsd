package gov.noaa.nssl.edex.plugin.phiplume.impl;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;

//import org.opengis.feature.Property;
//import org.opengis.feature.simple.SimpleFeature;
//import org.opengis.feature.simple.SimpleFeatureType;
//import org.opengis.geometry.BoundingBox;
import org.geotools.api.feature.Property;
import org.geotools.api.feature.simple.SimpleFeature;
import org.geotools.api.feature.simple.SimpleFeatureType;
import org.geotools.api.geometry.BoundingBox;
import org.geotools.data.memory.MemoryFeatureCollection;
import org.geotools.data.simple.SimpleFeatureIterator;
import org.geotools.data.store.DataFeatureCollection;
import org.geotools.feature.simple.SimpleFeatureTypeBuilder;
import org.geotools.geometry.jts.ReferencedEnvelope;
import org.geotools.referencing.crs.DefaultGeographicCRS;
import org.locationtech.jts.geom.Geometry;

/**
 * GeoJSONFeatureCollection: FeatureCollection class for GeoJSON files
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date           Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jun 27, 2016   17912      pwang       Initial creation
 *
 * </pre>
 *
 * @author pwang
 * @version 1.0
 */

public class GeoJSONFeatureCollection extends DataFeatureCollection {

    protected List<MemoryFeatureCollection> colls;

    public GeoJSONFeatureCollection(List<MemoryFeatureCollection> mcolls) {
        this.colls = mcolls;
    }

    @Override
    protected Iterator<SimpleFeature> openIterator() throws IOException {
        return new GeoJSONFeatureIterator();
    }

    @SuppressWarnings({ "rawtypes" })
    @Override
    public boolean removeAll(Collection arg0) {
        Iterator<MemoryFeatureCollection> i = colls.iterator();
        boolean rval = false;
        while (i.hasNext()) {
            rval = rval || i.next().removeAll(arg0);
        }
        return rval;
    }

    @SuppressWarnings("rawtypes")
    @Override
    public boolean retainAll(Collection arg0) {
        Iterator<MemoryFeatureCollection> i = colls.iterator();
        boolean rval = false;
        while (i.hasNext()) {
            rval = rval || i.next().retainAll(arg0);
        }
        return rval;
    }

    @Override
    public <T> T[] toArray(T[] array) {
        List<Object> rval = new ArrayList<Object>();
        Iterator<SimpleFeature> i = this.iterator();
        while (i.hasNext()) {
            rval.add(i.next());
        }
        return rval.toArray(array);
    }

    @Override
    public SimpleFeatureType getSchema() {
        Iterator<SimpleFeature> iterator = iterator();
        SimpleFeature sf = null;
        if (iterator.hasNext()) {
            sf = iterator.next();
        } else {
            return null;
        }

        if (sf.getFeatureType() != null) {
            // Assume GeoJSON contains only one schema for all features in a
            // GeoJSON file
            return sf.getFeatureType();
        }

        // If the FeatureType is null, build one

        SimpleFeatureTypeBuilder typeBuilder = new SimpleFeatureTypeBuilder();

        // Set feature type name
        typeBuilder.setName(sf.getName());

        // Set feature type CRS
        typeBuilder.setCRS(DefaultGeographicCRS.WGS84);

        // Set geometry
        Geometry geo = (Geometry) sf.getDefaultGeometry();
        typeBuilder.setDefaultGeometry("the_geom");
        typeBuilder.add("the_geom", geo.getClass());

        // Set columns
        List<Property> props = (List<Property>) sf.getProperties();
        for (Property p : props) {
            if (p.getName() != null && p.getValue() != null) {
                typeBuilder.add(p.getName().toString(),
                        p.getValue().getClass());
            }
        }

        SimpleFeatureType type = typeBuilder.buildFeatureType();
        return type;

    }

    private class GeoJSONFeatureIterator implements Iterator<SimpleFeature> {

        protected int curr = 0;

        protected SimpleFeatureIterator iter;

        @Override
        public boolean hasNext() {
            if ((iter != null) && iter.hasNext()) {
                return true;
            }
            while (curr < colls.size()) {
                if (iter != null) {
                    iter.close();
                }
                iter = colls.get(curr++).features();
                if (iter.hasNext()) {
                    return true;
                }
            }

            if (iter != null) {
                iter.close();
            }
            return false;
        }

        @Override
        public SimpleFeature next() {
            if (hasNext()) {
                return iter.next();
            } else {
                return null;
            }

        }

        @Override
        public void remove() {
            // not supported

        }

    }

    @Override
    public ReferencedEnvelope getBounds() {
        Iterator<SimpleFeature> iterator = iterator();
        ReferencedEnvelope rval = null;
        if (iterator.hasNext()) {
            SimpleFeature sf = iterator.next();
            BoundingBox bbox = sf.getBounds();
            rval = new ReferencedEnvelope(bbox);
        }
        while (iterator.hasNext()) {
            SimpleFeature sf = iterator.next();
            BoundingBox bbox = sf.getBounds();
            rval.expandToInclude(new ReferencedEnvelope(bbox));
        }
        if (rval == null) {
            rval = new ReferencedEnvelope();
        }
        return rval;
    }

    @Override
    public int getCount() throws IOException {
        int count = 0;
        Iterator<SimpleFeature> iterator = iterator();
        try {
            while (iterator.hasNext()) {
                iterator.next();
                count++;
            }
        } finally {
            close(iterator);
        }

        return count;
    }

}
