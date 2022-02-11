import { List, ListItem } from '@mui/material';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import ListCard from 'src/components/common/ListCard';
import { MainPage } from 'src/components/common/MainPage';
import { getImage } from 'src/services/images';
import { Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';

export const ProgressPage: FunctionComponent = () => {
    return (
        <MainPage title={getString('Navigation_progress')}>
            <List>
                <ListItem disableGutters={true} component={Link} to={Routes.phqProgress}>
                    <ListCard
                        title={getString('Progress_phq_assessment_title')}
                        imageSrc={getImage('Resources_values_button_image')}
                    />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={Routes.gadProgress}>
                    <ListCard
                        title={getString('Progress_gad_assessment_title')}
                        imageSrc={getImage('Resources_values_button_image')}
                    />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={Routes.activityProgress}>
                    <ListCard
                        title={getString('Progress_activity_tracking_title')}
                        imageSrc={getImage('Progress_activity_button_image')}
                    />
                </ListItem>
            </List>
        </MainPage>
    );
};

export default ProgressPage;
