import DateFnsUtils from '@date-io/date-fns';
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
    Switch,
    TextField,
    Typography,
    withTheme,
} from '@material-ui/core';
import { DatePicker, MuiPickersUtilsProvider, TimePicker } from '@material-ui/pickers';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getRouteParameter, Parameters } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { DayOfWeekFlags, daysOfWeekValues, IActivity, ILifeAreaValueActivity, KeyedMap } from 'src/services/types';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

export interface IAddEditActivityFormProps extends IFormProps {}

const isFlagSet = (value: DayOfWeekFlags, flag: DayOfWeekFlags) => {
    return (value & flag) == flag;
};

const getDayString = (day: DayOfWeekFlags) => {
    if (day == DayOfWeekFlags.Monday) {
        return 'Monday';
    } else if (day == DayOfWeekFlags.Tuesday) {
        return 'Tuesday';
    } else if (day == DayOfWeekFlags.Wednesday) {
        return 'Wednesday';
    } else if (day == DayOfWeekFlags.Thursday) {
        return 'Thursday';
    } else if (day == DayOfWeekFlags.Friday) {
        return 'Friday';
    } else if (day == DayOfWeekFlags.Saturday) {
        return 'Saturday';
    } else if (day == DayOfWeekFlags.Sunday) {
        return 'Sunday';
    }
    return 'Unknown';
};

const TextFieldWithBottomMargin = withTheme(
    styled(TextField)((props) => ({
        marginBottom: props.theme.spacing(1),
    }))
);

