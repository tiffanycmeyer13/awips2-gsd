package gov.noaa.gsd.viz.ensemble.display.common;

import java.util.Comparator;

import com.raytheon.uf.common.time.DataTime;
import com.raytheon.uf.viz.core.drawables.IDescriptor;
import com.raytheon.uf.viz.core.drawables.IDescriptor.FramesInfo;
import com.raytheon.uf.viz.core.rsc.AbstractVizResource;
import com.raytheon.uf.viz.core.rsc.IRefreshListener;
import com.raytheon.uf.viz.xy.timeseries.rsc.TimeSeriesResource;
import com.raytheon.viz.grid.rsc.GridNameGenerator;

import gov.noaa.gsd.viz.ensemble.control.EnsembleTool;
import gov.noaa.gsd.viz.ensemble.display.rsc.GeneratedEnsembleGridResource;
import gov.noaa.gsd.viz.ensemble.display.rsc.histogram.HistogramResource;
import gov.noaa.gsd.viz.ensemble.display.rsc.timeseries.GeneratedTimeSeriesResource;

/**
 * This class represents the abstract container which encapulates an
 * AbstractVizResource (that happens to be associated with the Ensemble Tool).
 * It provides a poor-man's approach at defining how to parse and extract common
 * resource metadata, an interface that doesn't already exist in the viz
 * resource class. Similar approaches have been attempted in other resource data
 * classes (e.g. getMetaDataMap) but were not necessarily reusable. This class
 * exists to attempt to fill an unusual void in the hierarchy of an
 * AbstractVizResource as there is no convenient way to extract commonly known
 * meteorological metadata information from the resource (needs verification).
 *
 * This abstact class forces derived classes to define the equals() and hashCode
 * methods, among other notable getters.
 *
 * In order to create a class of this type call the factory method (see
 * createResourceHolder).
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Nov 17, 2014    5056     polster     Initial creation
 * Jan 17, 2016    13211    polster     Renamed class from GenericResourceHolder
 *                                      to AbstractResourceHolder
 * Dec 29, 2016    19325    jing        Deal with Image display type in equals()
 * Jun 27  2017    19325    jing        Reinvestigate equals() and save as TODO
 * Nov 14  2021    99971    srussell    Added AbstractResourceHolder.EnsIDComparator
 *
 * </pre>
 *
 * @author polster
 * @author jing
 * @version 1.0
 */

