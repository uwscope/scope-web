import { Grid } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import { MedicalInformation } from 'src/components/PatientDetail/MedicalInformation';
import { PsychiatryInformation } from 'src/components/PatientDetail/PsychiatryInformation';
import { SessionInformation } from 'src/components/PatientDetail/SessionInformation';
import { TreatmentInformation } from 'src/components/PatientDetail/TreatmentInformation';

export const PatientInformation: FunctionComponent = () => {
    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            <Grid item xs={12} sm={6}>
                <MedicalInformation />
            </Grid>
            <Grid item xs={12} sm={6}>
                <PsychiatryInformation />
            </Grid>
            <Grid item xs={12} sm={12}>
                <TreatmentInformation />
            </Grid>
            <Grid item xs={12} sm={12}>
                <SessionInformation />
            </Grid>
        </Grid>
    );
};

export default PatientInformation;
