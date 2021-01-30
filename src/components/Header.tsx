import { Avatar, Grid, withTheme } from '@material-ui/core';
import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import MenuIcon from '@material-ui/icons/Menu';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import { useStores } from '../stores/stores';
import PatientSearch from './PatientSearch';

const Container = styled.div({
    flexGrow: 1,
});

const MenuButton = withTheme(
    styled(IconButton)((props) => ({
        marginRight: props.theme.spacing(2),
    }))
);

const Title = styled(Grid)({
    flexGrow: 1,
});

// TODO: Hook up to actual patient list
const fruits = ['apple', 'banana', 'orange', 'kiwi', 'strawberry'];

export const Header: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const onPatientSelect = (name: string) => {
        console.log('TODO: selected', name);
    };

    return (
        <Container>
            <AppBar position="static">
                <Toolbar>
                    <MenuButton edge="start" color="inherit" aria-label="menu">
                        <MenuIcon />
                    </MenuButton>
                    <Grid container direction="row" justify="flex-start" alignItems="center" spacing={2}>
                        <Grid item>
                            <Avatar alt="Scope logo" src="/assets/scope-logo.png" />
                        </Grid>
                        <Title item>
                            <Typography variant="h6">{rootStore.appTitle}</Typography>
                        </Title>
                        <Grid item>
                            <PatientSearch options={fruits} onSelect={onPatientSelect} />
                        </Grid>
                    </Grid>
                    <Button color="inherit">Login</Button>
                </Toolbar>
            </AppBar>
        </Container>
    );
});

export default Header;
