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
 * Class to represent a TRECS documented procedure
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
public class TrecsExecProcedure {

    private boolean isDefault = false;

    private boolean isSelected = false;

    private String name = "";

    private List<TrecsExecCategory> categories = new ArrayList();

    private TrecsExecCategory selectedCategory = null;

    private TrecsExecCategory defaultCategory = null;

    public TrecsExecProcedure(String name) {
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException(
                    "TrecsExecProcedure() received a null or empty name.");
        }
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean isDefault() {
        return isDefault;
    }

    public void setDefault(boolean isDefault) {
        this.isDefault = isDefault;
    }

    public boolean isSelected() {
        return isSelected;
    }

    public void setSelected(boolean isSelected) {
        this.isSelected = isSelected;
    }

    public List<TrecsExecCategory> getCategories() {
        return categories;
    }

    public void setCategories(List<TrecsExecCategory> categories) {
        if (categories == null) {
            categories = new ArrayList();
        }
        this.categories = categories;
    }

    public TrecsExecCategory getSelectedCategory() {
        return selectedCategory;
    }

    public void setSelectedCategory(TrecsExecCategory selectedCategory) {
        this.selectedCategory = selectedCategory;
    }

    public TrecsExecCategory getDefaultCategory() {
        return defaultCategory;
    }

    public void setDefaultCategory(TrecsExecCategory defaultCategory) {
        this.defaultCategory = defaultCategory;
    }

    @Override
    public String toString() {
        return "TrecsExecProcedure [isDefault=" + isDefault + ", isSelected="
                + isSelected + ", name=" + name + ", categories=" + categories
                + ", selectedCategory=" + selectedCategory + "]";
    }

}