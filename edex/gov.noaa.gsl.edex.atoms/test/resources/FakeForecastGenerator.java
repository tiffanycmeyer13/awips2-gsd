

import java.io.BufferedReader;
import java.util.*;
import java.io.*;
import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.io.File;
import java.io.FileInputStream;
import java.util.concurrent.ThreadLocalRandom;

/**
* Usage:
*   javac FakeForecastGenerator.java
*   java FakeForecastGenerator PhyEventID FcstType OriginTime
*     where FcstType = TTT, RIFT, SIFT, ATFM, Derived, Hybrid
*       and OriginTime in YYYY-MM-DD'T'HH:MM:SS format as below:
*
*   EXAMPLE: java FakeForecastGenerator JimEQ TTT 2023-04-25T16:10:29
**/
public class FakeForecastGenerator {

    private static final String[] BERING_SEA_STNS = new String[] {
            ""
    };
    
    // 2022-05-18T00:06:06  OriginTime
    final static String DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ss";
    final static SimpleDateFormat dateFormatter = new SimpleDateFormat(DATE_FORMAT);
    private static DecimalFormat AMP_FORMATTER = new DecimalFormat("0.00");

    static{
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));
        AMP_FORMATTER.setRoundingMode(RoundingMode.HALF_DOWN);
    }
    
    public static void main(String[] args) throws Exception{

        String fcstType = "";
        Date originTime = null;
        String eqId = "";
        try {
            eqId = args[0];
            fcstType = args[1];
            if( !fcstType.equals("TTT") && !fcstType.equals("SIFT") && !fcstType.equals("RIFT")) {
                throw new Exception("Type must be RIFT SIFT or TTT");
            }
            originTime = dateFormatter.parse(args[2]);
        } catch (Exception e ) {
            System.out.println("Usage: java FakeForecastGenerator [EQ CustomId] [FcstType] [OriginTime]");
            System.out.println("Ex: java FakeForecastGenerator Arctic_Cat11 TTT 2022-05-18T00:06:06");
            System.out.println("Ex: java FakeForecastGenerator Arctic_Cat11 RIFT 2022-05-18T00:06:06");
            System.out.println("  Output: tfsFcst_FAKE_DATA.xml");
            System.exit(0);
        }
        
        // Country to list of stations
        Map<String, List<FakeStn>> stations = new HashMap<>();

        File inFile = new File( "./FcstStns.txt");
        BufferedReader reader = new BufferedReader( new FileReader(inFile));
        String line = reader.readLine();
        while( line != null ) { 
            line = line.replace("\"", "");
            try {
                StringTokenizer toker = new StringTokenizer(line, ";");
                String id = toker.nextToken();
                String name = toker.nextToken();
                String state = toker.nextToken();
                String country = toker.nextToken();

                FakeStn fakeStn = new FakeStn(id, name, state, country);
                List<FakeStn> countryListOfStations = stations.get(country);
                if( countryListOfStations == null ) {
                    countryListOfStations = new ArrayList<>();
                    stations.put(country, countryListOfStations);
                }
    /*
                if( "Hawaii".equals( state ) ) {
                  FakeStn fakeStn = new FakeStn(id, name, state, country);
                  List<FakeStn> countryListOfStations = stations.get(country);
                  if( countryListOfStations == null ) {
                      countryListOfStations = new ArrayList<>();
                      stations.put(country, countryListOfStations);
                  }
                  countryListOfStations.add(fakeStn);
                  System.out.println( line );
                }
    */
                countryListOfStations.add(fakeStn);
            } catch (Exception e) {
                System.out.println("Here's the offending line: " + line );
                throw e;
            }
            System.out.println( line );
            line = reader.readLine();
        }
        reader.close();
        
        // If it's TTT, then create arrival times for all stations
        if( fcstType.equals("TTT")) {
            generateArrivalTimes(originTime, stations);
        }
        // If it's RIFT or SIFT, then create arrival times for all stations and only create 
        // significant Amplitudes for a few country's stations
        else {
            generateArrivalTimes(originTime, stations);
            generateAmplitudes(stations);
        }
        
        Date now = new Date();
        File outFile = new File("./tfsFcst_FAKE_DATA.xml");
        PrintWriter writer = new PrintWriter( new FileOutputStream( outFile ));
        writer.println("<atomsTsunamiForecastData>");
        writer.println("  <EventID>" + eqId + "</EventID>");
        writer.println("  <Source>" + "PTWC" + "</Source>");
        writer.println("  <ForecastType>" + fcstType + "</ForecastType>");
        writer.println("  <CreationTime>" + dateFormatter.format(now) + "</CreationTime>");
        writer.println("  <ForecastRunTime>" + dateFormatter.format(now) + "</ForecastRunTime>");
        for(Map.Entry<String, List<FakeStn>> entry : stations.entrySet()) {
            for( FakeStn stn : entry.getValue()) {
                writer.println("  <atomsForecastRecord>");
                writer.println("    <StationID>" + stn.id + "</StationID>");
                writer.println("    <ArrivalTime>" + stn.arrivalTime + "</ArrivalTime>");
                if( stn.amplitude != null ) { 
                    writer.println("    <Amplitude>" + stn.amplitude + "</Amplitude>");
                }
                writer.println("  </atomsForecastRecord>");
            }
        }
        writer.println("</atomsTsunamiForecastData>");
        writer.close();
        
        System.out.println("Fake forecast data written to: ./" + outFile.getName() );
    }
    
    private static void generateArrivalTimes(Date originTime, Map<String, List<FakeStn>> stations) {
        // If it's TTT, then create arrival times for all stations
        long baseTime = originTime.getTime();
        for(Map.Entry<String, List<FakeStn>> entry : stations.entrySet()) {
            // Find a single time for the country, between 30 - 630 minutes
            int twoHourBin = ThreadLocalRandom.current().nextInt(0, 5);
            int minMinutes = 30 + twoHourBin * 120;
            int maxMinutes = 30 + (twoHourBin + 1) * 120;
            int countryArrivalTimeMinute = ThreadLocalRandom.current().nextInt(minMinutes, maxMinutes);
            
            // now for each station in that country, go up or down 30e minutes so all arrival times 
            // are within an hour of each other for that country
            for( FakeStn stn : entry.getValue()) {
                // TORP BELOW
                if( "Jello Pudding Pop".equals(stn.country) ) {
                    countryArrivalTimeMinute = 120;
                    System.out.println("TORP " + stn.country + " getting "+ countryArrivalTimeMinute);
                }
//                else if( "British Virgin Is.".equals(stn.country) ) {
//                    countryArrivalTimeMinute = 60;
//                    System.out.println("TORP " + stn.country + " getting "+ countryArrivalTimeMinute);
//                }
//                else if( "US Virgin Islands".equals(stn.state) ) {
//                    countryArrivalTimeMinute = 90;
//                    System.out.println("TORP " + stn.country + " getting "+ countryArrivalTimeMinute);
//                }
//                else if( "Dominican Republic".equals(stn.country) ) {
//                    countryArrivalTimeMinute = 150;
//                    System.out.println("TORP " + stn.country + " getting "+ countryArrivalTimeMinute);
//                }
//                else if( "Venezuela".equals(stn.country) ) {
//                    System.out.println("TORP " + stn.country + " getting "+ countryArrivalTimeMinute);
//                    countryArrivalTimeMinute = 180;
//                }
                else {
                    countryArrivalTimeMinute = 360;
                }
                // TORP ABOVE
                int fluxMinutes = ThreadLocalRandom.current().nextInt(-29, 30);
                long arrivalTime = baseTime + (countryArrivalTimeMinute + fluxMinutes) * 60 *1000L;
                stn.arrivalTime = dateFormatter.format(new Date(arrivalTime));
            }
        }
    }

    private static void generateAmplitudes(Map<String, List<FakeStn>> stations) {
        double bins[] = {0.0, 0.3, 1.0, 3.0, 6.0};
        for(Map.Entry<String, List<FakeStn>> entry : stations.entrySet()) {

            for( FakeStn stn : entry.getValue()) {
                if( "California".equals(stn.state) ) {
                    // 0-0.3, 0.3 - 1.0, 1.0 - 3.0, 3.0 - 4.0 lets say
//                    double amplitude = ThreadLocalRandom.current().nextDouble(1.01, 3.0);
                    double amplitude = ThreadLocalRandom.current().nextDouble(0.0, 0.2);
                    stn.amplitude = AMP_FORMATTER.format(amplitude);
                    System.out.println("TORP " + stn.country + " getting amp = "+ amplitude);
                }
//                else if( "Oregon".equals(stn.state) || "Washington".equals(stn.state) ) {
//                  // 0-0.3, 0.3 - 1.0, 1.0 - 3.0, 3.0 - 4.0 lets say
//                  double amplitude = ThreadLocalRandom.current().nextDouble(0.3, 0.99);
//                  stn.amplitude = AMP_FORMATTER.format(amplitude);
//                  System.out.println("TORP " + stn.country + " getting amp = "+ amplitude);
//                }

//                else if( "British Virgin Is.".equals(stn.country) || "US Virgin Islands".equals(stn.state) ) {
//                    // 0-0.3, 0.3 - 1.0, 1.0 - 3.0, 3.0 - 4.0 lets say
//                    double amplitude = ThreadLocalRandom.current().nextDouble(1.0, 3.0);
//                    stn.amplitude = AMP_FORMATTER.format(amplitude);
//                    System.out.println("TORP " + stn.country + " getting amp = "+ amplitude);
//                }
//                else if( "Chile".equals(stn.country) ) {
//                    // 0-0.3, 0.3 - 1.0, 1.0 - 3.0, 3.0 - 4.0 lets say
//                    double amplitude = ThreadLocalRandom.current().nextDouble(0.0, 0.29999);
//                    stn.amplitude = AMP_FORMATTER.format(amplitude);
//                    System.out.println("TORP " + stn.country + " getting amp = "+ amplitude);
//                }
                else {
                    double amplitude = ThreadLocalRandom.current().nextDouble(0.0, 0.29);
                    stn.amplitude = AMP_FORMATTER.format(amplitude);
                }
            }
/*
            // Silly. Let's say only ~11% of countries have > 0.3
            if(ThreadLocalRandom.current().nextInt(0, 100) <= 50 ) {
                // now for each station in that country
                for( FakeStn stn : entry.getValue()) {
                    // 0-0.3, 0.3 - 1.0, 1.0 - 3.0, 3.0 - 4.0 lets say
                    double amplitude = ThreadLocalRandom.current().nextDouble(0.31, 4.0);
                    stn.amplitude = AMP_FORMATTER.format(amplitude);
                }
            }
*/
        }
    }

    private static class FakeStn { 
        String id;
        String name;
        String state;
        String country;
        String arrivalTime;
        String amplitude;

        public FakeStn(String id, String name, String state, String country ) {
            this.name = name;
            this.id = id;
            this.state = state;
            this.country = country;
        }
    }
}
