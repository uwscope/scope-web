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
import { action, runInAction } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent, ReactNode } from 'react';
import { useNavigate, useParams } from 'react-router';
import { Link } from 'react-router-dom';
import {IActivity, IValue} from 'shared/types';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import { DetailPage } from 'src/components/common/DetailPage';
import StatefulDialog from 'src/components/common/StatefulDialog';
import FormSection, { HeaderText, HelperText, SubHeaderText } from 'src/components/Forms/FormSection';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import { getFormLink, getFormPath, Parameters, ParameterValues } from 'src/services/routes';
import { LifeAreaIdOther } from "shared/enums";
import { ILifeAreaContent } from "shared/types";


interface IActivitiesSection {
    activities: IActivity[];
    valueId?: string;
    handleMoreClickActivity: (activity: IActivity, event: React.MouseEvent<HTMLElement>) => void;
}

const ActivitiesSection: FunctionComponent<IActivitiesSection> = (props: IActivitiesSection) => {
    const rootStore = useStores();
    const { patientStore } = rootStore;

    const renderActivityDetail = (activity: IActivity): ReactNode => {
        return (
            <Stack spacing={1}>
                {(activity.enjoyment || activity.importance) && (
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
                )}
                {(!!activity.activityId) && (() => {
                    const activitySchedules = patientStore.getActivitySchedulesByActivityId(activity.activityId);
                    const repeatActivitySchedules = activitySchedules.filter((as) => { return as.hasRepetition; });

                    return (
                        <Fragment>
                            {(activitySchedules.length == 0) && (
                                <HelperText>No Schedule</HelperText>
                            )}
                            {(activitySchedules.length == 1 && repeatActivitySchedules.length == 0) && (
                                <HelperText>{`1 Schedule`}</HelperText>
                            )}
                            {(activitySchedules.length == 1 && repeatActivitySchedules.length == 1) && (
                                <HelperText>{`1 Schedule, with Repeating`}</HelperText>
                            )}
                            {(activitySchedules.length > 1 && repeatActivitySchedules.length == 0) && (
                                <HelperText>{`${activitySchedules.length} Schedules`}</HelperText>
                            )}
                            {(activitySchedules.length > 1 && repeatActivitySchedules.length > 0) && (
                                <HelperText>{`${activitySchedules.length} Schedules, with ${repeatActivitySchedules.length} with Repeating`}</HelperText>
                            )}
                        </Fragment>
                    );
                })()}
            </Stack>
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
                        onClick={(e) => props.handleMoreClickActivity(activity, e)}
                        size="large"
                    >
                        <MoreVertIcon/>
                    </IconButton>
                </Grid>
                {idx < sortedActivities.length - 1 && <Divider variant="middle" />}
            </Fragment>
        ));
    };

    return (
        <Stack spacing={1}>
            {renderActivities(props.activities)}
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography sx={{ paddingRight: 1 }}>{`${props.activities.length + 1}.`}</Typography>
                <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    startIcon={<AddIcon />}
                    component={Link}
                    to={getFormLink(
                        ParameterValues.form.addActivity,
                        {
                            [Parameters.valueId]: props.valueId as string,
                            [Parameters.addSchedule]: ParameterValues.addSchedule.false,
                        }
                    )}
                >
                    {getString('values_inventory_add_activity')}
                </Button>
            </Box>
        </Stack>
    );
}

interface IValueEditFormSection {
    error: boolean;
    loading: boolean;
    value: IValue;
    activityExamples: string[];
    handleMoreClickValue: (value: IValue, event: React.MouseEvent<HTMLElement>) => void;
    handleMoreClickActivity: (activity: IActivity, event: React.MouseEvent<HTMLElement>) => void;
}

