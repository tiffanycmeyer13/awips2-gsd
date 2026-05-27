package gov.noaa.nssl.edex.plugin.phiplume.impl;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import org.geotools.api.feature.simple.SimpleFeatureType;
import org.geotools.api.feature.type.Name;
import org.geotools.data.memory.MemoryFeatureCollection;
import org.geotools.feature.NameImpl;
import org.geotools.geometry.jts.ReferencedEnvelope;
import org.geotools.util.URLs;

import com.raytheon.uf.common.json.JsonException;
import com.raytheon.uf.common.json.geo.IGeoJsonService;
import com.raytheon.uf.common.json.geo.SimpleGeoJsonService;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;

/**
 * Implement a representation for a GeoJSON File
 *
 * Represented GeoJSON file
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date           Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jun 9, 2016    17912      pwang       Initial creation
 *
 * </pre>
 *
 * @author pwang
 * @version 1.0
 */

/**
 * TODO Add Description
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jul 7, 2016            pwang     Initial creation
 *
 * </pre>
 *
 * @author pwang
 * @version 1.0
 */
public class GeoJSONFile {

    private IUFStatusHandler logger = UFStatus.getHandler(GeoJSONFile.class);

    private static final String NAME_VERSION_SEPARATE = "_";

    private File file;

    private String name;

    private String extension;

    private String abdPath;

    private int version;

    private Date dateTime;

    private boolean local = true;

    private boolean canWrite = false;

    private boolean memoryMapped = false;

    private GeoJSONFeatureCollection features;

    /**
     * GeoJSONFile constructor
     *
     * @param gjsonFile
     */
    public GeoJSONFile(File gjsonFile) {
        this.file = gjsonFile;
        if (init(file)) {
            initFileInfo(file);
        }
    }

    /**
     * GeoJSONFile constructor
     *
     * @param url
     */
    public GeoJSONFile(URL url) {
        this.file = URLs.urlToFile(url);
        if (init(file)) {
            initFileInfo(file);
        }
    }

    /**
     * init GeoJSON file
     *
     * @param gjson
     * @return
     */
    private boolean init(File gjson) {
        boolean ok = true;
        try (InputStream is = new FileInputStream(gjson)) {
            if (is != null) {
                IGeoJsonService json = new SimpleGeoJsonService();
                List<MemoryFeatureCollection> colls = new ArrayList<MemoryFeatureCollection>();
                colls.add((MemoryFeatureCollection) json
                        .deserializeFeatureCollection(is));
                features = new GeoJSONFeatureCollection(colls);
            }
        } catch (FileNotFoundException e) {
            logger.error("GeoJSON file is not find: " + gjson.getAbsolutePath(),
                    e);
            ok = false;
        } catch (JsonException je) {
            logger.error("decoding json failed: " + gjson.getAbsolutePath(),
                    je);
            ok = false;
        } catch (IOException ioe) {
            logger.error("Create InputStream failed for the file: "
                    + gjson.getAbsolutePath(), ioe);
            ok = false;
        }
        return ok;
    }

    /**
     * initFileInfo
     *
     * @param gjson
     */
    private void initFileInfo(File gjson) {

        // File name (base)
        String fileName = gjson.getName();
        int beginNameIndex = fileName.lastIndexOf("/");
        int beginExtIndex = fileName.lastIndexOf(".");

        String fileNameVersion = fileName.substring(beginNameIndex + 1,
                beginExtIndex);

        /**
         * This is reserved for future enhancement. GeoJSON file can be named as
         * namestring_nn.geojson nn which follows a separator " _ " indicated
         * the this may be a series of GeoJSON files for a single event
         */
        this.name = fileNameVersion;
//        String[] nameversion = fileNameVersion.split(NAME_VERSION_SEPARATE);
//        if (nameversion != null && nameversion.length > 1) {
//            try {
//                this.version = Integer.parseInt(nameversion[1]);
//            } catch (NumberFormatException e) {
//                logger.error(
//                        "Parse file version failed for : " + fileNameVersion,
//                        e);
//                this.version = 0;
//            }
//        } else {
//            // No version
//            this.version = 0;
//        }

        // this.type = featureType.
        this.extension = fileName.substring(beginExtIndex + 1);
        this.abdPath = gjson.getAbsolutePath();
        this.dateTime = new Date(gjson.lastModified());

        logger.info("GeoJSON File Info: Name = " + this.name + " version = "
                + this.version + " ext = " + this.extension + " path = "
                + this.abdPath + " TimeStamp = " + this.dateTime.toString());

    }

    /**
     * getBounds
     *
     * @return
     */
    public ReferencedEnvelope getBounds() {
        return features.getBounds();
    }

    /**
     * getCount counts of features
     *
     * @return
     */
    public int getCount() {
        try {
            return features.getCount();
        } catch (IOException e) {
            logger.error("Failed to get count of features in the file: ", e);
        }
        return 0;
    }

    /**
     * BuildFeatureType
     *
     * @return
     */
    public SimpleFeatureType buildFeatureType() {
        return features.getSchema();
    }

    /**
     * getTypeName
     *
     * @return
     */
    public String getTypeName() {
        return name;
    }

    /**
     * createTypeNames
     *
     * @return
     * @throws IOException
     */
    public List<Name> createTypeNames() throws IOException {
        Name typeName = new NameImpl(this.name);
        return Collections.singletonList(typeName);
    }

    /**
     * @return the file
     */
    public File getFile() {
        return file;
    }

    /**
     * @param file
     *            the file to set
     */
    public void setFile(File file) {
        this.file = file;
    }

    /**
     * @return the name
     */
    public String getName() {
        return name;
    }

    /**
     * @param name
     *            the name to set
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * @return the extension
     */
    public String getExtension() {
        return extension;
    }

    /**
     * @param extension
     *            the extension to set
     */
    public void setExtension(String extension) {
        this.extension = extension;
    }

    /**
     * @return the version
     */
    public int getVersion() {
        return version;
    }

    /**
     * @param version
     *            the version to set
     */
    public void setVersion(int version) {
        this.version = version;
    }

    /**
     * @return the features
     */
    public GeoJSONFeatureCollection getFeatures() {
        return features;
    }

    /**
     * @param features
     *            the features to set
     */
    public void setFeatures(GeoJSONFeatureCollection features) {
        this.features = features;
    }

    /**
     * @return the abdPath
     */
    public String getAbdPath() {
        return abdPath;
    }

    /**
     * message
     *
     * @param abdPath
     *            the abdPath to set
     */
    public void setAbdPath(String abdPath) {
        this.abdPath = abdPath;
    }

    /**
     * @return the dateTime
     */
    public Date getDateTime() {
        return dateTime;
    }

    /**
     * @param dateTime
     *            the dateTime to set
     */
    public void setDateTime(Date dateTime) {
        this.dateTime = dateTime;
    }

    /**
     * @return the local
     */
    public boolean isLocal() {
        return local;
    }

    /**
     * @param local
     *            the local to set
     */
    public void setLocal(boolean local) {
        this.local = local;
    }

    /**
     * @return the canWrite
     */
    public boolean canWrite() {
        return canWrite;
    }

    /**
     * @return the memoryMapped
     */
    public boolean isMemoryMapped() {
        return memoryMapped;
    }

    /**
     * @param memoryMapped
     *            the memoryMapped to set
     */
    public void setMemoryMapped(boolean memoryMapped) {
        this.memoryMapped = memoryMapped;
    }

}