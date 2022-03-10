import { Divider, List, ListItem } from '@mui/material';
import React, { FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { Link } from 'react-router-dom';
import ListCard from 'src/components/common/ListCard';
import { MainPage } from 'src/components/common/MainPage';
import Section from 'src/components/common/Section';
import { getImage } from 'src/services/images';
import { getFormPath, ParameterValues, Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

export const ResourcesPage: FunctionComponent = () => {
    const { authStore } = useStores();
    const navigate = useNavigate();

    const onLogout = () => {
        authStore.logout();
        navigate(-1);
    };
    return (
        <MainPage title={getString('Navigation_resources')}>
            <Section>
                <List>
                    <ListItem
                        alignItems="flex-start"
                        disableGutters={true}
                        component={Link}
                        to={Routes.valuesInventory}>
                        <ListCard
                            title={getString('Resources_inventory_title')}
                            subtitle={getString('Resources_inventory_subtitle')}
                            imageSrc={getImage('Resources_values_button_image')}
                        />
                    </ListItem>
                    <ListItem alignItems="flex-start" disableGutters={true} component={Link} to={Routes.worksheets}>
                        <ListCard
                            title={getString('Resources_resources_title')}
                            subtitle={getString('Resources_resources_subtitle')}
                            imageSrc={getImage('Resources_worksheets_button_image')}
                        />
                    </ListItem>
                    <ListItem
                        alignItems="flex-start"
                        disableGutters={true}
                        component={Link}
                        to={getFormPath(ParameterValues.form.safetyPlan)}>
                        <ListCard
                            title={getString('Resources_safety_plan_title')}
                            subtitle={getString('Resources_safety_plan_subtitle')}
                            imageSrc={getImage('Resources_safety_button_image')}
                        />
                    </ListItem>
                    <ListItem
                        alignItems="flex-start"
                        disableGutters={true}
                        component={Link}
                        to={Routes.crisisresources}>
                        <ListCard
                            title={getString('Resources_crisis_resources_title')}
                            subtitle={getString('Resources_crisis_resources_subtitle')}
                            imageSrc={getImage('Resources_crisis_resources_button_image')}
                        />
                    </ListItem>
                    <Divider />
                    <ListItem alignItems="flex-start" disableGutters={true} component={Link} to={Routes.aboutus}>
                        <ListCard
                            title={getString('Resources_about_us_title')}
                            subtitle={getString('Resources_about_us_subtitle')}
                            imageSrc={getImage('Resources_about_us_button_image')}
                        />
                    </ListItem>
                    <ListItem alignItems="flex-start" disableGutters={true} component={Link} to={''} onClick={onLogout}>
                        <ListCard
                            title={getString('Resources_logout_title')}
                            subtitle={getString('Resources_logout_subtitle')}
                            imageSrc={getImage('Resources_logout_button_image')}
                        />
                    </ListItem>
                </List>
            </Section>
        </MainPage>
    );
};

export default ResourcesPage;
