/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.pem.plot;

import java.util.ArrayList;
import java.util.List;

import gov.noaa.gsl.common.dataplugin.pem.IPhysicalEvent;

/**
 * This is the base class for Physical Event Plotters, which will render
 * Physical Events in the PEMMapDisplay
 * 
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jan 10, 2023            weingruber             Initial Creation
 *
 * </pre>
 * 
 * @author awips
 *
 */
public abstract class PEPlotter extends AbstractPlotter {

    public PEPlotter(PlotConfig config) {
        super(config);
    }

    public void setPhysicalEvents(List<IPhysicalEvent> events) {
        setData(events);
    }

    public List<IPhysicalEvent> getPhysicalEvents() {
        if (getData() == null) {
            return new ArrayList<>();
        }

        return (List<IPhysicalEvent>) getData();
    }
}
