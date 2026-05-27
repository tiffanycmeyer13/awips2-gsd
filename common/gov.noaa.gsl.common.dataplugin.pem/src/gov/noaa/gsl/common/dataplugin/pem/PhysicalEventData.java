/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.pem;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Inheritance;
import jakarta.persistence.InheritanceType;

/**
 * A default implementation of IPhysicalEventData , primarily existing so that
 * we can specify a Hibernate mapping for it, since an interface such as
 * IPhysicalEventData can not be an @Entity, and hence can not be mapped as a
 * relationship to/from the PhysicalEvent entity class.
 *
 * NOTE: I don't think Hibernate/edex should be creating a table for this class
 * if it is abstract, when doing TABLE_PER_CLASS inheritance. However it is
 * creating the table for some reason, and theoretically as a result, there is a
 * foreign key violation when saving a new PhysicalEvent with a new
 * PhysicalEventData subclass:
 *
 * ERROR: insert or update on table "phy_event" violates foreign key constraint.
 *
 * And so, I don't think we can make this class abstract, which seems really
 * bad. What's even worse is that if we do NOT make it abstract, we end up with
 * a phy_event_data table that does NOT get populated when a new subclass of
 * PhysicalEventData is saved into the subclass's table - only the subclass
 * table gets the new row. Foobar.
 *
 * @TODO Make this class abstract (see NOTE above).
 *
 *       <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Dec 13, 2021        Robert.Weingruber     Initial Creation
 *
 *       </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
@DynamicSerialize
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public class PhysicalEventData implements IPhysicalEventData {

    @Id
    @GeneratedValue
    @Column(name = "phy_event_data_id")
    protected int id;

    public PhysicalEventData() {
    }

    /**
     * Basically a no-op since we do not copy the id
     */
    @Override
    public void copyFrom(IPhysicalEventData other) {
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getId() {
        return id;
    }

    @Override
    public int hashCode() {
        return super.hashCode();
    }

    @Override
    public boolean equals(Object obj) {
        return super.equals(obj);
    }

    /**
     * @TODO See NOTE at the top of this class. We cant make this class
     *       abstract, so therefore we cant have an abstract method, so
     *       therefore we have to return unknown. Lame.
     */
    @Override
    public PhysicalEventType getPhysicalEventType() {
        return PhysicalEventType.UNKNOWN;
    }
}
