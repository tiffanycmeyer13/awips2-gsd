/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atomsImagery;

import java.io.File;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataplugin.annotations.DataURI;
import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.atoms.TfsData;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import jakarta.persistence.Transient;
import jakarta.persistence.UniqueConstraint;

/**
 *
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

@DynamicSerialize
@Entity
@SequenceGenerator(initialValue = 1, name = PluginDataObject.ID_GEN, sequenceName = "tfs_imagery_seq")
@Table(name = "tfs_imagery", uniqueConstraints = {
        @UniqueConstraint(columnNames = { "phy_event_custom_id",
                "filename" }) })
//TODO Add Index for query performance
public class TfsImageryDescriptor extends PluginDataObject implements TfsData {

    public static final String PLUGIN_NAME = "atomsImagery";

    private static String parentDir = "/data/fxa/ATOMS/dissemination";

    private static String dissemScriptsDir = "/data/fxa/ATOMS/scripts";

    static {
        // By default, let's just create this directory. If they
        // give us a different one by calling setParentDataDir via
        // XML, then we'll just not use the one we're creating here.
        setParentDataDir(parentDir);
    }

    public static String getParentDataDir() {
        return parentDir;
    }

    public static void setParentDataDir(String dataDirPath) {
        if (dataDirPath != null && !dataDirPath.isEmpty()) {
            parentDir = dataDirPath;
            try {
                File dataDir = new File(parentDir);
                if (!dataDir.exists()) {
                    dataDir.mkdirs();
                }
            } catch (Exception e) {
                e.printStackTrace(System.err);
            }
        }
    }

    public static String getDissemScriptsDir() {
        return dissemScriptsDir;
    }

    public static void setDissemScriptsDir(String dissemScriptsDirPath) {
        if (dissemScriptsDirPath != null && !dissemScriptsDirPath.isEmpty()) {
            dissemScriptsDir = dissemScriptsDirPath;
        }
    }

    /*
     * NOTE: @DataURI(position = 0) is for dataTime from superclass, which
     * probably doesn't make sense for our imagery.
     */

    /**
     * This is the custom id of the physical event that this imagery refers to.
     * You can retrieve the PhysicalEvent via the appropriate DAO.
     */
    @DynamicSerializeElement
    @DataURI(position = 1)
    @Column(name = "phy_event_custom_id")
    private String phyEventCustomId;

    @DynamicSerializeElement
    @DataURI(position = 2)
    @Column
    private String filename;

    @Transient
    private File file;

    /**
     * This is the source / organization that uploaded the XML for this imagery
     */
    @DynamicSerializeElement
    @Column(nullable = true)
    private String tfsDataSource = "";

    @DynamicSerializeElement
    @Column(nullable = true)
    private String tfsUser = "";

    @Override
    public String getTfsDataSource() {
        return tfsDataSource;
    }

    @Override
    public void setTfsDataSource(String source) {
        if (source == null) {
            source = "";
        }
        this.tfsDataSource = source;
    }

    @Override
    public String getTfsUser() {
        return tfsUser;
    }

    @Override
    public void setTfsUser(String user) {
        if (user == null) {
            user = "";
        }
        this.tfsUser = user;
    }

    public String getPhyEventCustomId() {
        return phyEventCustomId;
    }

    public void setPhyEventCustomId(String phyEventCustomId) {
        this.phyEventCustomId = phyEventCustomId;
    }

    @Override
    public String getPluginName() {
        return PLUGIN_NAME;
    }

    public String getFilename() {
        return filename;
    }

    public void setFilename(String filename) {
        this.filename = filename;
    }

    public File getFile() {
        return file;
    }

    public void setFile(File file) {
        this.file = file;
    }
}
