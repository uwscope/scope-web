import { Avatar, Grid, Menu, MenuItem } from '@material-ui/core';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import Logo from 'src/assets/scope-logo.png';
import PatientSearch from 'src/components/chrome/PatientSearch';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

const Title = styled(Grid)({
    flexGrow: 1,
});

const state = observable<{ anchorEl: HTMLElement | null }>({
    anchorEl: null,
});

export interface IHeaderProps {
    onDrawerOpen: () => void;
}

export const HeaderContent: FunctionComponent = observer(() => {
    const rootStore = useStores();

    const onPatientSelect = (name: string) => {
        console.log('TODO: selected', name);
    };

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
                <div>
                    <Menu
                        id="lock-menu"
                        anchorEl={state.anchorEl}
                        keepMounted
                        open={Boolean(state.anchorEl)}
                        onClose={() => handleClose()}>
                        <MenuItem onClick={(_) => handleLogout()}>Log out</MenuItem>
                    </Menu>
                    <Button color="inherit" onClick={(e) => handleClickName(e)}>
                        {rootStore.userStore.name}
                    </Button>
                </div>
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
        <Grid container direction="row" justify="flex-start" alignItems="center" spacing={2}>
            <Grid item>
                <Avatar alt="Scope logo" src={Logo} />
            </Grid>
            <Title item>
                <Typography variant="h6">{rootStore.appTitle}</Typography>
            </Title>
            <Grid item>
                <PatientSearch
                    options={rootStore.patientsStore.patients.map((p) => p.name)}
                    onSelect={onPatientSelect}
                />
            </Grid>
            {loginButton()}
        </Grid>
    );
});

export default HeaderContent;
