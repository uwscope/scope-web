import { Link, Stack, Typography } from '@mui/material';
import { action } from 'mobx';
import React, { FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { DetailPage } from 'src/components/common/DetailPage';
import { getString } from 'src/services/strings';
import styled, { withTheme } from 'styled-components';

const HeaderText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.h6.fontSize,
        fontWeight: props.theme.typography.fontWeightBold,
        lineHeight: 1,
        textTransform: 'uppercase',
    })),
);

const ListDiv = styled.ul({
    marginBlockStart: '0.5em',
    marginBlockEnd: '0.5em',
});

export const CrisisResourcesPage: FunctionComponent = () => {
    const navigate = useNavigate();

    const handleGoBack = action(() => {
        navigate(-1);
    });

    return (
        <DetailPage title={getString('Resources_crisis_resources_title')} onBack={handleGoBack}>
            <Stack spacing={4}>
                <HeaderText>All resources are available 24x7</HeaderText>
                <div>
                    <Typography variant="body1">
                        <b>National Suicide Prevention Lifeline</b> - {'  '}
                        <Link
                            href="https://suicidepreventionlifeline.org/"
                            target="_blank"
                            sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                            https://suicidepreventionlifeline.org/
                        </Link>
                    </Typography>
                    <ListDiv>
                        <li>
                            <Typography variant="body1">
                                Suicide & Crisis Lifeline - Call {' '}
                                <Link
                                    href="tel:988/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    988
                                </Link>
                                {' '} or {' '}
                                <Link
                                    href="tel:18002738255/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    1-800-273-TALK (8255)
                                </Link>
                            </Typography>
                        </li>
                        <li>
                            <Typography variant="body1">
                                Lifeline Web Chat - {' '}
                                <Link
                                    href="https://suicidepreventionlifeline.org/chat/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    https://suicidepreventionlifeline.org/chat/
                                </Link>
                            </Typography>
                        </li>
                        <li>
                            <Typography variant="body1">
                                Crisis Text Line - {' '}
                                <Link
                                    href="https://www.crisistextline.org/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    https://www.crisistextline.org/
                                </Link>
                                {' '} - Text {' '}
                                <Link
                                    href="sms:988/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    988
                                </Link>
                                {' '} or Text "HOME" to {' '}
                                <Link
                                    href="sms:741741/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    741741
                                </Link>
                            </Typography>
                        </li>
                    </ListDiv>
                </div>
                <div>
                    <Typography variant="body1">
                        <b>Crisis Connection</b> (Crisis Lines in Washington State)
                    </Typography>
                    <ListDiv>
                        <Typography variant="body1">
                            <li>
                                <Link href="https://www.crisisconnections.org/24-hour-crisis-line/" target="_blank">
                                    https://www.crisisconnections.org/24-hour-crisis-line/
                                </Link>
                            </li>
                        </Typography>
                    </ListDiv>
                </div>
            </Stack>
        </DetailPage>
    );
};

export default CrisisResourcesPage;
