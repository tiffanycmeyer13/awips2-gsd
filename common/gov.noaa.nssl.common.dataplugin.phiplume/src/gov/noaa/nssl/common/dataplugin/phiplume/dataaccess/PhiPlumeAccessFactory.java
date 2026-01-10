/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Earth System Research Laboratory (ESRL),
 * Global Systems Division (GSD),
 * Evaluation & Decision Support Branch (EDS)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.nssl.common.dataplugin.phiplume.dataaccess;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;

import com.raytheon.uf.common.dataaccess.IDataRequest;
import com.raytheon.uf.common.dataaccess.exception.IncompatibleRequestException;
import com.raytheon.uf.common.dataaccess.geom.IGeometryData;
import com.raytheon.uf.common.dataaccess.impl.AbstractDataPluginFactory;
import com.raytheon.uf.common.dataaccess.impl.DefaultGeometryData;
import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.dataquery.requests.RequestConstraint;
import com.raytheon.uf.common.dataquery.responses.DbQueryResponse;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.time.DataTime;

import gov.noaa.nssl.common.dataplugin.phiplume.AbstractPhiPlumeRecord;

/**
 * TODO: Description
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * MMM DD, YYYY            TBD_USER          Initial creation
 *
 * </pre>
 *
 * @author TBD_USER
 * @version 1.0
 */
public class PhiPlumeAccessFactory extends AbstractDataPluginFactory {

    private static final IUFStatusHandler log = UFStatus
            .getHandler(AbstractPhiPlumeRecord.class);

    private static final GeometryFactory geomFactory = new GeometryFactory();

//    @Override
//    public String[] getRequiredIdentifiers(IDataRequest request) {
//        return new String[] { "objectType" };
//    }

    /*
     * NOTE: Update AVAILABLE_PARAMETERS to coincide with AbstractPhiPlumeRecord
     */
    public static final String[] AVAILABLE_PARAMETERS = { "objectType",
            "probability", "speed", "direction", "id", "hazardType",
            "validStart", "validEnd", "dataURI", "probsevereAttrs",
            "best_csi_threshold" };

    @Override
    public String[] getAvailableLocationNames(IDataRequest request) {
        throw new IncompatibleRequestException(
                this.getClass() + " does not support location names");
    }

    @Override
    public String[] getAvailableParameters(IDataRequest request) {
        return AVAILABLE_PARAMETERS;
    }

    @Override
    public String[] getOptionalIdentifiers(IDataRequest request) {
        return new String[] { PluginDataObject.DATAURI_ID };
    }

    @Override
    protected Map<String, RequestConstraint> buildConstraintsFromRequest(
            IDataRequest request) {
        Map<String, RequestConstraint> rcMap = new HashMap<>();

        Map<String, Object> identifiers = request.getIdentifiers();
        if (identifiers != null) {
            for (Entry<String, Object> entry : identifiers.entrySet()) {
                Object value = entry.getValue();
                if (value instanceof RequestConstraint) {
                    rcMap.put(entry.getKey(), (RequestConstraint) value);
                } else {
                    rcMap.put(entry.getKey(),
                            new RequestConstraint(value.toString()));
                }
            }
        }
        return rcMap;
    }

    @Override
    protected IGeometryData[] getGeometryData(IDataRequest request,
            DbQueryResponse dbQueryResponse) {
        Map<DataTime, List<AbstractPhiPlumeRecord>> results = unpackResults(
                dbQueryResponse);

        if (results.isEmpty()) {
            return new IGeometryData[0];
        }

        List<IGeometryData> rval = new ArrayList<>();

        for (Entry<DataTime, List<AbstractPhiPlumeRecord>> resultEntry : results
                .entrySet()) {
            DataTime dt = resultEntry.getKey();

            List<AbstractPhiPlumeRecord> records = resultEntry.getValue();
            for (AbstractPhiPlumeRecord record : records) {

                /*
                 * NOTE: Need more data fields to coincide with updated
                 * AbstractPhiPlumeRecord
                 */

                Date validStart = record.getValidStart();
                Date validEnd = record.getValidEnd();
                Integer probability = record.getProbability();
                Integer speed = record.getSpeed();
                Integer direction = record.getDirection();
                String id = record.getIDnum();
                // String hazardType = record.getHazardType();
                String objectType = record.getObjectType();
                String dataURI = record.getDataURI();
                String bestCSI = record.getBest_csi_threshold();
                String probsevereAttrs = record.getProbsevereAttrs();

                Geometry warningGeom = record.getGeometry();

                DefaultGeometryData data = new DefaultGeometryData();
                data.setDataTime(dt);

                data.setGeometry(warningGeom);
                data.addAttribute("probability", probability);
                data.addAttribute("speed", speed);
                data.addAttribute("direction", direction);
                data.addAttribute("id", id);
                // data.addAttribute("hazardType", hazardType);
                data.addAttribute("objectType", objectType);
                data.addAttribute("validStart", validStart);
                data.addAttribute("validEnd", validEnd);
                data.addAttribute("dataURI", dataURI);
                data.addAttribute("best_csi_threshold", bestCSI);
                data.addAttribute("probsevereAttrs", probsevereAttrs);
                rval.add(data);
            }
        }

        return rval.toArray(new IGeometryData[rval.size()]);
    }

    /**
     * Unpack records from response and group by HDF5 file
     *
     * @param dbQueryResponse
     * @return
     */
    private Map<DataTime, List<AbstractPhiPlumeRecord>> unpackResults(
            DbQueryResponse dbQueryResponse) {
        // Bin up requests to the same hdf5
        Map<DataTime, List<AbstractPhiPlumeRecord>> dtMap = new HashMap<>();

        for (Map<String, Object> result : dbQueryResponse.getResults()) {
            Object object = result.get(null);
            if (object == null || !(object instanceof AbstractPhiPlumeRecord)) {
                log.warn("Unexpected result for PhiPlume: " + object);
                continue;
            }
            AbstractPhiPlumeRecord record = (AbstractPhiPlumeRecord) object;

            DataTime dt = record.getDataTime();

            List<AbstractPhiPlumeRecord> recList = dtMap.get(dt);
            if (recList == null) {
                recList = new ArrayList<>();
                dtMap.put(dt, recList);
            }
            recList.add(record);
        }
        return dtMap;
    }

    @Override
    public String[] getIdentifierValues(IDataRequest request,
            String identifierKey) {
        return getAvailableValues(request, identifierKey, String.class);
    }

}