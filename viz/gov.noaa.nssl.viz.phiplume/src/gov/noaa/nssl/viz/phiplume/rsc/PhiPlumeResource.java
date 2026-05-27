package gov.noaa.nssl.viz.phiplume.rsc;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.swt.graphics.RGB;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.LineString;
import org.locationtech.jts.geom.Point;
import org.locationtech.jts.geom.prep.PreparedGeometryFactory;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.geospatial.ReferencedCoordinate;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.status.UFStatus.Priority;
import com.raytheon.uf.common.time.DataTime;
import com.raytheon.uf.common.time.SimulatedTime;
import com.raytheon.uf.common.time.util.TimeUtil;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.drawables.IShadedShape;
import com.raytheon.uf.viz.core.drawables.IWireframeShape;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.MapDescriptor;
import com.raytheon.uf.viz.core.rsc.AbstractVizResource;
import com.raytheon.uf.viz.core.rsc.IResourceDataChanged;
import com.raytheon.uf.viz.core.rsc.LoadProperties;
import com.raytheon.uf.viz.core.rsc.capabilities.ColorableCapability;

import gov.noaa.nssl.common.dataplugin.phiplume.AbstractPhiPlumeRecord;
import gov.noaa.nssl.common.dataplugin.phiplume.PhiInterpolatedRecord;
import gov.noaa.nssl.common.dataplugin.phiplume.PhiPlumeRecord;

