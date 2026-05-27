package gov.noaa.gsl.common.dataplugin.atomsForecast;

import java.util.Objects;

import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;
import com.raytheon.uf.common.serialization.annotations.DynamicSerializeElement;

/**
 *
 * A place holder for PTWC Warning Point data
 *
 * <pre>
*
* SOFTWARE HISTORY
* Date         Ticket#    Engineer          Description
* ------------ ---------- ----------------- --------------------------
* Dec 09, 2025        Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
@DynamicSerialize
public class PtwcWarningPoint {

    @DynamicSerializeElement
    private String customId = "";

    @DynamicSerializeElement
    private String name = "";

    @DynamicSerializeElement
    private String country = "";

    @DynamicSerializeElement
    private String domain = "";

    public String getCustomId() {
        return customId;
    }

    public void setCustomId(String customId) {
        if (customId == null) {
            customId = "";
        }
        this.customId = customId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        if (name == null) {
            name = "";
        }
        this.name = name;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        if (country == null) {
            country = "";
        }
        this.country = country;
    }

    public String getDomain() {
        return domain;
    }

    public void setDomain(String domain) {
        if (domain == null) {
            domain = "";
        }
        this.domain = domain;
    }

    @Override
    public int hashCode() {
        return Objects.hash(country, customId, domain, name);
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
        PtwcWarningPoint other = (PtwcWarningPoint) obj;
        return Objects.equals(country, other.country)
                && Objects.equals(customId, other.customId)
                && Objects.equals(domain, other.domain)
                && Objects.equals(name, other.name);
    }

}
