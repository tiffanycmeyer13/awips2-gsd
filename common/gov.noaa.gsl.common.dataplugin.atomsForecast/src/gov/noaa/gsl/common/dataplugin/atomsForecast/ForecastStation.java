/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.atomsForecast;

import java.util.Objects;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.pem.ILonLat;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

/**
 *
 * A station representing a point for a tsunami forecast.
 *
 * NOTE Originally this class was the same as the Sea Level Station (for SLObs),
 * but the metadata for both stations was dramatically different, and hence, I
 * split the stations into two different classes. Also, there is no inheritance
 * relationship because I don't want to take the hibernate performance hit for
 * joining tables, etc, when querying for stations, and inheriting from a base
 * Station class wouldn't get us very far anyway.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Dec 13, 2021        Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */

@DynamicSerialize
@Entity
@Table(name = "forecast_station", uniqueConstraints = {
        @UniqueConstraint(columnNames = { "customId" }) })
public class ForecastStation implements ILonLat {

    @DynamicSerializeElement
    @Id
    @GeneratedValue
    private int id;

    @DynamicSerializeElement
    @Column
    private String customId;

    /**
     * TODO Should lat/lon be a Geometry?
     */
    @DynamicSerializeElement
    @Column
    private float latitude;

    @DynamicSerializeElement
    @Column
    private float longitude;

    @DynamicSerializeElement
    @Column
    private String name;

    @DynamicSerializeElement
    @Column
    private String state;

    @DynamicSerializeElement
    @Column
    private String country;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    @Override
    public float getLatitude() {
        return latitude;
    }

    public void setLatitude(float latitude) {
        this.latitude = latitude;
    }

    @Override
    public float getLongitude() {
        return longitude;
    }

    public void setLongitude(float longitude) {
        this.longitude = longitude;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCustomId() {
        return customId;
    }

    public void setCustomId(String customId) {
        this.customId = customId;
    }

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    @Override
    public int hashCode() {
        return Objects.hash(country, customId, latitude, longitude, name,
                state);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        ForecastStation other = (ForecastStation) obj;
        return Objects.equals(country, other.country)
                && Objects.equals(customId, other.customId)
                && Float.floatToIntBits(latitude) == Float
                        .floatToIntBits(other.latitude)
                && Float.floatToIntBits(longitude) == Float
                        .floatToIntBits(other.longitude)
                && Objects.equals(name, other.name)
                && Objects.equals(state, other.state);
    }

}
