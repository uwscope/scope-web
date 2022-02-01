import {
    DialogContentText,
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Select,
    SelectChangeEvent,
    styled,
    TextField,
} from '@mui/material';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useHistory, useParams } from 'react-router';
import { ILifeAreaValueActivity } from 'shared/types';
import ListDetailPage, { IListItem } from 'src/components/ValuesInventory/ListDetailPage';
import { getActivityDetailText } from 'src/components/ValuesInventory/values';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

const DropDown = styled(FormControl)({
    minWidth: 150,
});

export const ValueDetail: FunctionComponent = observer(() => {
    const { valueId } = useParams<{ lifeareaId: string; valueId: string }>();
    const rootStore = useStores();
    const { patientStore } = rootStore;
    const value = patientStore.getValueById(valueId);

    if (!value) {
        return null;
    }

    const viewState = useLocalObservable<{
        openAdd: boolean;
        selectedActivity: ILifeAreaValueActivity | undefined;
        activityName: string;
        enjoyment: number;
        importance: number;
    }>(() => ({
        openAdd: false,
        selectedActivity: undefined,
        activityName: '',
        enjoyment: 0,
        importance: 0,
    }));

    const history = useHistory();

    const handleGoBack = action(() => {
        history.goBack();
    });

    const handleAddActivity = action(() => {
        if (viewState.selectedActivity) {
            patientStore.updateActivityInValue(
                valueId,
                viewState.selectedActivity.id,
                viewState.activityName,
                viewState.enjoyment,
                viewState.importance
            );
        } else {
            patientStore.addActivityToValue(valueId, viewState.activityName, viewState.enjoyment, viewState.importance);
        }
        handleCancelAdd();
    });

    const handleDeleteActivity = action((activityId: string) => {
        patientStore.deleteActivityFromValue(valueId, activityId);
    });

    const handleChangeName = action((event: React.ChangeEvent<HTMLInputElement>) => {
        viewState.activityName = event.target.value;
    });

    const handleChangeEnjoyment = action((event: SelectChangeEvent<number>) => {
        viewState.enjoyment = Number(event.target.value);
    });

    const handleChangeImportance = action((event: SelectChangeEvent<number>) => {
        viewState.importance = Number(event.target.value);
    });

    const handleOpenAdd = action(() => {
        viewState.selectedActivity = undefined;
        viewState.activityName = '';
        viewState.enjoyment = 0;
        viewState.importance = 0;
        viewState.openAdd = true;
    });

    const handleCancelAdd = action(() => {
        viewState.openAdd = false;
    });

    const handleItemClick = action((activityId: string) => {
        viewState.selectedActivity = value.activities.slice().find((a) => a.id == activityId);

        if (!!viewState.selectedActivity) {
            viewState.activityName = viewState.selectedActivity.name;
            viewState.enjoyment = viewState.selectedActivity.enjoyment || 0;
            viewState.importance = viewState.selectedActivity.importance || 0;
        }

        viewState.openAdd = true;
    });

    return (
        <ListDetailPage
            title={value.name}
            onBack={handleGoBack}
            addButtonText={getString('Values_inventory_dialog_add_activity')}
            addDialogTitle={getString(
                !!viewState.selectedActivity
                    ? 'Values_inventory_dialog_add_activity_edit'
                    : 'Values_inventory_dialog_add_activity'
            )}
            addContent={
                <Fragment>
                    <InputLabel id="activity_enjoyment">
                        {getString('Values_inventory_dialog_add_activity_name')}
                    </InputLabel>
                    <TextField
                        autoFocus
                        margin="dense"
                        variant="outlined"
                        value={viewState.activityName}
                        onChange={handleChangeName}
                        fullWidth
                    />

                    <DialogContentText>{getString('Values_inventory_dialog_add_activity_prompt')}</DialogContentText>
                    <Grid container spacing={3} component="div">
                        <Grid item component="div">
                            <DropDown>
                                <InputLabel id="activity_enjoyment">
                                    {getString('Values_inventory_dialog_add_activity_enjoyment')}
                                </InputLabel>
                                <Select
                                    labelId="activity_enjoyment"
                                    value={viewState.enjoyment}
                                    onChange={handleChangeEnjoyment}>
                                    {[...Array(11).keys()].map((v) => (
                                        <MenuItem key={v} value={v}>
                                            {v}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </DropDown>
                        </Grid>
                        <Grid item component="div">
                            <DropDown>
                                <InputLabel id="activity_importance">
                                    {getString('Values_inventory_dialog_add_activity_importance')}
                                </InputLabel>
                                <Select
                                    labelId="activity_importance"
                                    value={viewState.importance}
                                    onChange={handleChangeImportance}>
                                    {[...Array(11).keys()].map((v) => (
                                        <MenuItem key={v} value={v}>
                                            {v}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </DropDown>
                        </Grid>
                    </Grid>
                </Fragment>
            }
            onOpenAdd={handleOpenAdd}
            onCancelAdd={handleCancelAdd}
            exampleHeaderText={getString('Values_inventory_value_item_example_activities')}
            examples={getString('Values_inventory_value_item_examples').split('\n')}
            instruction={getString('Values_inventory_value_item_activities_none')}
            listHeaderText={getString('Values_inventory_value_item_activities_header')}
            listHelpText={getString('Values_inventory_value_item_activities_help')}
            onItemClick={handleItemClick}
            items={value.activities.map(
                (activity) =>
                    ({
                        id: activity.id,
                        primaryText: activity.name,
                        secondaryText: getActivityDetailText(activity.enjoyment || 0, activity.importance || 0),
                    } as IListItem)
            )}
            onItemDelete={handleDeleteActivity}
            onItemAdded={handleAddActivity}
            openAdd={viewState.openAdd}
            canAdd={!!viewState.activityName}
        />
    );
});

export default ValueDetail;
