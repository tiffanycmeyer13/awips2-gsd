/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Weather Informatics and Decision Support Division (WIDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.viz.atoms.trecs;

import java.util.ArrayList;
import java.util.List;

/**
 * Class to represent a TRECS documented procedure's category, that is
 * executable in python
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Jul 31, 2023   100405    Robert Weingruber Initial creation.
 * </pre>
 *
 * @author Robert Weingruber
 * @version 1.0
 */
public class TrecsExecCategory {

    private String pythonExecClassname;

    private String name = "";

    private List<String> conditions = new ArrayList();

    private List<String> actions = new ArrayList();

    public TrecsExecCategory(String name) {
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException(
                    "TrecsExecCategory() received a null or empty name.");
        }
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<String> getConditions() {
        return conditions;
    }

    public void setConditions(List<String> conditions) {
        if (conditions != null) {
            this.conditions = conditions;
        }
    }

    public List<String> getActions() {
        return actions;
    }

    public void setActions(List<String> actions) {
        if (actions != null) {
            this.actions = actions;
        }
    }

    public String getPythonExecClassname() {
        return pythonExecClassname;
    }

    public void setPythonExecClassname(String pythonExecClassname) {
        this.pythonExecClassname = pythonExecClassname;
    }

    @Override
    public String toString() {
        return "TrecsExecCategory [name=" + name + "]";
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((actions == null) ? 0 : actions.hashCode());
        result = prime * result
                + ((conditions == null) ? 0 : conditions.hashCode());
        result = prime * result + ((name == null) ? 0 : name.hashCode());
        result = prime * result + ((pythonExecClassname == null) ? 0
                : pythonExecClassname.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        TrecsExecCategory other = (TrecsExecCategory) obj;
        if (actions == null) {
            if (other.actions != null)
                return false;
        } else if (!actions.equals(other.actions))
            return false;
        if (conditions == null) {
            if (other.conditions != null)
                return false;
        } else if (!conditions.equals(other.conditions))
            return false;
        if (name == null) {
            if (other.name != null)
                return false;
        } else if (!name.equals(other.name))
            return false;
        if (pythonExecClassname == null) {
            if (other.pythonExecClassname != null)
                return false;
        } else if (!pythonExecClassname.equals(other.pythonExecClassname))
            return false;
        return true;
    }

}