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
import { IActivity, KeyedMap } from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getRouteParameter, Parameters } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

export interface IAddEditActivityFormProps extends IFormProps {}

interface ImportableActivity {
    activity: string;
    value: string;
    lifeareaId: string;
}

export const AddEditActivityForm: FunctionComponent<IAddEditActivityFormProps> = observer(() => {
    const rootStore = useStores();
    const { patientStore, appContentConfig } = rootStore;
    const { valuesInventory } = patientStore;
    const { lifeAreas } = appContentConfig;

    const activityId = getRouteParameter(Parameters.activityId);

    let activity: IActivity | undefined = undefined;
    if (!!activityId) {
        activity = patientStore.getActivityById(activityId);
    }

    const viewState = useLocalObservable<{
        openActivityDialog: boolean;
    }>(() => ({
        openActivityDialog: false,
    }));

    const dataState = useLocalObservable<IActivity>(() => ({
        ...activity,
        name: activity?.name || '',
        value: activity?.value || '',
        lifeareaId: activity?.lifeareaId || '',
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
        isActive: activity?.isActive || true,
        isDeleted: activity?.isDeleted || false,
    }));

    const values = valuesInventory?.values || [];
    const groupedActivities: KeyedMap<ImportableActivity[]> = {};
    let activityCount = 0;

    values.forEach((value) => {
        const lifearea = value.lifeareaId;
        if (!groupedActivities[lifearea]) {
            groupedActivities[lifearea] = [];
        }

        value.activities.forEach((activity) => {
            groupedActivities[lifearea].push({
                activity: activity.name,
                value: value.name,
                lifeareaId: lifearea,
            });

            activityCount += groupedActivities[lifearea].length;
        });
    });

    const handleSubmit = action(async () => {
        const activity = toJS(dataState);

        try {
            if (!!activity.activityId) {
                await patientStore.updateActivity({
                    ...dataState,
                    repeatDayFlags: dataState.hasRepetition ? dataState.repeatDayFlags : undefined,
                    reminderTimeOfDay: dataState.hasReminder ? dataState.reminderTimeOfDay : undefined,
                });
            } else {
                await patientStore.addActivity({
                    ...dataState,
                    repeatDayFlags: dataState.hasRepetition ? dataState.repeatDayFlags : undefined,
                    reminderTimeOfDay: dataState.hasReminder ? dataState.reminderTimeOfDay : undefined,
                });
            }

            return !patientStore.loadActivitiesState.error;
        } catch {
            return false;
        }
    });

    const handleOpenImportActivity = action(() => {
        viewState.openActivityDialog = true;
    });

    const handleImportActivityItemClick = action((activity: ImportableActivity | undefined) => {
        viewState.openActivityDialog = false;

        if (!!activity) {
            dataState.name = activity.activity;
            dataState.value = activity.value;
            dataState.lifeareaId = activity.lifeareaId;
        }
    });

    const handleSelectValue = action((event: SelectChangeEvent<string>) => {
        dataState.value = event.target.value as string;
    });

    const handleSelectLifearea = action((event: SelectChangeEvent<string>) => {
        dataState.lifeareaId = event.target.value as string;
    });

    const handleRepeatChange = action((checked: boolean, day: DayOfWeek) => {
        if (dataState.repeatDayFlags != undefined) {
            dataState.repeatDayFlags[day] = checked;
        }
    });

    const handleValueChange = action((key: string, value: any) => {
        (dataState as any)[key] = value;
    });

    const namePage = (
        <Stack spacing={4}>
            <FormSection
                prompt={getString('Form_add_activity_describe_name')}
                help={getString('Form_add_activity_describe_name_help')}
                content={
                    <Fragment>
                        <TextField
                            fullWidth
                            value={dataState.name}
                            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                                handleValueChange('name', event.target.value)
                            }
                            variant="outlined"
                            multiline
                        />
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
                    </Fragment>
                }
            />

            <FormSection
                addPaddingTop
                prompt={getString('Form_add_activity_describe_value')}
                help={getString('Form_add_activity_describe_value_help')}
                content={
                    <Select variant="outlined" value={dataState.value || ''} onChange={handleSelectValue} fullWidth>
                        {values.map((value, idx) => (
                            <MenuItem key={idx} value={value.name}>
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
        </Stack>
    );

    const editPage = (
        <Stack spacing={4}>
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
        </Stack>
    );

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

    const pages = [
        {
            content: !!activity ? editPage : namePage,
            canGoNext: !!dataState.name && !!dataState.value && !!dataState.lifeareaId,
        },
        {
            content: schedulePage,
            canGoNext: activity?.startDateTime
                ? compareAsc(clearTime(activity?.startDateTime), clearTime(dataState.startDateTime)) <= 0
                : compareAsc(clearTime(new Date()), clearTime(dataState.startDateTime)) <= 0,
        },
        {
            content: repetitionPage,
            canGoNext:
                !dataState.hasRepetition ||
                (dataState.repeatDayFlags && Object.values(dataState.repeatDayFlags).filter((v) => v).length > 0),
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
