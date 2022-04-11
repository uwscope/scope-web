import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const PageHeader = withTheme(
    styled.div((props) => ({
        position: 'fixed',
        fontWeight: 600,
        width: '100%',
        display: 'flex',
        flexDirection: 'row',
        zIndex: 1,
        backgroundColor: 'rgba(255, 255, 255, 0.5)',
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
    })),
);

const PageHeaderText = styled.div({
    flexGrow: 1,
});

const PageContainer = styled.div({
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    overflowY: 'auto',
});

const PageContentContainer = withTheme(
    styled.div((props) => ({
        flexGrow: 1,
        [props.theme.breakpoints.up('phone')]: {
            padding: props.theme.spacing(14, 2, 12, 2),
        },
        [props.theme.breakpoints.up('tablet')]: {
            padding: props.theme.spacing(19, 8, 12, 8),
        },
        [props.theme.breakpoints.up('laptop')]: {
            padding: props.theme.spacing(19, 20, 12, 20),
        },
    }))
);

export interface IMainPageProps {
    title: string;
    action?: React.ReactElement;
}

export const MainPage: FunctionComponent<IMainPageProps> = (props) => {
    const { title, action, children } = props;
    return (
        <PageContainer>
            <PageHeader>
                <PageHeaderText>{title}</PageHeaderText>
                {action}
            </PageHeader>
            <PageContentContainer>{children}</PageContentContainer>
        </PageContainer>
    );
};
