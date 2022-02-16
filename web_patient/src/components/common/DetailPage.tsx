import { AppBar, IconButton, Toolbar, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import BackIcon from '@mui/icons-material/ArrowBack';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const PageContainer = styled.div({
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    width: '100%',
    overflow: 'hidden',
});

const PageContentContainer = withTheme(
    styled.div((props) => ({
        flexGrow: 1,
        overflowY: 'auto',
        [props.theme.breakpoints.up('phone')]: {
            padding: props.theme.spacing(9, 2, 2, 2),
        },
        [props.theme.breakpoints.up('tablet')]: {
            padding: props.theme.spacing(17, 8, 8, 8),
        },
        [props.theme.breakpoints.up('laptop')]: {
            padding: props.theme.spacing(17, 20, 8, 20),
        },
    }))
);

export interface IDetailPageProps {
    title: string;
    onBack?: () => void;
}

export const DetailPage: FunctionComponent<IDetailPageProps> = (props) => {
    const { title, children, onBack } = props;

    return (
        <PageContainer>
            <AppBar>
                <Toolbar>
                    <IconButton
                        edge="start"
                        color="inherit"
                        onClick={onBack}
                        aria-label="back"
                        size="large">
                        <BackIcon />
                    </IconButton>
                    <Typography variant="h6" noWrap>
                        {title}
                    </Typography>
                </Toolbar>
            </AppBar>
            <PageContentContainer>{children}</PageContentContainer>
        </PageContainer>
    );
};

export default DetailPage;
