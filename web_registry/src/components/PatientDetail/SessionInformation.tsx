import { Grid } from '@mui/material';
import React, { FunctionComponent } from 'react';
import { SessionInfo } from 'src/components/PatientDetail/SessionInfo';

export const SessionInformation: FunctionComponent = () => {
    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            <Grid item xs={12} sm={12}>
                <SessionInfo />
            </Grid>
        </Grid>
    );
};

export default SessionInformation;
