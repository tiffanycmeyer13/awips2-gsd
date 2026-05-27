package gov.noaa.nssl.edex.plugin.phiplume.impl;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.StringJoiner;
import java.util.TimeZone;

import org.geotools.api.feature.simple.SimpleFeature;
import org.geotools.data.simple.SimpleFeatureIterator;
import org.geotools.geometry.jts.WKTReader2;
import org.locationtech.jts.geom.Geometry;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.time.DataTime;
import com.raytheon.uf.common.time.util.TimeUtil;
import com.raytheon.uf.common.util.Pair;

import gov.noaa.nssl.common.dataplugin.phiplume.AbstractPhiPlumeRecord;
import gov.noaa.nssl.common.dataplugin.phiplume.PhiInterpolatedRecord;
import gov.noaa.nssl.common.dataplugin.phiplume.PhiPlumeRecord;
import gov.noaa.nssl.common.dataplugin.phiplume.impl.PhiPlumeObject;

public class PhiPlumeParser {
    private final IUFStatusHandler statusHandler = UFStatus
            .getHandler(PhiPlumeParser.class);

    private static final String decimalFormatStr = "#";

    // Initialize DecimalFormat object to format data for each shape
    private static DecimalFormat df = new DecimalFormat(decimalFormatStr);

    int currentShape = -1;

    private List<PhiPlumeObject> shapes;

    private Pair<String, String> startEndStrings;

    private Date fileValidTime;

    public PhiPlumeParser() {
    }

    @SuppressWarnings("unchecked")
    public PhiPlumeParser(File file) {
        df.setMaximumFractionDigits(0);
        String fname = file.getName();

        try {
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> jsonMap = mapper.readValue(file, Map.class);
            Map<String, Object> fileValidTimeMap = (Map<String, Object>) jsonMap
                    .get("fileValidTime");
            Object fileValidEpoch = fileValidTimeMap.get("unixEpoch");
            if (fileValidEpoch.getClass() == Integer.class) {
                fileValidEpoch = fileValidEpoch.toString();
            }
            fileValidTime = string2Date((String) fileValidEpoch);

        } catch (FileNotFoundException e) {
            System.out.println(
                    "GeoJSON file is not find: " + file.getAbsolutePath());
            e.printStackTrace();
            fileValidTime = null;
        } catch (IOException ioe) {
            System.out.println("Create InputStream failed for the file: "
                    + file.getAbsolutePath());
            ioe.printStackTrace();
            fileValidTime = null;
        }

        System.out.println("PARSER-0: " + fname);
        if (fname.contains("phi_Interpolated")) {
            startEndStrings = new Pair<>("valid_start", "valid_end");
        } else if (fname.contains("phi_Rec")) {
            startEndStrings = new Pair<>("start_time", "end_time");
        } else {
            startEndStrings = new Pair<>("", "");
        }

        shapes = setData(file);
        if ((shapes != null) && (shapes.size() > 0)) {
            currentShape = 0;
        }
    }

    public List<PhiPlumeObject> getShapes() {
        return shapes;
    }

    public void setShapes(List<PhiPlumeObject> shapes) {
        this.shapes = shapes;
    }

    /**
     * Determines if parser contains any more reports
     *
     * @return Boolean object defining "Does this parser contain any more
     *         reports?"
     */
    public boolean hasNext() {
        boolean next = (shapes != null);
        if (next) {
            next = ((currentShape >= 0) && (currentShape < shapes.size()));
        }
        if (!next) {
            shapes = null;
            currentShape = -1;
        }
        return next;
    }

    /**
     * Gets the next available report and returns a null reference if no more
     * reports are available.
     *
     * @return Next available shape object
     */
    public PhiPlumeObject next() {

        PhiPlumeObject shape = null;
        if (currentShape < 0) {
            return shape;
        }
        if (currentShape >= shapes.size()) {
            shapes = null;
            currentShape = -1;
        } else {
            shape = shapes.get(currentShape++);
        }
        return shape;
    }

