import { Button, CircularProgress, CssBaseline, Dialog, Typography } from '@mui/material';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import withTheme from '@mui/styles/withTheme';
import { observer } from 'mobx-react';
import { default as React, FunctionComponent } from 'react';
import Footer from 'src/components/chrome/Footer';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

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
        marginTop: props.theme.customSizes.headerHeight,
        overflow: 'hidden',
    }))
);

const AppBarContainer = withTheme(
    styled(AppBar)((props) => ({
        transition: props.theme.transitions.create(['width', 'margin'], {
            easing: props.theme.transitions.easing.sharp,
        }),
        width: '100%',
    }))
);

export interface IChromeProps {
    headerContent: React.ReactNode;
    children: React.ReactNode;
}

export const Chrome: FunctionComponent<IChromeProps> = observer((props) => {
    const rootStore = useStores();

    return (
        <RootContainer>
            <Dialog open={rootStore.appState != 'Fulfilled'}>
                {rootStore.appState == 'Pending' ? (
                    <LoadingContainer>
                        <CircularProgress />
                        <Typography variant="h6">Loading Registry</Typography>
                    </LoadingContainer>
                ) : (
                    <LoadingContainer>
                        <Button color="inherit" onClick={() => rootStore.login()}>
                            Log in
                        </Button>
                    </LoadingContainer>
                )}
            </Dialog>
            <CssBaseline />
            <AppBarContainer position="fixed">
                <Toolbar variant="dense">{props.headerContent}</Toolbar>
            </AppBarContainer>
            <MainContainer>{props.children}</MainContainer>
            <Footer></Footer>
        </RootContainer>
    );
});

export default Chrome;
