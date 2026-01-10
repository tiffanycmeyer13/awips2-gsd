import java.util.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

public class FcstStationReplace {
    
    private static final String[][] REPLACE  = new String[][] {
        {"PWIL", "TOC"},
        {"CHEN", "COC"},
        {"BUEN", "BAH"},
        {"NCPT", "ECP"},
        {"PETR", "PTI2"},
        {"ENSE", "SOC"},
        {"AMAL", "CHL"},
        {"STCR", "CHR"},
        {"CULE", "CLB"},
        {"LAME", "LMS"},
        {"SANJ", "SJU"},
        {"PNPR", "PNL"},
        {"YABU", "YBC"},
        {"AREC", "ARC"},
        {"LALI", "LLI"},
    };
    
    private static final String[] DATA_DIRS = new String[] {"otherTfsTestData", "threatDBTestData"};
    private static final String PREFIX = "tfsFcst";
    private static final String SUFFIX = ".xml";

    public static void main(String[] args) throws Exception {

        for( String childDir : DATA_DIRS ) {
            File dir = new File( "./" + childDir );
            File[] fcstFilesUgh = dir.listFiles( new FilenameFilter() {
                public boolean accept(File dir, String name) {
                    return (name.startsWith(PREFIX) && name.endsWith(SUFFIX));
                }});
            File[] fcstFiles = Arrays.copyOf( fcstFilesUgh, fcstFilesUgh.length + 1 );
            fcstFiles[fcstFiles.length - 1] = new File( "./FcstStns.txt");
            for( File fcstFile : fcstFiles ) {
                List<String> inLines = Files.readAllLines(Paths.get(fcstFile.getPath()));
                List<String> outLines = new ArrayList(inLines.size());
                for( String line : inLines ) {
                    for( String[] replacePair : REPLACE ) {
                        line = line.replace(replacePair[0], replacePair[1]);
                    }
                    outLines.add(line);
                }
                Files.write(Paths.get(fcstFile.getPath()), outLines);
            }
        }
    }
}


