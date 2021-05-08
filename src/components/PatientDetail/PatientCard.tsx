import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Typography,
    withTheme,
} from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { differenceInYears, format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { GridDateField, GridDropdownField, GridTextField } from 'src/components/common/GridField';
import LabeledField from 'src/components/common/LabeledField';
import {
    clinicCodeValues,
    depressionTreatmentStatusValues,
    patientGenderValues,
    patientPronounValues,
    patientRaceEthnicityValues,
    patientSexValues,
} from 'src/services/enums';
import { IPatientProfile } from 'src/services/types';
import { IPatientStore } from 'src/stores/PatientStore';
import styled from 'styled-components';

const Container = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(2.5),
    }))
);

const Name = styled(Typography)({
    fontWeight: 600,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
});

const EditButton = withTheme(
    styled(Button)((props) => ({
        marginLeft: props.theme.spacing(1),
    }))
);

const Header = styled.div({
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
});

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
            {getTextField('MRN', MRN, 'mrn')}
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

const state = observable<{ open: boolean } & IPatientProfile>({
    open: false,
    name: 'unknown',
    MRN: 'unknown',
    clinicCode: 'Other',
    depressionTreatmentStatus: 'Other',
    birthdate: new Date(),
    sex: 'Male',
    gender: 'Male',
    pronoun: 'He/Him',
    race: 'White',
    primaryOncologyProvider: 'unknown',
    primaryCareManager: 'unknown',
});

export interface IPatientCardProps {
    patient: IPatientStore;
    loading?: boolean;
}

export const PatientCard: FunctionComponent<IPatientCardProps> = observer((props) => {
    const { patient, loading } = props;

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!patient) {
            Object.assign(state, patient);
        }

        state.open = true;
    });

    const onSave = action(() => {
        const { open, ...patientData } = { ...state };
        patient?.updatePatientData(patientData);
        state.open = false;
    });

    return (
        <Container>
            <Header>
                <Name variant="h5" gutterBottom>
                    {patient.name}
                </Name>
                <EditButton
                    variant="outlined"
                    size="small"
                    color="primary"
                    startIcon={<EditIcon />}
                    disabled={loading}
                    onClick={handleOpen}
                    key="Edit">
                    Edit
                </EditButton>
            </Header>

            <LabeledField label="mrn" value={patient.MRN} />
            <LabeledField label="clinic code" value={patient.clinicCode} />
            <LabeledField label="treatment status" value={patient.depressionTreatmentStatus} />
            <br />
            <LabeledField label="dob" value={format(patient.birthdate, 'MM/dd/yyyy')} />
            <LabeledField label="age" value={differenceInYears(Date.now(), patient.birthdate)} />
            <LabeledField label="sex" value={patient.sex} />
            <LabeledField label="race" value={patient.race} />
            <LabeledField label="gender" value={patient.gender} />
            <LabeledField label="pronouns" value={patient.pronoun} />
            <br />
            <LabeledField label="oncology provider" value={patient.primaryOncologyProvider} />
            <LabeledField label="care manager" value={patient.primaryCareManager} />

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>Edit Medical Information</DialogTitle>
                <DialogContent>
                    <EditPatientProfileContent {...state} onValueChange={onValueChange} />
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
        </Container>
    );
});

export default PatientCard;