export const AddEditActivityForm: FunctionComponent<IAddEditActivityFormProps> = observer(() => {
    const rootStore = useStores();
    const { patientStore, appConfig } = rootStore;
    const { valueActivities, values } = patientStore;
    const { lifeAreas } = appConfig;

    const activityId = getRouteParameter(Parameters.activityId);

    let activity: IActivity | undefined = undefined;
    if (!!activityId) {
        activity = patientStore.getActivityById(activityId);
    }

    const viewState = useLocalObservable<{
        hasData: boolean;
        openActivityDialog: boolean;
    }>(() => ({
        hasData: false,
        openActivityDialog: false,
    }));

    const dataState = useLocalObservable<IActivity>(() => ({
        id: activityId || '',
        name: activity?.name || '',
        value: activity?.value || '',
        lifeareaId: activity?.lifeareaId || '',
        startDate: activity?.startDate || new Date(),
        timeOfDay: activity?.timeOfDay || 9,
        hasReminder: activity?.hasReminder || false,
        reminderTimeOfDay: activity?.reminderTimeOfDay || 9,
        hasRepetition: activity?.hasRepetition || false,
        repeatDayFlags: activity?.repeatDayFlags || DayOfWeekFlags.None,
        isActive: activity?.isActive || true,
    }));

    const groupedActivities: KeyedMap<ILifeAreaValueActivity[]> = {};
    valueActivities.forEach((activity) => {
        const lifearea = activity.lifeareaId;
        if (!groupedActivities[lifearea]) {
            groupedActivities[lifearea] = [];
        }

        groupedActivities[lifearea].push(activity);
    });

    const handleSubmit = action(() => {
        return patientStore.updateActivity(dataState);
    });

    const handleOpenImportActivity = action(() => {
        viewState.openActivityDialog = true;
    });

    const handleImportActivityItemClick = action((activity: ILifeAreaValueActivity | undefined) => {
        viewState.openActivityDialog = false;

        if (!!activity) {
            dataState.name = activity.name;
            dataState.value = patientStore.getValueById(activity.valueId)?.name || '';
            dataState.lifeareaId = activity.lifeareaId;
        }
    });

    const handleSelectValue = action((event: React.ChangeEvent<{ value: unknown }>) => {
        dataState.value = event.target.value as string;
    });

    const handleSelectLifearea = action((event: React.ChangeEvent<{ value: unknown }>) => {
        dataState.lifeareaId = event.target.value as string;
    });

    const handleRepeatChange = action((checked: boolean, day: DayOfWeekFlags) => {
        if (checked) {
            dataState.repeatDayFlags = dataState.repeatDayFlags | day;
        } else {
            dataState.repeatDayFlags &= ~day;
        }
    });

    const handleValueChange = action((key: string, value: any) => {
        (dataState as any)[key] = value;
    });

    const namePage = (
        <Fragment>
            <FormSection
                prompt={getString('Form_add_activity_describe_name')}
                help={getString('Form_add_activity_describe_name_help')}
                content={
                    <Fragment>
                        <TextFieldWithBottomMargin
                            fullWidth
                            value={dataState.name}
                            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                                handleValueChange('name', event.target.value)
                            }
                            variant="outlined"
                            multiline
                        />
                        {valueActivities.length > 0 && (
                            <Grid container justify="flex-end">
                                <Chip
                                    variant="outlined"
                                    color="primary"
                                    size="small"
                                    label={getString('Form_add_activity_describe_name_import_button')}
                                    onClick={handleOpenImportActivity}
                                />
                                <Dialog
                                    maxWidth="xs"
                                    open={viewState.openActivityDialog}
                                    onClose={() => handleImportActivityItemClick(undefined)}>
                                    <DialogTitle>
                                        {getString('Form_add_activity_describe_name_import_dialog_title')}
                                    </DialogTitle>

                                    <DialogContent dividers>
                                        <List disablePadding>
                                            {Object.keys(groupedActivities).map((lifearea) => (
                                                <Fragment key={lifearea}>
                                                    <ListSubheader disableGutters>{lifearea}</ListSubheader>
                                                    {groupedActivities[lifearea].map((activity) => (
                                                        <ListItem
                                                            disableGutters
                                                            button
                                                            onClick={() => handleImportActivityItemClick(activity)}
                                                            key={activity.id}>
                                                            <ListItemText primary={activity.name} />
                                                        </ListItem>
                                                    ))}
                                                </Fragment>
                                            ))}
                                        </List>
                                    </DialogContent>
                                </Dialog>
                            </Grid>
                        )}
                    </Fragment>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString('Form_add_activity_describe_value')}
                help={getString('Form_add_activity_describe_value_help')}
                content={
                    <Select variant="outlined" value={dataState.value || ''} onChange={handleSelectValue} fullWidth>
                        {values.map((value) => (
                            <MenuItem key={value.id} value={value.name}>
                                {value.name}
                            </MenuItem>
                        ))}
                    </Select>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString('Form_add_activity_describe_lifearea')}
                content={
                    <Select
                        variant="outlined"
                        value={dataState.lifeareaId || ''}
                        onChange={handleSelectLifearea}
                        fullWidth>
                        {lifeAreas.map((lifearea) => (
                            <MenuItem key={lifearea.id} value={lifearea.id}>
                                {lifearea.name}
                            </MenuItem>
                        ))}
                    </Select>
                }
            />
        </Fragment>
    );

    const editPage = (
        <Fragment>
            <FormSection
                prompt={getString('Form_add_activity_describe_name_label')}
                content={
                    <TextField
                        fullWidth
                        value={dataState.name}
                        onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                            handleValueChange('name', event.target.value)
                        }
                        variant="outlined"
                        multiline
                    />
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString('Form_add_activity_describe_value_label')}
                content={<TextField fullWidth value={dataState.value} disabled variant="outlined" multiline />}
            />

            <FormSection
                addPaddingTop
                prompt={getString('Form_add_activity_describe_lifearea_label')}
                content={
                    <TextField
                        fullWidth
                        value={lifeAreas.find((la) => la.id == dataState.lifeareaId)?.name}
                        disabled
                        variant="outlined"
                        multiline
                    />
                }
            />
        </Fragment>
    );

    const schedulePage = (
        <Fragment>
            <FormSection
                prompt={getString(!!activity ? 'Form_add_activity_date_label' : 'Form_add_activity_date')}
                content={
                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        <DatePicker
                            fullWidth
                            inputVariant="outlined"
                            format="MM/dd/yyyy"
                            margin="none"
                            value={dataState.startDate || ''}
                            onChange={(date: Date | null) => handleValueChange('startDate', date)}
                            disablePast={true}
                            InputLabelProps={{
                                shrink: true,
                            }}
                        />
                    </MuiPickersUtilsProvider>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString(!!activity ? 'Form_add_activity_time_label' : 'Form_add_activity_time')}
                content={
                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        <TimePicker
                            fullWidth
                            inputVariant="outlined"
                            format="hh:mm a"
                            margin="none"
                            value={new Date(1, 1, 1, dataState.timeOfDay, 0, 0) || new Date()}
                            onChange={(date: Date | null) => handleValueChange('timeOfDay', date?.getHours())}
                            ampm={true}
                            views={['hours']}
                            InputLabelProps={{
                                shrink: true,
                            }}
                        />
                    </MuiPickersUtilsProvider>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString(!!activity ? 'Form_add_activity_reminder_section' : 'Form_add_activity_reminder')}
                content={
                    <Grid container alignItems="center" spacing={1} justify="flex-start">
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
                        !!activity ? 'Form_add_activity_reminder_time_label' : 'Form_add_activity_reminder_time'
                    )}
                    content={
                        <MuiPickersUtilsProvider utils={DateFnsUtils}>
                            <TimePicker
                                fullWidth
                                inputVariant="outlined"
                                format="hh:mm a"
                                margin="none"
                                value={new Date(1, 1, 1, dataState.reminderTimeOfDay, 0, 0) || new Date()}
                                onChange={(date: Date | null) =>
                                    handleValueChange('reminderTimeOfDay', date?.getHours())
                                }
                                ampm={true}
                                views={['hours']}
                                InputLabelProps={{
                                    shrink: true,
                                }}
                            />
                        </MuiPickersUtilsProvider>
                    }
                />
            )}
        </Fragment>
    );

    const repetitionPage = (
        <Fragment>
            <FormSection
                prompt={getString(!!activity ? 'Form_add_activity_repetition_section' : 'Form_add_activity_repetition')}
                content={
                    <Grid container alignItems="center" spacing={1} justify="flex-start">
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
                        !!activity ? 'Form_add_activity_repetition_days_label' : 'Form_add_activity_repetition_days'
                    )}
                    content={
                        <FormGroup row>
                            {daysOfWeekValues.map((day) => {
                                return (
                                    <FormControlLabel
                                        key={day}
                                        control={
                                            <Checkbox
                                                checked={isFlagSet(dataState.repeatDayFlags, day)}
                                                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                                    handleRepeatChange((e.target as HTMLInputElement).checked, day)
                                                }
                                                value={DayOfWeekFlags.Sunday}
                                            />
                                        }
                                        label={getDayString(day)}
                                    />
                                );
                            })}
                        </FormGroup>
                    }
                />
            )}
        </Fragment>
    );

    const pages = [
        {
            content: !!activity ? editPage : namePage,
            canGoNext: !!dataState.name && !!dataState.value && !!dataState.lifeareaId,
        },
        {
            content: schedulePage,
            canGoNext: true,
        },
        {
            content: repetitionPage,
            canGoNext: !dataState.hasRepetition || dataState.repeatDayFlags != DayOfWeekFlags.None,
        },
    ];

    return (
        <FormDialog
            title={!!dataState.id ? getString('Form_edit_activity_title') : getString('Form_add_activity_title')}
            isOpen={true}
            canClose={!viewState.hasData}
            pages={pages}
            onSubmit={handleSubmit}
            submitToast={getString('Form_add_activity_submit_success')}></FormDialog>
    );
});

export default AddEditActivityForm;
