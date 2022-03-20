import { Box, CircularProgress, Fade, Typography } from '@mui/material';
import { observer, useLocalObservable } from 'mobx-react';
import { runInAction } from 'mobx';
import { default as React, Fragment, FunctionComponent, useEffect } from 'react';
import Splash from 'src/assets/splash-image.jpg';
import Login from 'src/components/chrome/Login';
import { useServices } from 'src/services/services';
import { IRootStore, RootStore } from 'src/stores/RootStore';
import { StoreProvider } from 'src/stores/stores';
import styled, { withTheme } from 'styled-components';
import AppLoader from 'src/components/chrome/AppLoader';

const RootContainer = styled.div({
    height: '100vh',
    width: '100vw',
    display: 'flex',
    flexDirection: 'row',
    position: 'absolute',
    top: 0,
});

const ImageContainer = withTheme(
    styled.div((props) => ({
        height: '100%',
        [props.theme.breakpoints.down('md')]: {
            width: '100%',
            position: 'absolute',
        },
        [props.theme.breakpoints.up('md')]: {
            width: '50%',
        },
    })),
);

const LoginContainer = withTheme(
    styled.div((props) => ({
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        [props.theme.breakpoints.down('md')]: {
            width: '100%',
            position: 'absolute',
        },
        [props.theme.breakpoints.up('md')]: {
            width: '50%',
        },
    })),
);

const ProgressContainer = withTheme(
    styled.div((props) => ({
        width: 400,
        minHeight: 200,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderRadius: props.theme.spacing(4),
        padding: props.theme.spacing(4),
        [props.theme.breakpoints.down('md')]: {
            padding: props.theme.spacing(8),
        },
    })),
);

const FailureContainer = withTheme(
    styled.div((props) => ({
        width: 400,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderRadius: props.theme.spacing(4),
        padding: props.theme.spacing(4),
        [props.theme.breakpoints.down('md')]: {
            padding: props.theme.spacing(8),
        },
    })),
);

const SplashImage = styled.img({
    width: '100%',
    height: '100%',
    objectFit: 'cover',
});

export interface IAppHost {
    children: React.ReactNode;
}

export const AppHost: FunctionComponent<IAppHost> = observer((props) => {
    const { children } = props;

    const state = useLocalObservable<{
        store: IRootStore | undefined;
        failed: boolean;
        ready: boolean;
    }>(() => ({
        store: undefined,
        failed: false,
        ready: false,
    }));

    useEffect(() => {
        const { configService } = useServices();

        configService
            .getServerConfig()
            .then((serverConfig) => {
                // Create the RootStore
                const newStore = new RootStore(serverConfig);
                runInAction(() => {
                    state.store = newStore;
                });

                newStore.authStore.initialize();
            })
            .catch((error) => {
                console.error('Failed to retrieve server configuration', error);
                runInAction(() => {
                    state.failed = true;
                });
            });
    }, []);

    useEffect(() => {
        runInAction(() => {
            if (state.store?.authStore.isAuthenticated) {
                const { registryService } = useServices();
                registryService.applyAuth(
                    () => state.store?.authStore.getToken(),
                    () => state.store?.authStore.refreshToken(),
                );

                state.ready = true;
                state.store?.patientsStore.load(
                    () => state.store?.authStore.getToken(),
                    () => state.store?.authStore.refreshToken(),
                );
            }

            if (!state.store?.authStore.isAuthenticated) {
                state.ready = false;
                state.store?.reset();
            }
        });
    }, [state.store?.authStore.isAuthenticated]);

    return (
        <Fragment>
            {state.ready && state.store?.authStore.isAuthenticated && (
                <Fragment>
                    <StoreProvider store={state.store}>{children}</StoreProvider>
                </Fragment>
            )}
            <AppLoader isLoading={!!state.store?.authStore.isAuthenticating} text="Logging in..." />
            <Fade in={!state.store?.authStore.isAuthenticated} timeout={500}>
                <RootContainer>
                    <ImageContainer>
                        <SplashImage src={Splash} />
                    </ImageContainer>
                    <LoginContainer>
                        {!!state.store ? (
                            <Login authStore={state.store.authStore} />
                        ) : !state.failed ? (
                            <ProgressContainer>
                                <CircularProgress />
                                <Box sx={{ height: 40 }} />
                                <Typography>Connecting to service...</Typography>
                            </ProgressContainer>
                        ) : (
                            <FailureContainer>
                                <Typography variant="h1">Sorry!</Typography>
                                <Typography variant="h5">
                                    The registry is not available at this moment. Please try again later.
                                </Typography>
                            </FailureContainer>
                        )}
                    </LoginContainer>
                </RootContainer>
            </Fade>
        </Fragment>
    );
});

export default AppHost;
