package gov.noaa.gsl.edex.pem.plugin;

import com.raytheon.uf.edex.routes.EDEXRouteBuilder;

public class PEMCamelRoutes extends EDEXRouteBuilder {

    @Override
    public void configure() throws Exception {
        // @formatter:off
        from("jms-durable:queue:Ingest.Pem")
          .setHeader("pluginName", constant("pem"))
          .doTry()
              .pipeline()
                  .bean("stringToFile")
                  .bean("pemDecoder", "decode")
                  .to("direct:persistIndexAlert")
          .endDoTry()
          .doCatch(Throwable.class)
              .to("log:pem?level=ERROR")
          .endDoTry()
          .end()
          .setId("pemIngestRoute");
        // @formatter:on
    }
}
