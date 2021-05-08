import { Grid } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import AssessmentInfo from 'src/components/PatientDetail/AssessmentInfo';
import ClinicalHistory from 'src/components/PatientDetail/ClinicalHistory';
import { SessionInfo } from 'src/components/PatientDetail/SessionInfo';
import { TreatmentInfo } from 'src/components/PatientDetail/TreatmentInfo';

export const PatientInformation: FunctionComponent = () => {
    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            <Grid item xs={12} sm={12}>
                <ClinicalHistory />
            </Grid>
            <Grid item xs={12} sm={12}>
                <TreatmentInfo />
            </Grid>
            <Grid item xs={12} sm={12}>
                <SessionInfo />
            </Grid>
            <Grid item xs={12} sm={12}>
                <AssessmentInfo />
            </Grid>
        </Grid>
    );
};

export default PatientInformation;