public class PhiPlumeResource
        extends AbstractVizResource<PhiPlumeResourceData, MapDescriptor> {

    private final IUFStatusHandler statusHandler = UFStatus
            .getHandler(AbstractPhiPlumeRecord.class);

    private Map<DataTime, ArrayList<AbstractPhiPlumeRecord>> unprocessedRecords = new HashMap<DataTime, ArrayList<AbstractPhiPlumeRecord>>();

    private Map<DataTime, ArrayList<AbstractPhiPlumeRecord>> frames = new HashMap<DataTime, ArrayList<AbstractPhiPlumeRecord>>();

    private DataTime displayedDataTime;

    private static boolean isTimeAgnostic = false;

    protected List<AbstractPhiPlumeRecord> records = new ArrayList<>();

    protected final Object paintLock = new Object();

    protected DataTime earliestRequested;

    protected static PreparedGeometryFactory pgf = new PreparedGeometryFactory();

    protected static final String DEFAULT_FORMAT = "HHmm'Z'";

    protected static final String LONG_FORMAT = "HH:mm'Z' EEE ddMMMyy";

    protected static final String DAY_FORMAT = "HH:mm'Z' EEE";

    protected List<AbstractPhiPlumeRecord> recordsToLoad;

    protected String resourceName;

    protected RGB color;

    protected PhiPlumeResource(PhiPlumeResourceData resourceData,
            LoadProperties loadProperties) {
        super(resourceData, loadProperties, isTimeAgnostic);
        resourceData.addChangeListener(new IResourceDataChanged() {
            @Override
            public void resourceChanged(ChangeType type, Object object) {
                if (type == ChangeType.DATA_UPDATE) {
                    PluginDataObject[] pdo = (PluginDataObject[]) object;
                    for (PluginDataObject p : pdo) {
                        if (p instanceof AbstractPhiPlumeRecord) {
                            addRecord((AbstractPhiPlumeRecord) p);
                        }
                    }
                }
                issueRefresh();
            }
        });

        color = getCapability((ColorableCapability.class)).getColor();

    }

    /**
     * Method that declares if the resource is time agnostic. A time agnostic
     * resource does not pertain to time (e.g. static map backgrounds)
     *
     * @return true if resource is time agnostic
     */
    @Override
    public boolean isTimeAgnostic() {
        return isTimeAgnostic;
    }

    /**
     * @see com.raytheon.uf.viz.core.rsc.AbstractVizResource#disposeInternal()
     */
    @Override
    protected void disposeInternal() {
        clearDisplayFrames();
    }

    protected void clearDisplayFrames() {
        synchronized (frames) {
            if (!frames.isEmpty()) {
                frames.clear();
            }
        }
    }

//    @Override
//    protected void initInternal(IGraphicsTarget target) throws VizException {
//        FramesInfo info = descriptor.getFramesInfo();
//        DataTime[] times = info.getFrameTimes();
//
//        if ((times != null) && (times.length > 0)) {
//            // Request data for "earliest" time
//            requestData(times[0]);
//        }
//        // scheduleRefreshTask(this);
//
//    }

//    @SuppressWarnings("unchecked")
//    protected void requestData(DataTime earliest) throws VizException {
//        Map<String, RequestConstraint> map = (Map<String, RequestConstraint>) resourceData
//                .getMetadataMap().clone();
//        if (earliestRequested != null) {
//            // don't request data we've already requested
//            String[] times = { earliest.toString(),
//                    earliestRequested.toString() };
//            RequestConstraint constraint = new RequestConstraint();
//            constraint.setConstraintType(ConstraintType.BETWEEN);
//            constraint.setBetweenValueList(times);
//            map.put("validEnd", constraint);
//        } else {
//            RequestConstraint endConstraint = new RequestConstraint(
//                    earliest.toString(), ConstraintType.GREATER_THAN_EQUALS);
//            map.put("validEnd", endConstraint);
//        }
//
//        earliestRequested = earliest;
//
//        PluginDataObject[] pdos;
//        try {
//            pdos = DataCubeContainer.getData(map);
//        } catch (DataCubeException e) {
//            throw new VizException(e);
//        }
//
//        addRecord(pdos);
//
//    }

    @Override
    public String inspect(ReferencedCoordinate coord) throws VizException {
        ArrayList<AbstractPhiPlumeRecord> frameRecs = null;
        synchronized (frames) {
            frameRecs = frames.get(this.displayedDataTime);
        }
        if (frameRecs == null) {
            return "";
        }

        Coordinate latLon = new Coordinate();
        try {
            latLon = coord.asLatLon();
        } catch (Exception e1) {
            statusHandler.handle(Priority.ERROR,
                    "Error converting ReferencedCoordinate to Lat/Lon", e1);
        }
        GeometryFactory geom = new GeometryFactory();
        Point point = geom.createPoint(latLon);

        StringBuilder sample = new StringBuilder();
        for (AbstractPhiPlumeRecord record : frameRecs) {
            Geometry recordGeom = record.getGeometry();
            if (recordGeom.contains(point)) {
                if (sample.length() > 0) {
                    sample.append("\n");
                }
                sample.append("\nID: " + record.getIDnum());
                sample.append(
                        "\nPHI Probability: " + record.getProbability() + "%");
                String[] formattedStartEndTime = getFormattedDateTime(record,
                        0);
                sample.append("\nStart: " + formattedStartEndTime[0]);
                sample.append("\nEnd: " + formattedStartEndTime[1]);

                if (record.getClass() == PhiPlumeRecord.class) {
                    String bestCSI = record.getBest_csi_threshold();
                    if (bestCSI != null) {
                        sample.append("\n\tBest CSI Threshold:" + bestCSI);
                    }
                }
                if (record.getClass() == PhiInterpolatedRecord.class) {
                    // String joiner = "\u0009"; // Tab but CAVE
                    // doesn't honor
                    String joiner = "     ";
                    int width = 10;
                    String probSevereAttrs = record.getProbsevereAttrs();
                    if (probSevereAttrs != null) {
                        sample.append(
                                "\n\n                 --PROB SVR ATTRS--\n");
                        String[] attrs = probSevereAttrs.split(",");
                        Arrays.sort(attrs);
                        int ctr = 0;
                        ArrayList<String> pairs = new ArrayList<String>();
                        for (String attr : attrs) {
                            String[] kv = attr.split("::");
                            String attVal = kv[0] + ": " + kv[1];
                            pairs.add(attVal);
                            if (ctr % 3 == 0) {
                                if (pairs.size() > 2) {
                                    String thisLine = String.format(
                                            "%-20s%-20s%-20s%n", pairs.get(0),
                                            pairs.get(1), pairs.get(2));
                                    sample.append(thisLine);
                                }
                                pairs.clear();
                            }
                            ctr++;
                        }
                        if (!pairs.isEmpty()) {
                            sample.append(String.join(joiner, pairs));
                        }
                    }
                }

            }
        }
        return sample.toString();
    }

    /**
     * Process all records for the displayedDataTime
     *
     * @param target
     * @param paintProps
     * @throws VizException
     */
    private void updateFrames(IGraphicsTarget target,
            PaintProperties paintProps) throws VizException {
        // Add any new records
        ArrayList<AbstractPhiPlumeRecord> newRecords = null;
        synchronized (unprocessedRecords) {
            newRecords = unprocessedRecords.remove(this.displayedDataTime);
        }
        if (newRecords != null && newRecords.size() > 0) {
            // If record is incomplete, data is missing and it shouldn't be
            // kept.
//            if (newRecord.isRecordComplete()) {
            synchronized (frames) {
//                frames.clear();
                for (AbstractPhiPlumeRecord newRecord : newRecords) {
                    addEvent(frames, this.displayedDataTime, newRecord);
//                frames.put(this.displayedDataTime, newRecord);
//                }
                }
            }
        }
    }

    @Override
    protected void paintInternal(IGraphicsTarget target,
            PaintProperties paintProps) throws VizException {

        this.displayedDataTime = paintProps.getDataTime();

        // First check to see if we need to process new data
        ArrayList<AbstractPhiPlumeRecord> unprocessed = null;
        synchronized (unprocessedRecords) {
            unprocessed = unprocessedRecords.get(this.displayedDataTime);
        }
        if (unprocessed != null) {
            updateFrames(target, paintProps);
        }

        // Hopefully we now have some data to display, if not bail
        ArrayList<AbstractPhiPlumeRecord> frameRecs = null;
        synchronized (frames) {
            frameRecs = frames.get(this.displayedDataTime);
        }
        if (frameRecs == null) {
            this.displayedDataTime = null;
            return;
        } else {
            GeometryFactory geometryFactory = new GeometryFactory();
            IWireframeShape iwfs = target.createWireframeShape(false,
                    descriptor);
            IShadedShape ss = target.createShadedShape(false,
                    descriptor.getGridGeometry());
            for (AbstractPhiPlumeRecord frameRec : frameRecs) {
                Geometry geom = frameRec.getGeometry();
                Coordinate[] geomCoords = geom.getCoordinates();
                iwfs.addLineSegment(geomCoords);
                LineString lineString = geometryFactory
                        .createLineString(geomCoords);
                ss.addPolygon(new LineString[] { lineString },
                        getCapability(ColorableCapability.class).getColor());

            }
//            target.drawWireframeShape(iwfs,
//                    getCapability((ColorableCapability.class)).getColor(), 2);
            target.drawShadedShape(ss, (float) 0.5);
        }

    }

    public static RGB hex2Rgb(String colorStr) {
        return new RGB(Integer.valueOf(colorStr.substring(1, 3), 16),
                Integer.valueOf(colorStr.substring(3, 5), 16),
                Integer.valueOf(colorStr.substring(5, 7), 16));
    }

//    private IWireframeShape createWireframeShapeFromGeometry(Geometry geo,
//            IGraphicsTarget target) throws VizException {
//        IWireframeShape wfs = target.createWireframeShape(false, descriptor);
//
//        JTSCompiler jtsCompiler = new JTSCompiler(null, wfs, descriptor);
//
//        JTSGeometryData geoData = jtsCompiler.createGeometryData();
//        RGB thisColor = getCapability(ColorableCapability.class).getColor();
//        geoData.setGeometryColor(thisColor);
//
//        jtsCompiler.handle(geo, geoData);
//        wfs.compile();
//
//        return wfs;
//    }
//
//    private IShadedShape createShadedShapeFromGeometry(Geometry geo,
//            IGraphicsTarget target) throws VizException {
//        IShadedShape ss = target.createShadedShape(false,
//                descriptor.getGridGeometry());
//
//        JTSCompiler jtsCompiler = new JTSCompiler(ss, null, descriptor);
//
//        JTSGeometryData geoData = jtsCompiler.createGeometryData();
//        RGB thisColor = getCapability(ColorableCapability.class).getColor();
//        geoData.setGeometryColor(thisColor);
//
//        jtsCompiler.handle(geo, geoData);
//        ss.setFillPattern(FillPatterns.getGLPattern("WHOLE"));
//        ss.compile();
//
//        return ss;
//    }

    public void addRecord(AbstractPhiPlumeRecord newRec) {
        DataTime dataTime = newRec.getDataTime();
        if (dataTime != null) {
            synchronized (unprocessedRecords) {
                addEvent(unprocessedRecords, dataTime, newRec);
//                unprocessedRecords.put(dataTime, newRec);
            }
        }
    }

    public static void addEvent(
            Map<DataTime, ArrayList<AbstractPhiPlumeRecord>> map, DataTime date,
            AbstractPhiPlumeRecord event) {

        // See if dataURI is present in list of AbstractPhiPlumeRecord for given
        // date
        if (map == null) {
            map.computeIfAbsent(date, k -> new ArrayList<>()).add(event);
            return;
        }

        ArrayList<AbstractPhiPlumeRecord> records = map.get(date);
        if (records == null) {
            map.computeIfAbsent(date, k -> new ArrayList<>()).add(event);
            return;
        }

        boolean dataURIPresent = false;
        for (AbstractPhiPlumeRecord record : records) {
            if (record.getDataURI().compareTo(event.getDataURI()) == 0) {
                dataURIPresent = true;
                break;
            }
        }
        if (dataURIPresent == false) {
            map.computeIfAbsent(date, k -> new ArrayList<>()).add(event);
            return;
        }

        if (dataURIPresent == false) {
            // Only alert if we get this far and dataURIPresent is not true
            System.err.println("RECORD NOT ADDED TO MAP: " + map.toString()
                    + " :: " + event.getDataURI());
        }
    }

    protected String[] getFormattedDateTime(AbstractPhiPlumeRecord record,
            double mapWidth) {
        String[] textToPrint = { "", "" };
        String startFormatString = DEFAULT_FORMAT;
        String endFormatString = DEFAULT_FORMAT;
        if (mapWidth == 0) {
            startFormatString = LONG_FORMAT;
            endFormatString = LONG_FORMAT;
        } else if (mapWidth <= 200) {
            startFormatString = DAY_FORMAT;
            endFormatString = DAY_FORMAT;
        }

        DateFormat startFormat = new SimpleDateFormat(startFormatString);
        startFormat.setTimeZone(TimeUtil.GMT_TIME_ZONE);
        textToPrint[0] = startFormat.format(record.getValidStart().getTime());

        DateFormat endFormat = new SimpleDateFormat(endFormatString);
        endFormat.setTimeZone(TimeUtil.GMT_TIME_ZONE);
        textToPrint[1] = endFormat.format(record.getValidEnd().getTime());

        return textToPrint;

    }

//    protected void disposeEntry(final PlumeEntry entry) {
//        if (entry.wireframeShape != null || entry.shadedShape != null) {
//            VizApp.runAsync(() -> {
//                if (entry.shadedShape != null) {
//                    entry.shadedShape.dispose();
//                }
//                if (entry.wireframeShape != null) {
//                    entry.wireframeShape.dispose();
//                }
//            });
//        }
//    }

//    @Override
//    public void resourceChanged(ChangeType type, Object object) {
//        if (type == ChangeType.DATA_UPDATE) {
//            PluginDataObject[] pdo = (PluginDataObject[]) object;
//            synchronized (PhiPlumeResource.this) {
//                {
//                    try {
//                        addRecord(pdo);
//                    } catch (VizException e) {
//                        statusHandler.handle(Priority.SIGNIFICANT,
//                                e.getLocalizedMessage(), e);
//                    }
//                }
//            }
//
//        } else if (type != null && type == ChangeType.CAPABILITY) {
//            if (object instanceof ImagingCapability) {
//                ImagingCapability newImgCap = (ImagingCapability) object;
//                // resourceData.setAlpha(this.alpha);
//
//            }
//        }
//
//        issueRefresh();
//    }

//    @Override
//    public void project(CoordinateReferenceSystem crs) throws VizException {
//        super.project(crs);
//        issueRefresh();
//
//    }

    @Override
    public String getName() {
        StringBuilder name = new StringBuilder().append(
                resourceData.name != null ? resourceData.name : resourceName);

        DataTime[] times = this.descriptor.getFramesInfo().getFrameTimes();
        int timeIdx = this.descriptor.getFramesInfo().getFrameIndex();

        // handle last frame differently, it should always be the latest time
        boolean lastFrame = false;
        if (timeIdx == times.length - 1) {
            lastFrame = true;
        }
        DataTime time = null;

        // get time to display
        if (lastFrame) {
            time = new DataTime(SimulatedTime.getSystemTime().getTime());
        } else if (timeIdx > -1 && timeIdx < times.length) {
            time = times[timeIdx];
        }

        // add time to legend
        if (time != null) {
            name.append(" ").append(time.getLegendString());
        }
        return name.toString();
    }

    @Override
    protected void initInternal(IGraphicsTarget target) throws VizException {
        // TODO Auto-generated method stub

    }

    /**
     * @see com.raytheon.uf.viz.core.rsc.AbstractVizResource#remove(com.raytheon.uf.common.time.DataTime)
     */
    @Override
    public void remove(DataTime time) {
        super.remove(time);
        synchronized (frames) {
            frames.remove(time);
        }
        synchronized (unprocessedRecords) {
            unprocessedRecords.remove(time);
        }
    }

}
