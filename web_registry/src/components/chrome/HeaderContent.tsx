import { Avatar, Grid, Menu, MenuItem } from '@mui/material';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useHistory, useRouteMatch } from 'react-router';
import Logo from 'src/assets/scope-logo.png';
import { useStores } from 'src/stores/stores';

const state = observable<{ anchorEl: HTMLElement | null }>({
    anchorEl: null,
});

export const HeaderContent: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const history = useHistory();

    let match = useRouteMatch('/patient/:recordId');

    var patientName = '';
    if (!!match && !!match.params) {
        const { recordId } = match?.params as any;
        if (!!recordId) {
            const currentPatient = rootStore.patientsStore.getPatientByRecordId(recordId);
            if (!!currentPatient) {
                patientName = currentPatient.name;
            }
        }
    }

    const handleClickName = action((event: React.MouseEvent<HTMLElement>) => {
        state.anchorEl = event.currentTarget;
    });

    const handleLogout = action(() => {
        rootStore.authStore.logout();
        state.anchorEl = null;
    });

    const handleClose = action(() => {
        state.anchorEl = null;
    });

    return (
        <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="center"
        >
            <Grid item>
                <Avatar alt="Scope logo" src={Logo} />
            </Grid>
            <Grid item>
                <Button
                    color="inherit"
                    onClick={!!patientName ? () => history.goBack() : undefined}
                >
                    <Typography variant="h6">{rootStore.appTitle}</Typography>
                </Button>
            </Grid>
            <Grid item flexGrow={1}>
                {!!patientName ? (
                    <Typography>{`/  ${patientName}`}</Typography>
                ) : null}
            </Grid>
            <div>
                <Menu
                    id="lock-menu"
                    anchorEl={state.anchorEl}
                    keepMounted
                    open={Boolean(state.anchorEl)}
                    onClose={() => handleClose()}
                >
                    <MenuItem onClick={(_) => handleLogout()}>Log out</MenuItem>
                </Menu>
                <Button color="inherit" onClick={(e) => handleClickName(e)}>
                    {rootStore.authStore.currentUserIdentity?.name}
                </Button>
            </div>
        </Grid>
    );
});

export default HeaderContent;
