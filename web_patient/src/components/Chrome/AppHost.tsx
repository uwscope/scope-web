import { Box, CircularProgress, Fade, Typography } from '@mui/material';
import _ from 'lodash';
import { runInAction } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import { default as React, Fragment, FunctionComponent, useEffect } from 'react';
import { Login } from 'src/components/Chrome/Login';
import { getPatientServiceInstance } from 'shared/patientService';
import { useServices } from 'src/services/services';
import { IRootStore, RootStore } from 'src/stores/RootStore';
import { StoreProvider } from 'src/stores/stores';
import styled, { withTheme } from 'styled-components';
import AppLoader from 'src/components/Chrome/AppLoader';

const LoginContainer = withTheme(
    styled.div((props) => ({
        width: '100vw',
        height: '100vh',
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
            if (state.store?.authStore.isAuthenticated && state.store?.authStore.currentUserIdentity?.patientId) {
                const newPatientService = getPatientServiceInstance(
                    CLIENT_CONFIG.flaskBaseUrl,
                    state.store?.authStore.currentUserIdentity?.patientId,
                );
                newPatientService.applyAuth(
                    () => state.store?.authStore.getToken(),
                    () => state.store?.authStore.refreshToken(),
                );
                state.store?.createPatientStore(newPatientService);
                state.ready = true;
            }
        });
    }, [state.store?.authStore.isAuthenticated]);

    return (
        <Fragment>
            {state.ready && state.store && (
                <Fragment>
                    <StoreProvider store={state.store}>{children}</StoreProvider>
                </Fragment>
            )}

            <AppLoader isLoading={!!state.store?.authStore.isAuthenticating} text="Logging in..." />
            <Fade in={!state.store?.authStore.isAuthenticated} timeout={500}>
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
                                The app is not available at this moment. Please try again later.
                            </Typography>
                        </FailureContainer>
                    )}
                </LoginContainer>
            </Fade>
        </Fragment>
    );
});

export default AppHost;
