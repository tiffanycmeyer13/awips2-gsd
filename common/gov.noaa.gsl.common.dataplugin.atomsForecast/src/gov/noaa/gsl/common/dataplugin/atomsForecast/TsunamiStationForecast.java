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

import java.util.Date;
import java.util.Objects;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.pem.ILonLat;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

/**
 *
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
@Table(name = "tsunami_station_fcst")
public class TsunamiStationForecast implements ILonLat {

    @Id
    @GeneratedValue
    private int id;

    @DynamicSerializeElement
    @ManyToOne
    @JoinColumn(name = "station_id")
    private ForecastStation station;

    @DynamicSerializeElement
    @Column
    private Date arrivalTime;

    @DynamicSerializeElement
    @Column
    private float amplitude = Float.NaN;

    @DynamicSerializeElement
    @Column
    private int duration;

    public ForecastStation getStation() {
        return station;
    }

    public void setStation(ForecastStation station) {
        this.station = station;
    }

    public Date getArrivalTime() {
        return arrivalTime;
    }

    public void setArrivalTime(Date arrivalTime) {
        this.arrivalTime = arrivalTime;
    }

    public float getAmplitude() {
        return amplitude;
    }

    public void setAmplitude(float amplitude) {
        this.amplitude = amplitude;
    }

    public int getDuration() {
        return duration;
    }

    public void setDuration(int duration) {
        this.duration = duration;
    }

    @Override
    public float getLatitude() {
        if (station != null) {
            return station.getLatitude();
        } else {
            return Float.NaN;
        }
    }

    @Override
    public float getLongitude() {
        if (station != null) {
            return station.getLongitude();
        } else {
            return Float.NaN;
        }
    }

    @Override
    public int hashCode() {
        return Objects.hash(amplitude, arrivalTime, duration, station);
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
        TsunamiStationForecast other = (TsunamiStationForecast) obj;
        return Float.floatToIntBits(amplitude) == Float
                .floatToIntBits(other.amplitude)
                && Objects.equals(arrivalTime, other.arrivalTime)
                && duration == other.duration
                && Objects.equals(station, other.station);
    }

}
