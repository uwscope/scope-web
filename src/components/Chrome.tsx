import { Container, withTheme } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import Footer from './Footer';
import Header from './Header';

// Theme can be passed to styles. Not being used now.
const MainContainer = withTheme(
    styled(Container)((props) => ({
        height: '100%',
        marginTop: props.theme.spacing(3),
        marginBottom: props.theme.spacing(6),
    }))
);

export const Chrome: FunctionComponent = observer((props) => {
    return (
        <div>
            <Header></Header>
            <main>
                <MainContainer>{props.children}</MainContainer>
            </main>
            <Footer></Footer>
        </div>
    );
});

export default Chrome;
