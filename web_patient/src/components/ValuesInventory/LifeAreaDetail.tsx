import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import {
    Box,
    Button,
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    MenuItem,
    Select,
    SelectChangeEvent,
    Stack,
    TextField,
    Typography,
} from '@mui/material';
import { random } from 'lodash';
import { action, runInAction, toJS } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useNavigate, useParams } from 'react-router';
import { ILifeAreaValue, ILifeAreaValueActivity, IValuesInventory } from 'shared/types';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import { DetailPage } from 'src/components/common/DetailPage';
import StatefulDialog from 'src/components/common/StatefulDialog';
import FormSection, { HeaderText, HelperText, SubHeaderText } from 'src/components/Forms/FormSection';
import { getActivityDetailText } from 'src/components/ValuesInventory/values';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

interface IValueEditFormSection {
    error: boolean;
    loading: boolean;
    value: ILifeAreaValue;
    activityExamples: string[];
    handleEditValue: () => void;
    handleCancelEditActivity: () => void;
    handleSaveValueActivities: (newValue: ILifeAreaValue) => Promise<void>;
}

const ValueEditFormSection = observer((props: IValueEditFormSection) => {
    const {
        error,
        loading,
        value,
        activityExamples,
        handleEditValue,
        handleCancelEditActivity,
        handleSaveValueActivities,
    } = props;

    const viewState = useLocalObservable<{
        openAddActivity: boolean;
        editActivityIdx: number;
    }>(() => ({
        openAddActivity: false,
        editActivityIdx: -1,
    }));

    const handleAddActivityItem = action(() => {
        viewState.openAddActivity = true;
        viewState.editActivityIdx = -1;
    });

    const handleEditActivityItem = action((idx: number) => {
        viewState.openAddActivity = true;
        viewState.editActivityIdx = idx;
    });

    const handleSaveActivity = action(async (newActivity: ILifeAreaValueActivity) => {
        const newValue = { ...toJS(value) };
        newValue.activities = newValue.activities?.slice() || [];

        if (viewState.editActivityIdx >= 0) {
            newValue.activities[viewState.editActivityIdx] = newActivity;
        } else {
            newValue.activities.push(newActivity);
        }

        await handleSaveValueActivities(newValue);

        runInAction(() => {
            if (!error) {
                viewState.openAddActivity = false;
            }
        });
    });

    const handleDeleteActivity = action(async () => {
        const newValue = { ...toJS(value) };
        newValue.activities = newValue.activities?.slice() || [];

        if (viewState.editActivityIdx >= 0) {
            newValue.activities.splice(viewState.editActivityIdx, 1);
            await handleSaveValueActivities(newValue);
        }

        runInAction(() => {
            if (!error) {
                viewState.openAddActivity = false;
            }
        });
    });

    const handleCancelActivity = action(() => {
        handleCancelEditActivity();
        viewState.openAddActivity = false;
    });

    return (
        <Stack spacing={0}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
                <SubHeaderText>{value.name}</SubHeaderText>
                <IconButton aria-label="edit" onClick={handleEditValue}>
                    <EditIcon />
                </IconButton>
            </Stack>
            <Stack spacing={1}>
                {value.activities.map((activity, idx) => (
                    <Grid container direction="row" alignItems="flex-start" key={idx} flexWrap="nowrap">
                        <Grid item>
                            <Typography sx={{ paddingRight: 1 }}>{`${idx + 1}.`}</Typography>
                        </Grid>
                        <Grid item flexGrow={1} overflow="hidden">
                            <Stack spacing={0}>
                                <Typography variant="body1" noWrap>
                                    {activity.name}
                                </Typography>
                                <HelperText>
                                    {getActivityDetailText(activity.enjoyment, activity.importance)}
                                </HelperText>
                            </Stack>
                        </Grid>
                        <IconButton size="small" aria-label="edit" onClick={() => handleEditActivityItem(idx)}>
                            <EditIcon fontSize="small" />
                        </IconButton>
                    </Grid>
                ))}
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography sx={{ paddingRight: 1 }}>{`${value.activities.length + 1}.`}</Typography>
                    <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={handleAddActivityItem}>
                        {getString('Values_inventory_add_activity')}
                    </Button>
                </Box>
            </Stack>
            {viewState.openAddActivity && (
                <AddEditActivityDialog
                    error={error}
                    loading={loading}
                    open={viewState.openAddActivity}
                    value={value.name}
                    activity={viewState.editActivityIdx >= 0 ? value.activities[viewState.editActivityIdx] : undefined}
                    examples={activityExamples}
                    handleCancel={handleCancelActivity}
                    handleSave={handleSaveActivity}
                    handleDelete={viewState.editActivityIdx >= 0 ? handleDeleteActivity : undefined}
                />
            )}
        </Stack>
    );
});

