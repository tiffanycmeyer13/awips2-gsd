package gov.noaa.nssl.edex.plugin.phiplume;

import com.raytheon.uf.edex.routes.EDEXRouteBuilder;

/**
 * Camel routes converted from file "phiplume-ingest.xml"
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * 2025-04-02   N/A    kevin.manross   Initial creation (from auto-generated)
 *
 * </pre>
 */

public class PhiPlumeCamelRoutes extends EDEXRouteBuilder {

    public PhiPlumeCamelRoutes() {
    }

    @Override
    public void configure() throws Exception {
        // @formatter:off
        from("jms-durable:queue:Ingest.Phiplume")
          .setHeader("pluginName", constant("phiplume"))
          .doTry()
              .pipeline()
                  .bean("stringToFile")
                  .bean("phiplumeDecoder", "decode")
                  .to("direct:persistIndexAlert")
          .endDoTry()
          .doCatch(Throwable.class)
              .to("log:phiplume?level=ERROR&showBody=true")
          .endDoTry()
          .end()
          .setId("phiplumeIngestRoute");
        // @formatter:on
    }
}