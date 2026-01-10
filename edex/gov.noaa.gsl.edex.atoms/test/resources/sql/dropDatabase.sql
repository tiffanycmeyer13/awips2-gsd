update awips.plugin_info
  set initialized = false
  where name = 'pem' or name = 'atoms' or name = 'atomsForecast' or name ='atomsSeaLevelObs' or name = 'atomsImagery';
drop table awips.phy_event cascade;
drop table awips.seismic_event_data cascade;
drop table awips.volcanic_event_data cascade;
drop table awips.landslide_event_data cascade;
drop table awips.unknown_event_data cascade;
drop table awips.physicaleventdata cascade;
drop table awips.tsunami_fcst cascade;
drop table awips.tsunami_station_fcst cascade;
drop table awips.sealevel_observations cascade;
drop table awips.sea_level_obs cascade;
drop table awips.forecast_station cascade; 
drop table awips.sea_level_station cascade; 
drop table awips.addl_seismic_event_data cascade;
drop table awips.tfs_imagery cascade;