const AddEditValueDialog: FunctionComponent<{
    open: boolean;
    isEdit: boolean;
    lifearea: string;
    value: string;
    examples: string[];
    error?: boolean;
    loading?: boolean;
    handleChange: (change: string) => void;
    handleCancel: () => void;
    handleDelete?: () => void;
    handleSave: () => void;
}> = (props) => {
    const {
        open,
        isEdit,
        lifearea,
        value,
        examples,
        error,
        loading,
        handleCancel,
        handleChange,
        handleDelete,
        handleSave,
    } = props;
    return (
        <StatefulDialog
            open={open}
            error={error}
            loading={loading}
            title={
                isEdit
                    ? getString('Values_inventory_dialog_edit_value')
                    : getString('Values_inventory_dialog_add_value')
            }
            content={
                <Stack spacing={2}>
                    <SubHeaderText>{lifearea}</SubHeaderText>
                    <Examples title={getString('Values_inventory_values_example_title')} examples={examples} />
                    <TextField
                        autoFocus
                        margin="dense"
                        variant="outlined"
                        label={getString('Values_inventory_dialog_add_value_label')}
                        value={value}
                        onChange={(event: React.ChangeEvent<HTMLInputElement>) => handleChange(event.target.value)}
                        fullWidth
                    />
                </Stack>
            }
            handleCancel={handleCancel}
            handleDelete={handleDelete}
            handleSave={handleSave}
            disableSave={!value}
        />
    );
};

