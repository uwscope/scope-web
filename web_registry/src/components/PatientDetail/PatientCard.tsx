import EditIcon from '@mui/icons-material/Edit';
import { Button, Divider, Grid, LinearProgress, Snackbar, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { format } from 'date-fns';
import { action, observable, runInAction } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent, useEffect, useState } from 'react';
import { IPatientProfile, KeyedMap } from 'shared/types';
import LabeledField from 'src/components/common/LabeledField';
import { EditPatientProfileDialog } from 'src/components/PatientDetail/PatientProfileDialog';
import { usePatient } from 'src/stores/stores';
import styled from 'styled-components';

const Container = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(2.5),
    })),
);

const Name = styled(Typography)({
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    margin: 0,
});

const EditButton = withTheme(
    styled(Button)((props) => ({
        marginLeft: props.theme.spacing(1),
    })),
);

const Header = styled.div({
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
});

const Loading = withTheme(styled(LinearProgress)({ height: 1 }));

const state = observable<{ open: boolean }>({
    open: false,
});

export interface IPatientCardProps {
    loading?: boolean;
    error?: boolean;
}

export const PatientCard: FunctionComponent<IPatientCardProps> = observer((props) => {
    const { loading, error } = props;
    const patient = usePatient();
    const { profile } = patient;

    const [openError, setOpenError] = useState(error);

    useEffect(() => {
        setOpenError(error);
    }, [error]);

    const handleErrorClose = () => {
        setOpenError(false);
    };

    const handleClose = action(() => {
        state.open = false;
        patient.loadProfileState.resetState();
    });

    const handleOpen = action(() => {
        state.open = true;
    });

    const onSave = action(async (newPatient: IPatientProfile) => {
        await patient.updateProfile(newPatient);

        runInAction(() => {
            if (!patient.loadProfileState.error) {
                state.open = false;
            }
        });
    });

    const generateRaceText = (flags: KeyedMap<boolean | string>) => {
        var concatValues = Object.keys(flags)
            .filter((k) => flags[k])
            .join(', ');

        return concatValues;
    };

    return (
        <Container>
            <Grid container spacing={2} direction="column" justifyContent="flex-start" alignItems="stretch">
                <Grid item>
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
                </Grid>

                <Grid item>{loading ? <Loading /> : <Divider />}</Grid>
                <Grid item>
                    <LabeledField label="mrn" value={profile.MRN} />
                    <LabeledField label="clinic code" value={profile.clinicCode} />
                </Grid>
                <Grid item>
                    <LabeledField
                        label="dob"
                        value={!!profile.birthdate ? format(profile.birthdate, 'MM/dd/yyyy') : '--'}
                    />
                    <LabeledField label="age" value={patient.age >= 0 ? patient.age : '--'} />
                    <LabeledField label="sex" value={profile.sex} />
                    <LabeledField
                        label="race"
                        value={profile.race != undefined ? generateRaceText(profile.race) : 'unknown'}
                    />
                    <LabeledField label="ethnicity" value={profile.ethnicity} />
                    <LabeledField label="gender" value={profile.gender} />
                    <LabeledField label="pronouns" value={profile.pronoun} />
                </Grid>

                <Grid item>
                    <LabeledField
                        label="primary oncology provider"
                        value={profile.primaryOncologyProvider?.name || '--'}
                    />
                    <LabeledField label="primary social worker" value={profile.primaryCareManager?.name || '--'} />
                    <LabeledField label="treatment status" value={profile.depressionTreatmentStatus} />
                    <LabeledField label="follow-up schedule" value={profile.followupSchedule} />
                </Grid>
                {state.open && (
                    <EditPatientProfileDialog
                        profile={profile}
                        open={state.open}
                        onClose={handleClose}
                        onSavePatient={onSave}
                        loading={loading}
                        error={error}
                    />
                )}
                <Snackbar
                    open={openError && !state.open}
                    message={`Sorry, there was an error processing your request. Please try again.`}
                    autoHideDuration={2000}
                    onClose={handleErrorClose}
                />
            </Grid>
        </Container>
    );
});

export default PatientCard;
