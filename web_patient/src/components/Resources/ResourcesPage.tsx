import { List, ListItem } from '@mui/material';
import React, { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';
import ListCard from 'src/components/common/ListCard';
import { MainPage } from 'src/components/common/MainPage';
import { getImage } from 'src/services/images';
import { getFormPath, ParameterValues, Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';

export const ResourcesPage: FunctionComponent = () => {
    return (
        <MainPage title={getString('Navigation_resources')}>
            <List>
                <ListItem disableGutters={true} component={Link} to={Routes.valuesInventory}>
                    <ListCard
                        title={getString('Resources_inventory_title')}
                        subtitle={getString('Resources_inventory_subtitle')}
                        imageSrc={getImage('Resources_values_button_image')}
                    />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={Routes.worksheets}>
                    <ListCard
                        title={getString('Resources_resources_title')}
                        subtitle={getString('Resources_resources_subtitle')}
                        imageSrc={getImage('Resources_worksheets_button_image')}
                    />
                </ListItem>
                <ListItem disableGutters={true} component={Link} to={getFormPath(ParameterValues.form.safetyPlan)}>
                    <ListCard
                        title={getString('Resources_safety_plan_title')}
                        subtitle={getString('Resources_safety_plan_subtitle')}
                        imageSrc={getImage('Resources_safety_button_image')}
                    />
                </ListItem>
            </List>
        </MainPage>
    );
};

export default ResourcesPage;
