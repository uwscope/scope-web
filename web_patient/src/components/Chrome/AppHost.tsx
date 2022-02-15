import { Box, CircularProgress, Fade, Typography } from '@mui/material';
import _ from 'lodash';
import { observer } from 'mobx-react';
import { default as React, Fragment, FunctionComponent, useEffect, useState } from 'react';
import { Login } from 'src/components/Chrome/Login';
import { getPatientServiceInstance } from 'src/services/patientService';
import { IRootService, ServiceProvider, useServices } from 'src/services/services';
import { IRootStore, RootStore } from 'src/stores/RootStore';
import { StoreProvider } from 'src/stores/stores';
import styled, { withTheme } from 'styled-components';

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

    const [store, setStore] = useState<IRootStore>();
    const [service, setService] = useState<IRootService>(useServices());
    const [failed, setFailed] = useState(false);
    const [ready, setReady] = useState(false);

    useEffect(() => {
        const { configService } = service;

        configService
            .getServerConfig()
            .then((serverConfig) => {
                // Create the RootStore
                const newStore = new RootStore(serverConfig);
                setStore(newStore);
            })
            .catch((error) => {
                console.error('Failed to retrieve server configuration', error);
                setFailed(true);
            });
    }, []);

    useEffect(() => {
        const { appService, configService } = service;

        if (store?.authStore.isAuthenticated && store?.authStore.currentUserIdentity?.authToken) {
            const newPatientService = getPatientServiceInstance(
                [CLIENT_CONFIG.flaskBaseUrl, 'patient', store?.authStore.currentUserIdentity.identityId]
                    .map((s) => _.trim(s, '/'))
                    .join('/'),
            );
            const newService = {
                appService,
                configService,
                patientService: newPatientService,
            };

            newPatientService.applyAuth(store?.authStore.currentUserIdentity?.authToken);
            setService(newService);
            setReady(true);
        }
    }, [store?.authStore.isAuthenticated]);

    return (
        <Fragment>
            {ready && store && (
                <Fragment>
                    <ServiceProvider service={service}>
                        <StoreProvider store={store}>{children}</StoreProvider>
                    </ServiceProvider>
                </Fragment>
            )}
            <Fade in={!store?.authStore.isAuthenticated} timeout={500}>
                <LoginContainer>
                    {!!store ? (
                        <Login authStore={store.authStore} />
                    ) : !failed ? (
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
