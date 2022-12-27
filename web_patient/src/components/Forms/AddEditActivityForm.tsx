import {
    DatePicker,
    TimePicker,
} from '@mui/lab';
import {
    Checkbox,
    // Chip,
    // Dialog,
    // DialogContent,
    // DialogTitle,
    FormControlLabel,
    FormGroup,
    Grid,
    // InputLabel,
    // List,
    // ListItem,
    // ListItemText,
    // ListSubheader,
    MenuItem,
    Select,
    SelectChangeEvent,
    Stack,
    Switch,
    TextField,
    Typography,
} from '@mui/material';
// import { compareAsc } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import {DayOfWeek, DayOfWeekFlags, daysOfWeekValues} from 'shared/enums';
import {clearTime, toUTCDateOnly} from 'shared/time';
import { IActivity, IActivitySchedule /* IValue, ILifeAreaValue, KeyedMap */ } from 'shared/types';
import { IFormPage, FormDialog } from 'src/components/Forms/FormDialog';
import { FormSection, HelperText, SubHeaderText} from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getRouteParameter, Parameters, ParameterValues } from "src/services/routes";
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import {
    getDayOfWeek,
    // minDate,
} from 'shared/time';

export interface IAddEditActivityFormProps extends IFormProps {}

export const AddEditActivityForm: FunctionComponent<IAddEditActivityFormProps> = observer(() => {
    const routeParamForm = getRouteParameter(Parameters.form) as string;
    const routeParamAddSchedule = getRouteParameter(Parameters.addSchedule) == ParameterValues.addSchedule.true;

    const rootStore = useStores();
    const { patientStore, appContentConfig } = rootStore;
    // const { valuesInventory } = patientStore;
    const { lifeAreas } = appContentConfig;

    //
    // View state related to creating or editing an Activity
    //

    interface IActivityViewStateModeNone {
        mode: 'none';
    }
    interface IActivityViewStateModeAdd {
        mode: 'addActivity';
        valueId?: string;
    }
    interface IActivityViewStateModeEdit {
        mode: 'editActivity';
        editActivity: IActivity;
    }
    type IActivityViewModeState = IActivityViewStateModeNone | IActivityViewStateModeAdd | IActivityViewStateModeEdit;

    interface IActivityViewState {
        displayedName: string;

        name: string;
        lifeAreaId: string;
        valueId: string;
        enjoyment: number;
        importance: number;

        modeState: IActivityViewModeState;
    }

    const initialActivityViewState: IActivityViewState = ((): IActivityViewState => {
        const defaultViewState: IActivityViewState = {
            displayedName: '',

            name: '',
            lifeAreaId: '',
            valueId: '',
            enjoyment: -1,
            importance: -1,

            modeState: {
                mode: 'none',
            },
        };

        if (routeParamForm == ParameterValues.form.addActivity) {
            const routeValueId = getRouteParameter(Parameters.valueId);
            const valueIdAndLifeAreaId = (() => {
                if (!routeValueId) {
                    return {};
                }

                const value = patientStore.getValueById(routeValueId);
                console.assert(!!value, 'addActivity value not found');
                if (!value) {
                    return {};
                }

                return {
                    valueId: routeValueId,
                    lifeAreaId: value.lifeAreaId,
                }
            })();

            if(!valueIdAndLifeAreaId.valueId) {
                return defaultViewState;
            } else {
                return {
                    ...defaultViewState,

                    ...valueIdAndLifeAreaId,

                    modeState: {
                        mode: 'addActivity',
                        valueId: valueIdAndLifeAreaId.valueId,
                    },
                };
            }
        } else if (routeParamForm == ParameterValues.form.editActivity) {
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

                const value = patientStore.getValueById(editActivity.valueId);
                console.assert(!!value, 'editActivity value not found');
                if (!value) {
                    return {};
                }

                return {
                    valueId: editActivity.valueId,
                    lifeAreaId: value.lifeAreaId,
                }
            })();

            return {
                ...defaultViewState,

                displayedName: editActivity.name,

                name: editActivity.name,
                ...valueIdAndLifeAreaId,
                enjoyment: editActivity.enjoyment ? editActivity.enjoyment : defaultViewState.enjoyment,
                importance: editActivity.importance ? editActivity.importance : defaultViewState.importance,

                modeState: {
                    mode: 'editActivity',
                    editActivity: {
                        ...editActivity
                    }
                },
            };
        }

        return defaultViewState;
    })();

    const activityViewState = useLocalObservable<IActivityViewState>(() => initialActivityViewState);

    //
    // View state related to creating or editing an ActivitySchedule
    //

    interface IActivityScheduleViewStateModeNone {
        mode: 'none';
    }
    interface IActivityScheduleViewStateModeAdd {
        mode: 'addActivitySchedule';
        activityId: string;
    }
    interface IActivityScheduleViewStateModeEdit {
        mode: 'editActivitySchedule';
        editActivitySchedule: IActivitySchedule;
    }
    type IActivityScheduleViewModeState = IActivityScheduleViewStateModeNone | IActivityScheduleViewStateModeAdd | IActivityScheduleViewStateModeEdit;

    interface IActivityScheduleViewState {
        minValidDate: Date;

        displayedDate: Date | null;
        displayedTimeOfDay: Date | null;

        date: Date;
        timeOfDay: number;
        hasRepetition: boolean;
        repeatDayFlags: DayOfWeekFlags;

        modeState: IActivityScheduleViewModeState;
    }

    const initialActivityScheduleViewState: IActivityScheduleViewState = ((): IActivityScheduleViewState => {
        const _defaultDate = clearTime(new Date());
        const _defaultTimeOfDay = 9;
        const defaultViewState: IActivityScheduleViewState = {
            displayedDate: _defaultDate,
            minValidDate: clearTime(new Date()),
            displayedTimeOfDay: new Date(1, 1, 1, _defaultTimeOfDay, 0, 0),

            date: _defaultDate,
            timeOfDay: _defaultTimeOfDay,

            hasRepetition: false,
            repeatDayFlags: Object.assign(
                {},
                ...daysOfWeekValues.map((dayOfWeek: DayOfWeek) => ({
                    [dayOfWeek]: false,
                })),
            ),

            modeState: {
                mode: 'none',
            },
        };

        // ActivityScheduling can also be accessed when routeParamForm is ParameterValues.form.addActivity.
        // In that case, the viewState is updated after the activity is created.
        if (routeParamForm == ParameterValues.form.addActivitySchedule) {
            const routeActivityId = getRouteParameter(Parameters.activityId);
            console.assert(!!routeActivityId, 'editActivity parameter activityId not found');
            if (!routeActivityId) {
                return defaultViewState;
            }

            return {
                ...defaultViewState,
                modeState: {
                    mode: 'addActivitySchedule',
                    activityId: routeActivityId,
                }
            }
        } else if (routeParamForm == ParameterValues.form.editActivitySchedule) {
            // TODO Activity Refactor
        }

        return defaultViewState;
    })();

    const activityScheduleViewState = useLocalObservable<IActivityScheduleViewState>(() => initialActivityScheduleViewState);

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

    const handleSubmitActivity = action(async () => {
        try {
            if (activityViewState.modeState.mode == 'addActivity') {
                // TODO Activity Refactor: check that our 'add' is valid
                // is not an empty name
                // is a unique name

                // Construct the activity that will be created
                const createActivity: IActivity = {
                    name: activityViewState.name,
                    enjoyment: activityViewState.enjoyment >= 0 ? activityViewState.enjoyment : undefined,
                    importance: activityViewState.importance >= 0 ? activityViewState.importance : undefined,
                    valueId: activityViewState.valueId ? activityViewState.valueId : undefined,

                    editedDateTime: new Date(),
                };

                // Create the activity
                const createdActivity = await patientStore.addActivity(createActivity);

                // Use the created activity to initiate creation of a schedule
                if (createdActivity?.activityId) {
                    activityScheduleViewState.modeState = {
                        mode: "addActivitySchedule",
                        activityId: createdActivity.activityId,
                    }
                }
            } else if (activityViewState.modeState.mode == 'editActivity') {
                // TODO Activity Refactor: check that our 'edit' is valid
                // is not an empty name
                // the value still exists
                // - update should fail due to rev conflict if it does not?
                // - what does the client actually do?
                // is a unique name
                // the value changed?

                const editActivity: IActivity = {
                    ...activityViewState.modeState.editActivity,

                    name: activityViewState.name,
                    enjoyment: activityViewState.enjoyment >= 0 ? activityViewState.enjoyment : undefined,
                    importance: activityViewState.importance >= 0 ? activityViewState.importance : undefined,
                    valueId: activityViewState.valueId ? activityViewState.valueId : undefined,

                    editedDateTime: new Date(),
                }

                await patientStore.updateActivity(editActivity);
            }

            return !patientStore.loadActivitiesState.error;
        } catch {
            return false;
        }
    });

    const handleSubmitActivitySchedule = action(async () => {
        try {
            if (activityScheduleViewState.modeState.mode == 'addActivitySchedule') {
                // TODO Activity Refactor: check that our 'add' is valid

                const createActivitySchedule: IActivitySchedule = {
                    activityId: activityScheduleViewState.modeState.activityId,
                    date: toUTCDateOnly(activityScheduleViewState.date),
                    timeOfDay: activityScheduleViewState.timeOfDay,

                    hasRepetition: activityScheduleViewState.hasRepetition,
                    repeatDayFlags: activityScheduleViewState.hasRepetition ? activityScheduleViewState.repeatDayFlags : undefined,

                    // TODO Future Support for Reminders
                    hasReminder: false,

                    editedDateTime: new Date(),
                };

                await patientStore.addActivitySchedule(createActivitySchedule);
            } else if (activityScheduleViewState.modeState.mode == 'editActivitySchedule') {
                // TODO Activity Refactor: check that our 'edit' is valid

                const editActivitySchedule: IActivitySchedule = {
                    ...activityScheduleViewState.modeState.editActivitySchedule,

                    date: toUTCDateOnly(activityScheduleViewState.date),
                    timeOfDay: activityScheduleViewState.timeOfDay,

                    hasRepetition: activityScheduleViewState.hasRepetition,
                    repeatDayFlags: activityScheduleViewState.hasRepetition ? activityScheduleViewState.repeatDayFlags : undefined,

                    editedDateTime: new Date(),
                }

                await patientStore.updateActivitySchedule(editActivitySchedule);
            }

            return !patientStore.loadActivitySchedulesState.error;
        } catch {
            return false;
        }
    });

    /*
    // TODO Activity Refactor: Create and Select Value During Activity Editing
    const handleAddValueOpen = action(() => {
    });
    */

    const handleActivityChangeName = action((event: React.ChangeEvent<HTMLInputElement>) => {
        // DisplayedName can only trimStart because full trim means never being able to add a space
        activityViewState.displayedName = event.target.value.trimStart();

        activityViewState.name = activityViewState.displayedName.trim();
    });

    const handleActivitySelectEnjoyment = action((event: SelectChangeEvent<number>) => {
        activityViewState.enjoyment = Number(event.target.value);
    });

    const handleActivitySelectImportance = action((event: SelectChangeEvent<number>) => {
        activityViewState.importance = Number(event.target.value);
    });

    const handleActivitySelectLifeArea = action((event: SelectChangeEvent<string>) => {
        activityViewState.lifeAreaId = event.target.value as string;
        activityViewState.valueId = '';
    });

    const handleActivitySelectValue = action((event: SelectChangeEvent<string>) => {
        activityViewState.valueId = event.target.value as string;
    });

    const handleActivityScheduleChangeDate = action((date: Date | null) => {
        activityScheduleViewState.displayedDate = date;

        if (activityScheduleValidateDate(date).valid) {
            activityScheduleViewState.date = date as Date;
        }
    });

    const handleActivityScheduleChangeTimeOfDay = action((date: Date | null) => {
        activityScheduleViewState.displayedTimeOfDay = date;

        if (activityScheduleValidateTimeOfDay(date).valid) {
            activityScheduleViewState.timeOfDay = (date as Date).getHours();
        }
    });

    const handleActivityScheduleChangeHasRepetition = action((event: React.ChangeEvent<HTMLInputElement>) => {
        activityScheduleViewState.hasRepetition = event.target.checked;

        // Clear all flags back to false
        Object.assign(
            activityScheduleViewState.repeatDayFlags,
            ...daysOfWeekValues.map((dayOfWeek: DayOfWeek) => ({
                [dayOfWeek]: false,
            })),
        )

        // If we just enabled repetition, default to the day of week from the scheduled date
        if (activityScheduleViewState.hasRepetition) {
            activityScheduleViewState.repeatDayFlags[getDayOfWeek(activityScheduleViewState.date)] = true;
        }
    });

    const handleActivityScheduleChangeRepeatDays = action((event: React.ChangeEvent<HTMLInputElement>, dayOfWeek: DayOfWeek) => {
        activityScheduleViewState.repeatDayFlags[dayOfWeek] = event.target.checked;
    });

    const activityValidateNext = () => {
        // Name cannot be blank
        if (!activityViewState.name) {
            return {
                valid: false,
                error: true,
            };
        }

        // Name must validate
        const validateName = activityValidateName(activityViewState.name);
        if (validateName.error) {
            return validateName;
        }

        return {
            valid: true,
            error: false,
        }
    }

    const activityValidateName = (name: string) => {
        // Name must be unique, accounting for case-insensitive comparisons
        const nameIsUnique = patientStore.activities.filter((activity: IActivity): boolean => {
            // In case of edit, do not validate against the activity being edited
            if (activityViewState.modeState.mode == 'editActivity') {
                return activity.activityId != activityViewState.modeState.editActivity.activityId;
            }

            return true;
        }).findIndex((activity: IActivity): boolean => {
            // Search for a case-insensitive match
            return activity.name.toLocaleLowerCase() == name.toLocaleLowerCase();
        }) < 0;
        if(!nameIsUnique) {
            return {
                valid: false,
                error: true,
                errorMessage: getString('form_add_edit_activity_name_validation_not_unique'),
            };
        }

        return {
            valid: true,
            error: false,
        };
    }

    const activityScheduleValidateDate = (date: Date | null) => {
        if (!date || date.toString() == "Invalid Date") {
            return {
                valid: false,
                error: true,
                errorMessage: getString('form_add_edit_activity_schedule_date_validation_invalid_format'),
            };
        }

        if (date < activityScheduleViewState.minValidDate) {
            return {
                valid: false,
                error: true,
                errorMessage: "Date must be on or after " +
                    activityScheduleViewState.minValidDate.toLocaleDateString() +
                    ".",
            };
        }

        return {
            valid: true,
            error: false,
        };
    }

    const activityScheduleValidateTimeOfDay = (date: Date | null) => {
        if (!date || date.toString() == "Invalid Date") {
            return {
                valid: false,
                error: true,
                errorMessage: getString('form_add_edit_activity_schedule_time_of_day_validation_invalid_format'),
            };
        }

        return {
            valid: true,
            error: false,
        };
    }

    /* TODO Activity Refactor: Abandoned Activity Import Code
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
    */

    // Validate name, not displayed name, because we want to ignore whitespace that will be trimmed
    const _activityPageValidateName = activityValidateName(activityViewState.name);
    const _hideLifeAreaAndValue = (
        activityViewState.modeState.mode == "addActivity" &&
        !!activityViewState.modeState.valueId
    );
    const activityPage = (
        <Stack spacing={4}>
            <FormSection
                prompt={getString('form_add_edit_activity_name_prompt')}
                help={getString('form_add_edit_activity_name_help')}
                content={
                    <Fragment>
                        <TextField
                            fullWidth
                            value={activityViewState.displayedName}
                            onChange={handleActivityChangeName}
                            variant="outlined"
                            multiline
                            error={_activityPageValidateName.error}
                            helperText={
                                _activityPageValidateName.error &&
                                _activityPageValidateName.errorMessage
                            }
                        />
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
                        value={activityViewState.enjoyment}
                        onChange={handleActivitySelectEnjoyment}
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
                        value={activityViewState.importance}
                        onChange={handleActivitySelectImportance}
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

            {(!_hideLifeAreaAndValue && <FormSection
                addPaddingTop
                prompt={getString('form_add_edit_activity_life_area_value_prompt')}
                help={getString('form_add_edit_activity_life_area_value_help')}
                content={
                    <Fragment>
                        <SubHeaderText>{getString('form_add_edit_activity_life_area_label')}</SubHeaderText>
                        <HelperText>{getString('form_add_edit_activity_life_area_help')}</HelperText>
                        <Select
                            variant="outlined"
                            value={activityViewState.lifeAreaId}
                            onChange={handleActivitySelectLifeArea}
                            fullWidth
                        >
                            <MenuItem key='' value=''></MenuItem>
                            // TODO Activity Refactor: Sort life areas
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
                            value={activityViewState.valueId}
                            onChange={handleActivitySelectValue}
                            fullWidth
                            disabled={!activityViewState.lifeAreaId}
                            // TODO Activity Refactor: Validate
                        >
                            <MenuItem key='' value=''></MenuItem>
                            // TODO Activity Refactor: Sort values
                            {activityViewState.lifeAreaId && (
                                patientStore.getValuesByLifeAreaId(activityViewState.lifeAreaId).map((value, idx) => (
                                    <MenuItem key={idx} value={value.valueId}>
                                        {value.name}
                                    </MenuItem>
                                ))
                            )}
                        </Select>
                        {/*
                        TODO Activity Refactor: Support Creation of a New Value
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
                        */}
                    </Fragment>
                }
            />)}
        </Stack>
    );

    const _activitySchedulePageValidateDate = activityScheduleValidateDate(activityScheduleViewState.displayedDate);
    const _activitySchedulePageValidateTimeOfDay = activityScheduleValidateTimeOfDay(activityScheduleViewState.displayedTimeOfDay);
    const activitySchedulePage = (
        <Stack spacing={4}>
            <FormSection
                prompt={getString('form_add_edit_activity_schedule_when_prompt')}
                content={
                    <Fragment>
                        <SubHeaderText>{getString('form_add_edit_activity_schedule_date_label')}</SubHeaderText>
                        <HelperText>{getString('form_add_edit_activity_schedule_date_help')}</HelperText>
                        <DatePicker
                            value={activityScheduleViewState.date}
                            onChange={handleActivityScheduleChangeDate}
                            minDate={activityScheduleViewState.minValidDate}
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
                                    error={_activitySchedulePageValidateDate.error}
                                    helperText={
                                        _activitySchedulePageValidateDate.error &&
                                        _activitySchedulePageValidateDate.errorMessage
                                    }
                                />
                            )}
                        />
                        <SubHeaderText>{getString('form_add_edit_activity_schedule_time_of_day_label')}</SubHeaderText>
                        <HelperText>{getString('form_add_edit_activity_schedule_time_of_day_help')}</HelperText>
                        <TimePicker
                            value={new Date(1, 1, 1, activityScheduleViewState.timeOfDay, 0, 0)}
                            onChange={handleActivityScheduleChangeTimeOfDay}
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
                                    error={_activitySchedulePageValidateTimeOfDay.error}
                                    helperText={
                                        _activitySchedulePageValidateTimeOfDay.error &&
                                        _activitySchedulePageValidateTimeOfDay.errorMessage
                                    }
                                />
                            )}
                            ampm={true}
                            views={['hours']}
                        />
                    </Fragment>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString("form_add_edit_activity_schedule_has_repetition_prompt")}
                content={
                    <Grid container alignItems="center" spacing={1} justifyContent="flex-start">
                        <Grid item>
                            <Typography>{getString('Form_button_no')}</Typography>
                        </Grid>
                        <Grid item>
                            <Switch
                                checked={activityScheduleViewState.hasRepetition}
                                color="default"
                                onChange={handleActivityScheduleChangeHasRepetition}
                                name="onOff"
                            />
                        </Grid>
                        <Grid item>
                            <Typography>{getString('Form_button_yes')}</Typography>
                        </Grid>
                    </Grid>
                }
            />

            {activityScheduleViewState.hasRepetition && (
                <FormSection
                    addPaddingTop
                    prompt={getString('form_add_edit_activity_schedule_repeat_days_prompt')}
                    content={
                        <FormGroup>
                            {daysOfWeekValues.map((dayOfWeek) => {
                                return (
                                    <FormControlLabel
                                        key={dayOfWeek}
                                        control={
                                            <Checkbox
                                                checked={activityScheduleViewState.repeatDayFlags[dayOfWeek]}
                                                onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                                                    handleActivityScheduleChangeRepeatDays(event, dayOfWeek)
                                                }
                                                value={dayOfWeek}
                                            />
                                        }
                                        label={dayOfWeek}
                                    />
                                );
                            })}
                        </FormGroup>
                    }
                />
            )}
        </Stack>
    );

    { /* TODO Activity Refactor: Abandoned Schedule and Notification Code
    const reminderPage = (
        <Stack spacing={4}>
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

    const pages: IFormPage[] = [];
    if (
        (routeParamForm == ParameterValues.form.addActivity) ||
        (routeParamForm == ParameterValues.form.editActivity)
    ) {
        pages.push({
            content: activityPage,
            title: (() => {
                if (activityViewState.modeState.mode == "addActivity") {
                    return getString("form_add_activity_title");
                } else if (activityViewState.modeState.mode == "editActivity") {
                    return getString("form_edit_activity_title");
                } else {
                    return undefined;
                }
            })(),
            canGoNext: activityValidateNext().valid,
            onSubmit: handleSubmitActivity,
        });
    }

    if (
        ((routeParamForm == ParameterValues.form.addActivity) && routeParamAddSchedule) ||
        (routeParamForm == ParameterValues.form.addActivitySchedule) ||
        (routeParamForm == ParameterValues.form.editActivitySchedule)
    ) {
        pages.push(
            {
                content: activitySchedulePage,
                canGoNext: true,
                onSubmit: handleSubmitActivitySchedule,
                // TODO Activity Refactor: Update for valid form submission state
            }
        );
    }

    return (
        <FormDialog
            isOpen={true}
            canClose={false}
            loading={patientStore.loadActivitiesState.pending}
            pages={pages}
            // TODO Activity Refactor
            // submitToast={getString('Form_add_activity_submit_success')}>
            submitToast={"TODO Activity Refactor"}
        />
    );
});

export default AddEditActivityForm;
