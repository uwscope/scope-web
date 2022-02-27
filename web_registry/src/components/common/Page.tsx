import { Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

export const Page = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(3),
        overflowX: 'hidden',
        overflowY: 'auto',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
    })),
);

export const PageHeaderTitle: FunctionComponent = (props) => {
    return <Typography variant="h5">{props.children}</Typography>;
};

export const PageHeaderSubtitle: FunctionComponent = (props) => {
    return <Typography variant="caption">{props.children}</Typography>;
};

const HeaderContainer = withTheme(
    styled.div((props) => ({
        marginBottom: props.theme.spacing(2),
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'stretch',
    })),
);

const HeaderContent = styled.div({
    flexGrow: 1,
});

export const PageHeaderContainer: FunctionComponent = (props) => {
    return (
        <HeaderContainer>
            <HeaderContent>{props.children}</HeaderContent>
        </HeaderContainer>
    );
};
