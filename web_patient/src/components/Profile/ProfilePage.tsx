import { List, ListItem } from '@mui/material';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import ListCard from 'src/components/common/ListCard';
import { MainPage } from 'src/components/common/MainPage';
import { getImage } from 'src/services/images';
import { getFormPath, ParameterValues, Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';

export const ProfilePage: FunctionComponent = () => {
    return (
        <MainPage title={getString('Navigation_profile')}>
            <List>
                <ListItem disableGutters={true} component={Link} to={Routes.valuesInventory}>
                    <ListCard
                        title={getString('Profile_inventory_title')}
                        subtitle={getString('Profile_inventory_subtitle')}
                        imageSrc={getImage('Profile_values_button_image')}
                    />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={Routes.resources}>
                    <ListCard
                        title={getString('Profile_resources_title')}
                        subtitle={getString('Profile_resources_subtitle')}
                        imageSrc={getImage('Profile_worksheets_button_image')}
                    />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={getFormPath(ParameterValues.form.safetyPlan)}>
                    <ListCard
                        title={getString('Profile_safety_plan_title')}
                        subtitle={getString('Profile_safety_plan_subtitle')}
                        imageSrc={getImage('Profile_safety_button_image')}
                    />
                </ListItem>
            </List>
        </MainPage>
    );
};

export default ProfilePage;