const AddEditActivityDialog: FunctionComponent<{
    open: boolean;
    error: boolean;
    loading: boolean;
    value: string;
    activity?: ILifeAreaValueActivity;
    examples: string[];
    handleCancel: () => void;
    handleDelete?: () => void;
    handleSave: (newActivity: ILifeAreaValueActivity) => void;
}> = observer((props) => {
    const { open, error, loading, value, activity, examples, handleCancel, handleDelete, handleSave } = props;
    const isEdit = !!activity;

    const viewState = useLocalObservable<{
        name: string;
        enjoyment: number;
        importance: number;
    }>(() => ({
        name: activity?.name || '',
        enjoyment: activity?.enjoyment || 0,
        importance: activity?.importance || 0,
    }));

    const canSave =
        !!viewState.name &&
        (viewState.name != activity?.name ||
            viewState.enjoyment != activity?.enjoyment ||
            viewState.importance != activity?.importance);

    const handleChangeName = action((event: React.ChangeEvent<HTMLInputElement>) => {
        viewState.name = event.target.value;
    });

    const handleChangeEnjoyment = action((event: SelectChangeEvent<number>) => {
        viewState.enjoyment = Number(event.target.value);
    });

    const handleChangeImportance = action((event: SelectChangeEvent<number>) => {
        viewState.importance = Number(event.target.value);
    });

    return (
        <StatefulDialog
            open={open}
            error={error}
            loading={loading}
            title={
                isEdit
                    ? getString('Values_inventory_dialog_edit_activity')
                    : getString('Values_inventory_dialog_add_activity')
            }
            content={
                <Stack spacing={2}>
                    <SubHeaderText>{value}</SubHeaderText>
                    <Examples title={getString('Values_inventory_value_item_example_activities')} examples={examples} />
                    <TextField
                        autoFocus
                        margin="dense"
                        variant="outlined"
                        label={getString('Values_inventory_dialog_add_activity_label')}
                        value={viewState.name}
                        onChange={handleChangeName}
                        fullWidth
                    />
                    <HelperText>{getString('Values_inventory_dialog_add_activity_prompt')}</HelperText>
                    <FormControl fullWidth>
                        <InputLabel id="activity-enjoyment">
                            {getString('Values_inventory_dialog_add_activity_enjoyment')}
                        </InputLabel>
                        <Select
                            labelId="activity-enjoyment-label"
                            id="activity-enjoyment"
                            value={viewState.enjoyment}
                            onChange={handleChangeEnjoyment}>
                            {[...Array(11).keys()].map((v) => (
                                <MenuItem key={v} value={v}>
                                    {v}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl fullWidth>
                        <InputLabel id="activity-importance-label">
                            {getString('Values_inventory_dialog_add_activity_importance')}
                        </InputLabel>
                        <Select
                            labelId="activity-importance-label"
                            id="activity-importance"
                            value={viewState.importance}
                            onChange={handleChangeImportance}>
                            {[...Array(11).keys()].map((v) => (
                                <MenuItem key={v} value={v}>
                                    {v}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Stack>
            }
            handleCancel={handleCancel}
            handleDelete={handleDelete}
            handleSave={() =>
                handleSave({
                    ...toJS(viewState),
                    createdDateTime: activity?.createdDateTime || new Date(),
                    editedDateTime: new Date(),
                })
            }
            disableSave={!canSave}
        />
    );
});

const Examples: FunctionComponent<{ title: string; examples: string[] }> = (props) => {
    const { title, examples } = props;
    return (
        <HelperText>
            <div>{`${title}:`}</div>
            {examples.map((ex, idx) => (
                <div key={idx}>{`${idx + 1}. ${ex}`}</div>
            ))}
        </HelperText>
    );
};

export const LifeAreaDetail: FunctionComponent = observer(() => {
    const { lifeareaId } = useParams<{ lifeareaId: string }>();
    if (!lifeareaId) {
        return null;
    }
    const rootStore = useStores();
    const { patientStore } = rootStore;
    const lifeareaContent = rootStore.getLifeAreaContent(lifeareaId);

    if (!lifeareaContent) {
        return null;
    }

    const values = patientStore.valuesInventory?.values || [];

    const viewState = useLocalObservable<{
        openAddValue: boolean;
        newValue: string;
        editValueIdx: number;
    }>(() => ({
        openAddValue: false,
        newValue: '',
        editValueIdx: -1,
    }));

    const navigate = useNavigate();

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const handleAddValue = action(() => {
        viewState.openAddValue = true;
        viewState.newValue = '';
        viewState.editValueIdx = -1;
    });

    const handleEditValue = (idx: number) =>
        action(() => {
            viewState.openAddValue = true;
            viewState.editValueIdx = idx;
            viewState.newValue = values[idx].name;
        });

    const handleCancelValue = action(() => {
        viewState.openAddValue = false;
        patientStore.loadValuesInventoryState.resetState();
    });

    const handleCancelEditActivity = action(() => {
        patientStore.loadValuesInventoryState.resetState();
    });

    const handleChangeValue = action((change: string) => {
        viewState.newValue = change;
    });

    const handleSaveValue = action(async () => {
        const { valuesInventory } = patientStore;
        const clonedInventory = toJS(valuesInventory);

        const newValues = clonedInventory.values || [];

        if (viewState.editValueIdx >= 0) {
            newValues[viewState.editValueIdx].name = viewState.newValue;
            newValues[viewState.editValueIdx].editedDateTime = new Date();
        } else {
            newValues.push({
                name: viewState.newValue,
                lifeareaId: lifeareaId,
                activities: [],
                createdDateTime: new Date(),
                editedDateTime: new Date(),
            } as ILifeAreaValue);
        }

        const newValuesInventory = {
            ...clonedInventory,
            lastUpdatedDateTime: new Date(),
            values: newValues,
        } as IValuesInventory;

        await patientStore.updateValuesInventory(newValuesInventory);

        runInAction(() => {
            if (!patientStore.loadValuesInventoryState.error) {
                viewState.openAddValue = false;
            }
        });
    });

    const handleSaveValueActivities = (idx: number) =>
        action(async (newValue: ILifeAreaValue) => {
            const { valuesInventory } = patientStore;
            const clonedInventory = toJS(valuesInventory);

            const newValues = clonedInventory.values?.slice() || [];
            newValues[idx] = newValue;

            const newValuesInventory = {
                ...clonedInventory,
                lastUpdatedDateTime: new Date(),
                values: newValues,
            } as IValuesInventory;

            await patientStore.updateValuesInventory(newValuesInventory);
        });

    const handleDeleteValue = action(async () => {
        const { valuesInventory } = patientStore;
        const clonedInventory = toJS(valuesInventory);

        let newValues = clonedInventory.values || [];

        if (viewState.editValueIdx >= 0) {
            newValues.splice(viewState.editValueIdx, 1);
        }

        const newValuesInventory = {
            ...toJS(valuesInventory),
            lastUpdatedDateTime: new Date(),
            values: newValues,
        } as IValuesInventory;

        await patientStore.updateValuesInventory(newValuesInventory);

        if (!patientStore.loadValuesInventoryState.error) {
            viewState.openAddValue = false;
        }
    });

    const valueExamples = lifeareaContent.examples.map((e) => e.name);
    const activityExamples = lifeareaContent.examples[
        random(lifeareaContent.examples.length - 1, false)
    ].activities.map((a) => a.name);

    return (
        <DetailPage title={lifeareaContent.name} onBack={handleGoBack}>
            <ContentLoader
                state={patientStore.loadValuesInventoryState}
                name="values & activities inventory"
                onRetry={() => patientStore.loadValuesInventory()}>
                <Stack spacing={6}>
                    {values?.filter((v) => v.lifeareaId == lifeareaId).length == 0 ? (
                        <FormSection
                            prompt={getString('Values_inventory_values_existing_title')}
                            subPrompt={getString('Values_inventory_values_empty_subprompt')}
                            content={
                                <Examples
                                    title={getString('Values_inventory_values_example_title')}
                                    examples={valueExamples}
                                />
                            }
                        />
                    ) : (
                        <Stack spacing={0}>
                            <HeaderText>{getString('Values_inventory_values_existing_title')}</HeaderText>
                            <Stack spacing={4}>
                                {values.map((value, idx) => {
                                    if (value.lifeareaId == lifeareaId) {
                                        return (
                                            <ValueEditFormSection
                                                error={patientStore.loadValuesInventoryState.error}
                                                loading={patientStore.loadValuesInventoryState.pending}
                                                value={value}
                                                activityExamples={activityExamples}
                                                handleEditValue={handleEditValue(idx)}
                                                handleCancelEditActivity={handleCancelEditActivity}
                                                handleSaveValueActivities={handleSaveValueActivities(idx)}
                                                key={idx}
                                            />
                                        );
                                    }
                                })}
                            </Stack>
                        </Stack>
                    )}
                    <FormSection
                        prompt={
                            values?.filter((v) => v.lifeareaId == lifeareaId).length > 0
                                ? getString('Values_inventory_values_more_title')
                                : ''
                        }
                        content={
                            <Button
                                sx={{ marginTop: 1, alignSelf: 'flex-start' }}
                                variant="contained"
                                color="primary"
                                startIcon={<AddIcon />}
                                onClick={handleAddValue}>
                                {getString('Values_inventory_add_value')}
                            </Button>
                        }
                    />
                </Stack>
                <AddEditValueDialog
                    open={viewState.openAddValue}
                    isEdit={viewState.editValueIdx >= 0}
                    lifearea={lifeareaContent.name}
                    value={viewState.newValue}
                    examples={valueExamples}
                    error={patientStore.loadValuesInventoryState.error}
                    loading={patientStore.loadValuesInventoryState.pending}
                    handleCancel={handleCancelValue}
                    handleChange={handleChangeValue}
                    handleSave={handleSaveValue}
                    handleDelete={viewState.editValueIdx >= 0 ? handleDeleteValue : undefined}
                />
            </ContentLoader>
        </DetailPage>
    );
});

export default LifeAreaDetail;
