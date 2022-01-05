import { Avatar, Grid, Menu, MenuItem } from '@mui/material';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
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
            const currentPatient = rootStore.getPatientByRecordId(recordId);
            if (!!currentPatient) {
                patientName = currentPatient.name;
            }
        }
    }

    const handleClickName = action((event: React.MouseEvent<HTMLElement>) => {
        state.anchorEl = event.currentTarget;
    });

    const handleLogout = action(() => {
        rootStore.logout();
        state.anchorEl = null;
    });

    const handleClose = action(() => {
        state.anchorEl = null;
    });

    const loginButton = () => {
        if (rootStore.loginState == 'Fulfilled') {
            return (
                <Fragment>
                    <Menu
                        id="lock-menu"
                        anchorEl={state.anchorEl}
                        keepMounted
                        open={Boolean(state.anchorEl)}
                        onClose={() => handleClose()}>
                        <MenuItem onClick={(_) => handleLogout()}>Log out</MenuItem>
                    </Menu>
                    <Button color="inherit" onClick={(e) => handleClickName(e)}>
                        {rootStore.userName}
                    </Button>
                </Fragment>
            );
        } else {
            return (
                <Button color="inherit" onClick={() => rootStore.login()}>
                    Log in
                </Button>
            );
        }
    };

    return (
        <Grid container direction="row" justifyContent="flex-start" alignItems="center" spacing={2}>
            <Grid item>
                <Avatar alt="Scope logo" src={Logo} />
            </Grid>
            <Grid item>
                <Button color="inherit" onClick={!!patientName ? () => history.goBack() : undefined}>
                    <Typography variant="h6">{rootStore.appTitle}</Typography>
                </Button>
            </Grid>
            <Grid item flexGrow={1}>
                {!!patientName ? <Typography>{`/  ${patientName}`}</Typography> : null}
            </Grid>
            <Grid item>{loginButton()}</Grid>
        </Grid>
    );
});

export default HeaderContent;
