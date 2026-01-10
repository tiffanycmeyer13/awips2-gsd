package gov.noaa.gsl.edex.atoms.utilities;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gov.noaa.gsl.common.dataplugin.atoms.ReverseTTTRegion;
import ucar.ma2.Array;
import ucar.ma2.Index;
import ucar.ma2.Range;
import ucar.ma2.Section;
import ucar.nc2.Dimension;
import ucar.nc2.NetcdfFile;
import ucar.nc2.Variable;

public class ReverseTTTUtilities {

    private static final Logger logger = LoggerFactory
            .getLogger(ReverseTTTUtilities.class);

    private static Map<ReverseTTTRegion, String> FILENAMES = new HashMap<>();

    static {
        FILENAMES.put(ReverseTTTRegion.HAWAII,
                "/awips2/edex/HawaiiReverseTTT.grd");
        FILENAMES.put(ReverseTTTRegion.GUAM, "/awips2/edex/GuamReverseTTT.grd");
        FILENAMES.put(ReverseTTTRegion.AMSAM,
                "/awips2/edex/AmSamReverseTTT.grd");
        FILENAMES.put(ReverseTTTRegion.PRVI, "/awips2/edex/PRVIReverseTTT.grd");
    }

    /**
     * @param lon
     *            Degrees -180 <= lon < 180
     * @param lat
     *            Degrees -90 < lat <= 90
     * @param region
     * @return
     */
    public static float getTravelTime(float lon, float lat,
            ReverseTTTRegion region) {
        if (lon < -180 || lon >= 180 || lat <= -90 || lat > 90) {
            return Float.NaN;
        }

        if (lon < 0.0f) {
            lon = lon + 360f;
        }
        NetcdfFile ncfile = null;
        try {
            ncfile = NetcdfFile.open(FILENAMES.get(region));
            // z = hours
            Variable v = ncfile.findVariable("z");
            if (v == null) {
                return Float.NaN;
            }
            Dimension latDim = v.getDimension(0);
            Dimension lonDim = v.getDimension(1);

            int latIndex = (int) (((lat + 90.0) / 180.0) * latDim.getLength()
                    + 0.5);
            int lonIndex = (int) ((lon / 360.0) * lonDim.getLength() + 0.5);

            List ranges = new ArrayList();
            ranges.add(new Range(latIndex, latIndex));
            ranges.add(new Range(lonIndex, lonIndex));
            Array data = v.read(new Section(ranges));

            // Assume shape is [0, 0]
            Index dataIndex = data.getIndex();
            float hours = data.getFloat(dataIndex.set(0, 0));
            return hours;
        } catch (Exception e) {
            logger.error(ReverseTTTUtilities.class.getName()
                    + " received exception while accessing grd file ("
                    + FILENAMES.get(region) + "). ");
            e.printStackTrace(System.err);
            logger.error(ReverseTTTUtilities.class.getName()
                    + " received exception while accessing grd file ("
                    + FILENAMES.get(region) + "). ");
            e.printStackTrace(System.out);
        } finally {
            try {
                ncfile.close();
            } catch (Exception e) {
            }
        }
        return Float.NaN;
    }
}
