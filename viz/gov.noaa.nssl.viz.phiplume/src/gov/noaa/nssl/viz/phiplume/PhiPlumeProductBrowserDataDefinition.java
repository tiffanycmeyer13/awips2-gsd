package gov.noaa.nssl.viz.phiplume;

import java.util.ArrayList;
import java.util.List;

import com.raytheon.uf.common.localization.PathManagerFactory;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.common.status.UFStatus.Priority;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.procedures.Bundle;
import com.raytheon.uf.viz.core.rsc.LoadProperties;
import com.raytheon.uf.viz.core.rsc.ResourceType;
import com.raytheon.uf.viz.productbrowser.AbstractProductBrowserDataDefinition;
import com.raytheon.uf.viz.productbrowser.ProductBrowserLabel;
import com.raytheon.uf.viz.productbrowser.ProductBrowserPreference;
import com.raytheon.viz.ui.BundleProductLoader;
import com.raytheon.viz.ui.EditorUtil;

import gov.noaa.nssl.viz.phiplume.rsc.PhiPlumeResourceData;

/**
 * NOAA/NSSL Phi Plume Model Product Browser Data Definition
 *
 * Defines product browser access to NOAA/NSSL Phi Plume Model data
 *
 * <pre>
 * SOFTWARE HISTORY Date Ticket# Engineer Description ------------ ----------
 * ----------- -------------------------- 22 May 2022 #103581 kmanross Initial
 * Creation.
 *
 * </pre
 *
 * @author Kevin Manross
 * @version 1.0
 *
 */
public class PhiPlumeProductBrowserDataDefinition
        extends AbstractProductBrowserDataDefinition<PhiPlumeResourceData> {

    IUFStatusHandler statusHandler = UFStatus
            .getHandler(PhiPlumeProductBrowserDataDefinition.class);

    /**
     * Constructor defining new instance of this class
     */
    public PhiPlumeProductBrowserDataDefinition() {
        displayName = "NOAA/NSSL Phi Plume";
        loadProperties = new LoadProperties();
    }

    /**
     * @see com.raytheon.uf.viz.productbrowser.AbstractProductBrowserDataDefinition#getResourceData()
     */
    @Override
    public PhiPlumeResourceData getResourceData() {
        return new PhiPlumeResourceData();
    }

    /**
     * @see com.raytheon.uf.viz.productbrowser.AbstractProductBrowserDataDefinition#populateData(java.lang.String[])
     */
    @Override
    public List<ProductBrowserLabel> populateData(String[] selection) {
        List<ProductBrowserLabel> labels = new ArrayList<ProductBrowserLabel>();
        ProductBrowserLabel label = new ProductBrowserLabel(
                "NOAA/NSSL Phi Plume Model", "Phi Plumes");
        label.setProduct(true);
        labels.add(label);
        return labels;
    }

    /**
     * @see com.raytheon.uf.viz.productbrowser.AbstractProductBrowserDataDefinition#buildProductList(java.util.List)
     */
    @Override
    public List<String> buildProductList(List<String> historyList) {
        return historyList;
    }

    /**
     * @see com.raytheon.uf.viz.productbrowser.AbstractProductBrowserDataDefinition#constructResource(java.lang.String[],
     *      com.raytheon.uf.viz.core.rsc.ResourceType)
     */
    @Override
    public void constructResource(String[] selection, ResourceType type) {
        try {
            Bundle b = Bundle.unmarshalBundle(PathManagerFactory
                    .getPathManager().getStaticFile("bundles/phiPlume.xml"));
            new BundleProductLoader(EditorUtil.getActiveVizContainer(), b)
                    .run();
        } catch (VizException e1) {
            statusHandler.handle(Priority.PROBLEM,
                    "Could not create resource for NOAA/NSSL PhiPlume Overlay Model data",
                    e1);
        }
    }

    /**
     * @see com.raytheon.uf.viz.productbrowser.AbstractProductBrowserDataDefinition#configurePreferences()
     */
    @Override
    public List<ProductBrowserPreference> configurePreferences() {
        return super.configurePreferences();
    }

}
