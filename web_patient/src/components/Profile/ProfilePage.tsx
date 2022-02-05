import { List, ListItem } from '@mui/material';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import MyNotesImageSrc from 'src/assets/mynotes.jpeg';
import MySafetyPlanImageSrc from 'src/assets/safetyplan.jpeg';
import ListCard from 'src/components/common/ListCard';
import { MainPage } from 'src/components/common/MainPage';
import { Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';

export const ProfilePage: FunctionComponent = () => {
    return (
        <MainPage title={getString('Navigation_profile')}>
            <List>
                <ListItem disableGutters={true} component={Link} to={Routes.valuesInventory}>
                    <ListCard
                        title={getString('Profile_inventory_title')}
                        subtitle={getString('Profile_inventory_subtitle')}
                        imageUrl={MySafetyPlanImageSrc}
                    />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={Routes.resources}>
                    <ListCard
                        title={getString('Profile_resources_title')}
                        subtitle={getString('Profile_resources_subtitle')}
                        imageUrl={MyNotesImageSrc}
                    />
                </ListItem>
                <ListItem disableGutters={true}>
                    <ListCard
                        title="My Safety Plan"
                        subtitle="Emergency contacts and resources"
                        imageUrl={MySafetyPlanImageSrc}
                    />
                </ListItem>
                <ListItem disableGutters={true}>
                    <ListCard
                        title="My Notes"
                        subtitle="Values, goals, activities, responsibilities"
                        imageUrl={MyNotesImageSrc}
                    />
                </ListItem>
            </List>
        </MainPage>
    );
};

export default ProfilePage;
