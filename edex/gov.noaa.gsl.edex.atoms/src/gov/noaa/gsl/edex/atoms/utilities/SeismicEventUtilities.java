/**
 *  This software was developed and / or modified by the
     * National Oceanic and Atmospheric Administration (NOAA),
     * Global Systems Laboratory (GSL),
     * Evaluation & Decision Support Division (EDS),
     * Weather Information Systems Evolution Branch (WISE)
     *
     * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
     */
package gov.noaa.gsl.edex.atoms.utilities;

import java.util.ArrayList;
import java.util.List;

import ucar.ma2.Array;
import ucar.ma2.Index;
import ucar.ma2.Range;
import ucar.ma2.Section;
import ucar.nc2.NetcdfFile;
import ucar.nc2.Variable;

/**
 * A class with utilities for seismic events
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Dec 13, 2021        Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */

public class SeismicEventUtilities {
    private static final String DIST_TO_COAST_FILE = "/awips2/edex/dist2coast_01deg.nc";

    private static final String DIST_VAR = "dist";

    /**
     * Returns distance to coastline, in km. Positive means OFFshore, negative
     * means ONshore.
     *
     * @param lon
     *            Degrees -180 <= lon < 180
     * @param lat
     *            Degrees -90 < lat <= 90
     * @return
     */
    public static Integer getDistanceToCoastline(float lon, float lat) {

        if (lon < -180 || lon >= 180 || lat <= -90 || lat > 90) {
            return null;
        }

        // In the file, lon goes from -180 to 180, and lat goes from
        // 90 to -90

        // Do some rounding.
        // 12.6577 = 1266; 12.6544 = 1265; -12.6577 = -1266
        int lonIndex = (int) ((lon >= 0 ? (lon * 100 + 0.5)
                : (lon * 100 - 0.5)));
        // Make X in range 0 .. 35999
        lonIndex += 18000;

        // Since the lon/index values go from 90/0 to -90/18000
        lat = -lat;
        // Make Y in range 0 .. 17999
        int latIndex = (int) ((lat >= 0 ? (lat * 100 + 0.5)
                : (lat * 100 - 0.5)));
        latIndex += 9000;

        NetcdfFile ncfile = null;
        try {
            ncfile = NetcdfFile.open(DIST_TO_COAST_FILE);
            Variable v = ncfile.findVariable(DIST_VAR);
            if (v == null) {
                return null;
            }
            List ranges = new ArrayList();
            ranges.add(new Range(latIndex, latIndex));
            ranges.add(new Range(lonIndex, lonIndex));
            Array data = v.read(new Section(ranges));

            // Assume shape is [0, 0]
            Index dataIndex = data.getIndex();
            int distance = data.getShort(dataIndex.set(0, 0));
            return distance;

        } catch (Exception e) {
            System.err.println(SeismicEventUtilities.class.getName()
                    + " received exception while accessing Netcdf file ("
                    + DIST_TO_COAST_FILE + "). ");
            e.printStackTrace(System.err);
            return null;
        } finally {
            try {
                ncfile.close();
            } catch (Exception e) {
            }
        }
    }

    public static void main(String args[]) {

        float lat = 40.3F;
        float lon = -124.7F;
        int km = getDistanceToCoastline(lon, lat);
        System.out.println("Dist to Coast = " + km
                + (km >= 0 ? " km OFFshore" : " km ONshore"));
    }

//    public static void main(String args[]) throws Exception {
//        File directory = new File(
//                "/home/awips/code/tsunami/edex/gov.noaa.gsl.edex.atoms/test/resources");
//        File[] fileList = directory.listFiles();
//
//        File mvScriptFile = new File(
//                "/home/awips/code/tsunami/edex/gov.noaa.gsl.edex.atoms/test/resources/"
//                        + "moveEmTORP");
//        PrintWriter mvScriptWriter = new PrintWriter(
//                new FileOutputStream(mvScriptFile));
//
//        for (File infile : fileList) {
//            if (infile.getName().startsWith("tfsTest")
//                    && infile.getName().endsWith(".xml")) {
//                System.err.println("fileName = " + infile.getName());
//                SAXReader builder = new SAXReader();
//                Document document = builder.read(infile);
//                Element atomsEventDataElement = document.getRootElement();
//                Element latElem = atomsEventDataElement.element("Latitude");
//                Element lonElem = atomsEventDataElement.element("Longitude");
//                float lat = Float.parseFloat(latElem.getText());
//                float lon = Float.parseFloat(lonElem.getText());
//                int distToCoastKm = getDistanceToCoastline(lon, lat);
//                String locName = "";
//
//                Element dataRecordElem = atomsEventDataElement
//                        .element("atomsEventDataRecord");
//                if (dataRecordElem.element("LocationName") != null) {
//                    locName = dataRecordElem.element("LocationName").getText();
//                }
//
//                File outFile = new File(
//                        "/home/awips/code/tsunami/edex/gov.noaa.gsl.edex.atoms/test/resources/"
//                                + infile.getName() + ".tmp");
//                PrintWriter writer = new PrintWriter(
//                        new FileOutputStream(outFile));
//                BufferedReader inFileReader = new BufferedReader(
//                        new InputStreamReader(new FileInputStream(infile)));
//                String line = inFileReader.readLine();
//                while (line != null) {
//                    if (line.contains("<atomsEventDataRecord>")) {
//                        writer.println("  <LocationName>" + locName
//                                + "</LocationName>");
//                        writer.println("  <DistanceToCoast>" + distToCoastKm
//                                + "</DistanceToCoast>");
//                    }
//                    if (!line.contains("LocationName")) {
//                        writer.println(line);
//                    }
//                    line = inFileReader.readLine();
//                }
//                inFileReader.close();
//                writer.flush();
//                writer.close();
//
//                mvScriptWriter.println("mv " + outFile.getName() + " "
//                        + infile.getName() + ";");
//                // Test optional locName, localLocaName + region
//            }
//        }
//        mvScriptWriter.flush();
//        mvScriptWriter.close();
//    }
}
