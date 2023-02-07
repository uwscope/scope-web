import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import {
    Button,
    Divider,
    Grid,
    IconButton,
    List,
    ListItem,
    ListItemSecondaryAction,
    ListItemText,
    Menu,
    MenuItem,
    Stack,
    Switch,
    Typography,
} from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { format, isSameDay } from 'date-fns';
import { action, runInAction } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent, ReactNode } from 'react';
import { useNavigate } from 'react-router';
import { Link } from 'react-router-dom';
import { DayOfWeekFlags, daysOfWeekValues } from 'shared/enums';
import { IActivity, IActivitySchedule, IScheduledActivity } from 'shared/types';
import Calendar from 'src/components/CarePlan/Calendar';
import { MainPage } from 'src/components/common/MainPage';
import ScheduledListItem from 'src/components/common/ScheduledListItem';
import Section from 'src/components/common/Section';
import { getFormLink, getFormPath, Parameters, ParameterValues } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';
import { HelperText } from 'src/components/Forms/FormSection';
import { formatDateOnly, formatDayOfWeekOnly, formatTimeOfDayOnly, getDayOfWeekCount } from 'shared/time';
import { sortActivitiesByName, sortActivitySchedulesByDateAndTime } from 'shared/sorting';
import StatefulDialog from 'src/components/common/StatefulDialog';

const CompactList = withTheme(
    styled(List)((props) => ({
        marginLeft: props.theme.spacing(-2),
        marginRight: props.theme.spacing(-2),
        'li>.MuiListItemIcon-root': {
            minWidth: 36,
        },
    })),
);

const ActivityScheduleList = withTheme(
    styled(List)((props) => ({
        paddingLeft: props.theme.spacing(2),
        // marginRight: props.theme.spacing(0),
        paddingTop: props.theme.spacing(0),
        'li>.MuiListItemIcon-root': {
            minWidth: 36,
        },
    })),
);

