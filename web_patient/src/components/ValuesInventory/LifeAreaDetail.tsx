import { TextField } from '@mui/material';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useNavigate, useParams } from 'react-router';
import ListDetailPage, { IListItem } from 'src/components/ValuesInventory/ListDetailPage';
import { getActivitiesString } from 'src/components/ValuesInventory/values';
import { Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

export const LifeAreaDetail: FunctionComponent = observer(() => {
    const { lifeareaId } = useParams<{ lifeareaId: string }>();
    if (!lifeareaId) {
        return null;
    }
    const rootStore = useStores();
    const { patientStore } = rootStore;
    const lifeareaContent = rootStore.getLifeAreaContent(lifeareaId);
    const lifeareaValues = patientStore.values.filter((v) => v.lifeareaId == lifeareaId);

    if (!lifeareaContent) {
        return null;
    }

    const viewState = useLocalObservable<{
        openAdd: boolean;
        addedValue: string;
    }>(() => ({
        openAdd: false,
        addedValue: '',
    }));

    const navigate = useNavigate();

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const handleAddValue = action(() => {
        patientStore.addValueToLifearea(lifeareaId, viewState.addedValue);
        handleCancelAdd();
    });

    const handleDeleteValue = action((valueId: string) => {
        patientStore.deleteValueFromLifearea(lifeareaId, valueId);
    });

    const handleChangeValue = action((event: React.ChangeEvent<HTMLInputElement>) => {
        viewState.addedValue = event.target.value;
    });

    const handleOpenAdd = action(() => {
        viewState.openAdd = true;
        viewState.addedValue = '';
    });

    const handleCancelAdd = action(() => {
        viewState.openAdd = false;
        viewState.addedValue = '';
    });

    return (
        <ListDetailPage
            title={lifeareaContent.name}
            onBack={handleGoBack}
            addButtonText={getString('Values_inventory_dialog_add_value')}
            addDialogTitle={getString('Values_inventory_dialog_add_value')}
            addContent={
                <TextField
                    autoFocus
                    margin="dense"
                    variant="outlined"
                    value={viewState.addedValue}
                    onChange={handleChangeValue}
                    fullWidth
                />
            }
            onOpenAdd={handleOpenAdd}
            onCancelAdd={handleCancelAdd}
            exampleHeaderText={getString('Values_inventory_values_none')}
            examples={lifeareaContent.examples.map((e) => e.name)}
            instruction={getString('Values_inventory_values_none')}
            listHeaderText={getString('Values_inventory_values_header')}
            listHelpText={getString('Values_inventory_values_help')}
            getItemLinkRoute={(itemId) => `/${Routes.valuesInventory}/${lifeareaId}/${itemId}`}
            items={lifeareaValues.map(
                (value) =>
                    ({
                        id: value.id,
                        primaryText: value.name,
                        secondaryText: getActivitiesString(value.activities.length),
                    } as IListItem)
            )}
            onItemDelete={handleDeleteValue}
            onItemAdded={handleAddValue}
            openAdd={viewState.openAdd}
            canAdd={!!viewState.addedValue}
        />
    );
});

export default LifeAreaDetail;
