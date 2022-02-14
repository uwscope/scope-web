import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
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
import { action, toJS } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate, useParams } from 'react-router';
import { ILifeAreaValue, ILifeAreaValueActivity, IValuesInventory } from 'shared/types';
import { DetailPage } from 'src/components/common/DetailPage';
import FormSection, { Container, ContentContainer, PromptText, SubPromptText } from 'src/components/Forms/FormSection';
import { getActivityDetailText } from 'src/components/ValuesInventory/values';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

interface IValueEditFormSection {
    value: ILifeAreaValue;
    activityExamples: string[];
    handleEditValue: () => void;
    handleSaveValueActivities: (newValue: ILifeAreaValue) => void;
}

const ValueEditFormSection = observer((props: IValueEditFormSection) => {
    const { value, activityExamples, handleEditValue, handleSaveValueActivities } = props;

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

    const handleSaveActivity = action((newActivity: ILifeAreaValueActivity) => {
        const newValue = { ...toJS(value) };
        newValue.activities = newValue.activities || [];

        if (viewState.editActivityIdx >= 0) {
            newValue.activities[viewState.editActivityIdx] = newActivity;
        } else {
            newValue.activities.push(newActivity);
        }

        handleSaveValueActivities(newValue);

        viewState.openAddActivity = false;
    });

    const handleDeleteActivity = action(() => {
        const newValue = { ...toJS(value) };
        newValue.activities = newValue.activities || [];

        if (viewState.editActivityIdx >= 0) {
            newValue.activities.splice(viewState.editActivityIdx, 1);
            handleSaveValueActivities(newValue);
        }

        viewState.openAddActivity = false;
    });

    const handleCancelActivity = action(() => {
        viewState.openAddActivity = false;
    });

    return (
        <Container>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
                <SubPromptText>{value.name}</SubPromptText>
                <IconButton aria-label="edit" onClick={handleEditValue}>
                    <EditIcon />
                </IconButton>
            </Stack>
            <ContentContainer>
                <Stack spacing={4}>
                    {value.activities.map((activity, idx) => (
                        <Grid container direction="row" alignItems="flex-start" key={idx}>
                            <Grid item>
                                <Typography sx={{ paddingRight: 1 }}>{`${idx + 1}.`}</Typography>
                            </Grid>
                            <Grid item flexGrow={1}>
                                <Stack spacing={1}>
                                    <Typography>{activity.name}</Typography>
                                    <Typography>
                                        {getActivityDetailText(activity.enjoyment, activity.importance)}
                                    </Typography>
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
            </ContentContainer>
            {viewState.openAddActivity && (
                <AddEditActivityDialog
                    open={viewState.openAddActivity}
                    activity={viewState.editActivityIdx >= 0 ? value.activities[viewState.editActivityIdx] : undefined}
                    examples={activityExamples}
                    handleCancel={handleCancelActivity}
                    handleSave={handleSaveActivity}
                    handleDelete={viewState.editActivityIdx >= 0 ? handleDeleteActivity : undefined}
                />
            )}
        </Container>
    );
});

const AddEditValueDialog: FunctionComponent<{
    open: boolean;
    isEdit: boolean;
    value: string;
    examples: string[];
    handleChange: (change: string) => void;
    handleCancel: () => void;
    handleDelete?: () => void;
    handleSave: () => void;
}> = (props) => {
    const { open, isEdit, value, examples, handleCancel, handleChange, handleDelete, handleSave } = props;
    return (
        <Dialog open={open} fullWidth maxWidth="phone">
            <DialogTitle id="form-dialog-title">
                {isEdit
                    ? getString('Values_inventory_dialog_edit_value')
                    : getString('Values_inventory_dialog_add_value')}
            </DialogTitle>
            <DialogContent>
                <TextField
                    autoFocus
                    margin="dense"
                    variant="outlined"
                    label={getString('Values_inventory_dialog_add_value_label')}
                    value={value}
                    onChange={(event: React.ChangeEvent<HTMLInputElement>) => handleChange(event.target.value)}
                    fullWidth
                />
                <Examples title={getString('Values_inventory_values_example_title')} examples={examples} />
            </DialogContent>
            <DialogActions>
                <Button onClick={handleCancel} color="primary">
                    {getString('Form_button_cancel')}
                </Button>
                {handleDelete && (
                    <Button onClick={handleDelete} color="primary">
                        {getString('Form_button_delete')}
                    </Button>
                )}
                <Button onClick={handleSave} color="primary" disabled={!value}>
                    {getString('Form_button_save')}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

const AddEditActivityDialog: FunctionComponent<{
    open: boolean;
    activity?: ILifeAreaValueActivity;
    examples: string[];
    handleCancel: () => void;
    handleDelete?: () => void;
    handleSave: (newActivity: ILifeAreaValueActivity) => void;
}> = observer((props) => {
    const { open, activity, examples, handleCancel, handleDelete, handleSave } = props;
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
        viewState.name != activity?.name ||
        viewState.enjoyment != activity?.enjoyment ||
        viewState.importance != activity?.importance;

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
        <Dialog open={open} fullWidth maxWidth="phone">
            <DialogTitle id="form-dialog-title">
                {isEdit
                    ? getString('Values_inventory_dialog_edit_activity')
                    : getString('Values_inventory_dialog_add_activity')}
            </DialogTitle>
            <DialogContent>
                <Examples title={getString('Values_inventory_values_example_title')} examples={examples} />
                <TextField
                    autoFocus
                    margin="dense"
                    variant="outlined"
                    label={getString('Values_inventory_dialog_add_activity_label')}
                    value={viewState.name}
                    onChange={handleChangeName}
                    fullWidth
                />
                <DialogContentText>{getString('Values_inventory_dialog_add_activity_prompt')}</DialogContentText>
                <Grid container spacing={3} component="div">
                    <Grid item component="div">
                        <FormControl>
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
                        </FormControl>
                    </Grid>
                    <Grid item component="div">
                        <FormControl>
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
                        </FormControl>
                    </Grid>
                </Grid>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleCancel} color="primary">
                    {getString('Form_button_cancel')}
                </Button>
                {handleDelete && (
                    <Button onClick={handleDelete} color="primary">
                        {getString('Form_button_delete')}
                    </Button>
                )}
                <Button
                    onClick={() =>
                        handleSave({
                            ...toJS(viewState),
                            dateCreated: activity?.dateCreated || new Date(),
                            dateEdited: new Date(),
                        })
                    }
                    color="primary"
                    disabled={!canSave}>
                    {getString('Form_button_save')}
                </Button>
            </DialogActions>
        </Dialog>
    );
});

const Examples: FunctionComponent<{ title: string; examples: string[] }> = (props) => {
    const { title, examples } = props;
    return (
        <div>
            <div>{`${title}:`}</div>
            {examples.map((ex, idx) => (
                <div key={idx}>{`${idx + 1}. ${ex}`}</div>
            ))}
        </div>
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
            newValues[viewState.editValueIdx].dateEdited = new Date();
        } else {
            newValues.push({
                name: viewState.newValue,
                lifeareaId: lifeareaId,
                activities: [],
                dateCreated: new Date(),
                dateEdited: new Date(),
            } as ILifeAreaValue);
        }

        const newValuesInventory = {
            ...toJS(valuesInventory),
            lastUpdatedDate: new Date(),
            values: newValues,
        } as IValuesInventory;

        await patientStore.updateValuesInventory(newValuesInventory);

        viewState.openAddValue = false;
    });

    const handleSaveValueActivities = (idx: number) =>
        action(async (newValue: ILifeAreaValue) => {
            const { valuesInventory } = patientStore;
            const clonedInventory = toJS(valuesInventory);

            const newValues = clonedInventory.values || [];
            newValues[idx] = newValue;

            const newValuesInventory = {
                ...toJS(valuesInventory),
                lastUpdatedDate: new Date(),
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
            lastUpdatedDate: new Date(),
            values: newValues,
        } as IValuesInventory;

        await patientStore.updateValuesInventory(newValuesInventory);

        viewState.openAddValue = false;
    });

    // const handleDeleteValue = action((valueId: string) => {
    //     patientStore.deleteValueFromLifearea(lifeareaId, valueId);
    // });

    // const handleChangeValue = action((event: React.ChangeEvent<HTMLInputElement>) => {
    //     viewState.addedValue = event.target.value;
    // });

    // const handleOpenAdd = action(() => {
    //     viewState.openAdd = true;
    //     viewState.addedValue = '';
    // });

    // const handleCancelAdd = action(() => {
    //     viewState.openAdd = false;
    //     viewState.addedValue = '';
    // });

    const valueExamples = lifeareaContent.examples.map((e) => e.name);
    const activityExamples = lifeareaContent.examples[
        random(lifeareaContent.examples.length - 1, false)
    ].activities.map((a) => a.name);

    return (
        <DetailPage title={lifeareaContent.name} onBack={handleGoBack}>
            <Stack spacing={4}>
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
                    <Fragment>
                        <PromptText>{getString('Values_inventory_values_existing_title')}</PromptText>
                        {values.map((value, idx) => {
                            if (value.lifeareaId == lifeareaId) {
                                return (
                                    <ValueEditFormSection
                                        value={value}
                                        activityExamples={activityExamples}
                                        handleEditValue={handleEditValue(idx)}
                                        handleSaveValueActivities={handleSaveValueActivities(idx)}
                                        key={idx}
                                    />
                                );
                            }
                        })}
                    </Fragment>
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
                value={viewState.newValue}
                examples={valueExamples}
                handleCancel={handleCancelValue}
                handleChange={handleChangeValue}
                handleSave={handleSaveValue}
                handleDelete={viewState.editValueIdx >= 0 ? handleDeleteValue : undefined}
            />
        </DetailPage>
    );
});

export default LifeAreaDetail;
