import { Divider, List, ListItem, ListItemIcon, ListItemText, Typography } from '@mui/material';
import { styled } from '@mui/styles';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { Link } from 'react-router-dom';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import DetailPage from 'src/components/common/DetailPage';
import { getActivitiesCountString, getLifeAreaIcon, getValuesCountString } from 'src/components/ValuesInventory/values';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

const InstructionText = styled(Typography)({
    lineHeight: 1,
});

export const ValuesInventoryHome: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const { lifeAreas } = rootStore.appContentConfig;
    const navigate = useNavigate();
    const { patientStore } = rootStore;

    const handleGoBack = action(() => {
        navigate(-1);
    });

    return (
        <DetailPage title={getString('Values_inventory_title')} onBack={handleGoBack}>
            <InstructionText paragraph>{getString('Values_inventory_instruction1')}</InstructionText>
            <InstructionText paragraph>{getString('Values_inventory_instruction2')}</InstructionText>
            <InstructionText paragraph>{getString('Values_inventory_instruction3')}</InstructionText>
            <InstructionText paragraph>{getString('Values_inventory_instruction4')}</InstructionText>
            <ContentLoader
                state={patientStore.loadValuesInventoryState}
                name="values & activities inventory"
                onRetry={() => patientStore.loadValuesInventory()}>
                <List>
                    {lifeAreas.map((la, idx) => {
                        const lifeAreaActivities = patientStore.getActivitiesByLifeAreaId(la.id);
                        const lifeAreaValues = patientStore.getValuesByLifeAreaId(la.id);

                        return (
                            <Fragment key={la.id}>
                                <ListItem disableGutters button component={Link} to={`${la.id}`}>
                                    <ListItemIcon>{getLifeAreaIcon(la.id)}</ListItemIcon>
                                    <ListItemText
                                        primary={la.name}
                                        secondary={
                                            getValuesCountString(lifeAreaValues.length) +
                                            '; ' +
                                            getActivitiesCountString(lifeAreaActivities.length)
                                        }
                                    />
                                </ListItem>
                                {idx < lifeAreas.length - 1 && <Divider variant="middle" />}
                            </Fragment>
                        );
                    })}
                    <ListItem disableGutters button component={Link} to={`Other`}>
                        <ListItemIcon>{getLifeAreaIcon('Other')}</ListItemIcon>
                        <ListItemText
                            primary={'Other'}
                            secondary={getActivitiesCountString(patientStore.getActivitiesWithoutValueId().length)}
                        />
                    </ListItem>
                </List>
            </ContentLoader>
        </DetailPage>
    );
});

export default ValuesInventoryHome;
