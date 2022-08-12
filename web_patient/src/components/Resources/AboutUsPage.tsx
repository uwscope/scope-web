import { Avatar, Stack, Typography } from '@mui/material';
import { action } from 'mobx';
import React, { FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { DetailPage } from 'src/components/common/DetailPage';
import { getString } from 'src/services/strings';
import Logo from 'src/assets/scope-logo.png';

export const AboutUsPage: FunctionComponent = () => {
    const navigate = useNavigate();

    const handleGoBack = action(() => {
        navigate(-1);
    });

    return (
        <DetailPage title={getString('Resources_about_us_title')} onBack={handleGoBack}>
            <Stack spacing={4}>
                <Avatar
                    alt="Scope logo"
                    src={Logo}
                    sx={{ width: 128, height: 128, alignSelf: 'center' }}
                    variant="square"
                />
                <Typography>
                    The SCOPE app is designed to improve the delivery of Collaborative Care, a team-based approach to
                    whole-person care. You can use the app to track your mood, symptoms, medications and activities, and
                    to share critical information with your clinical social worker. With the help of the SCOPE app, you
                    and your social worker will figure out what treatment strategies and activities work best to help
                    you feel better.
                </Typography>
                <Typography>
                    This app was designed by researchers at the University of Washington and Seattle Cancer Alliance,
                    with input from patients like you.
                </Typography>
                <Typography>
                    The app is part of the SCOPE study funded by the National Cancer Institute. The goal of our research
                    is to determine if new tools such as this app can help improve patient care, reduce distressing
                    symptoms, and improve quality of life for people going through cancer treatment. If the app is
                    helpful, we will make it widely available to people being treated at other cancer centers.
                </Typography>
            </Stack>
        </DetailPage>
    );
};

export default AboutUsPage;
