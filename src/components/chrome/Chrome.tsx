import {
    CircularProgress,
    CssBaseline,
    Dialog,
    Divider,
    Drawer,
    IconButton,
    Typography,
    withTheme,
} from '@material-ui/core';
import AppBar, { AppBarProps } from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import MenuIcon from '@material-ui/icons/Menu';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import { default as React, FunctionComponent } from 'react';
import Footer from 'src/components/chrome/Footer';
import { useStores } from 'src/stores/stores';
import styled, { ThemedStyledProps } from 'styled-components';

const RootContainer = styled.div({
    display: 'flex',
    flexDirection: 'column',
    height: 'calc(100vh)',
});

const LoadingContainer = withTheme(
    styled.div((props) => ({
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: props.theme.spacing(3),
    }))
);

const MainContainer = withTheme(
    styled.main((props) => ({
        flexGrow: 1,
        marginLeft: 73,
        marginTop: props.theme.customSizes.headerHeight,
        height: `calc(100% - ${props.theme.customSizes.headerHeight + props.theme.customSizes.footerHeight}px)`,
        overflow: 'hidden',
    }))
);

const ToobarContainer = withTheme(
    styled.div((props) => ({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        padding: props.theme.spacing(0, 1),
        // necessary for content to be below app bar
        ...props.theme.mixins.toolbar,
    }))
);

// TODO: Refactor common style -- there's a typing issue
const MiniDrawer = withTheme(
    styled(Drawer)((props) => ({
        width: props.open ? props.theme.customSizes.drawerWidth : props.theme.spacing(7) + 1,
        flexShrink: 0,
        whiteSpace: 'nowrap',
        transition: props.open
            ? props.theme.transitions.create('width', {
                  easing: props.theme.transitions.easing.sharp,
                  duration: props.theme.transitions.duration.enteringScreen,
              })
            : props.theme.transitions.create('width', {
                  easing: props.theme.transitions.easing.sharp,
                  duration: props.theme.transitions.duration.leavingScreen,
              }),
        overflowX: props.open ? 'auto' : 'hidden',
        [props.theme.breakpoints.up('sm')]: props.open
            ? undefined
            : {
                  width: props.theme.spacing(9) + 1,
              },
        '>.MuiDrawer-paper': {
            width: props.open ? props.theme.customSizes.drawerWidth : props.theme.spacing(7) + 1,
            transition: props.open
                ? props.theme.transitions.create('width', {
                      easing: props.theme.transitions.easing.sharp,
                      duration: props.theme.transitions.duration.enteringScreen,
                  })
                : props.theme.transitions.create('width', {
                      easing: props.theme.transitions.easing.sharp,
                      duration: props.theme.transitions.duration.leavingScreen,
                  }),
            overflowX: props.open ? 'auto' : 'hidden',
            [props.theme.breakpoints.up('sm')]: props.open
                ? undefined
                : {
                      width: props.theme.spacing(9) + 1,
                  },
        },
    }))
);

const AppBarContainer = withTheme(
    styled(AppBar)((props: ThemedStyledProps<AppBarProps & { open: boolean }, any>) => ({
        zIndex: props.theme.zIndex.drawer + 1,
        transition: props.theme.transitions.create(['width', 'margin'], {
            easing: props.theme.transitions.easing.sharp,
            duration: props.open
                ? props.theme.transitions.duration.enteringScreen
                : props.theme.transitions.duration.leavingScreen,
        }),
        marginLeft: props.open ? props.theme.customSizes.drawerWidth : undefined,
        width: props.open ? `calc(100% - ${props.theme.customSizes.drawerWidth}px)` : undefined,
    }))
);

const MenuButton = withTheme(
    styled(IconButton)((props: ThemedStyledProps<AppBarProps & { open: boolean }, any>) => ({
        marginRight: 36, //props.theme.spacing(2),
        display: props.open ? 'none' : undefined,
    }))
);

const state = observable<{ drawerOpen: boolean }>({
    drawerOpen: false,
});

const handleDrawerOpen = action(() => {
    state.drawerOpen = true;
});

const handleDrawerClose = action(() => {
    state.drawerOpen = false;
});

export interface IChromeProps {
    headerContent: React.ReactNode;
    drawerContent: React.ReactNode;
    children: React.ReactNode;
}

export const Chrome: FunctionComponent<IChromeProps> = observer((props) => {
    const rootStore = useStores();

    return (
        <RootContainer>
            <Dialog open={rootStore.appState != 'Fulfilled'}>
                <LoadingContainer>
                    <CircularProgress />
                    <Typography variant="h6">Loading Registry</Typography>
                </LoadingContainer>
            </Dialog>
            <CssBaseline />
            <AppBarContainer position="fixed" open={state.drawerOpen}>
                <Toolbar>
                    <MenuButton
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        onClick={handleDrawerOpen}
                        open={state.drawerOpen}>
                        <MenuIcon />
                    </MenuButton>
                    {props.headerContent}
                </Toolbar>
            </AppBarContainer>

            <MiniDrawer variant="permanent" open={state.drawerOpen}>
                <ToobarContainer>
                    <IconButton onClick={handleDrawerClose}>
                        <ChevronLeftIcon />
                    </IconButton>
                </ToobarContainer>
                <Divider />
                {props.drawerContent}
            </MiniDrawer>
            <MainContainer>{props.children}</MainContainer>
            <Footer></Footer>
        </RootContainer>
    );
});

export default Chrome;