const ValueEditFormSection = observer((props: IValueEditFormSection) => {
    const {
        // error,
        // loading,
        value,
        // activityExamples,
        handleMoreClickValue,
        handleMoreClickActivity,
    } = props;

    const rootStore = useStores();
    const { patientStore } = rootStore;


    const valueActivities = patientStore.getActivitiesByValueId(value.valueId as string);

    return (
        <Stack spacing={0}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
                <SubHeaderText>{value.name}</SubHeaderText>
                <IconButton
                    edge="end"
                    aria-label="more"
                    onClick={(e) => handleMoreClickValue(value, e)}
                    size="large"
                >
                    <MoreVertIcon/>
                </IconButton>
            </Stack>
            <ActivitiesSection
                activities={valueActivities}
                valueId={value.valueId}
                handleMoreClickActivity={handleMoreClickActivity}
            />
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
    const {
        open,
        isEdit,
        lifeArea,
        value,
        examples,
        error,
        loading,
        handleCancel,
        handleChange,
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
                    <SubHeaderText>{lifeArea}</SubHeaderText>
                    <Examples title={getString('values_inventory_values_example_title')} examples={examples} />
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
            <Stack spacing={1}>
                <div>{`${title}:`}</div>
                {examples.map((ex, idx) => (
                    <div key={idx}>{`${idx + 1}. ${ex}`}</div>
                ))}
            </Stack>
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
    if (!lifeAreaContent && lifeAreaId != LifeAreaIdOther) {
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
    });

    const handleChangeValue = action((change: string) => {
        viewState.name = change;
    });

    const handleDeleteValue = action(async () => {
        // TODO Activity Refactor: Add delete confirmation.
        const value = viewState.selectedValue;

        // Remove the popup menu
        viewState.moreTargetValueEl = undefined;

        if (!!value) {
            await patientStore.deleteValue(value);
        }
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
        const activity = viewState.selectedActivity;

        // Remove the popup menu
        viewState.moreTargetActivityEl = undefined;

        navigate(getFormPath(
            ParameterValues.form.editActivity,
            {
                [Parameters.activityId as string]:
                activity?.activityId as string
            }
        ));
    });

    const handleDeleteActivity = action(async () => {
        // TODO Activity Refactor: Display some kind of confirmation
        const activity = viewState.selectedActivity;

        // Remove the popup menu
        viewState.moreTargetActivityEl = undefined;

        if (!!activity) {
            await patientStore.deleteActivity(activity);
        }
    });

    const handleAddActivitySchedule = action(() => {
        const activity = viewState.selectedActivity;

        // Remove the popup menu
        viewState.moreTargetActivityEl = undefined;

        navigate(getFormPath(
            ParameterValues.form.addActivitySchedule,
            {
                [Parameters.activityId as string]:
                activity?.activityId as string
            }
        ));
    });

    const displayLifeAreaName: string = (() => {
        if (lifeAreaId == LifeAreaIdOther) {
            return getString('values_inventory_life_area_other_activities_name');
        } else {
            return (lifeAreaContent as ILifeAreaContent).name;
        }
    })();
    const displayValueExamples: string[] = (() => {
        if (lifeAreaContent) {
            return lifeAreaContent.examples.map((e) => e.name);
        } else {
            return [];
        }
    })();
    const displayActivityExamples: string[] = (() => {
        if (lifeAreaContent) {
            return lifeAreaContent?.examples[
                random(lifeAreaContent.examples.length - 1, false)
            ].activities.map((a) => a.name);
        } else {
            return [];
        }
    })();

    return (
        <DetailPage title={displayLifeAreaName} onBack={handleGoBack}>
            <ContentLoader
                state={patientStore.loadValuesInventoryState}
                name="values & activities inventory"
                onRetry={() => patientStore.loadValuesInventory()}
            >
                <Stack spacing={6}>
                    {
                        lifeAreaId == LifeAreaIdOther ? (
                            <FormSection
                                prompt={getString('values_inventory_life_area_other_activities_title')}
                                subPrompt={getString('values_inventory_life_area_other_activities_subprompt')}
                                content={
                                    <ActivitiesSection
                                        activities={patientStore.getActivitiesWithoutValueId()}
                                        handleMoreClickActivity={handleMoreClickActivity}
                                    />
                                }
                            />
                        ) : (
                            <Fragment>
                                {
                                    patientStore.getValuesByLifeAreaId(lifeAreaId).length == 0 ? (
                                        <FormSection
                                            prompt={getString('values_inventory_values_identify_title')}
                                            subPrompt={getString('values_inventory_values_empty_subprompt')}
                                            content={
                                                <Examples
                                                    title={getString('values_inventory_values_example_title')}
                                                    examples={displayValueExamples}
                                                />
                                            }
                                        />
                                    ) : (
                                        <Stack spacing={0}>
                                            <HeaderText>{getString('values_inventory_values_identify_existing_title')}</HeaderText>
                                            <Stack spacing={4}>
                                                {patientStore.getValuesByLifeAreaId(lifeAreaId).map((value) => {
                                                    return (
                                                        <Fragment key={value.valueId}>
                                                            <ValueEditFormSection
                                                                error={patientStore.loadValuesInventoryState.error}
                                                                loading={patientStore.loadValuesInventoryState.pending}
                                                                value={value}
                                                                activityExamples={displayActivityExamples}
                                                                handleMoreClickValue={handleMoreClickValue}
                                                                handleMoreClickActivity={handleMoreClickActivity}
                                                            />
                                                        </Fragment>
                                                    );
                                                })}
                                            </Stack>
                                        </Stack>
                                    )
                                }
                                <FormSection
                                    prompt={
                                        patientStore.getValuesByLifeAreaId(lifeAreaId).length > 0
                                            ? getString('values_inventory_values_identify_more_title')
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
                            </Fragment>
                        )
                    }
                </Stack>
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
                    <MenuItem onClick={handleAddActivitySchedule}>
                        {getString('values_inventory_activity_menu_add_schedule')}
                    </MenuItem>
                    <MenuItem onClick={handleDeleteActivity}>
                        {getString('values_inventory_activity_menu_delete')}
                    </MenuItem>
                </Menu>
                <AddEditValueDialog
                    open={viewState.openAddEditValue}
                    isEdit={viewState.modeState.mode == 'edit'}
                    lifeArea={displayLifeAreaName}
                    value={viewState.name}
                    examples={displayValueExamples}
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
