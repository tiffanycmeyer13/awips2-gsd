
import java.io.*;
import java.util.StringTokenizer;

public class JimRiftRegionsConverter { 
    
    public static void main (String args[]) throws Exception {
        
        BufferedReader reader = new BufferedReader( new FileReader("rift_regions.csv"));
        PrintWriter writer = new PrintWriter( new File("riftRegionFcstStations.sql"));
        
        String line = reader.readLine();
        while( line != null ) {
            StringTokenizer toker = new StringTokenizer(line, ",");
            String id = toker.nextToken();
            String symbol = toker.nextToken();
            String name = toker.nextToken();
            String state = toker.nextToken();
            if( state.equals("null")) {
                state = "";
            }
            String country = toker.nextToken();
            String latString = toker.nextToken();
            String lonString = toker.nextToken();
            
            String outLine = "(" + id + ",'" + symbol + "','" + name + "','" + state + "','" + country + "'," + latString + "," + lonString + "),";
            writer.println(outLine);
            
            line = reader.readLine();
        }
        
        reader.close();
        writer.flush();
        writer.close();
    }
}
