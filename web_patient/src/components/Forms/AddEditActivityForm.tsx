import { DatePicker, TimePicker } from '@mui/lab';
import {
    Checkbox,
    Chip,
    Dialog,
    DialogContent,
    DialogTitle,
    FormControlLabel,
    FormGroup,
    Grid,
    List,
    ListItem,
    ListItemText,
    ListSubheader,
    MenuItem,
    Select,
    SelectChangeEvent,
    Stack,
    Switch,
    TextField,
    Typography,
} from '@mui/material';
import { compareAsc } from 'date-fns';
import { action, toJS } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { DayOfWeek, daysOfWeekValues } from 'shared/enums';
import { clearTime } from 'shared/time';
import {IActivity, ILifeAreaValue, KeyedMap} from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getRouteParameter, Parameters } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

export interface IAddEditActivityFormProps extends IFormProps {}

export const AddEditActivityForm: FunctionComponent<IAddEditActivityFormProps> = observer(() => {
    const rootStore = useStores();
    const { patientStore, appContentConfig } = rootStore;
    // const { valuesInventory } = patientStore;
    const { lifeAreas } = appContentConfig;

    const routeForm = getRouteParameter(Parameters.form);

    const initialViewState: IViewState = (() => {
        const defaultViewState: IViewState = {
            name: '',
            lifeAreaId: '',
            valueId: '',
            enjoyment: -1,
            importance: -1,
            modeState: {
                mode: 'none',
            },
        };

        if (routeForm == ParameterValues.form.addActivity) {
            return {
                ...defaultViewState,
                modeState: {
                    mode: 'addActivity',
                },
            };
        } else if (routeForm == ParameterValues.form.editActivity) {
            const routeActivityId = getRouteParameter(Parameters.activityId);
            console.assert(!!routeActivityId, 'editActivity parameter activityId not found');
            if (!routeActivityId) {
                return defaultViewState;
            }

            const editActivity = patientStore.getActivityById(routeActivityId);
            console.assert(!!editActivity, 'editActivity activity not found');
            if (!editActivity) {
                return defaultViewState;
            }

            const valueIdAndLifeAreaId = (() => {
                if (!editActivity.valueId) {
                    return {};
                }

                const editValue = patientStore.getValueById(editActivity.valueId);
                console.assert(!!editValue, 'editActivity value not found');
                if (!editValue) {
                    return {};
                }

                return {
                    valueId: editActivity.valueId,
                    lifeAreaId: editValue.lifeAreaId,
                }
            })();

            return {
                ...defaultViewState,
                name: editActivity.name,
                ...valueIdAndLifeAreaId,
                enjoyment: editActivity.enjoyment ? editActivity.enjoyment : defaultViewState.enjoyment,
                importance: editActivity.importance ? editActivity.importance : defaultViewState.importance,
                modeState: {
                    mode: 'editActivity',
                    editActivity: {
                        ...toJS(editActivity)
                    }
                },
            }
        }

        return defaultViewState;
    })();

    interface IViewStateModeNone {
        mode: 'none';
    }
    interface IViewStateModeAddActivity {
        mode: 'addActivity';
    }
    interface IViewStateModeEditActivity {
        mode: 'editActivity';
        editActivity: IActivity;
    }
    type IViewModeState = IViewStateModeNone | IViewStateModeAddActivity | IViewStateModeEditActivity;

    interface IViewState {
        name: string;
        lifeAreaId: string;
        valueId: string;
        enjoyment: number;
        importance: number;
        modeState: IViewModeState;
    }

    const viewState = useLocalObservable<IViewState>(() => initialViewState);

    /* TODO Activity Refactor: Pending additions to ViewState
    const dataState = useLocalObservable<IActivity>(() => ({
        startDateTime: activity?.startDateTime || new Date(),
        timeOfDay: activity?.timeOfDay || 9,
        hasReminder: activity?.hasReminder || false,
        reminderTimeOfDay: activity?.reminderTimeOfDay || 9,
        hasRepetition: activity?.hasRepetition || false,
        repeatDayFlags: Object.assign(
            {},
            ...daysOfWeekValues.map((x) => ({
                [x]: !!activity?.repeatDayFlags?.[x],
            })),
        ),
    }));
    */

    const handleSubmit = action(async () => {
        try {
            if (viewState.modeState.mode == 'addActivity') {
                // TODO Activity Refactor: check that our 'add' is valid
                // is a unique name

                const createActivity = {
                    name: viewState.name,
                    enjoyment: viewState.enjoyment >= 0 ? viewState.enjoyment : undefined,
                    importance: viewState.importance >= 0 ? viewState.importance : undefined,
                    valueId: viewState.valueId ? viewState.valueId : undefined,

                    editedDateTime: new Date(),
                };

                await patientStore.addActivity(createActivity);
            } else if (viewState.modeState.mode == 'editActivity') {
                // TODO Activity Refactor: check that our 'edit' is valid
                // the value still exists
                // - update should fail due to rev conflict if it does not?
                // - what does the client actually do?
                // is a unique name
                // the value changed?

                const editActivity = {
                    ...viewState.modeState.editActivity,

                    name: viewState.name,
                    enjoyment: viewState.enjoyment >= 0 ? viewState.enjoyment : undefined,
                    importance: viewState.importance >= 0 ? viewState.importance : undefined,
                    valueId: viewState.valueId ? viewState.valueId : undefined,

                    editedDateTime: new Date(),
                }

                await patientStore.updateActivity(editActivity);
            }

            return !patientStore.loadActivitiesState.error;
        } catch {
            return false;
        }
    });

    const handleAddValueOpen = action(() => {
        // TODO Activity Refactor: Create and Select Value During Activity Editing
    });

    const handleChangeName = action((event: React.ChangeEvent<HTMLInputElement>) => {
        viewState.name = event.target.value;
    });

    const handleSelectEnjoyment = action((event: SelectChangeEvent<number>) => {
        viewState.enjoyment = Number(event.target.value);
    });

    const handleSelectImportance = action((event: SelectChangeEvent<number>) => {
        viewState.importance = Number(event.target.value);
    });

    const handleSelectLifeArea = action((event: SelectChangeEvent<string>) => {
        viewState.lifeAreaId = event.target.value as string;
        viewState.valueId = '';
    });

    const handleSelectValue = action((event: SelectChangeEvent<string>) => {
        viewState.valueId = event.target.value as string;
    });

    {/* TODO Activity Refactor: Abandoned Activity Import Code
    // const values = valuesInventory?.values || [];
    // const groupedActivities: KeyedMap<ImportableActivity[]> = {};
    // let activityCount = 0;

    // const values: ILifeAreaValue[] = [];
    // values.forEach((value) => {
    //     const lifearea = value.lifeareaId;
    //     if (!groupedActivities[lifearea]) {
    //         groupedActivities[lifearea] = [];
    //     }
    //
    //     value.activities.forEach((activity) => {
    //         groupedActivities[lifearea].push({
    //             activity: activity.name,
    //             value: value.name,
    //             lifeareaId: lifearea,
    //         });
    //
    //         activityCount += groupedActivities[lifearea].length;
    //     });
    // });

    const handleOpenImportActivity = action(() => {
        viewState.openImportActivity = true;
    });

    const handleImportActivityItemClick = action((activity: ImportableActivity | undefined) => {
        viewState.openActivityDialog = false;

        if (!!activity) {
            dataState.name = activity.activity;
            dataState.value = activity.value;
            dataState.lifeareaId = activity.lifeareaId;
        }
    });

    {activityCount > 0 && (
        <Grid container justifyContent="flex-end">
            <Chip
                sx={{ marginTop: 1 }}
                variant="outlined"
                color="primary"
                size="small"
                label={getString('Form_add_activity_describe_name_import_button')}
                onClick={handleOpenImportActivity}
            />
            <Dialog
                maxWidth="phone"
                open={viewState.openActivityDialog}
                onClose={() => handleImportActivityItemClick(undefined)}>
                <DialogTitle>
                    {getString('Form_add_activity_describe_name_import_dialog_title')}
                </DialogTitle>

                <DialogContent dividers>
                    <List disablePadding>
                        {Object.keys(groupedActivities).map((lifearea) => {
                            const lifeareaName =
                                lifeAreas.find((l) => l.id == lifearea)?.name || lifearea;
                            return (
                                <Fragment key={lifearea}>
                                    <ListSubheader disableGutters>{lifeareaName}</ListSubheader>
                                    {groupedActivities[lifearea].map((activity, idx) => (
                                        <ListItem
                                            disableGutters
                                            button
                                            onClick={() => handleImportActivityItemClick(activity)}
                                            key={idx}>
                                            <ListItemText primary={activity.activity} />
                                        </ListItem>
                                    ))}
                                </Fragment>
                            );
                        })}
                    </List>
                </DialogContent>
            </Dialog>
        </Grid>
    )}
    */}

    const activityPage = (
        <Stack spacing={4}>
            <FormSection
                prompt={getString('form_add_edit_activity_name_prompt')}
                help={getString('form_add_edit_activity_name_help')}
                content={
                    <Fragment>
                        <TextField
                            fullWidth
                            value={viewState.name}
                            onChange={handleChangeName}
                            variant="outlined"
                            multiline
                        />
                    </Fragment>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString('form_add_edit_activity_life_area_value_prompt')}
                help={getString('form_add_edit_activity_life_area_value_help')}
                content={
                    <Fragment>
                        <SubHeaderText>{getString('form_add_edit_activity_life_area_label')}</SubHeaderText>
                        <HelperText>{getString('form_add_edit_activity_life_area_help')}</HelperText>
                        <Select
                            variant="outlined"
                            value={viewState.lifeAreaId}
                            onChange={handleSelectLifeArea}
                            fullWidth
                        >
                            <MenuItem key='' value=''></MenuItem>
                            {lifeAreas.map((lifeArea) => (
                                <MenuItem key={lifeArea.id} value={lifeArea.id}>
                                    {lifeArea.name}
                                </MenuItem>
                            ))}
                        </Select>
                        <SubHeaderText>{getString('form_add_edit_activity_value_label')}</SubHeaderText>
                        <HelperText>{getString('form_add_edit_activity_value_help')}</HelperText>
                        <Select
                            variant="outlined"
                            value={viewState.valueId}
                            onChange={handleSelectValue}
                            fullWidth
                            disabled={!viewState.lifeAreaId}
                        >
                            <MenuItem key='' value=''></MenuItem>
                            {viewState.lifeAreaId && (
                                patientStore.getValuesByLifeAreaId(viewState.lifeAreaId).map((value, idx) => (
                                    <MenuItem key={idx} value={value.valueId}>
                                        {value.name}
                                    </MenuItem>
                                ))
                            )}
                        </Select>
                        <Grid container justifyContent="flex-end">
                            <Chip
                                sx={{ marginTop: 1 }}
                                variant="outlined"
                                color="primary"
                                size="small"
                                label={getString('form_add_edit_activity_add_value_button')}
                                onClick={handleAddValueOpen}
                            />
                        </Grid>
                    </Fragment>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString('form_add_edit_activity_enjoyment_prompt')}
                help={getString('form_add_edit_activity_enjoyment_help')}
                content={
                    <Select
                        labelId="activity-enjoyment-label"
                        id="activity-enjoyment"
                        value={viewState.enjoyment}
                        onChange={handleSelectEnjoyment}
                    >
                        <MenuItem key='' value='-1'></MenuItem>
                        {[...Array(11).keys()].map((v) => (
                            <MenuItem key={v} value={v}>
                                {v}
                            </MenuItem>
                        ))}
                    </Select>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString('form_add_edit_activity_importance_prompt')}
                help={getString('form_add_edit_activity_importance_help')}
                content={
                    <Select
                        labelId="activity-importance-label"
                        id="activity-importance"
                        value={viewState.importance}
                        onChange={handleSelectImportance}
                    >
                        <MenuItem key='' value='-1'></MenuItem>
                        {[...Array(11).keys()].map((v) => (
                            <MenuItem key={v} value={v}>
                                {v}
                            </MenuItem>
                        ))}
                    </Select>
                }
            />
        </Stack>
    );

    { /* TODO Activity Refactor: Abandoned Schedule and Notification Code
    const handleRepeatChange = action((checked: boolean, day: DayOfWeek) => {
        if (dataState.repeatDayFlags != undefined) {
            dataState.repeatDayFlags[day] = checked;
        }
    });

    const schedulePage = (
        <Stack spacing={4}>
            <FormSection
                prompt={getString(!!activity ? 'Form_add_activity_date_label' : 'Form_add_activity_date')}
                content={
                    <DatePicker
                        value={dataState.startDateTime || ''}
                        onChange={(date: Date | null) => handleValueChange('startDateTime', date)}
                        minDate={activity?.startDateTime || new Date()}
                        renderInput={(params) => (
                            <TextField
                                variant="outlined"
                                margin="none"
                                fullWidth
                                {...params}
                                InputLabelProps={{
                                    shrink: true,
                                    sx: { position: 'relative' },
                                }}
                            />
                        )}
                    />
                }
            />
            <FormSection
                addPaddingTop
                prompt={getString(!!activity ? 'Form_add_activity_time_label' : 'Form_add_activity_time')}
                content={
                    <TimePicker
                        value={new Date(1, 1, 1, dataState.timeOfDay, 0, 0) || new Date()}
                        onChange={(date: Date | null) => handleValueChange('timeOfDay', date?.getHours())}
                        renderInput={(params) => (
                            <TextField
                                variant="outlined"
                                margin="none"
                                fullWidth
                                {...params}
                                InputLabelProps={{
                                    shrink: true,
                                    sx: { position: 'relative' },
                                }}
                            />
                        )}
                        ampm={true}
                        views={['hours']}
                    />
                }
            />
            <FormSection
                addPaddingTop
                prompt={getString(!!activity ? 'Form_add_activity_reminder_section' : 'Form_add_activity_reminder')}
                content={
                    <Grid container alignItems="center" spacing={1} justifyContent="flex-start">
                        <Grid item>
                            <Typography>{getString('Form_button_no')}</Typography>
                        </Grid>
                        <Grid item>
                            <Switch
                                checked={dataState.hasReminder}
                                color="default"
                                onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                                    handleValueChange('hasReminder', event.target.checked)
                                }
                                name="onOff"
                            />
                        </Grid>
                        <Grid item>
                            <Typography>{getString('Form_button_yes')}</Typography>
                        </Grid>
                    </Grid>
                }
            />
            {dataState.hasReminder && (
                <FormSection
                    addPaddingTop
                    prompt={getString(
                        !!activity ? 'Form_add_activity_reminder_time_label' : 'Form_add_activity_reminder_time',
                    )}
                    content={
                        <TimePicker
                            value={new Date(1, 1, 1, dataState.reminderTimeOfDay, 0, 0) || new Date()}
                            onChange={(date: Date | null) => handleValueChange('reminderTimeOfDay', date?.getHours())}
                            renderInput={(params) => (
                                <TextField
                                    variant="outlined"
                                    margin="none"
                                    fullWidth
                                    {...params}
                                    InputLabelProps={{
                                        shrink: true,
                                        sx: { position: 'relative' },
                                    }}
                                />
                            )}
                            ampm={true}
                            views={['hours']}
                        />
                    }
                />
            )}
        </Stack>
    );

    const repetitionPage = (
        <Stack spacing={4}>
            <FormSection
                prompt={getString(!!activity ? 'Form_add_activity_repetition_section' : 'Form_add_activity_repetition')}
                content={
                    <Grid container alignItems="center" spacing={1} justifyContent="flex-start">
                        <Grid item>
                            <Typography>{getString('Form_button_no')}</Typography>
                        </Grid>
                        <Grid item>
                            <Switch
                                checked={dataState.hasRepetition}
                                color="default"
                                onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                                    handleValueChange('hasRepetition', event.target.checked)
                                }
                                name="onOff"
                            />
                        </Grid>
                        <Grid item>
                            <Typography>{getString('Form_button_yes')}</Typography>
                        </Grid>
                    </Grid>
                }
            />

            {dataState.hasRepetition && (
                <FormSection
                    addPaddingTop
                    prompt={getString(
                        !!activity ? 'Form_add_activity_repetition_days_label' : 'Form_add_activity_repetition_days',
                    )}
                    content={
                        <FormGroup row>
                            {daysOfWeekValues.map((day) => {
                                return (
                                    <FormControlLabel
                                        key={day}
                                        control={
                                            <Checkbox
                                                checked={dataState.repeatDayFlags?.[day]}
                                                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                                    handleRepeatChange((e.target as HTMLInputElement).checked, day)
                                                }
                                                value={day}
                                            />
                                        }
                                        label={day}
                                    />
                                );
                            })}
                        </FormGroup>
                    }
                />
            )}
        </Stack>
    );

    // {
    //     content: schedulePage,
    //     canGoNext: true,
    //     // TODO Activity Refactor
    //     // activity?.startDateTime
    //     //     ? compareAsc(clearTime(activity?.startDateTime), clearTime(dataState.startDateTime)) <= 0
    //     //     : compareAsc(clearTime(new Date()), clearTime(dataState.startDateTime)) <= 0,
    // },
    // {
    //     content: repetitionPage,
    //     canGoNext: true,
    //     // TODO Activity Refactor
    //     // !dataState.hasRepetition ||
    //     // (dataState.repeatDayFlags && Object.values(dataState.repeatDayFlags).filter((v) => v).length > 0),
    // },

    */ }

    const pages = [
        {
            content: activityPage,
            canGoNext: true,
            // TODO Activity Refactor
            // !!dataState.name && !!dataState.value && !!dataState.lifeareaId,
        },
    ];

    return (
        <FormDialog
            title={
                !!dataState.activityId ? getString('Form_edit_activity_title') : getString('Form_add_activity_title')
            }
            isOpen={true}
            canClose={false}
            loading={patientStore.loadActivitiesState.pending}
            pages={pages}
            onSubmit={handleSubmit}
            submitToast={getString('Form_add_activity_submit_success')}></FormDialog>
    );
});

export default AddEditActivityForm;
