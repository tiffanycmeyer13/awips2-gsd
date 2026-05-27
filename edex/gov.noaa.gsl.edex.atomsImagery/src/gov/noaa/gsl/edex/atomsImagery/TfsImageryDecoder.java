package gov.noaa.gsl.edex.atomsImagery;

import java.io.File;
import java.util.Date;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.time.DataTime;

import gov.noaa.gsl.common.dataplugin.atomsImagery.TfsImageryDescriptor;

public class TfsImageryDecoder {

    /*
     * Filename format should be something like:
     *
     * TFSEnergyMap.eventID.jpg TFSTravelTimesMap.eventID.kml
     * TFSPolygonMap.eventID.txt or even TFSEnergyMap.partOfId.more.moreToo.ext
     *
     * the eventID is anything between the prefix and the extension
     *
     * You get the idea.
     */
    private final static String[] FILENAME_PREFIXES = { "TFSEnergyMap",
            "TFSTravelTimesMap", "TFSPolygonMap" };

    /**
     * Properties can not be set on the DAO since the Plugin is required for the
     * DAO creation, and the DAO is required for the Plugin creation. Which came
     * first, the chicken or the egg? And so we have this property here on the
     * Decoder, to set the value on the TfsImageryDescriptor to be used by the
     * DAO.
     *
     * @param dataDir
     */
    public static void setParentDataDir(String dataDir) {
        TfsImageryDescriptor.setParentDataDir(dataDir);
    }

    public static String getParentDataDir() {
        return TfsImageryDescriptor.getParentDataDir();
    }

    /**
     * Again, properties can not be set on the DAO since the Plugin is required
     * for the DAO creation, and the DAO is required for the Plugin creation.
     * Which came first, the chicken or the egg? And so we have this property
     * here on the Decoder, to set the value on the TfsImageryDescriptor to be
     * used by the DAO.
     *
     * @param dissemScriptsDir
     */
    public static void setDissemScriptsDir(String dissemScriptsDir) {
        TfsImageryDescriptor.setDissemScriptsDir(dissemScriptsDir);
    }

    public static String getDissemScriptsDir() {
        return TfsImageryDescriptor.getDissemScriptsDir();
    }

    public PluginDataObject[] decode(File file) throws Exception {

        if (file == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + "::decode(:File) method got a null File.");
        }

        /*
         * First check the filename format, getting eventID etc
         */
        String filename = file.getName();
        String eventID = "";
        for (String prefix : FILENAME_PREFIXES) {
            /*
             * Filename should be prefix.eventID.addlPartOfTheID.more.extension.
             * So the eventID is anything between the prefix and the extension
             */
            if (filename.startsWith(prefix)) {
                String[] words = filename.split("\\.");
                if (words != null && words.length >= 3) {
                    // Put id back together, but skip the prefix and extension
                    for (int i = 1; i < (words.length - 1); i++) {
                        eventID += words[i];
                        // If there's another one, add the . back in
                        if ((i + 1) < (words.length - 1)) {
                            eventID += ".";
                        }
                    }
                    break;
                }
            }
        }
        if (eventID == null || eventID.isEmpty()) {
            throw new IllegalArgumentException(getClass().getName()
                    + "::decode(:File) received a File whose name (" + filename
                    + ") doesn't seem to " + "be in the form of "
                    + FILENAME_PREFIXES
                    + ".eventid.ext (for example, TFSEnergyMap.someEQ.Id.moreId.ext)");
        }

        TfsImageryDescriptor desc = new TfsImageryDescriptor();

        DataTime dataTime = new DataTime(new Date());
        desc.setDataTime(dataTime);

        desc.setFilename(file.getName());
        desc.setPhyEventCustomId(eventID);
        desc.setFile(file);

        return new PluginDataObject[] { desc };
    }

    public static void main(String args[]) {

        String filename = "TFSEnergyMap.Alaska.Cat1.jpg";
        StringBuilder eventID = new StringBuilder();
        for (String prefix : FILENAME_PREFIXES) {
            /*
             * Filename should be prefix.eventID.addlPartOfTheID.more.extension.
             * So the eventID is anything between the prefix and the extension
             */
            if (filename.startsWith(prefix)) {
                String[] words = filename.split("\\.");
                if (words != null && words.length >= 3) {
                    // Put id back together, but skip the prefix and extension
                    for (int i = 1; i < (words.length - 1); i++) {
                        eventID.append(words[i]);
                        // If there's another one, add the . back in
                        if ((i + 1) < (words.length - 1)) {
                            eventID.append(".");
                        }
                    }
                    break;
                }
            }
        }
        System.err.println("Event ID = " + eventID.toString());
    }
}
