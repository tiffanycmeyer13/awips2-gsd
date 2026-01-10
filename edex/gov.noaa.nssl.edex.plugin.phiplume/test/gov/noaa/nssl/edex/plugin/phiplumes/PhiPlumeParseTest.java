package gov.noaa.nssl.edex.plugin.phiplumes;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;

import org.geotools.api.feature.Property;
import org.geotools.api.feature.simple.SimpleFeature;
import org.geotools.data.memory.MemoryFeatureCollection;
import org.geotools.data.simple.SimpleFeatureIterator;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.raytheon.uf.common.json.JsonException;
import com.raytheon.uf.common.json.geo.IGeoJsonService;
import com.raytheon.uf.common.json.geo.SimpleGeoJsonService;
import com.raytheon.uf.common.time.util.TimeUtil;

import gov.noaa.nssl.common.dataplugin.phiplume.impl.PhiPlumeObject;
import gov.noaa.nssl.edex.plugin.phiplume.impl.GeoJSONFeatureCollection;
import gov.noaa.nssl.edex.plugin.phiplume.impl.GeoJSONFile;

public class PhiPlumeParseTest {
    private static GeoJSONFeatureCollection features;

    private static final String decimalFormatStr = "#";

    public static void main(String[] args) throws Exception {

        // Initialize DecimalFormat object to format data for each shape
        DecimalFormat df = new DecimalFormat(decimalFormatStr);
        df.setMaximumFractionDigits(0);
        boolean ok = true;
        File gjson = new File(
        // "/run/media/awips/MAX/transfer_20220502/lightning-PHI-Plumes-valid-20191021014800-created-20220502194649.json");
        // "/home/awips/code/PhiPlumes_20240718/KOAX/severe-PHI-Plumes-valid-20240521195800-created-20240718193938.json");
//                "/home/awips/code/phi_Interpolated_QC_Sev_20250709_123800.geojson");
//                "/home/awips/code/phi_Rec_QC_Sev_20250709_123800.geojson");
//                "/data_store/PHI/geojsons/QC/recommenders/phi_Rec_QC_Sev_20250912_201000.geojson");

//                "/data_store/PHI/geojsons/QC/interpolated_objects/phi_Interpolated_QC_Sev_20251006_224600.geojson");
                "/home/awips/code/DeleteMe/QC/interpolated_objects/phi_Interpolated_QC_Sev_20250517_200800.geojson");

        try {
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> jsonMap = mapper.readValue(gjson, Map.class);
            Map<String, Object> fileValidTimeMap = (Map<String, Object>) jsonMap
                    .get("fileValidTime");
            System.out.println("fileValidTime: " + fileValidTimeMap);
            Object fileValidEpoch = fileValidTimeMap.get("unixEpoch");
            System.out.println("Class??? " + fileValidEpoch.getClass());
            System.out.println("\t" + fileValidEpoch);
            if (fileValidEpoch.getClass() == Integer.class) {
                fileValidEpoch = fileValidEpoch.toString();
            }
            System.out.println(
                    "\tepoch: " + string2Date((String) fileValidEpoch));

        } catch (FileNotFoundException e) {
            System.out.println(
                    "GeoJSON file is not find: " + gjson.getAbsolutePath());
            e.printStackTrace();
            ok = false;
        } catch (IOException ioe) {
            System.out.println("Create InputStream failed for the file: "
                    + gjson.getAbsolutePath());
            ioe.printStackTrace();
            ok = false;
        }

        try (InputStream is = new FileInputStream(gjson)) {
            System.out.println("In Try");
            System.out.println("is: " + is);
            if (is != null) {
//                JsonService json = new BasicJsonService();
//                Map<String, Object> map = (Map<String, Object>) json
//                        .deserialize(is, LinkedHashMap.class);

                IGeoJsonService geojson = new SimpleGeoJsonService();
                List<MemoryFeatureCollection> colls = new ArrayList<MemoryFeatureCollection>();

                colls.add((MemoryFeatureCollection) geojson
                        .deserializeFeatureCollection(is));

                features = new GeoJSONFeatureCollection(colls);
                System.out.println("FEATURES-0: " + features);

                // Use GeoJSONFile plugin to parse PhiPlume file in GeoJSON
                // format
                System.out.println(gjson.getName());
                GeoJSONFile decoded = new GeoJSONFile(gjson);

                // Try decoding and populate PhiPlumeObjects
                GeoJSONFeatureCollection features = decoded.getFeatures();

                SimpleFeatureIterator featureIterator = features.features();

                // Initialize PhiPlumeObject array
                List<PhiPlumeObject> shapes = new ArrayList<PhiPlumeObject>();

//                    // Begin Decoding and Populating PhiPlume Objects
//                    try {

                while (featureIterator.hasNext()) {
                    SimpleFeature feature = featureIterator.next();
                    // System.out.println("\nFeature: " + feature);
                    List<Object> attributes = feature.getAttributes();

                    for (Property p : feature.getProperties()) {
                        System.out.print("\t" + p.getName());
                        if (p.getValue() instanceof java.util.LinkedHashMap) {
                            LinkedHashMap dataVals = (LinkedHashMap) p
                                    .getValue();

                            System.out.println("\t: " + dataVals);
//                            dataVals.forEach((key, value) -> System.out.println(
//                                    "Key: " + key + ", Value: " + value));
                            for (Object key : dataVals.keySet()) {
                                Object value = dataVals.get(key);

                                System.out.print("Key: " + key + ", Value");
                                if (value != null) {
                                    System.out.print(
                                            " (" + value.getClass() + ")");
                                }
                                System.out.println(": " + value);

                            }
                        } else {
                            System.out.println(" : " + p.getValue());
                        }
                    }
                    System.out.println("\n");

//                    for (Object attr : attributes) {
//                        System.out.println("\t" + attr);
//                    }
                    System.out.println("================\n");
                }

            }
        } catch (FileNotFoundException e) {
            System.out.println(
                    "GeoJSON file is not find: " + gjson.getAbsolutePath());
            e.printStackTrace();
            ok = false;
        } catch (JsonException je) {
            System.out.println(
                    "decoding json failed: " + gjson.getAbsolutePath());
            je.printStackTrace();
            ok = false;
        } catch (IOException ioe) {
            System.out.println("Create InputStream failed for the file: "
                    + gjson.getAbsolutePath());
            ioe.printStackTrace();
            ok = false;
        }
    }

