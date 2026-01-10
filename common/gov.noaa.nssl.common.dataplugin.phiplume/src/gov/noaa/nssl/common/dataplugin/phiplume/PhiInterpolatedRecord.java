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
@SequenceGenerator(initialValue = 1, name = PluginDataObject.ID_GEN, sequenceName = "phiinterpolatedseq")
@Table(name = PhiInterpolatedRecord.PLUGIN_NAME, uniqueConstraints = {
        @UniqueConstraint(name = "uk_phiinterpolated_datauri_fields", columnNames = {
                "dataURI" }) })
@org.hibernate.annotations.Table(appliesTo = PhiInterpolatedRecord.PLUGIN_NAME, indexes = {
        @Index(name = "phiinterpolated_refTimeIndex", columnNames = {
                "refTime" }) })

@DynamicSerialize
public class PhiInterpolatedRecord extends AbstractPhiPlumeRecord {

    private static final long serialVersionUID = 1L;

    public static final String PLUGIN_NAME = "phiinterpolated";

//    public enum PROBSEVEREKEYS{
//      // See https://cimss.ssec.wisc.edu/severe_conv/training/ProbSevere_v2_FileDescription.pdf
//    FLASHRATE("flashRate"),
//            p98llaz=0.004,
//            probWind=4,
//            mlcape=694,
//            duration4=60,
//            maxllaz=0.005,
//            lightningJump=0,
//            glaciation=0,
//            flashDensity=0.11,
//            rh7045=0,
//            wb0=5.5,
//            abh=6.64,
//            probHail=12,
//            srh01km=137,
//            mWind79=39,
//            prob=13,
//            shear=51,
//            probTor=2,
//            mlcin=-9,
//            duration5=60,
//            lr75=0,
//            mesh=0.15,
//            cape=1337,
//            p98mlaz=0.005,
//            besttrack=1014224,
//            growth=0,
//            vilDensity=0.6
//
//                    private final String fieldName;
//
//            PROBSEVEREKEYS(String name) {
//                fieldName = name;
//            }
//
//            /**
//             * @return the field name
//             */
//            public String getFieldName() {
//                return fieldName;
//
//    }

    /**
     * Default empty constructor
     */
    public PhiInterpolatedRecord() {
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
