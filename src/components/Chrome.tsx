import { Container } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled, { withTheme } from 'styled-components';
import Footer from './Footer';
import Header from './Header';

const MainContainer = withTheme(
    styled(Container)((props) => ({
        height: '100%',
        marginTop: 24,
        marginBottom: 48,
    }))
);

export const Chrome: FunctionComponent = observer(() => {
    return (
        <div>
            <Header></Header>
            <main>
                <MainContainer>This is the main part of the page</MainContainer>
            </main>
            <Footer></Footer>
        </div>
    );
});

export default Chrome;
