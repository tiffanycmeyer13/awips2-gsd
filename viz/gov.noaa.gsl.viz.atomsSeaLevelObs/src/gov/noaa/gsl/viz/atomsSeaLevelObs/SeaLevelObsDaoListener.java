package gov.noaa.gsl.viz.atomsSeaLevelObs;

public interface SeaLevelObsDaoListener {

    void seaLevelObsAdded(String customEventId);

    void seaLevelObsRemoved(String customEventId);

    void seaLevelObsChanged(String customEventId);

}
