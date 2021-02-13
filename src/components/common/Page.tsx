import { Typography, withTheme } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

export const Page = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(3),
        overflowX: 'hidden',
        overflowY: 'auto',
        height: '100%',
    }))
);

export const PageHeaderContainer = withTheme(
    styled.div((props) => ({
        marginBottom: props.theme.spacing(2),
    }))
);

const Title = styled(Typography)({
    minHeight: 48,
});

export const PageHeaderTitle: FunctionComponent = (props) => {
    return <Title variant="h4">{props.children}</Title>;
};

export const PageHeaderSubtitle: FunctionComponent = (props) => {
    return <Typography variant="caption">{props.children}</Typography>;
};
