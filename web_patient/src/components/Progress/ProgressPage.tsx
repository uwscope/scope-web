import { List, ListItem } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import MyNotesImageSrc from 'src/assets/mynotes.jpeg';
import MySafetyPlanImageSrc from 'src/assets/safetyplan.jpeg';
import ListCard from 'src/components/common/ListCard';
import { MainPage } from 'src/components/common/MainPage';
import { Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';

export const ProgressPage: FunctionComponent = () => {
    return (
        <MainPage title={getString('Navigation_progress')}>
            <List>
                <ListItem disableGutters={true} component={Link} to={Routes.phqProgress}>
                    <ListCard title={getString('Progress_phq_assessment_title')} imageUrl={MySafetyPlanImageSrc} />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={Routes.gadProgress}>
                    <ListCard title={getString('Progress_gad_assessment_title')} imageUrl={MySafetyPlanImageSrc} />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={Routes.activityProgress}>
                    <ListCard title={getString('Progress_activity_tracking_title')} imageUrl={MyNotesImageSrc} />
                </ListItem>
            </List>
        </MainPage>
    );
};

export default ProgressPage;
