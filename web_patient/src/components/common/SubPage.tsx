import { Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const PageHeader = withTheme(
    styled(Typography)((props) => ({
        position: 'fixed',
        fontWeight: 600,
        [props.theme.breakpoints.up('phone')]: {
            fontSize: '1.5em',
            padding: props.theme.spacing(4, 2),
        },
        [props.theme.breakpoints.up('tablet')]: {
            fontSize: '2em',
            padding: props.theme.spacing(4, 8),
        },
        [props.theme.breakpoints.up('laptop')]: {
            fontSize: '2.5em',
            padding: props.theme.spacing(4, 20),
        },
    }))
);

const PageContainer = styled.div({
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
});

const PageContentContainer = withTheme(
    styled.div((props) => ({
        flexGrow: 1,
        overflowY: 'auto',
        [props.theme.breakpoints.up('phone')]: {
            padding: props.theme.spacing(12, 2, 12, 2),
            paddingTop: 0,
            marginTop: props.theme.spacing(12),
        },
        [props.theme.breakpoints.up('tablet')]: {
            padding: props.theme.spacing(17, 8, 12, 8),
            paddingTop: 0,
            marginTop: props.theme.spacing(17),
        },
        [props.theme.breakpoints.up('laptop')]: {
            padding: props.theme.spacing(17, 20, 12, 20),
            paddingTop: 0,
            marginTop: props.theme.spacing(17),
        },
    }))
);

export interface IMainPageProps {
    title: string;
}

export const MainPage: FunctionComponent<IMainPageProps> = (props) => {
    const { title, children } = props;
    return (
        <PageContainer>
            <PageHeader>{title}</PageHeader>
            <PageContentContainer>{children}</PageContentContainer>
        </PageContainer>
    );
};
