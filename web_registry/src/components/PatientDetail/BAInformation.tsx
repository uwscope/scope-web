import { Grid } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import BAActivities from 'src/components/PatientDetail/BAActivities';
import { BAChecklist } from 'src/components/PatientDetail/BAChecklist';

export const BAInformation: FunctionComponent = () => {
    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            <Grid item xs={12} sm={12}>
                <BAChecklist />
            </Grid>
            <Grid item xs={12} sm={12}>
                <BAActivities />
            </Grid>
        </Grid>
    );
};

export default BAInformation;