    public void setShapeAttributes(SimpleFeature feature,
            PhiPlumeObject shape) {
        // Initialize PhiPlumeObject and populate with contents in
        // properties list

        String start = startEndStrings.getFirst();
        Object validStart = feature.getAttribute(start);
        System.out.println("VALIDSTART: " + start + ", " + validStart);
        shape.setValidStart(df.format(validStart));

        String end = startEndStrings.getSecond();
        Object validEnd = feature.getAttribute(end);
        System.out.println("VALIDEND: " + end + ", " + validEnd);
        shape.setValidEnd(df.format(validEnd));

        Object IDnum = feature.getAttribute("id");
        shape.setIDnum(IDnum.toString());

        Object speed = feature.getAttribute("speed");
        shape.setSpeed(speed.toString());

        Object direction = feature.getAttribute("direction");
        shape.setDirection(direction.toString());

        Object probability = feature.getAttribute("probability");
        shape.setProbability(probability.toString());

        Object bestCSI = feature.getAttribute("best_csi_threshold");
        if (bestCSI != null) {
            shape.setBest_csi_threshold(bestCSI.toString());
        }

        // shape.setHazardType("severe");

    }

    @SuppressWarnings("rawtypes")
    public void setShapeAttributes(LinkedHashMap feature,
            PhiPlumeObject shape) {
        // Initialize PhiPlumeObject and populate with contents in
        // properties list

        String start = startEndStrings.getFirst();
        Object validStart = feature.get(start);
        shape.setValidStart(df.format(validStart));

        String end = startEndStrings.getSecond();
        Object validEnd = feature.get(end);
        shape.setValidEnd(df.format(validEnd));

        Object IDnum = feature.get("id");
        shape.setIDnum(IDnum.toString());

        Object speed = feature.get("Speed");
        shape.setSpeed(speed.toString());

        Object direction = feature.get("Direction");
        shape.setDirection(direction.toString());

        Object probability = feature.get("probs_interp");
        shape.setProbability(probability.toString());

        Object probSevereAttrs = feature.get("ProbSevere");
        System.out.println("PROBSEVERE:" + probSevereAttrs);
        if (probSevereAttrs != null
                && probSevereAttrs.getClass() == LinkedHashMap.class) {
            System.out.println("\tHERE-0" + probSevereAttrs.getClass());
            StringJoiner dataJoiner = new StringJoiner(",");
            for (Map.Entry<String, Object> entry : ((LinkedHashMap<String, Object>) probSevereAttrs)
                    .entrySet()) {
                System.out
                        .println("\t\t" + entry.getKey().replaceAll("\"", ""));
                System.out.println("\t\t\t" + String.valueOf(entry.getValue())
                        .replaceAll("\"", ""));
                String kv = entry.getKey().replaceAll("\"", "") + "::" + (String
                        .valueOf(entry.getValue()).replaceAll("\"", ""));
                dataJoiner.add(kv);

            }
            shape.setProbsevereAttrs(dataJoiner.toString());
        }

        // shape.setHazardType("severe");

    }

