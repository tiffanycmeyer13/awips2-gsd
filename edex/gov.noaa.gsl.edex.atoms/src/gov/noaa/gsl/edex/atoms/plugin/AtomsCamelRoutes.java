package gov.noaa.gsl.edex.atoms.plugin;

import com.raytheon.uf.edex.routes.EDEXRouteBuilder;

public class AtomsCamelRoutes extends EDEXRouteBuilder {

    @Override
    public void configure() throws Exception {
        // @formatter:off
        from("jms-durable:queue:Ingest.Atoms")
          .setHeader("pluginName", constant("atoms"))
          .doTry()
              .pipeline()
                  .bean("stringToFile")
                  .bean("atomsDecoder", "decode")
                  .to("direct:persistIndexAlert")
          .endDoTry()
          .doCatch(Throwable.class)
              .to("log:atoms?level=ERROR")
          .endDoTry()
          .end()
          .setId("atomsIngestRoute");
        // @formatter:on
    }
}
