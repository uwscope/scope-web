import { CssBaseline, withTheme } from '@material-ui/core';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import { observer } from 'mobx-react';
import { default as React, FunctionComponent } from 'react';
import Footer from 'src/components/chrome/Footer';
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
    return (
        <RootContainer>
            <CssBaseline />
            <AppBarContainer position="fixed">
                <Toolbar>{props.headerContent}</Toolbar>
            </AppBarContainer>
            <MainContainer>{props.children}</MainContainer>
            <Footer></Footer>
        </RootContainer>
    );
});

export default Chrome;
