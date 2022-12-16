import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import {
    Box,
    Button,
    // FormControl,
    Divider,
    Grid,
    IconButton,
    // InputLabel,
    Menu,
    MenuItem,
    // Select,
    // SelectChangeEvent,
    Stack,
    TextField,
    Typography,
} from '@mui/material';
import { random } from 'lodash';
import { action, runInAction, toJS } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent, ReactNode } from 'react';
import { useNavigate, useParams } from 'react-router';
import { Link } from 'react-router-dom';
import { IActivity, IValue } from 'shared/types';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import { DetailPage } from 'src/components/common/DetailPage';
import StatefulDialog from 'src/components/common/StatefulDialog';
import FormSection, { HeaderText, HelperText, SubHeaderText } from 'src/components/Forms/FormSection';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import { getFormLink, ParameterValues } from 'src/services/routes';

interface IValueEditFormSection {
    error: boolean;
    loading: boolean;
    value: IValue;
    activityExamples: string[];
    handleCancelEditActivity: () => void;
    handleMoreClickValue: (value: IValue, event: React.MouseEvent<HTMLElement>) => void;
    handleMoreClickActivity: (activity: IActivity, event: React.MouseEvent<HTMLElement>) => void;
}

const ValueEditFormSection = observer((props: IValueEditFormSection) => {
    const {
        // error,
        // loading,
        value,
        // activityExamples,
        // handleCancelEditActivity,
        handleMoreClickValue,
        handleMoreClickActivity,
    } = props;

    const rootStore = useStores();
    const { patientStore } = rootStore;

    const renderActivityDetail = (activity: IActivity): ReactNode => {
        // TODO Activity Refactor: Enhance this with ActivitySchedule data
        return (
            (activity.enjoyment || activity.importance) && (
                <HelperText>
                    {activity.enjoyment && (
                        <Fragment>
                            {getString('values_inventory_value_activity_enjoyment')} {activity.enjoyment}
                        </Fragment>
                    )}
                    {activity.enjoyment && activity.importance && ' / '}
                    {activity.importance && (
                        <Fragment>
                            {getString('values_inventory_value_activity_importance')} {activity.importance}
                        </Fragment>
                    )}
                </HelperText>
            )
        );
    };

    const renderActivities = (activities: IActivity[]): ReactNode => {
        const sortedActivities = activities
            .slice()
            .sort((a, b) => a.name.toLocaleLowerCase().localeCompare(b.name.toLocaleLowerCase()));

        return sortedActivities.map((activity, idx) => (
            <Fragment key={activity.activityId as string}>
                <Grid container direction="row" alignItems="flex-start" flexWrap="nowrap">
                    <Grid item>
                        <Typography sx={{ paddingRight: 1 }}>{`${idx + 1}.`}</Typography>
                    </Grid>
                    <Grid item flexGrow={1} overflow="hidden">
                        <Stack spacing={0}>
                            <Typography variant="body1" noWrap>
                                {activity.name}
                            </Typography>
                            {renderActivityDetail(activity)}
                        </Stack>
                    </Grid>
                    <IconButton
                        edge="end"
                        aria-label="more"
                        onClick={(e) => handleMoreClickActivity(activity, e)}
                        size="large">
                        <MoreVertIcon />
                    </IconButton>
                </Grid>
                {idx < sortedActivities.length - 1 && <Divider variant="middle" />}
            </Fragment>
        ));
    };

    const valueActivities = patientStore.getActivitiesByValueId(value.valueId as string);

    return (
        <Stack spacing={0}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
                <SubHeaderText>{value.name}</SubHeaderText>
                <IconButton edge="end" aria-label="more" onClick={(e) => handleMoreClickValue(value, e)} size="large">
                    <MoreVertIcon />
                </IconButton>
            </Stack>
            <Stack spacing={1}>
                {renderActivities(valueActivities)}

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography sx={{ paddingRight: 1 }}>{`${valueActivities.length + 1}.`}</Typography>
                    <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        startIcon={<AddIcon />}
                        component={Link}
                        to={getFormLink(ParameterValues.form.addActivity)}>
                        {getString('values_inventory_add_activity')}
                    </Button>
                </Box>
            </Stack>
        </Stack>
    );
});

