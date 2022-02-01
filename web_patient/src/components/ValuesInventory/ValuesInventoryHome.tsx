import { Divider, List, ListItem, ListItemIcon, ListItemText, Typography } from '@mui/material';
import { styled } from '@mui/styles';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useHistory } from 'react-router';
import { Link } from 'react-router-dom';
import { DetailPage } from 'src/components/common/DetailPage';
import { getActivitiesString, getLifeAreaIcon, getValuesString } from 'src/components/ValuesInventory/values';
import { Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

const InstructionText = styled(Typography)({
    lineHeight: 1,
});

export const ValuesInventoryHome: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const { lifeAreas } = rootStore.appConfig;
    const history = useHistory();
    const { patientStore } = rootStore;

    const handleGoBack = action(() => {
        history.goBack();
    });

    return (
        <DetailPage title={getString('Values_inventory_title')} onBack={handleGoBack}>
            <InstructionText paragraph>{getString('Values_inventory_instruction1')}</InstructionText>
            <InstructionText paragraph>{getString('Values_inventory_instruction2')}</InstructionText>
            <InstructionText paragraph>{getString('Values_inventory_instruction3')}</InstructionText>
            <InstructionText paragraph>{getString('Values_inventory_instruction4')}</InstructionText>
            <List>
                {lifeAreas.map((la, idx) => {
                    const lifeareaValues = patientStore.values.filter((v) => v.lifeareaId == la.id);
                    const activitiesCount = lifeareaValues.map((v) => v.activities.length).reduce((l, r) => l + r, 0);

                    return (
                        <Fragment>
                            <ListItem
                                disableGutters
                                button
                                key={la.id}
                                component={Link}
                                to={`/${Routes.valuesInventory}/${la.id}`}>
                                <ListItemIcon>{getLifeAreaIcon(la.id)}</ListItemIcon>
                                <ListItemText
                                    primary={la.name}
                                    secondary={`${getValuesString(lifeareaValues.length)}; ${getActivitiesString(
                                        activitiesCount
                                    )}`}
                                />
                            </ListItem>
                            {idx < lifeAreas.length - 1 && <Divider variant="middle" />}
                        </Fragment>
                    );
                })}
            </List>
        </DetailPage>
    );
});

export default ValuesInventoryHome;
