import { Grid } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import PHQProgress from 'src/components/PatientDetail/PHQProgress';

export const ProgressInformation: FunctionComponent = () => {
    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            <Grid item xs={12} sm={12}>
                <PHQProgress />
            </Grid>
        </Grid>
    );
};

export default ProgressInformation;
