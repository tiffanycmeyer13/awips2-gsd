package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs;

import java.util.Date;
import java.util.List;

public interface ISeaLevelObsDao {

    /**
     * Returns the SeaLevelObservations found for the given customEventId and
     * optional refTime.
     *
     * @param customEventId
     * @param refTime
     *            optional and may be null.
     * @return
     */
    List<SeaLevelObservations> getSeaLevelObservations(String customEventId,
            Date refTime);
}
