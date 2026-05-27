package gov.noaa.gsl.viz.atomsForecast;

public interface TsunamiForecastDaoListener {

    void tsunamiForecastAdded(String customEventId);

    void tsunamiForecastRemoved(String customEventId);

    void tsunamiForecastChanged(String customEventId);

}