    @SuppressWarnings("rawtypes")
    private List<PhiPlumeObject> setData(File file) {

        try {
            // Use GeoJSONFile plugin to parse PhiPlume file in GeoJSON format
            System.out.println(file.getName());
            GeoJSONFile decoded = new GeoJSONFile(file);

            // Try decoding and populate PhiPlumeObjects
            GeoJSONFeatureCollection features = decoded.getFeatures();
            SimpleFeatureIterator featureIterator = features.features();

            // Initialize PhiPlumeObject array
            List<PhiPlumeObject> shapes = new ArrayList<PhiPlumeObject>();

            // Begin Decoding and Populating PhiPlume Objects
            try {

                while (featureIterator.hasNext()) {
                    PhiPlumeObject shape = new PhiPlumeObject();

                    SimpleFeature feature = featureIterator.next();
                    Object polygonWKT = feature.getAttribute("the_geom");
                    shape.setPolygonWKT(polygonWKT.toString());

                    List<Object> attributes = feature.getAttributes();
                    LinkedHashMap dataVals = (LinkedHashMap) feature
                            .getAttribute("data");
                    if (dataVals == null) {
                        setShapeAttributes(feature, shape);
                    } else {
                        setShapeAttributes(dataVals, shape);
                    }

                    // System.out.println("FEATURES-0: " + attributes);

                    shapes.add(shape);
                }
            } finally {
                this.shapes = shapes;
                featureIterator.close();
            }

        } catch (Throwable e) {
            System.out.println("An Error Occured When Parsing PhiPlume File: "
                    + file.toString());
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return shapes;
    }

    public List<AbstractPhiPlumeRecord> getRecords() {
        List<AbstractPhiPlumeRecord> records = new ArrayList<AbstractPhiPlumeRecord>();

        for (PhiPlumeObject shape : shapes) {

            AbstractPhiPlumeRecord tempRecord = null;
            String objectType = null;
            // Init classes for record creation
            if (startEndStrings.getFirst().contains("valid")) {
                tempRecord = new PhiInterpolatedRecord();
                objectType = "interpolatedProbSevereObject";
            } else {
                tempRecord = new PhiPlumeRecord();
                objectType = "recommender";
            }

            tempRecord.setValidStart(string2Date(shape.getValidStart()));
            tempRecord.setValidEnd(string2Date(shape.getValidEnd()));
            tempRecord.setIDnum(shape.getIDnum());
            tempRecord.setSpeed(string2Int(shape.getSpeed()));
            tempRecord.setDirection(string2Int(shape.getDirection()));
            tempRecord.setProbability(string2Int(shape.getProbability()));
            tempRecord.setPolygonWKT(shape.getPolygonWKT());
            tempRecord.setProbsevereAttrs(shape.getProbsevereAttrs());
            tempRecord.setBest_csi_threshold(shape.getBest_csi_threshold());
            tempRecord.setObjectType(objectType);

            try {
                tempRecord.setGeometry(string2Geom(shape.getPolygonWKT()));
            } catch (org.locationtech.jts.io.ParseException e) {
                // TODO Auto-generated catch block
                System.out.println(
                        "FAILED - setting setPolygon() in PhiPlumeRecord with polyWKT = "
                                + shape.getPolygonWKT());
                e.printStackTrace();
            }
            Calendar timeStamp = Calendar.getInstance();
            if (fileValidTime != null) {
                timeStamp.setTime(fileValidTime);
            } else {
                System.err.println(
                        "ERROR [PhiPlumeParer]: fileValidTime is null. Using getValidStart() which may not be accurate for PHI Interpolated ProbSevere Objects");
                timeStamp.setTime(tempRecord.getValidStart());
            }
            timeStamp.setTimeZone(TimeZone.getTimeZone("GMT"));
            tempRecord.setDataTime(new DataTime(timeStamp));

            records.add(tempRecord);
        }
        return records;
    }

    public Integer string2Int(String string) {
        return Integer.valueOf(string);
    }

    public Boolean string2Bool(String string) {
        return Boolean.valueOf(string);
    }

    public Date string2Date(String string) {
        // Initialize DecimalFormat object to format data for each shape
        DecimalFormat df = new DecimalFormat(decimalFormatStr);
        df.setMaximumFractionDigits(0);
        string = padRightZeros(string, 13);
        Calendar c = TimeUtil.newCalendar();
        c.setTimeInMillis(Long.valueOf(string));
        c.setTimeZone(TimeZone.getTimeZone("GMT"));
        return c.getTime();
    }

    public Date string2DateModulo(String string) {
        // Modulo to nearest 2 minute time - needed for lightning plumes to
        // match grid_time of other threats
        DecimalFormat df = new DecimalFormat(decimalFormatStr);
        df.setMaximumFractionDigits(0);
        string = padRightZeros(string, 13);
        Double dateModulo = Double.valueOf(string);
        Double remainder = dateModulo % 120000; // Modulo 2 minutes in
                                                // miliseconds
        Calendar c = TimeUtil.newCalendar();
        string = df.format(dateModulo - remainder);
        c.setTimeInMillis(Long.valueOf(string));
        c.setTimeZone(TimeZone.getTimeZone("GMT"));
        return c.getTime();
    }

    public Geometry string2Geom(String polyWKT)
            throws org.locationtech.jts.io.ParseException {
        WKTReader2 reader = new WKTReader2();
        Geometry poly = null;
        poly = reader.read(polyWKT);
        return poly;
    }

    public Double string2Double(String string) {
        // return Double.valueOf(string);
        return (double) Math.round(Double.valueOf(string));
    }

    public String padRightZeros(String inputString, int length) {
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

}
