import { Grid } from '@mui/material';
import React, { FunctionComponent } from 'react';
import ClinicalHistory from 'src/components/PatientDetail/ClinicalHistory';
import { TreatmentInfo } from 'src/components/PatientDetail/TreatmentInfo';

export const PatientInformation: FunctionComponent = () => {
    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            <Grid item xs={12} sm={6}>
                <ClinicalHistory />
            </Grid>
            <Grid item xs={12} sm={6}>
                <TreatmentInfo />
            </Grid>
        </Grid>
    );
};

export default PatientInformation;
