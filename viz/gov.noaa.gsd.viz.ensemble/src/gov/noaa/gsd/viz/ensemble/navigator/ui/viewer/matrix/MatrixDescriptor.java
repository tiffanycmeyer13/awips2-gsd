package gov.noaa.gsd.viz.ensemble.navigator.ui.viewer.matrix;

import jakarta.xml.bind.annotation.XmlAccessType;
import jakarta.xml.bind.annotation.XmlAccessorType;
import jakarta.xml.bind.annotation.XmlRootElement;

import org.geotools.api.referencing.crs.CoordinateReferenceSystem;
import org.geotools.coverage.grid.GeneralGridGeometry;
import org.locationtech.jts.geom.Coordinate;

import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.MapDescriptor;

/**
 * 
 * The matrix descriptor is needed in support of the VizMatrixEditor.
 * 
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Dec 1, 2017            polster     Initial creation
 *
 * </pre>
 *
 * @author polster
 */
@XmlAccessorType(XmlAccessType.NONE)
@XmlRootElement
public class MatrixDescriptor extends MapDescriptor {

    public MatrixDescriptor() throws VizException {
        super();
    }

    public MatrixDescriptor(CoordinateReferenceSystem crs, Coordinate llCoord,
            Coordinate urCoord) throws VizException {
        super(crs, llCoord, urCoord);
    }

    public MatrixDescriptor(GeneralGridGeometry gridGeometry) {
        super(gridGeometry);
    }

}
