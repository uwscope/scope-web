import { Grid } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import { BAChecklist } from 'src/components/PatientDetail/BAChecklist';
import ValuesInventory from 'src/components/PatientDetail/ValuesInventory';

export const BehavioralInformation: FunctionComponent = () => {
    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            <Grid item xs={12} sm={12}>
                <BAChecklist />
            </Grid>
            <Grid item xs={12} sm={12}>
                <ValuesInventory />
            </Grid>
        </Grid>
    );
};

export default BehavioralInformation;
