package gov.noaa.gsl.common.dataplugin.atomsSeaLevelObs;

import java.util.Date;
import java.util.Objects;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

import gov.noaa.gsl.common.dataplugin.pem.ILonLat;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@DynamicSerialize
@Entity
@Table(name = "sea_level_obs")
public class SeaLevelObs implements ILonLat {

    @Id
    @GeneratedValue
    private int id;

    @DynamicSerializeElement
    @ManyToOne
    @JoinColumn(name = "station_id", nullable = false)
    private SeaLevelStation station;

    @DynamicSerializeElement
    @Column(name = "sensor_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private SLOSensorType sensorType;

    @DynamicSerializeElement
    @Column(name = "obs_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private SLOObsType obsType;

    @DynamicSerializeElement
    @Column(name = "startTime", nullable = false)
    private Date startTime;

    @DynamicSerializeElement
    @Column(name = "endTime", nullable = true)
    private Date endTime;

    @DynamicSerializeElement
    @Column(name = "amplitude", nullable = true)
    private Float amplitude;

    @DynamicSerializeElement
    @Column(name = "period", nullable = true)
    private Float period;

    @DynamicSerializeElement
    @Column(name = "firstWavePositive", nullable = true)
    private Boolean firstWavePositive;

    @DynamicSerializeElement
    @Column(name = "tsunamiDetected", nullable = true)
    private Boolean tsunamiDetected;

    @DynamicSerializeElement
    @Column(name = "msrmt1Clipped", nullable = true)
    private Boolean msrmt1Clipped;

    @DynamicSerializeElement
    @Column(name = "msrmt2Clipped", nullable = true)
    private Boolean msrmt2Clipped;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public SeaLevelStation getStation() {
        return station;
    }

    public void setStation(SeaLevelStation station) {
        this.station = station;
    }

    public SLOSensorType getSensorType() {
        return sensorType;
    }

    public void setSensorType(SLOSensorType sensorType) {
        this.sensorType = sensorType;
    }

    public SLOObsType getObsType() {
        return obsType;
    }

    public void setObsType(SLOObsType obsType) {
        this.obsType = obsType;
    }

    public Date getStartTime() {
        return startTime;
    }

    public void setStartTime(Date startTime) {
        this.startTime = startTime;
    }

    public Date getEndTime() {
        return endTime;
    }

    public void setEndTime(Date endTime) {
        this.endTime = endTime;
    }

    public Float getAmplitude() {
        return amplitude;
    }

    public void setAmplitude(Float amplitude) {
        this.amplitude = amplitude;
    }

    public Float getPeriod() {
        return period;
    }

    public void setPeriod(Float period) {
        this.period = period;
    }

    public Boolean isFirstWavePositive() {
        return firstWavePositive;
    }

    public void setFirstWavePositive(Boolean firstWavePositive) {
        this.firstWavePositive = firstWavePositive;
    }

    public Boolean isTsunamiDetected() {
        return tsunamiDetected;
    }

    public void setTsunamiDetected(Boolean tsunamiDetected) {
        this.tsunamiDetected = tsunamiDetected;
    }

    public Boolean isMsrmt1Clipped() {
        return msrmt1Clipped;
    }

    public void setMsrmt1Clipped(Boolean msrmt1Clipped) {
        this.msrmt1Clipped = msrmt1Clipped;
    }

    public Boolean isMsrmt2Clipped() {
        return msrmt2Clipped;
    }

    public void setMsrmt2Clipped(Boolean msrmt2Clipped) {
        this.msrmt2Clipped = msrmt2Clipped;
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
        return Objects.hash(amplitude, endTime, firstWavePositive,
                msrmt1Clipped, msrmt2Clipped, obsType, period, sensorType,
                startTime, station, tsunamiDetected);
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
        SeaLevelObs other = (SeaLevelObs) obj;
        return Objects.equals(amplitude, other.amplitude)
                && Objects.equals(endTime, other.endTime)
                && Objects.equals(firstWavePositive, other.firstWavePositive)
                && Objects.equals(msrmt1Clipped, other.msrmt1Clipped)
                && Objects.equals(msrmt2Clipped, other.msrmt2Clipped)
                && obsType == other.obsType
                && Objects.equals(period, other.period)
                && sensorType == other.sensorType
                && Objects.equals(startTime, other.startTime)
                && Objects.equals(station, other.station)
                && Objects.equals(tsunamiDetected, other.tsunamiDetected);
    }
}
