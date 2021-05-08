import { CircularProgress, Typography, withTheme } from '@material-ui/core';
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

const PageTitle = styled(Typography)({
    minHeight: 48,
});

export const PageHeaderTitle: FunctionComponent = (props) => {
    return <PageTitle variant="h5">{props.children}</PageTitle>;
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
    }))
);

const HeaderContent = styled.div({
    flexGrow: 1,
});
export interface IPageHeaderContainerProps {
    loading?: boolean;
}

export const PageHeaderContainer: FunctionComponent<IPageHeaderContainerProps> = (props) => {
    return (
        <HeaderContainer>
            <HeaderContent>{props.children}</HeaderContent>
            {props.loading ? <CircularProgress /> : null}
        </HeaderContainer>
    );
};
