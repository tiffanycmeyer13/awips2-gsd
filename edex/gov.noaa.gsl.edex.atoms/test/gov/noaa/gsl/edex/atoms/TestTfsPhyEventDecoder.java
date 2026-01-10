package gov.noaa.gsl.edex.atoms;

import java.io.File;

public class TestTfsPhyEventDecoder {

    public static void main(String[] args) {

        TfsPhysicalEventDecoder decoder = new TfsPhysicalEventDecoder();
        try {
            decoder.decode(new File("/home/awips/tfsTestData/phyEvent.xml"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
