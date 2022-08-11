import {
    Button,
    CssBaseline,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
} from '@mui/material';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import withTheme from '@mui/styles/withTheme';
import { default as React, FunctionComponent, useEffect, useState } from 'react';
import { useIdleTimer } from 'react-idle-timer';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

const RootContainer = styled.div({
    display: 'flex',
    flexDirection: 'column',
    height: 'calc(100vh)',
});

const MainContainer = withTheme(
    styled.main((props) => ({
        flexGrow: 1,
        marginTop: props.theme.customSizes.headerHeight,
        overflowY: 'hidden',
        overflowX: 'scroll',
        minWidth: 1200,
    })),
);

const AppBarContainer = withTheme(
    styled(AppBar)((props) => ({
        transition: props.theme.transitions.create(['width', 'margin'], {
            easing: props.theme.transitions.easing.sharp,
        }),
        width: '100%',
    })),
);

export interface IChromeProps {
    headerContent: React.ReactNode;
    children: React.ReactNode;
}

const idleTimeout = 1000 * 60 * 15;
const promptTimeout = 1000 * 60 * 1;

export const Chrome: FunctionComponent<IChromeProps> = (props) => {
    const { authStore } = useStores();

    const [open, setOpen] = useState(false);
    const [remaining, setRemaining] = useState(0);

    const onPrompt = () => {
        setOpen(true);
        setRemaining(promptTimeout);
    };

    const onIdle = () => {
        setOpen(false);
        setRemaining(0);
        authStore.logout();
    };

    const onActive = () => {
        setOpen(false);
        setRemaining(0);
    };

    const { getRemainingTime, isPrompted, reset } = useIdleTimer({
        timeout: idleTimeout,
        promptTimeout,
        onPrompt,
        onIdle,
        onActive,
    });

    const handleStillHere = () => {
        setOpen(false);
        reset();
    };

    useEffect(() => {
        const interval = setInterval(() => {
            if (isPrompted()) {
                setRemaining(Math.ceil(getRemainingTime() / 1000));
            }
        }, 1000);
        return () => {
            clearInterval(interval);
        };
    }, []);

    return (
        <RootContainer>
            <CssBaseline />
            <AppBarContainer position="fixed">
                <Toolbar variant="dense">{props.headerContent}</Toolbar>
            </AppBarContainer>
            <MainContainer>{props.children}</MainContainer>
            <Dialog maxWidth="xs" open={open}>
                <DialogTitle>{'Session timeout'}</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        {`You have been idle for ${
                            idleTimeout / 1000 / 60
                        } minutes. You will be automatically signed out in ${remaining} seconds.`}
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleStillHere}>I'm still here</Button>
                </DialogActions>
            </Dialog>
        </RootContainer>
    );
};

export default Chrome;
