import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { differenceInYears } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDateField, GridDropdownField, GridTextField } from 'src/components/common/GridField';
import {
    ClinicCode,
    clinicCodeValues,
    PatientSex,
    patientSexValues,
    TreatmentRegimen,
    treatmentRegimenValues,
} from 'src/services/enums';
import { useStores } from 'src/stores/stores';

interface IMedicalInfo {
    primaryCareManager: string;
    sex: PatientSex;
    birthdate: Date;
    clinicCode: ClinicCode;
    treatmentRegimen: TreatmentRegimen;
    medicalDiagnosis: string;
}

interface IMedicalInformationContentProps extends Partial<IMedicalInfo> {
    editable?: boolean;
    onValueChange: (key: string, value: any) => void;
}

const MedicalInformationContent: FunctionComponent<IMedicalInformationContentProps> = (props) => {
    const {
        editable,
        primaryCareManager,
        sex,
        birthdate,
        clinicCode,
        treatmentRegimen,
        medicalDiagnosis,
        onValueChange,
    } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridTextField
                editable={editable}
                label="Care Manager"
                value={primaryCareManager}
                onChange={(text) => onValueChange('primaryCareManager', text)}
            />
            <GridDropdownField
                editable={editable}
                label="Sex"
                value={sex}
                options={patientSexValues}
                onChange={(text) => onValueChange('sex', text)}
            />
            <GridDateField
                editable={editable}
                label="Date of Birth"
                value={birthdate}
                onChange={(text) => onValueChange('birthdate', text)}
            />
            <GridTextField
                editable={false}
                label="Age"
                value={differenceInYears(new Date(), birthdate ?? new Date())}
            />
            <GridDropdownField
                editable={editable}
                label="Clinic code"
                value={clinicCode}
                options={clinicCodeValues}
                onChange={(text) => onValueChange('clinicCode', text)}
            />
            <GridDropdownField
                editable={editable}
                label="Treatment Regimen"
                value={treatmentRegimen}
                options={treatmentRegimenValues}
                onChange={(text) => onValueChange('treatmentRegimen', text)}
            />
            <GridTextField
                fullWidth={true}
                editable={editable}
                multiline={true}
                maxLine={4}
                label="Primary Medical Diagnosis"
                value={medicalDiagnosis}
                onChange={(text) => onValueChange('medicalDiagnosis', text)}
            />
        </Grid>
    );
};

const state = observable<{ open: boolean } & IMedicalInfo>({
    open: false,
    primaryCareManager: '',
    sex: 'Male',
    birthdate: new Date(),
    clinicCode: 'Breast',
    treatmentRegimen: 'Other',
    medicalDiagnosis: '',
});

export const MedicalInformation: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!currentPatient) {
            state.primaryCareManager = currentPatient.primaryCareManager;
            state.sex = currentPatient.sex;
            state.birthdate = currentPatient.birthdate;
            state.clinicCode = currentPatient.clinicCode;
            state.treatmentRegimen = currentPatient.treatmentRegimen;
            state.medicalDiagnosis = currentPatient.medicalDiagnosis;
        }

        state.open = true;
    });

    const onSave = action(() => {
        const { open, ...patientData } = { ...state };
        currentPatient?.updatePatientData(patientData);
        state.open = false;
    });

    return (
        <ActionPanel
            id="medical"
            title="Medical Information"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <EditIcon />, text: 'Edit', onClick: handleOpen } as IActionButton]}>
            <MedicalInformationContent
                editable={false}
                primaryCareManager={currentPatient?.primaryCareManager}
                sex={currentPatient?.sex}
                birthdate={currentPatient?.birthdate}
                clinicCode={currentPatient?.clinicCode}
                treatmentRegimen={currentPatient?.treatmentRegimen}
                medicalDiagnosis={currentPatient?.medicalDiagnosis}
                onValueChange={onValueChange}
            />

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>Edit Medical Information</DialogTitle>
                <DialogContent>
                    <MedicalInformationContent editable={true} {...state} onValueChange={onValueChange} />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={onSave} color="primary">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default MedicalInformation;
