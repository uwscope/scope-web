import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { GridDateField, GridDropdownField, GridTextField } from 'src/components/common/GridField';
import {
    clinicCodeValues,
    depressionTreatmentStatusValues,
    patientGenderValues,
    patientPronounValues,
    patientRaceEthnicityValues,
    patientSexValues,
} from 'src/services/enums';
import { IPatientProfile } from 'src/services/types';

interface IEditPatientProfileContentProps extends Partial<IPatientProfile> {
    onValueChange: (key: string, value: any) => void;
}

const EditPatientProfileContent: FunctionComponent<IEditPatientProfileContentProps> = (props) => {
    const {
        name,
        MRN,
        clinicCode,
        depressionTreatmentStatus,
        birthdate,
        race,
        sex,
        gender,
        pronoun,
        primaryOncologyProvider,
        primaryCareManager,
        onValueChange,
    } = props;

    const getTextField = (label: string, value: any, propName: string) => (
        <GridTextField editable label={label} value={value} onChange={(text) => onValueChange(propName, text)} />
    );

    const getDropdownField = (label: string, value: any, options: any, propName: string) => (
        <GridDropdownField
            editable
            label={label}
            value={value}
            options={options}
            onChange={(text) => onValueChange(propName, text)}
        />
    );

    return (
        <Grid container spacing={2} alignItems="stretch">
            {getTextField('Patient Name', name, 'name')}
            {getTextField('MRN', MRN, 'MRN')}
            {getDropdownField('Clinic Code', clinicCode, clinicCodeValues, 'clinicCode')}
            {getDropdownField(
                'Treatment Status',
                depressionTreatmentStatus,
                depressionTreatmentStatusValues,
                'depressionTreatmentStatus'
            )}
            <GridDateField
                editable
                label="Date of Birth"
                value={birthdate}
                onChange={(text) => onValueChange('birthdate', text)}
            />
            {getDropdownField('Race/Ethnicity', race, patientRaceEthnicityValues, 'race')}
            {getDropdownField('Sex', sex, patientSexValues, 'sex')}
            {getDropdownField('Gender', gender, patientGenderValues, 'gender')}
            {getDropdownField('Pronouns', pronoun, patientPronounValues, 'pronoun')}
            {getTextField('Primary Oncology Provider', primaryOncologyProvider, 'primaryOncologyProvider')}
            {getTextField('Primary Care Manager', primaryCareManager, 'primaryCareManager')}
        </Grid>
    );
};

const emptyProfile = {
    name: '',
    MRN: '',
    clinicCode: 'Other',
    depressionTreatmentStatus: 'Other',
    birthdate: new Date(),
    sex: 'Male',
    gender: 'Male',
    pronoun: 'He/Him',
    race: 'White',
    primaryOncologyProvider: '',
    primaryCareManager: '',
} as IPatientProfile;

const state = observable<IPatientProfile>(emptyProfile);

interface IDialogProps {
    open: boolean;
    onClose: () => void;
}

interface IEditPatientProfileDialogProps extends IDialogProps {
    patient: IPatientProfile;
    onSavePatient: (patient: IPatientProfile) => void;
}

export interface IAddPatientProfileDialogProps extends IDialogProps {
    onAddPatient: (patient: IPatientProfile) => void;
}

export const AddPatientProfileDialog: FunctionComponent<IAddPatientProfileDialogProps> = observer((props) => {
    const { onAddPatient, open, onClose } = props;

    React.useEffect(
        action(() => {
            Object.assign(state, emptyProfile);
        }),
        []
    );

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const onSave = action(() => {
        onAddPatient(state);
    });

    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>Add Patient</DialogTitle>
            <DialogContent>
                <EditPatientProfileContent {...state} onValueChange={onValueChange} />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Cancel
                </Button>
                <Button onClick={onSave} color="primary">
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    );
});

export const EditPatientProfileDialog: FunctionComponent<IEditPatientProfileDialogProps> = observer((props) => {
    const { patient, open, onClose, onSavePatient } = props;

    React.useEffect(
        action(() => {
            Object.assign(state, patient);
        }),
        []
    );

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const onSave = action(() => {
        onSavePatient(state);
    });

    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>Edit Patient Information</DialogTitle>
            <DialogContent>
                <EditPatientProfileContent {...state} onValueChange={onValueChange} />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Cancel
                </Button>
                <Button onClick={onSave} color="primary">
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    );
});
