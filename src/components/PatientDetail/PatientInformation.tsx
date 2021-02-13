import { Grid } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import MedicalInformation from './MedicalInformation';
import PsychiatryInformation from './PsychiatryInformation';
import TreatmentInformation from './TreatmentInformation';

export const PatientInformation: FunctionComponent = observer(() => {
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
        </Grid>
    );
});

export default PatientInformation;
