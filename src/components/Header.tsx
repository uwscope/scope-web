import { Avatar, Grid, Menu, MenuItem, withTheme } from '@material-ui/core';
import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import MenuIcon from '@material-ui/icons/Menu';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import Logo from '../assets/scope-logo.png';
import { LoginStatus } from '../stores/RootStore';
import { useStores } from '../stores/stores';
import PatientSearch from './PatientSearch';

const MenuButton = withTheme(
    styled(IconButton)((props) => ({
        marginRight: props.theme.spacing(2),
    }))
);

const Title = styled(Grid)({
    flexGrow: 1,
});

const state = observable<{ anchorEl: HTMLElement | null }>({
    anchorEl: null,
});

export interface IHeaderProps {
    onDrawerOpen: () => void;
}

export const Header: FunctionComponent<IHeaderProps> = observer((props: IHeaderProps) => {
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
        if (rootStore.loginStatus == LoginStatus.LoggedOut) {
            return (
                <Button color="inherit" onClick={() => rootStore.login()}>
                    Log in
                </Button>
            );
        } else if (rootStore.loginStatus == LoginStatus.LoggedIn) {
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
        }
    };

    return (
        <AppBar position="static">
            <Toolbar>
                <MenuButton edge="start" color="inherit" aria-label="menu" onClick={props.onDrawerOpen}>
                    <MenuIcon />
                </MenuButton>
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
            </Toolbar>
        </AppBar>
    );
});

export default Header;
