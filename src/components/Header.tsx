import { withTheme } from '@material-ui/core';
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

const Container = styled.div({
    flexGrow: 1,
});

const MenuButton = withTheme(
    styled(IconButton)((props) => ({
        marginRight: props.theme.spacing(2),
    }))
);

const AppTitle = styled(Typography)({
    flexGrow: 1,
});

export const Header: FunctionComponent = observer(() => {
    const rootStore = useStores();

    return (
        <Container>
            <AppBar position="static">
                <Toolbar>
                    <MenuButton edge="start" color="inherit" aria-label="menu">
                        <MenuIcon />
                    </MenuButton>
                    <AppTitle variant="h6">{rootStore.appTitle}</AppTitle>
                    <Button color="inherit">Login</Button>
                </Toolbar>
            </AppBar>
        </Container>
    );
});

export default Header;
