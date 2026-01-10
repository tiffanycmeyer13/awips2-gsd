package gov.noaa.gsl.edex.atomsSeaLevelObs.plugin;

import com.raytheon.uf.edex.routes.EDEXRouteBuilder;

public class AtomsSeaLevelObsCamelRoutes extends EDEXRouteBuilder {

    @Override
    public void configure() throws Exception {
        // @formatter:off
        from("jms-durable:queue:Ingest.AtomsSeaLevelObs")
          .setHeader("pluginName", constant("atomsSeaLevelObs"))
          .doTry()
              .pipeline()
                  .bean("stringToFile")
                  .bean("atomsSeaLevelObsDecoder", "decode")
                  .to("direct:persistIndexAlert")
          .endDoTry()
          .doCatch(Throwable.class)
              .to("log:atomsSeaLevelObs?level=ERROR")
          .endDoTry()
          .end()
          .setId("atomsSeaLevelObsIngestRoute");
        // @formatter:on
    }
}