    public static Date string2Date(String string) {
        // Initialize DecimalFormat object to format data for each shape
        DecimalFormat df = new DecimalFormat(decimalFormatStr);
        df.setMaximumFractionDigits(0);
        string = padRightZeros(string, 13);
        Calendar c = TimeUtil.newCalendar();
        c.setTimeInMillis(Long.valueOf(string));
        c.setTimeZone(TimeZone.getTimeZone("GMT"));
        return c.getTime();
    }

    public static String padRightZeros(String inputString, int length) {
        if (inputString.length() >= length) {
            if (inputString.length() > length) {
                inputString = inputString.substring(0, length);
            }
            return inputString;
        }
        StringBuilder sb = new StringBuilder();
        sb.append(inputString);
        while (sb.length() < length) {
            sb.append('0');
        }
        // sb.append(inputString);

        return sb.toString();
    }

//    try {
//	File file = new File("/home/awips/HWT-2022/vectorPHIPlumes/shakedownFiles/severe-PHI-Plumes-valid-20210326015200-created-20220408201612.json");
//
//	GeoJSONFile decoded = new GeoJSONFile(file);
//
//	System.out.println(decoded.getCount());
//	GeoJSONFeatureCollection features = decoded.getFeatures();
//	SimpleFeatureIterator i = features.features();
//
//	System.out.println(decoded.getFeatures().getSchema());
//
//	int count = 1;
//	while (i.hasNext()) {
//		SimpleFeature feature = i.next();
//		System.out.println(feature.getProperty("canceled").getValue().toString());
//		count += 1;
//	}
//
//
//    } catch (Throwable e) {
//        // TODO Auto-generated catch block
//        e.printStackTrace();
//    }
}