export const CarePlanPage: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const {
        patientStore,
        appContentConfig: { lifeAreas },
    } = rootStore;
    const { taskItems } = patientStore;

    const navigate = useNavigate();
    const viewState = useLocalObservable<{
        selectedDate: Date;
        showActivities: boolean;
        deleteActivityConfirmOpen: boolean;
        moreTargetActivityEl: (EventTarget & HTMLElement) | undefined;
        selectedActivity: IActivity | undefined;
        deleteActivityScheduleConfirmOpen: boolean;
        moreTargetActivityScheduleEl: (EventTarget & HTMLElement) | undefined;
        selectedActivitySchedule: IActivitySchedule | undefined;
    }>(() => ({
        selectedDate: new Date(),
        showActivities: true,
        deleteActivityConfirmOpen: false,
        moreTargetActivityEl: undefined,
        selectedActivity: undefined,
        deleteActivityScheduleConfirmOpen: false,
        moreTargetActivityScheduleEl: undefined,
        selectedActivitySchedule: undefined,
    }));

    const selectedTaskItems = taskItems.filter((t) => isSameDay(t.dueDateTime, viewState.selectedDate));

    const handleDayClick = action((date: Date) => {
        viewState.selectedDate = date;
    });

    const handleViewToggle = action((event: React.ChangeEvent<HTMLInputElement>) => {
        viewState.showActivities = event.target.checked;
    });

    const handleTaskClick = action((item: IScheduledActivity) => () => {
        navigate(
            getFormPath(ParameterValues.form.activityLog, {
                [Parameters.activityId]: item.activityId,
                [Parameters.taskId]: item.scheduledActivityId,
            }),
        );
    });

    const getRepeatDayText = (repeatDayFlags: DayOfWeekFlags): string => {
        const repeatDayCount = getDayOfWeekCount(repeatDayFlags);

        if (repeatDayCount == 1) {
            return 'Repeat Weekly';
        } else if (repeatDayCount == 7) {
            return 'Repeat Every Day';
        } else {
            return daysOfWeekValues.reduce((accumulator, dayOfWeek) => {
                if (repeatDayFlags[dayOfWeek]) {
                    if (accumulator === '') {
                        return 'Repeat ' + formatDayOfWeekOnly(dayOfWeek);
                    } else {
                        return accumulator + ', ' + formatDayOfWeekOnly(dayOfWeek);
                    }
                } else {
                    return accumulator;
                }
            }, '');
        }
    };

    const handleActivityMoreClick = action((activity: IActivity, event: React.MouseEvent<HTMLElement>) => {
        viewState.selectedActivity = activity;
        viewState.moreTargetActivityEl = event.currentTarget;
    });

    const handleActivityMoreClose = action(() => {
        viewState.selectedActivity = undefined;
        viewState.moreTargetActivityEl = undefined;
    });

    const handleActivityEdit = action(() => {
        const activity = viewState.selectedActivity;

        // Remove the popup menu
        handleActivityMoreClose();

        navigate(
            getFormPath(ParameterValues.form.editActivity, {
                [Parameters.activityId as string]: activity?.activityId as string,
            }),
        );
    });

    const handleActivityDelete = action(() => {
        // Remove the popup menu
        // Do not reset the selectedActivity because dialog handlers need it
        viewState.moreTargetActivityEl = undefined;

        // Open delete confirmation dialog
        viewState.deleteActivityConfirmOpen = true;
    });

    const handleActivityDeleteConfirm = action(async () => {
        const activity = viewState.selectedActivity;

        if (!!activity) {
            await patientStore.deleteActivity(activity);
        }
        runInAction(() => {
            viewState.deleteActivityConfirmOpen = false;
            viewState.selectedActivity = undefined;
        });
    });

    const handleActivityDeleteCancel = action(() => {
        viewState.deleteActivityConfirmOpen = false;
        viewState.selectedActivity = undefined;
    });

    const handleActivityAddSchedule = action(() => {
        const activity = viewState.selectedActivity;

        // Remove the popup menu
        handleActivityMoreClose();

        navigate(
            getFormPath(ParameterValues.form.addActivitySchedule, {
                [Parameters.activityId as string]: activity?.activityId as string,
            }),
        );
    });

    const handleActivityScheduleMoreClick = action(
        (activitySchedule: IActivitySchedule, event: React.MouseEvent<HTMLElement>) => {
            viewState.selectedActivitySchedule = activitySchedule;
            viewState.moreTargetActivityScheduleEl = event.currentTarget;
        },
    );

    const handleActivityScheduleMoreClose = action(() => {
        viewState.selectedActivitySchedule = undefined;
        viewState.moreTargetActivityScheduleEl = undefined;
    });

    const handleActivityScheduleDelete = action(async () => {
        // Remove the popup menu
        // Do not reset the selectedActivitySchedule because dialog handlers need it
        viewState.moreTargetActivityScheduleEl = undefined;

        // Open delete confirmation dialog
        viewState.deleteActivityScheduleConfirmOpen = true;
    });

    const handleActivityScheduleDeleteConfirm = action(async () => {
        const activitySchedule = viewState.selectedActivitySchedule;

        if (!!activitySchedule) {
            await patientStore.deleteActivitySchedule(activitySchedule);
        }
        runInAction(() => {
            viewState.deleteActivityScheduleConfirmOpen = false;
            viewState.selectedActivitySchedule = undefined;
        });
    });

    const handleActivityScheduleDeleteCancel = action(() => {
        viewState.deleteActivityScheduleConfirmOpen = false;
        viewState.selectedActivitySchedule = undefined;
    });

    const handleActivityScheduleEdit = action(() => {
        const activitySchedule = viewState.selectedActivitySchedule;

        // Remove the popup menu
        handleActivityScheduleMoreClose();

        navigate(
            getFormPath(ParameterValues.form.editActivitySchedule, {
                [Parameters.activityScheduleId as string]: activitySchedule?.activityScheduleId as string,
            }),
        );
    });

    const renderActivitySchedule = (activitySchedule: IActivitySchedule): ReactNode => {
        return (
            <Stack spacing={1}>
                <HelperText>
                    {formatDateOnly(activitySchedule.date, 'EEE, MMM d') +
                        ', ' +
                        formatTimeOfDayOnly(activitySchedule.timeOfDay)}
                </HelperText>
                {activitySchedule.hasRepetition && (
                    <HelperText>{getRepeatDayText(activitySchedule.repeatDayFlags as DayOfWeekFlags)}</HelperText>
                )}
            </Stack>
        );
    };

    const renderActivitiesSection = (lifeAreaName: string, lifeAreaId: string, activities: IActivity[]): ReactNode => {
        const sortedActivities = sortActivitiesByName(activities);

        return (
            activities.length > 0 && (
                <Section title={lifeAreaName} key={lifeAreaId}>
                    <CompactList aria-labelledby="nested-list-subheader">
                        {sortedActivities.map((activity) => (
                            <Fragment key={activity.activityId}>
                                <ListItem
                                    alignItems="flex-start"
                                    button
                                    component={Link}
                                    to={getFormLink(ParameterValues.form.addActivitySchedule, {
                                        [Parameters.activityId as string]: activity?.activityId as string,
                                    })}
                                    sx={{ paddingBottom: 0 }}>
                                    <ListItemText
                                        secondaryTypographyProps={{
                                            component: 'div',
                                        }}
                                        primary={<Typography noWrap>{activity.name}</Typography>}
                                        secondary={
                                            <Fragment>
                                                {!!activity.valueId &&
                                                    patientStore.getValueById(activity.valueId)?.name}
                                            </Fragment>
                                        }
                                    />

                                    <ListItemSecondaryAction sx={{ alignItems: 'flex-start', height: '100%' }}>
                                        <IconButton
                                            edge="end"
                                            aria-label="more"
                                            onClick={(e) => handleActivityMoreClick(activity, e)}
                                            size="large">
                                            <MoreVertIcon />
                                        </IconButton>
                                    </ListItemSecondaryAction>
                                </ListItem>
                                {(() => {
                                    const sortedActivitySchedules = sortActivitySchedulesByDateAndTime(
                                        patientStore.getActivitySchedulesByActivityId(activity.activityId as string),
                                    );

                                    if (sortedActivitySchedules.length == 0) {
                                        // TODO: This really belong as part of the activity list item,
                                        //       but getting it to format correctly wasn't trivial
                                        return (
                                            <ActivityScheduleList>
                                                <ListItem
                                                    alignItems="flex-start"
                                                    button
                                                    component={Link}
                                                    to={getFormLink(ParameterValues.form.addActivitySchedule, {
                                                        [Parameters.activityId as string]:
                                                            activity?.activityId as string,
                                                    })}>
                                                    <HelperText>
                                                        {getString('careplan_activity_no_schedules')}
                                                    </HelperText>
                                                </ListItem>
                                            </ActivityScheduleList>
                                        );
                                    }

                                    return (
                                        <ActivityScheduleList>
                                            {sortedActivitySchedules.map(
                                                (activityScheduleCurrent, idxActivityScheduleCurrent) => (
                                                    <Fragment key={activityScheduleCurrent.activityScheduleId}>
                                                        <ListItem
                                                            alignItems="flex-start"
                                                            button
                                                            component={Link}
                                                            to={getFormLink(ParameterValues.form.editActivitySchedule, {
                                                                [Parameters.activityScheduleId as string]:
                                                                    activityScheduleCurrent.activityScheduleId as string,
                                                            })}>
                                                            {renderActivitySchedule(activityScheduleCurrent)}

                                                            <ListItemSecondaryAction>
                                                                <IconButton
                                                                    edge="end"
                                                                    aria-label="more"
                                                                    onClick={(e) =>
                                                                        handleActivityScheduleMoreClick(
                                                                            activityScheduleCurrent,
                                                                            e,
                                                                        )
                                                                    }
                                                                    size="large">
                                                                    <MoreVertIcon />
                                                                </IconButton>
                                                            </ListItemSecondaryAction>
                                                        </ListItem>
                                                        {idxActivityScheduleCurrent <
                                                            sortedActivitySchedules.length - 1 && (
                                                            <Divider variant="middle" />
                                                        )}
                                                    </Fragment>
                                                ),
                                            )}
                                        </ActivityScheduleList>
                                    );
                                })()}
                            </Fragment>
                        ))}
                    </CompactList>
                </Section>
            )
        );
    };

    const renderActivities = (): ReactNode => {
        return (
            <Fragment>
                <Menu
                    id="activity-menu"
                    anchorEl={viewState.moreTargetActivityEl}
                    keepMounted
                    open={Boolean(viewState.moreTargetActivityEl)}
                    onClose={handleActivityMoreClose}>
                    <MenuItem onClick={handleActivityAddSchedule}>
                        {getString('menuitem_activityschedule_add')}
                    </MenuItem>
                    <MenuItem onClick={handleActivityEdit}>{getString('menuitem_activity_edit')}</MenuItem>
                    <MenuItem onClick={handleActivityDelete}>{getString('menuitem_activity_delete')}</MenuItem>
                </Menu>
                <Menu
                    id="activityschedule-menu"
                    anchorEl={viewState.moreTargetActivityScheduleEl}
                    keepMounted
                    open={Boolean(viewState.moreTargetActivityScheduleEl)}
                    onClose={handleActivityScheduleMoreClose}>
                    <MenuItem onClick={handleActivityScheduleEdit}>
                        {getString('menuitem_activityschedule_edit')}
                    </MenuItem>
                    <MenuItem onClick={handleActivityScheduleDelete}>
                        {getString('menuitem_activityschedule_delete')}
                    </MenuItem>
                </Menu>
                {patientStore.activities.length > 0 ? (
                    <Fragment>
                        {lifeAreas.map((lifeArea) =>
                            renderActivitiesSection(
                                lifeArea.name,
                                lifeArea.id,
                                patientStore.getActivitiesByLifeAreaId(lifeArea.id),
                            ),
                        )}
                        {renderActivitiesSection(
                            getString('careplan_activities_other'),
                            'other',
                            patientStore.getActivitiesWithoutValueId(),
                        )}
                    </Fragment>
                ) : (
                    <Section title={getString('Careplan_add_activity')}>
                        <Typography variant="body2">{getString('Careplan_no_activities')}</Typography>
                    </Section>
                )}
            </Fragment>
        );
    };

    return (
        <MainPage
            title={getString('Navigation_careplan')}
            action={
                <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    startIcon={<AddIcon/>}
                    component={Link}
                    to={getFormLink(ParameterValues.form.addActivity, {
                        [Parameters.addSchedule]: ParameterValues.addSchedule.true,
                    })}
                >
                    {getString('Careplan_add_activity')}
                </Button>
            }>
            <Grid container alignItems="center" spacing={1} justifyContent="center">
                <Grid item>
                    <Typography color={viewState.showActivities ? 'textSecondary' : 'textPrimary'}>
                        {getString('Careplan_view_calendar')}
                    </Typography>
                </Grid>
                <Grid item>
                    <Switch
                        checked={viewState.showActivities}
                        color="default"
                        onChange={handleViewToggle}
                        name="onOff"
                    />
                </Grid>
                <Grid item>
                    <Typography color={viewState.showActivities ? 'textPrimary' : 'textSecondary'}>
                        {getString('Careplan_view_activity')}
                    </Typography>
                </Grid>
            </Grid>
            {viewState.showActivities ? (
                <div>{renderActivities()}</div>
            ) : (
                <div>
                    <Section>
                        <Calendar selectedDate={viewState.selectedDate} onDayClick={handleDayClick} />
                    </Section>
                    <Section title={`Plan for ${format(viewState.selectedDate, 'MM/dd/yyyy')}`}>
                        {selectedTaskItems.length > 0 ? (
                            <CompactList subheader={<li />}>
                                {selectedTaskItems.map((item, idx) => (
                                    <Fragment key={item.scheduledActivityId}>
                                        <ScheduledListItem item={item} onClick={handleTaskClick(item)} />
                                        {idx < selectedTaskItems.length - 1 && <Divider variant="middle" />}
                                    </Fragment>
                                ))}
                            </CompactList>
                        ) : (
                            <Typography variant="body2">{getString('Careplan_no_tasks')}</Typography>
                        )}
                    </Section>
                </div>
            )}
            <StatefulDialog
                open={viewState.deleteActivityConfirmOpen}
                title={getString('Form_confirm_delete_activity')}
                content={viewState.selectedActivity?.name as string}
                handleCancel={handleActivityDeleteCancel}
                handleDelete={handleActivityDeleteConfirm}
            />
            <StatefulDialog
                open={viewState.deleteActivityScheduleConfirmOpen}
                title={getString('Form_confirm_delete_activity_schedule')}
                content={''}
                handleCancel={handleActivityScheduleDeleteCancel}
                handleDelete={handleActivityScheduleDeleteConfirm}
            />
        </MainPage>
    );
});

export default CarePlanPage;
