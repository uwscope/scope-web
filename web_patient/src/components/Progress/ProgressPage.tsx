import { Divider, List, ListItem } from '@mui/material';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import ListCard from 'src/components/common/ListCard';
import { MainPage } from 'src/components/common/MainPage';
import Section from 'src/components/common/Section';
import { getImage } from 'src/services/images';
import { Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';

export const ProgressPage: FunctionComponent = () => {
    return (
        <MainPage title={getString('Navigation_progress')}>
            <Section>
                <List>
                    <ListItem disableGutters={true} component={Link} to={Routes.phqProgress}>
                        <ListCard
                            title={getString('Progress_phq_assessment_title')}
                            imageSrc={getImage('Progress_assessment_phq_button_image')}
                        />
                    </ListItem>
                    <Divider />
                    <ListItem disableGutters={true} component={Link} to={Routes.gadProgress}>
                        <ListCard
                            title={getString('Progress_gad_assessment_title')}
                            imageSrc={getImage('Progress_assessment_gad_button_image')}
                        />
                    </ListItem>
                    <Divider />
                    <ListItem disableGutters={true} component={Link} to={Routes.activityProgress}>
                        <ListCard
                            title={getString('Progress_activity_tracking_title')}
                            imageSrc={getImage('Progress_activity_button_image')}
                        />
                    </ListItem>
                    <Divider />
                    <ListItem disableGutters={true} component={Link} to={Routes.moodProgress}>
                        <ListCard
                            title={getString('Progress_mood_tracking_title')}
                            imageSrc={getImage('Progress_mood_button_image')}
                        />
                    </ListItem>
                </List>
            </Section>
        </MainPage>
    );
};

export default ProgressPage;
