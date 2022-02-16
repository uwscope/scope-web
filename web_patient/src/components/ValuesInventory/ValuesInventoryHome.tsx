import { Divider, List, ListItem, ListItemIcon, ListItemText, Typography } from '@mui/material';
import { styled } from '@mui/styles';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { Link } from 'react-router-dom';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import DetailPage from 'src/components/common/DetailPage';
import { getActivitiesString, getLifeAreaIcon, getValuesString } from 'src/components/ValuesInventory/values';
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
                        const lifeareaValues =
                            patientStore.valuesInventory?.values?.filter((v) => v.lifeareaId == la.id) || [];
                        const activitiesCount = lifeareaValues
                            .map((v) => v.activities.length)
                            .reduce((l, r) => l + r, 0);

                        return (
                            <Fragment key={la.id}>
                                <ListItem disableGutters button component={Link} to={`${la.id}`}>
                                    <ListItemIcon>{getLifeAreaIcon(la.id)}</ListItemIcon>
                                    <ListItemText
                                        primary={la.name}
                                        secondary={`${getValuesString(lifeareaValues.length)}; ${getActivitiesString(
                                            activitiesCount,
                                        )}`}
                                    />
                                </ListItem>
                                {idx < lifeAreas.length - 1 && <Divider variant="middle" />}
                            </Fragment>
                        );
                    })}
                </List>
            </ContentLoader>
        </DetailPage>
    );
});

export default ValuesInventoryHome;