const AddEditValueDialog: FunctionComponent<{
    open: boolean;
    isEdit: boolean;
    lifeArea: string;
    value: string;
    examples: string[];
    error?: boolean;
    loading?: boolean;
    handleChange: (change: string) => void;
    handleCancel: () => void;
    handleSave: () => void;
}> = (props) => {
    const { open, isEdit, lifeArea, value, examples, error, loading, handleCancel, handleChange, handleSave } = props;
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
                    <SubHeaderText>{lifeArea}</SubHeaderText>
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
            //handleDelete={handleDelete}
            handleSave={handleSave}
            disableSave={!value}
        />
    );
};

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
    const { lifeAreaId } = useParams<{ lifeAreaId: string }>();
    if (!lifeAreaId) {
        return null;
    }
    const rootStore = useStores();
    const { patientStore } = rootStore;
    const lifeAreaContent = rootStore.getLifeAreaContent(lifeAreaId);

    if (!lifeAreaContent) {
        return null;
    }

    interface IViewStateModeNone {
        mode: 'none';
    }
    interface IViewStateModeAdd {
        mode: 'add';
    }
    interface IViewStateModeEdit {
        mode: 'edit';
        editValue: IValue;
    }
    interface IViewState {
        openAddEditValue: boolean;
        name: string;
        modeState: IViewStateModeNone | IViewStateModeAdd | IViewStateModeEdit;

        moreTargetValueEl: (EventTarget & HTMLElement) | undefined;
        selectedValue: IValue | undefined;

        moreTargetActivityEl: (EventTarget & HTMLElement) | undefined;
        selectedActivity: IActivity | undefined;
    }

    const viewState = useLocalObservable<IViewState>(() => ({
        openAddEditValue: false,
        name: '',
        modeState: {
            mode: 'none',
        },
        moreTargetValueEl: undefined,
        selectedValue: undefined,
        moreTargetActivityEl: undefined,
        selectedActivity: undefined,
    }));

    const navigate = useNavigate();

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const handleMoreClickValue = action((value: IValue, event: React.MouseEvent<HTMLElement>) => {
        viewState.selectedValue = value;
        viewState.moreTargetValueEl = event.currentTarget;
    });

    const handleMoreCloseValue = action(() => {
        viewState.selectedValue = undefined;
        viewState.moreTargetValueEl = undefined;
    });

    const handleAddValue = action(() => {
        // Open AddEditValueDialog to Add value.

        viewState.openAddEditValue = true;
        viewState.name = '';
        viewState.modeState = {
            mode: 'add',
        };
    });

    const handleEditValue = action(() => {
        // Open AddEditValueDialog to Edit value.

        // valueId is sufficient for creating this interface callback,
        // but upon activation our viewState takes a copy of the value that is being edited.

        const value = viewState.selectedValue;
        console.assert(value, `Value to edit not found: ${value?.valueId}`);

        if (value) {
            viewState.moreTargetValueEl = undefined;
            viewState.openAddEditValue = true;
            viewState.name = value.name;
            viewState.modeState = {
                mode: 'edit',
                editValue: value,
            };
        }
    });

    const handleCancelValue = action(() => {
        viewState.openAddEditValue = false;
        // TODO Activity Refactor: No reason we should be reseting this?
        patientStore.loadValuesInventoryState.resetState();
    });

    const handleCancelEditActivity = action(() => {
        // TODO Activity Refactor: No reason we should be reseting this?
        patientStore.loadValuesInventoryState.resetState();
    });

    const handleChangeValue = action((change: string) => {
        viewState.name = change;
    });

    const handleDeleteValue = action(async () => {
        // TODO: Add delete confirmation.
        const value = viewState.selectedValue;

        // Remove the popup menu
        viewState.moreTargetValueEl = undefined;

        await patientStore.deleteValue(value as IValue);
    });

    const handleSaveValue = action(async () => {
        if (viewState.modeState.mode == 'add') {
            // TODO Activity Refactor: check that our 'add' is valid
            // is a unique name

            await patientStore.addValue({
                name: viewState.name,
                lifeAreaId: lifeAreaId,
                editedDateTime: new Date(),
            });
        } else if (viewState.modeState.mode == 'edit') {
            // TODO Activity Refactor: check that our 'edit' is valid
            // the value still exists
            // - update should fail due to rev conflict if it does not?
            // - what does the client actually do?
            // is a unique name
            // the value changed?

            await patientStore.updateValue({
                ...viewState.modeState.editValue,
                name: viewState.name,
                editedDateTime: new Date(),
            });
        }

        runInAction(() => {
            if (!patientStore.loadValuesState.error) {
                viewState.openAddEditValue = false;
            }
        });
    });

    const handleMoreClickActivity = action((activity: IActivity, event: React.MouseEvent<HTMLElement>) => {
        viewState.selectedActivity = activity;
        viewState.moreTargetActivityEl = event.currentTarget;
    });

    const handleMoreCloseActivity = action(() => {
        viewState.selectedActivity = undefined;
        viewState.moreTargetActivityEl = undefined;
    });

    const handleEditActivity = action(() => {
        // TODO Activity Refactor: Implement Activity Edit
        alert('Edit this activity');
    });

    const handleDeleteActivity = action(() => {
        // TODO Activity Refactor: Implement Activity Deletion
        alert('Delete this activity');
    });

    const handleScheduleActivity = action(() => {
        // TODO Activity Refactor: Implement Activity Scheduling
        alert('Schedule this activity');
    });

    const valueExamples = lifeAreaContent.examples.map((e) => e.name);
    const activityExamples = lifeAreaContent.examples[
        random(lifeAreaContent.examples.length - 1, false)
    ].activities.map((a) => a.name);

    return (
        <DetailPage title={lifeAreaContent.name} onBack={handleGoBack}>
            <ContentLoader
                state={patientStore.loadValuesInventoryState}
                name="values & activities inventory"
                onRetry={() => patientStore.loadValuesInventory()}>
                <Stack spacing={6}>
                    {patientStore.getValuesByLifeAreaId(lifeAreaId).length == 0 ? (
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
                                {patientStore.getValuesByLifeAreaId(lifeAreaId).map((value) => {
                                    return (
                                        <Fragment>
                                            <Menu
                                                id="value-menu"
                                                anchorEl={viewState.moreTargetValueEl}
                                                keepMounted
                                                open={Boolean(viewState.moreTargetValueEl)}
                                                onClose={handleMoreCloseValue}>
                                                <MenuItem onClick={handleEditValue}>
                                                    {getString('values_inventory_activity_menu_edit')}
                                                </MenuItem>
                                                <MenuItem onClick={handleDeleteValue}>
                                                    {getString('values_inventory_activity_menu_delete')}
                                                </MenuItem>
                                            </Menu>
                                            <Menu
                                                id="activity-menu"
                                                anchorEl={viewState.moreTargetActivityEl}
                                                keepMounted
                                                open={Boolean(viewState.moreTargetActivityEl)}
                                                onClose={handleMoreCloseActivity}>
                                                <MenuItem onClick={handleEditActivity}>
                                                    {getString('values_inventory_activity_menu_edit')}
                                                </MenuItem>
                                                <MenuItem onClick={handleScheduleActivity}>
                                                    {getString('values_inventory_activity_menu_schedule')}
                                                </MenuItem>
                                                <MenuItem onClick={handleDeleteActivity}>
                                                    {getString('values_inventory_activity_menu_delete')}
                                                </MenuItem>
                                            </Menu>
                                            <ValueEditFormSection
                                                error={patientStore.loadValuesInventoryState.error}
                                                loading={patientStore.loadValuesInventoryState.pending}
                                                value={value}
                                                activityExamples={activityExamples}
                                                handleCancelEditActivity={handleCancelEditActivity}
                                                handleMoreClickValue={handleMoreClickValue}
                                                handleMoreClickActivity={handleMoreClickActivity}
                                                key={value.valueId}
                                            />
                                        </Fragment>
                                    );
                                })}
                            </Stack>
                        </Stack>
                    )}
                    <FormSection
                        prompt={
                            patientStore.getValuesByLifeAreaId(lifeAreaId).length > 0
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
                    open={viewState.openAddEditValue}
                    isEdit={viewState.modeState.mode == 'edit'}
                    lifeArea={lifeAreaContent.name}
                    value={viewState.name}
                    examples={valueExamples}
                    error={patientStore.loadValuesInventoryState.error}
                    loading={patientStore.loadValuesInventoryState.pending}
                    handleCancel={handleCancelValue}
                    handleChange={handleChangeValue}
                    handleSave={handleSaveValue}
                />
            </ContentLoader>
        </DetailPage>
    );
});

export default LifeAreaDetail;

/* TODO Activity Refactor: Abandoned AddEditActivityDialog Code

const handleEditActivity = (activityId: string) =>
    // activityId is sufficient for creating this interface callback.
    action(() => {
        console.log(activityId);
        // const value = patientStore.values.find((value) => valueId == value.valueId);
        //
        // console.assert(value, `Value to edit not found: ${valueId}`);
        //
        // if (value) {
        //     viewState.openAddEditValue = true;
        //     viewState.name = value.name;
        //     viewState.modeState = {
        //         mode: 'edit',
        //         editValue: {
        //             ...toJS(value)
        //         },
        //     };
        // }
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
*/
