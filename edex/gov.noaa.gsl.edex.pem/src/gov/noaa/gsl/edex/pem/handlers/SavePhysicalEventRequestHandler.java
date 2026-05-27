/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */

package gov.noaa.gsl.edex.pem.handlers;

import java.io.IOException;
import java.util.zip.GZIPOutputStream;

import com.raytheon.uf.common.dataplugin.message.DataURINotificationMessage;
import com.raytheon.uf.common.serialization.SerializationException;
import com.raytheon.uf.common.serialization.SerializationUtil;
import com.raytheon.uf.common.serialization.comm.IRequestHandler;
import com.raytheon.uf.common.util.ByteArrayOutputStreamPool;
import com.raytheon.uf.common.util.PooledByteArrayOutputStream;
import com.raytheon.uf.edex.core.EdexException;
import com.raytheon.uf.edex.core.IMessageProducer;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.PhysicalEvent;
import gov.noaa.gsl.common.dataplugin.pem.request.SavePhysicalEventRequest;
import gov.noaa.gsl.common.dataplugin.pem.response.SavePhysicalEventResponse;
import gov.noaa.gsl.edex.pem.PhysicalEventEdexDao;

public class SavePhysicalEventRequestHandler
        implements IRequestHandler<SavePhysicalEventRequest> {

    /**
     * Buffer size.
     */
    private static final int GZIP_BUFFER_SIZE = 4096;

    /**
     * edex.alerts topic uri for data notifications
     */
    private static final String EDEX_ALERTS_TOPIC_URI = "jms-generic:topic:"
            + "edex.alerts" + "?timeToLive=60000";

    private IMessageProducer msgProducer;

    @Override
    public Object handleRequest(SavePhysicalEventRequest request)
            throws Exception {
        SavePhysicalEventResponse response = new SavePhysicalEventResponse();
        if (request == null) {
            return response;
        }

        PhysicalEventEdexDao dao = new PhysicalEventEdexDao(
                PhysicalEvent.PLUGIN_NAME);

        /*
         * Surprise, but the id of a PluginDataObject (ie PhysicalEvent) is not
         * serialized across the wire. So if someone tells us to save an event,
         * we won't have the correct ID in the event (or any id at all), and
         * hence hibernate will think it's new, and try to do a create where it
         * should do an update instead. So query for the event first, then
         * saveOrUpdate.
         */
        IPhysicalEvent rqstEvent = request.getPhysicalEvent();
        IPhysicalEvent eventToSave = rqstEvent;
        IPhysicalEvent existingEvent = dao
                .getPhysicalEvent(rqstEvent.getCustomId());

        if (existingEvent != null) {
            existingEvent.copyFrom(rqstEvent);
            eventToSave = existingEvent;
        }

        try {
            dao.saveOrUpdate(eventToSave);
        } catch (Exception e) {
            response.setError(e);
        }

        // Ugh. Cast.
        PhysicalEvent savedEvent = (PhysicalEvent) eventToSave;

        /*
         * Very unfortunate that it's the responsibility of this Handler to
         * issue a notification. Alternatives?
         */
        String dataURI = savedEvent.getDataURI();
        DataURINotificationMessage uriMsg = new DataURINotificationMessage();
        uriMsg.setDataURIs(new String[] { dataURI });

        byte[] bites = encodeMessage(uriMsg);
        msgProducer.sendAsyncUri(EDEX_ALERTS_TOPIC_URI, bites);
        return response;
    }

    /**
     * TODO This was copied from DataUriRouter, and it should really be put into
     * the SerializationUtil class, in ufcore.
     *
     * @param msg
     * @return
     * @throws EdexException
     */
    private byte[] encodeMessage(DataURINotificationMessage msg)
            throws EdexException {
        PooledByteArrayOutputStream baos = ByteArrayOutputStreamPool
                .getInstance().getStream();
        GZIPOutputStream gzippedURIs = null;

        try {
            gzippedURIs = new GZIPOutputStream(baos, GZIP_BUFFER_SIZE);
        } catch (IOException e) {
            throw new EdexException(getClass().getName()
                    + ": encodeMessage(...) Failed to prepare the gzipped data stream",
                    e);
        }

        try {
            SerializationUtil.transformToThriftUsingStream(msg, gzippedURIs);
            gzippedURIs.finish();
            gzippedURIs.flush();
            return baos.toByteArray();
        } catch (IOException e) {
            throw new EdexException(getClass().getName()
                    + ": encodeMessage(...) Failed to write the gzipped data stream",
                    e);
        } catch (SerializationException e) {
            throw new EdexException(getClass().getName()
                    + ": encodeMessage(...) Failed to serialize DataURINotificationMessage",
                    e);
        } finally {
            try {
                gzippedURIs.close();
            } catch (IOException e) {
                // ignore, we no longer need the stream
            }
        }
    }

    public void setMessageProducer(IMessageProducer msgProducer) {
        this.msgProducer = msgProducer;
    }
}
