package gov.noaa.gsl.edex.atomsForecast.plugin;

import com.raytheon.uf.edex.routes.EDEXRouteBuilder;

public class AtomsForecastCamelRoutes extends EDEXRouteBuilder {

    @Override
    public void configure() throws Exception {
        // @formatter:off
        from("jms-durable:queue:Ingest.AtomsFcst")
          .setHeader("pluginName", constant("atomsForecast"))
          .doTry()
              .pipeline()
                  .bean("stringToFile")
                  .bean("atomsFcstDecoder", "decode")
                  .to("direct:persistIndexAlert")
          .endDoTry()
          .doCatch(Throwable.class)
              .to("log:atomsFcst?level=ERROR")
          .endDoTry()
          .end()
          .setId("atomsFcstIngestRoute");
        // @formatter:on
    }
}
