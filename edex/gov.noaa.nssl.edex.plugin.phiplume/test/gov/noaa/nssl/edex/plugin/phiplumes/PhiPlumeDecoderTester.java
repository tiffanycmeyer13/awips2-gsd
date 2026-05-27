package gov.noaa.nssl.edex.plugin.phiplumes;

import java.io.File;

import com.raytheon.uf.common.dataplugin.PluginDataObject;

import gov.noaa.nssl.common.dataplugin.phiplume.AbstractPhiPlumeRecord;
import gov.noaa.nssl.common.dataplugin.phiplume.PhiInterpolatedRecord;
import gov.noaa.nssl.common.dataplugin.phiplume.PhiPlumeRecord;
import gov.noaa.nssl.edex.plugin.phiplume.PhiPlumeDecoder;

public class PhiPlumeDecoderTester {

    private AbstractPhiPlumeRecord phiPlumeType;

    private void init(File fileString) {
        String fname = fileString.getName();
        System.out.println("HERE-0: " + fname);
        if (fname.contains("phi_Interpolated")) {
            phiPlumeType = new PhiInterpolatedRecord();
            System.out.println("HERE-1: " + phiPlumeType);
        } else if (fname.contains("phi_Rec")) {
            phiPlumeType = new PhiPlumeRecord();
            System.out.println("HERE-2: " + phiPlumeType);
        }
        System.out.println("HERE-3: " + phiPlumeType);

        AbstractPhiPlumeRecord tempRecord = null;
        // Init classes for record creation
        if (phiPlumeType instanceof gov.noaa.nssl.common.dataplugin.phiplume.PhiPlumeRecord) {
            tempRecord = new PhiPlumeRecord();
            System.out.println("HERE-4: " + phiPlumeType);
        } else if (phiPlumeType instanceof gov.noaa.nssl.common.dataplugin.phiplume.PhiInterpolatedRecord) {
            tempRecord = new PhiInterpolatedRecord();
            System.out.println("HERE-5: " + phiPlumeType);
        }

        if (tempRecord == null) {
            System.err.println("ERROR: UNABLE TO PROPERLY INSTANTIATE RECORD: "
                    + phiPlumeType);
        }

        System.out.println("TMPRECORD is type: " + tempRecord);

    }

    public static void main(String[] args) {
        // TODO Auto-generated method stub
        // File fileString = new
        // File("/run/media/awips/MAX/transfer_20220502/tornado-PHI-Plumes-valid-20220502222400-created-20220502222420.json");
        // File fileString = new
        // File("/home/awips/HWT-2022/vectorPHIPlumes/transfer_20220503/subset_endofcase/severe-PHI-Plumes-valid-20220503214600-created-20220503214622.json");
        File fileString = new File(
//                "/home/awips/code/PhiPlumes_20240718/KOAX/severe-PHI-Plumes-valid-20240521195800-created-20240718193938.json");
                "/data_store/PHI/geojsons/QC/recommenders/phi_Rec_QC_Sev_20251006_224600.geojson");
//                "/data_store/PHI/geojsons/QC/interpolated_objects/phi_Interpolated_QC_Sev_20251006_224600.geojson");

        PhiPlumeDecoderTester test = new PhiPlumeDecoderTester();
//        test.init(fileString);

        PhiPlumeDecoder decoder = new PhiPlumeDecoder();
        try {
            PluginDataObject[] dataObjects = decoder.decode(fileString);
            System.out.println(dataObjects.toString());

            for (Object obj : dataObjects) {
                if (obj instanceof AbstractPhiPlumeRecord) {
                    AbstractPhiPlumeRecord record = (AbstractPhiPlumeRecord) obj;

                    // System.out.println("Start Values");
                    // System.out.println(record.getDataTime());
                    // System.out.println(record.getIDnum());
                    // //System.out.println(record.getPolygonWKT());
                    // System.out.println(record.getThreat());
                    // System.out.println(record.getGridTime());
                    // System.out.println(record.getValidStart());
                    // System.out.println(record.getValidEnd());
                    // System.out.println(record.getPolygon());

//                    System.out.println("Threat: " + record.getThreat());
//                    System.out.println("Issue: " + record.getIssue());
                    System.out.println("IDnum: " + record.getIDnum());
                    System.out.println("ValidStart: " + record.getValidStart());
                    System.out.println("ValidEnd: " + record.getValidEnd());
//                    System.out.println("GridTime: " + record.getGridTime());

//                    System.out.println("ObjOgcFid: " + record.getObjOgcFid());
//                    System.out.println("Discussion: " + record.getDiscussion());
//                    System.out.println("Severity: " + record.getSeverity());
//                    System.out.println("Source: " + record.getSource());
//                    System.out.println("Auto: " + record.getAuto());
                    System.out.println("Speed: " + record.getSpeed());
                    System.out.println("Direction: " + record.getDirection());
//                    System.out.println("Site: " + record.getSite());
//                    System.out.println("Username: " + record.getUsername());
//                    System.out.println("TimeAddDb: " + record.getTimeAddedDb());
//                    System.out.println(
//                            "ContourLevel: " + record.getContourLevel());
//                    System.out.println("OgcFid: " + record.getOgcFid());
//                    System.out.println("Canceled: " + record.getCanceled());
//                    System.out.println("Max: " + record.getMax());
                    System.out.println("PolygonWKT: " + record.getPolygonWKT());
                    System.out.println(
                            "ProbSevereAttrs: " + record.getProbsevereAttrs());
//                    System.out.println("PolyWKT isValid: "
//                            + record.getPolygon().isValid());
//                    if (record.getClass() == PhiInterpolatedRecord.class) {
//                        System.out.println("ProbSevere: ");
//                        Map<String, Object> probSevereAttrs = ((PhiInterpolatedRecord) record)
//                                .getArgsMap();
//                        for (Entry<String, Object> entry : probSevereAttrs
//                                .entrySet()) {
//                            System.out.println("Key: " + entry.getKey()
//                                    + ", Value: " + entry.getValue());
//                        }
//                    }
                    System.out.println("");

                }
            }
        } catch (Throwable e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

}
