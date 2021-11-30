import { Button, Divider, LinearProgress, Typography, withTheme } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { IPatientProfile } from 'shared/types';
import LabeledField from 'src/components/common/LabeledField';
import { EditPatientProfileDialog } from 'src/components/PatientDetail/PatientProfileDialog';
import { usePatient } from 'src/stores/stores';
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

const Loading = withTheme(styled(LinearProgress)({ height: 1 }));

const state = observable<{ open: boolean }>({
    open: false,
});

export interface IPatientCardProps {
    loading?: boolean;
}

export const PatientCard: FunctionComponent<IPatientCardProps> = observer((props) => {
    const { loading } = props;
    const patient = usePatient();
    const { profile } = patient;

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        state.open = true;
    });

    const onSave = action((newPatient: IPatientProfile) => {
        patient?.updateProfile(newPatient);
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

            {loading ? <Loading /> : <Divider />}
            <LabeledField label="mrn" value={profile.MRN} />
            <LabeledField label="clinic code" value={profile.clinicCode} />
            <br />
            <LabeledField label="dob" value={!!profile.birthdate ? format(profile.birthdate, 'MM/dd/yyyy') : '--'} />
            <LabeledField label="age" value={patient.age >= 0 ? patient.age : '--'} />
            <LabeledField label="sex" value={profile.sex} />
            <LabeledField label="race" value={profile.race} />
            <LabeledField label="gender" value={profile.gender} />
            <LabeledField label="pronouns" value={profile.pronoun} />
            <br />

            <LabeledField label="primary oncology provider" value={profile.primaryOncologyProvider?.name || '--'} />
            <LabeledField label="primary social worker" value={profile.primaryCareManager?.name || '--'} />
            <LabeledField label="treatment status" value={profile.depressionTreatmentStatus} />
            <LabeledField label="follow-up schedule" value={profile.followupSchedule} />

            <EditPatientProfileDialog
                profile={profile}
                open={state.open}
                onClose={handleClose}
                onSavePatient={onSave}
            />
        </Container>
    );
});

export default PatientCard;
