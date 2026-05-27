package gov.noaa.gsl.viz.pem.action;

import java.util.HashMap;

import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;

import com.raytheon.uf.common.dataquery.requests.RequestConstraint;
import com.raytheon.uf.common.dataquery.requests.RequestConstraint.ConstraintType;
import com.raytheon.uf.common.status.IUFStatusHandler;
import com.raytheon.uf.common.status.UFStatus;
import com.raytheon.uf.viz.core.comm.PerspectiveSpecificLoadProperties;
import com.raytheon.uf.viz.core.drawables.ResourcePair;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.IMapDescriptor;
import com.raytheon.uf.viz.core.rsc.AbstractVizResource;
import com.raytheon.uf.viz.core.rsc.GenericResourceData;
import com.raytheon.uf.viz.core.rsc.LoadProperties;
import com.raytheon.uf.viz.core.rsc.ResourceList;
import com.raytheon.uf.viz.d2d.core.D2DLoadProperties;
import com.raytheon.uf.viz.d2d.core.legend.D2DLegendResource;
import com.raytheon.uf.viz.d2d.core.time.D2DTimeMatcher;
import com.raytheon.uf.viz.d2d.core.time.LoadMode;
import com.raytheon.viz.ui.VizWorkbenchManager;
import com.raytheon.viz.ui.editor.AbstractEditor;
import com.raytheon.viz.ui.tools.map.AbstractMapTool;

import gov.noaa.gsl.viz.pem.dialog.PEMDialog;
import gov.noaa.gsl.viz.pem.rsc.PEMMapDisplay;
import gov.noaa.gsl.viz.pem.rsc.PEMMapResourceData;

/**
 * The loader to launch the physical event display resource from the tool bar.
 *
 * Before loading, check if the D2D works correctly. Fix few problems if need.
 *
 * <pre>
*
* SOFTWARE HISTORY
* Date         Ticket#    Engineer          Description
* ------------ ---------- ----------------- --------------------------
* Apr 19, 2922        Jing                  Initial creation
 *
 *
 * </pre>
 *
 * @author Jing
 *
 * @version 1.0
 *
 *
 */
@SuppressWarnings("deprecation")
public class PemDisplayAction extends AbstractMapTool {
    private static final transient IUFStatusHandler statusHandler = UFStatus
            .getHandler(PemDisplayAction.class);

    private PEMDialog pemDialog;

    @Override
    public Object execute(ExecutionEvent arg0) throws ExecutionException {

        // Xiangbao wrote all of this and I have no idea whether or not it
        // is correct. Certainly doesnt seem to work all of the time.
        // 8Gb of source for EDEX/AWIPS/CAVE is not documented
        // and the code is not self explanatory :-)

        /*
         * Ensure there is no previously created PEM resource;
         *
         * if there is, just use it, otherwise create a new one. Also make sure
         * that the number of panels in the main pane is only 1.
         */
        AbstractEditor editor = getEditor();
        if (editor == null || !(editor.getActiveDisplayPane()
                .getDescriptor() instanceof IMapDescriptor)) {
            Shell shell = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
                    .getShell();
            MessageDialog.openWarning(shell, "PEM Display",
                    "Cannot start the PEM Display without a map.");
            return null;
        }
        if (editor.getDisplayPanes().length > 1) {
            Shell shell = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
                    .getShell();
            MessageDialog.openWarning(shell, "PEM Display",
                    "Cannot start the PEM Display when in multi-panel mode.");
            return null;
        }

        IMapDescriptor desc = (IMapDescriptor) editor.getActiveDisplayPane()
                .getDescriptor();
        ResourceList rscList = desc.getResourceList();

        /* Is there a PEMMapDisplay resource */
        PEMMapDisplay pEMMapDisplay = null;
        for (ResourcePair rp : rscList) {
            AbstractVizResource<?, ?> rsc = rp.getResource();
            if (rsc instanceof PEMMapDisplay) {
                pEMMapDisplay = (PEMMapDisplay) rsc;
                break;
            }
        }

        /* Is there a loaded D2D Legend, just in case */
        D2DLegendResource legend = null;
        for (ResourcePair rp : rscList) {
            AbstractVizResource<?, ?> rsc = rp.getResource();
            if (rsc instanceof D2DLegendResource) {
                legend = (D2DLegendResource) rsc;
                break;
            }
        }

        /* Construct and load resources */
        if (pEMMapDisplay == null) {
            PEMMapResourceData data = new PEMMapResourceData();
            data.setRetrieveData(true);
            data.setUpdatingOnMetadataOnly(true);

            /* Set the meta data map in the PEMMapResourceData */
            HashMap<String, RequestConstraint> metadataMap = new HashMap<>();
            metadataMap.put("pluginName",
                    new RequestConstraint("pem", ConstraintType.EQUALS));
            data.setMetadataMap(metadataMap);

            /* Create a time matcher as D2D in the map descriptor */
            desc.setTimeMatcher(new D2DTimeMatcher());

            LoadProperties loadProperties = new LoadProperties();
            try {
                /* Create and set load properties */
                loadProperties.setLoadWithoutData(true);

                LoadMode loadMode = LoadMode.PROG_LOOP;

                /* Check the perspective properties */
                D2DLoadProperties dProp = null;
                PerspectiveSpecificLoadProperties pProp = loadProperties
                        .getPerspectiveProperty();
                if (pProp instanceof D2DLoadProperties) {
                    dProp = (D2DLoadProperties) pProp;
                } else {
                    dProp = new D2DLoadProperties();
                    loadProperties.setPerspectiveProperty(dProp);
                }
                dProp.setLoadMode(loadMode);
                loadMode = LoadMode.FORCED;// TODO

                pEMMapDisplay = (PEMMapDisplay) (data.construct(loadProperties,
                        desc));

                pEMMapDisplay.init(editor.getActiveDisplayPane().getTarget());

            } catch (VizException e) {
                System.err.println("Error while launching PEM Dispalay.");
                e.printStackTrace(System.err);
            }

            desc.getResourceList().add(pEMMapDisplay);

            /* load the legend if need */
            if (legend == null) {
                legend = new D2DLegendResource(new GenericResourceData(),
                        loadProperties);
                desc.getResourceList().add(legend);
            }
        } else {
            /*
             * TODO Check the case if the PEM dialog is normal, visible or
             * disposed
             */
        }

        Shell shell = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
                .getShell();
        if (pemDialog == null) {
            pemDialog = new PEMDialog(shell);
        }
        pemDialog.open();

        return null;
    }

    /**
     * Get the current editor.
     *
     * @return the current editor.
     *
     */
    public static AbstractEditor getEditor() {
        return (AbstractEditor) VizWorkbenchManager.getInstance()
                .getActiveEditor();
    }
}
