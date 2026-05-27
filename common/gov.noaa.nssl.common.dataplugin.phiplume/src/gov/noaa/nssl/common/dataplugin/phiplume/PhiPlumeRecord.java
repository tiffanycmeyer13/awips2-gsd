package gov.noaa.nssl.common.dataplugin.phiplume;

import org.hibernate.annotations.Index;

import com.raytheon.uf.common.dataplugin.PluginDataObject;
import com.raytheon.uf.common.serialization.annotations.DynamicSerialize;

import jakarta.persistence.Access;
import jakarta.persistence.AccessType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

@Entity
@SequenceGenerator(initialValue = 1, name = PluginDataObject.ID_GEN, sequenceName = "phiplumeseq")
@Table(name = PhiPlumeRecord.PLUGIN_NAME, uniqueConstraints = {
        @UniqueConstraint(name = "uk_phiplume_datauri_fields", columnNames = {
                "dataURI" }) })
@org.hibernate.annotations.Table(appliesTo = PhiPlumeRecord.PLUGIN_NAME, indexes = {
        @Index(name = "phiplume_refTimeIndex", columnNames = { "refTime" }) })

@DynamicSerialize
public class PhiPlumeRecord extends AbstractPhiPlumeRecord {

    private static final long serialVersionUID = 1L;

    public static final String PLUGIN_NAME = "phiplume";

    /**
     * Default empty constructor
     */
    public PhiPlumeRecord() {
        super();
    }

    @Override
    @Column
    @Access(AccessType.PROPERTY)
    public String getDataURI() {
        return super.getDataURI();
    }

    @Override
    public String getPluginName() {
        return PLUGIN_NAME;
    }
}
