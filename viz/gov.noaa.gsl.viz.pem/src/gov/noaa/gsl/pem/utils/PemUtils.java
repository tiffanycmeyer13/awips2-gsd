package gov.noaa.gsl.pem.utils;

import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.TimeZone;

/**
 * Utilities for the physical event display.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Apr 19, 2922        Jing                  Initial creation
 *
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 *
 *
 */
public class PemUtils {

    public static SimpleDateFormat getSecondTimeFormatter() {
        final SimpleDateFormat dateFormatter;
        dateFormatter = new SimpleDateFormat("yyyy-MM-dd' 'HH:mm:ss");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));

        return dateFormatter;
    }

    public static SimpleDateFormat getDateFormatter() {
        final SimpleDateFormat dateFormatter;
        dateFormatter = new SimpleDateFormat("yyyy-MM-dd");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));

        return dateFormatter;
    }

    public static SimpleDateFormat getHourMinuteFormatter() {
        final SimpleDateFormat dateFormatter;
        dateFormatter = new SimpleDateFormat("HH:mm");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));

        return dateFormatter;
    }

    public static SimpleDateFormat getHourMinuteSecFormatter() {
        final SimpleDateFormat dateFormatter;
        dateFormatter = new SimpleDateFormat("HH:mm:ss'Z'");
        dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));
        return dateFormatter;
    }

    public static String formatElapsedTime(Date startDate, Date endDate) {

        Instant start = Instant.ofEpochMilli(startDate.getTime());
        Instant end = Instant.ofEpochMilli(endDate.getTime());

        Duration timeElapsed = Duration.between(start, end);
        long elapsedSeconds = timeElapsed.getSeconds();

        String result = String.format("%d:%02d:%02d:%02d",
                (elapsedSeconds / 86400), (elapsedSeconds % 86400) / 3600,
                (elapsedSeconds % 3600) / 60, (elapsedSeconds % 60));

        return result;
    }
}
