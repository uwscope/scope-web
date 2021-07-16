import { Button, Typography, withTheme } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import { differenceInYears, format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import LabeledField from 'src/components/common/LabeledField';
import { EditPatientProfileDialog } from 'src/components/PatientDetail/PatientProfileDialog';
import { IPatientProfile } from 'src/services/types';
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

const state = observable<{ open: boolean }>({
    open: false,
});

export interface IPatientCardProps {
    loading?: boolean;
}

export const PatientCard: FunctionComponent<IPatientCardProps> = observer((props) => {
    const { loading } = props;
    const patient = usePatient();

    const handleClose = action(() => {
        state.open = false;
    });

    const handleOpen = action(() => {
        if (!!patient) {
            Object.assign(state, patient);
        }

        state.open = true;
    });

    const onSave = action((newPatient: IPatientProfile) => {
        patient?.updatePatientData(newPatient);
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
            <br />
            <LabeledField label="dob" value={format(patient.birthdate, 'MM/dd/yyyy')} />
            <LabeledField label="age" value={differenceInYears(Date.now(), patient.birthdate)} />
            <LabeledField label="sex" value={patient.sex} />
            <LabeledField label="race" value={patient.race} />
            <LabeledField label="gender" value={patient.gender} />
            <LabeledField label="pronouns" value={patient.pronoun} />
            <br />

            <LabeledField label="primary social worker" value={patient.primaryCareManager} />
            <LabeledField label="primary oncology provider" value={patient.primaryOncologyProvider} />

            <EditPatientProfileDialog
                patient={patient}
                open={state.open}
                onClose={handleClose}
                onSavePatient={onSave}
            />
        </Container>
    );
});

export default PatientCard;
