import ConnectWithoutContactIcon from '@mui/icons-material/ConnectWithoutContact';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import HomeIcon from '@mui/icons-material/Home';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import { BottomNavigation, BottomNavigationAction } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import BackgroundImageSrc from 'src/assets/background-small.jpeg';
import { AppLoader } from 'src/components/Chrome/AppLoader';
import GetFormDialog from 'src/components/Forms/GetFormDialog';
import { getCurrentPath, getLevel, Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

const Centered = styled.div({
    display: 'flex',
    justifyContent: 'center',
    height: '100%',
});

const ResponsiveContainer = styled.div({
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
});

const ContentContainer = styled.div({
    flexGrow: 1,
    height: '100%',
    overflowY: 'hidden',
});

const BottomBar = withTheme(
    styled(BottomNavigation)((props) => ({
        height: 64,
        minHeight: 64,
        position: 'fixed',
        bottom: 0,
        width: '100%',
        zIndex: 1,
        '&.MuiBottomNavigation-root': {
            background: props.theme.customPalette.panel,
        },
        '>.MuiBottomNavigationAction-root': {
            padding: 6,
        },
        [props.theme.breakpoints.up('phone')]: {
            justifyContent: 'center',
        },
        [props.theme.breakpoints.up('tablet')]: {
            justifyContent: 'center',
            paddingRight: props.theme.spacing(8),
            paddingLeft: props.theme.spacing(8),
        },
        [props.theme.breakpoints.up('laptop')]: {
            justifyContent: 'center',
            paddingRight: props.theme.spacing(20),
            paddingLeft: props.theme.spacing(20),
        },
    }))
);

const Background = styled.img({
    objectFit: 'cover',
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: -1,
    width: '100%',
    height: '100%',
});

export const Chrome: FunctionComponent = observer((props) => {
    const rootStore = useStores();

    const selectedPath = getCurrentPath() || Routes.home;
    const mainLevel = getLevel(selectedPath) == 1;

    return (
        <Centered>
            <ResponsiveContainer>
                <AppLoader isLoading={rootStore.loadState != 'Fulfilled'} text="Loading" />
                <GetFormDialog />
                {rootStore.loadState == 'Fulfilled' && (
                    <ContentContainer>
                        {mainLevel ? <Background src={BackgroundImageSrc} /> : null}
                        {props.children}
                    </ContentContainer>
                )}
                {mainLevel ? (
                    <BottomBar value={selectedPath} color="transparent">
                        <BottomNavigationAction
                            component={Link}
                            to="/"
                            label={getString('Navigation_home')}
                            value={Routes.home}
                            showLabel={true}
                            icon={<HomeIcon />}
                        />
                        <BottomNavigationAction
                            component={Link}
                            to={Routes.careplan}
                            label={getString('Navigation_careplan')}
                            value={Routes.careplan}
                            showLabel={true}
                            icon={<PlaylistAddCheckIcon />}
                        />
                        <BottomNavigationAction
                            component={Link}
                            to={Routes.progress}
                            label={getString('Navigation_progress')}
                            value={Routes.progress}
                            showLabel={true}
                            icon={<EqualizerIcon />}
                        />
                        <BottomNavigationAction
                            component={Link}
                            to={Routes.resources}
                            label={getString('Navigation_resources')}
                            value={Routes.resources}
                            showLabel={true}
                            icon={<ConnectWithoutContactIcon />}
                        />
                    </BottomBar>
                ) : null}
            </ResponsiveContainer>
        </Centered>
    );
});

export default Chrome;