public abstract class AbstractResourceHolder
        extends AbstractLegendComponentsProvider
        implements ITreeModelProvider, IRefreshListener {

    protected AbstractVizResource<?, ?> rsc;

    protected EnsembleMembersHolder parent = null;

    /*
     * Resources are either normally loaded, or generated client-side as in
     * calculated resources (mean, min, max, etc)
     */
    protected boolean isGenerated = false;

    protected boolean isIndividualProduct = true;

    public static AbstractResourceHolder createResourceHolder(
            AbstractVizResource<?, ?> rsc) {

        AbstractResourceHolder genericRsc = null;

        if (GeneratedEnsembleGridResource.class
                .isAssignableFrom(rsc.getClass())) {
            genericRsc = new GeneratedGridResourceHolder(rsc);
        } else if (GeneratedTimeSeriesResource.class
                .isAssignableFrom(rsc.getClass())) {
            genericRsc = new GeneratedTimeSeriesResourceHolder(rsc);
        } else if ((rsc instanceof AbstractVizResource<?, ?>)
                && (rsc instanceof GridNameGenerator.IGridNameResource)) {
            genericRsc = new GridResourceHolder(rsc);
        } else if (TimeSeriesResource.class.isAssignableFrom(rsc.getClass())) {
            genericRsc = new TimeSeriesResourceHolder(rsc);
        } else if (HistogramResource.class.isAssignableFrom(rsc.getClass())) {
            genericRsc = new HistogramGridResourceHolder(rsc);
        } else if (rsc instanceof AbstractVizResource<?, ?>) {
            genericRsc = new GenericResourceHolder(rsc);
        }
        return genericRsc;
    }

    /*
     * TODO: This commented out equals method which follows is still needed for
     * the Image product comparison. We will be putting this back in for the
     * 17.3.1 release.
     */
    // @Override
    // public boolean equals(Object o) {
    // boolean equals = false;
    // if (o instanceof AbstractResourceHolder) {
    // AbstractResourceHolder gr = (AbstractResourceHolder) o;
    // equals = this.getSpecificName().equals(gr.getSpecificName());
    // // Catch image case that the two names are different.
    // if (this.getRsc() == null || this.getRsc().getName() == null
    // || gr.getRsc() == null || gr.getRsc().getName() == null) {
    // if (gr.getRsc() == null) {
    // System.out.println(
    // ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> gr.getRsc() is
    // null.");
    // } else if (gr.getRsc().getName() == null) {
    // System.out.println(
    // ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    // gr.getRsc().getName() is null.");
    // }
    // new Exception().printStackTrace();
    //
    // } else if (!this.getRsc().getName().equals(gr.getRsc().getName())) {
    // equals = false;
    // }
    //
    // } else {
    // equals = false;
    // }
    // return equals;
    // }

    @Override
    public int hashCode() {
        return getSpecificName().hashCode();
    }

    protected AbstractResourceHolder() {

    }

    protected AbstractResourceHolder(AbstractVizResource<?, ?> rsc) {
        this.rsc = rsc;
    }

    public AbstractVizResource<?, ?> getRsc() {
        return rsc;
    }

    public void setRsc(AbstractVizResource<?, ?> rsc) {
        this.rsc = rsc;
    }

    public boolean isSelected() {
        boolean is = false;
        if (rsc != null) {
            is = rsc.getProperties().isVisible();
        }
        return is;
    }

    public boolean isGenerated() {
        return isGenerated;
    }

    public void setGenerated(boolean isEnsGenerated) {
        this.isGenerated = isEnsGenerated;
    }

    @Override
    public boolean isLoadedAtFrame() {

        if (getRsc() == null) {
            return false;
        }

        // Use the current resource to directly get the current FramesInfo
        // for avoid asynchronous issue.
        FramesInfo currentFrameInfo = getRsc().getDescriptor().getFramesInfo();
        if (currentFrameInfo == null) {
            return false;
        }

        // Get the frame index by the frame time
        DataTime[] frameTimes = currentFrameInfo.getFrameTimes();
        if (frameTimes == null || frameTimes.length < 1) {
            return false;
        }

        // Get the resource data time in current frame.
        DataTime resourceTime = currentFrameInfo.getTimeForResource(getRsc(),
                currentFrameInfo.getFrameIndex());
        if (resourceTime == null) {
            return false;
        }

        return true;

        // TODO: Verify if the data loaded at local.
        // D2DGridResource gridResource = null;
        // For none D2D grid resource do nothing to verify data currently
        // if (getRsc() instanceof D2DGridResource) {
        // gridResource = (D2DGridResource) getRsc();
        // } else {
        // return true;
        // }
        // Whether the resource grid data is in the current frame.
        // Refer to the loaded data in current frame, otherwise will do an extra
        // data request
        // to verify.It will not hurt any, just inefficient. because the
        // requestData(resourceTime)
        // is the only interface we can use. It will be best to added a
        // interface
        // "public boolean isDataLoaded(DataTime resourceTime)" in the
        // AbstractGrideResource class.
        // List<GeneralGridData> data = gridResource.requestData(resourceTime);
        // if (data != null ||data.isEmpty() ) {
        // return true;
        // }
        // return false;
    }

    public boolean isLoadedAtFrameInternal(FramesInfo info) {

        if (getRsc() == null) {
            return false;
        }

        // Use the current resource to directly get the current FramesInfo
        // for avoid asynchronous issue.
        FramesInfo currentFrameInfo = getRsc().getDescriptor().getFramesInfo();
        if (currentFrameInfo == null) {
            return false;
        }

        AbstractVizResource<?, ?> resource = getRsc();
        String name = resource.getName();
        if (name == null) {
            return false;
        }

        if (!resource.isTimeAgnostic()) {
            boolean hasTimes = false;
            DataTime[] times = info.getTimeMap().get(resource);
            if (times != null) {
                for (DataTime dt : times) {
                    if (dt != null) {
                        hasTimes = true;
                        break;
                    }
                }
            }
            if (!hasTimes) {
                return false;
            }

            DataTime time = getDataTimeForResource(getRsc(),
                    getRsc().getDescriptor(), info);

            if (time == null) {
                return false;
            }

            // Get the frame index by the frame time
            DataTime[] frameTimes = currentFrameInfo.getFrameTimes();
            if (frameTimes == null || frameTimes.length < 1) {
                return false;
            }

            // Check if this resource is loaded in any frame
            // by checking matched data time
            for (int i = 0; i < frameTimes.length; i++) {
                // Any matched resource data time for a frame
                DataTime memberTime = getRsc().getDescriptor().getFramesInfo()
                        .getTimeForResource(getRsc(), i);
                if (memberTime != null) {
                    return true;
                }
            }

        }
        return false;
    }

    private DataTime getDataTimeForResource(AbstractVizResource<?, ?> rsc,
            IDescriptor descriptor, FramesInfo info) {
        return info.getTimeForResource(rsc);
    }

    public abstract boolean requiresLoadCheck();

    @Override
    public void refresh() {
        if (EnsembleTool.getInstance().getToolLayer() != null) {
            EnsembleTool.getInstance().getToolLayer().updateElementInView(this);
        }
    }

    @Override
    public Object getParent() {
        return parent;
    }

    @Override
    public void setParent(EnsembleMembersHolder emh) {
        parent = emh;
    }

    /**
     * Is this an indivdual product or a group of products like an ensemble?
     */
    @Override
    public boolean isIndivdualProduct() {
        return isIndividualProduct;
    }

    /*-
     * Use this Comparator to sort collections of AbstractResourceHolders that
     * implement getEnsembleIdRaw() that you want sorted by perturbation.
     * This comparator will handle IDs that start with letters and end with
     * digits.
     * Example: ct110, p1,p2, n2.
     */
    public static Comparator<AbstractResourceHolder> EnsIDComparator = new Comparator<AbstractResourceHolder>() {

        @Override
        public int compare(AbstractResourceHolder arh1,
                AbstractResourceHolder arh2) {

            int result = 0;

            // get the Ensemble ID, example: ct110, p1,p2...p21
            String id1 = arh1.getEnsembleIdRaw();
            String id2 = arh2.getEnsembleIdRaw();

            // Split the ID into a prefix of alphabetic characters and
            // a suffix of digits
            // Example: p21 becomes p 21
            String[] tokens1 = id1.split("((?=\\d)|(?<=\\d))", 2);
            String[] tokens2 = id2.split("((?=\\d)|(?<=\\d))", 2);
            String prefixARH1 = tokens1[0];
            String prefixARH2 = tokens2[0];
            String suffixARH1 = tokens1[1];
            String suffixARH2 = tokens2[1];
            int suffix1 = Integer.parseInt(suffixARH1);
            int suffix2 = Integer.parseInt(suffixARH2);

            int prefixesCompared = prefixARH1.compareToIgnoreCase(prefixARH2);

            // The 2 alphabetic prefixes are not the same, return the
            // comparison result
            if (prefixesCompared != 0) {
                return prefixesCompared;
            }

            // Compare the integers of the suffix on the IDs
            if (suffix1 == suffix2) {
                result = 0;
            } else if (suffix1 > suffix2) {
                result = 1;
            } else {
                // if(suffix1 < suffix2 )
                result = -1;
            }

            return result;
        }

    };

}
