import { Grid } from '@mui/material';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import {
    clinicCodeValues,
    depressionTreatmentStatusValues,
    followupScheduleValues,
    patientEthnicityValues,
    patientGenderValues,
    patientPronounValues,
    patientRaceValues,
    patientSexValues,
    siteValues,
} from 'shared/enums';
import { toLocalDateOnly, toUTCDateOnly } from 'shared/time';
import { IPatientProfile, IProviderIdentity } from 'shared/types';
import { GridDateField, GridDropdownField, GridMultiSelectField, GridTextField } from 'src/components/common/GridField';
import StatefulDialog from 'src/components/common/StatefulDialog';

interface IEditPatientProfileContentProps extends Partial<IPatientProfile> {
    availableCareManagerNames: string[];
    onCareManagerChange: (providerName: string) => void;
    onValueChange: (key: string, value: any) => void;
}

const EditPatientProfileContent: FunctionComponent<IEditPatientProfileContentProps> = (props) => {
    const {
        name,
        MRN,
        clinicCode,
        depressionTreatmentStatus,
        followupSchedule,
        birthdate,
        race,
        ethnicity,
        sex,
        gender,
        pronoun,
        primaryOncologyProvider,
        primaryCareManager,
        availableCareManagerNames,
        site,
        onValueChange,
        onCareManagerChange,
    } = props;

    const getTextField = (label: string, value: any, propName: string, required?: boolean) => (
        <GridTextField
            editable
            label={label}
            value={value}
            onChange={(text) => onValueChange(propName, text)}
            required={required}
        />
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
            {getTextField('Patient Name', name, 'name', true)}
            {getTextField('MRN', MRN, 'MRN', true)}
            {getDropdownField('Clinic Code', clinicCode || '', clinicCodeValues, 'clinicCode')}
            {getDropdownField('Site', site || '', siteValues, 'site')}
            <GridDateField
                editable
                label="Date of Birth"
                value={birthdate}
                onChange={(text) => onValueChange('birthdate', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable
                label="Race"
                flags={Object.assign({}, ...patientRaceValues.map((x) => ({ [x]: !!race?.[x] })))}
                flagOrder={[...patientRaceValues]}
                onChange={(flags) => onValueChange('race', flags)}
            />
            {getDropdownField('Ethnicity', ethnicity || '', patientEthnicityValues, 'ethnicity')}
            {getDropdownField('Sex', sex || '', patientSexValues, 'sex')}
            {getDropdownField('Gender', gender || '', patientGenderValues, 'gender')}
            {getDropdownField('Pronouns', pronoun || '', patientPronounValues, 'pronoun')}
            {getTextField('Primary Oncology Provider', primaryOncologyProvider, 'primaryOncologyProvider')}
            <GridDropdownField
                editable
                label={'Primary Social Worker'}
                value={primaryCareManager?.name || ''}
                options={availableCareManagerNames}
                onChange={(text) => onCareManagerChange(text as string)}
            />
            {getDropdownField(
                'Treatment Status',
                depressionTreatmentStatus || '',
                depressionTreatmentStatusValues,
                'depressionTreatmentStatus',
            )}
            {getDropdownField('Follow-up Schedule', followupSchedule || '', followupScheduleValues, 'followupSchedule')}
        </Grid>
    );
};

const emptyProfile = {
    name: '',
    MRN: '',
    clinicCode: undefined,
    birthdate: undefined,
    race: undefined,
    ethnicity: undefined,
    sex: undefined,
    gender: undefined,
    pronoun: undefined,
    primaryOncologyProvider: undefined,
    primaryCareManager: undefined,
    depressionTreatmentStatus: undefined,
    followupSchedule: undefined,
    site: undefined,
} as IPatientProfile;

interface IDialogProps {
    open: boolean;
    error?: boolean;
    loading?: boolean;
    onClose: () => void;
}

interface IEditPatientProfileDialogProps extends IDialogProps {
    careManagers: IProviderIdentity[];
    profile: IPatientProfile;
    onSavePatient: (patient: IPatientProfile) => void;
}

export interface IAddPatientProfileDialogProps extends IDialogProps {
    careManagers: IProviderIdentity[];
    onAddPatient: (patient: IPatientProfile) => void;
}

export const AddPatientProfileDialog: FunctionComponent<IAddPatientProfileDialogProps> = observer((props) => {
    const { onAddPatient, open, error, loading, onClose, careManagers } = props;

    const state = useLocalObservable<IPatientProfile>(() => emptyProfile);

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const onCareManagerChange = action((name: string) => {
        const found = careManagers.find((c) => c.name == name);
        if (!!name && found) {
            state.primaryCareManager = found;
        } else {
            state.primaryCareManager = undefined;
        }
    });

    const onSave = action(() => {
        onAddPatient(state);
    });

    const availableCareManagerNames = careManagers.map((c) => c.name);

    return (
        <StatefulDialog
            open={open}
            error={error}
            loading={loading}
            title="Add Patient"
            content={
                <EditPatientProfileContent
                    {...state}
                    availableCareManagerNames={availableCareManagerNames}
                    onValueChange={onValueChange}
                    onCareManagerChange={onCareManagerChange}
                />
            }
            handleCancel={onClose}
            handleSave={onSave}
            disableSave={!state.name || !state.MRN}
        />
    );
});

export const EditPatientProfileDialog: FunctionComponent<IEditPatientProfileDialogProps> = observer((props) => {
    const { profile, open, error, loading, onClose, onSavePatient, careManagers } = props;

    const state = useLocalObservable<IPatientProfile>(() => {
        const existingProfile = { ...profile };

        if (profile.birthdate != undefined) {
            existingProfile.birthdate = toLocalDateOnly(profile.birthdate);
        }

        return existingProfile;
    });

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const onSave = action(() => {
        const updatedProfile = { ...state };

        if (state.birthdate != undefined) {
            updatedProfile.birthdate = toUTCDateOnly(state.birthdate);
        }

        onSavePatient(updatedProfile);
    });

    const onCareManagerChange = action((name: string) => {
        const found = careManagers.find((c) => c.name == name);
        if (!!name && found) {
            state.primaryCareManager = found;
        } else {
            state.primaryCareManager = undefined;
        }
    });

    const availableCareManagerNames = careManagers.map((c) => c.name);

    return (
        <StatefulDialog
            open={open}
            error={error}
            loading={loading}
            title="Edit Patient Information"
            content={
                <EditPatientProfileContent
                    {...state}
                    availableCareManagerNames={availableCareManagerNames}
                    onValueChange={onValueChange}
                    onCareManagerChange={onCareManagerChange}
                />
            }
            handleCancel={onClose}
            handleSave={onSave}
            disableSave={!state.name || !state.MRN}
        />
    );
});
