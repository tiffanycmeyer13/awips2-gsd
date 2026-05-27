package gov.noaa.gsl.edex.atomsImagery.plugin;

import com.raytheon.uf.edex.routes.EDEXRouteBuilder;

public class AtomsImageryCamelRoutes extends EDEXRouteBuilder {

    @Override
    public void configure() throws Exception {
        // @formatter:off
        from("jms-durable:queue:Ingest.AtomsImagery")
          .setHeader("pluginName", constant("atomsImagery"))
          .doTry()
              .pipeline()
                  .bean("stringToFile")
                  .bean("atomsImageryDecoder", "decode")
                  .to("direct:persistIndexAlert")
          .endDoTry()
          .doCatch(Throwable.class)
              .to("log:atomsImagery?level=ERROR")
          .endDoTry()
          .end()
          .setId("atomsImageryIngestRoute");
        // @formatter:on
    }
}
