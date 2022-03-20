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
    Switch,
    Typography,
} from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { format, isSameDay } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { Link } from 'react-router-dom';
import { DayOfWeekFlags, daysOfWeekValues } from 'shared/enums';
import { IActivity, IScheduledActivity, KeyedMap } from 'shared/types';
import Calendar from 'src/components/CarePlan/Calendar';
import { MainPage } from 'src/components/common/MainPage';
import ScheduledListItem from 'src/components/common/ScheduledListItem';
import Section from 'src/components/common/Section';
import { getFormLink, getFormPath, Parameters, ParameterValues } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

const CompactList = withTheme(
    styled(List)((props) => ({
        marginLeft: props.theme.spacing(-2),
        marginRight: props.theme.spacing(-2),
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
    const activities = patientStore.activities.filter((a) => !a.isDeleted);
    const navigate = useNavigate();
    const viewState = useLocalObservable<{
        selectedDate: Date;
        showActivities: boolean;
        moreTargetEl: (EventTarget & HTMLElement) | undefined;
        selectedActivity: IActivity | undefined;
    }>(() => ({
        selectedDate: new Date(),
        showActivities: true,
        moreTargetEl: undefined,
        selectedActivity: undefined,
    }));

    const selectedTaskItems = taskItems.filter((t) => isSameDay(t.dueDateTime, viewState.selectedDate));
    const groupedActivities: KeyedMap<IActivity[]> = {};
    activities.forEach((activity) => {
        const lifearea = activity.lifeareaId || getString('Careplan_activities_uncategorized');
        if (!groupedActivities[lifearea]) {
            groupedActivities[lifearea] = [];
        }

        groupedActivities[lifearea].push(activity);
    });

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

    const getRepeatDateText = (days: DayOfWeekFlags) => {
        if (Object.values(days).filter((v) => v).length == daysOfWeekValues.length) {
            return 'Everyday';
        } else {
            const dayStrings = new Array<string>();

            daysOfWeekValues.forEach((day) => {
                if (days[day]) {
                    if (day == 'Monday') {
                        dayStrings.push('M');
                    }
                    if (day == 'Tuesday') {
                        dayStrings.push('Tu');
                    }
                    if (day == 'Wednesday') {
                        dayStrings.push('W');
                    }
                    if (day == 'Thursday') {
                        dayStrings.push('Tr');
                    }
                    if (day == 'Friday') {
                        dayStrings.push('F');
                    }
                    if (day == 'Saturday') {
                        dayStrings.push('Sa');
                    }
                    if (day == 'Sunday') {
                        dayStrings.push('Su');
                    }
                }
            });
            return dayStrings.join(', ');
        }
    };

    const handleMoreClick = action((activity: IActivity, event: React.MouseEvent<HTMLElement>) => {
        viewState.selectedActivity = activity;
        viewState.moreTargetEl = event.currentTarget;
    });

    const handleMoreClose = action(() => {
        viewState.selectedActivity = undefined;
        viewState.moreTargetEl = undefined;
    });

    const handleActivate = action(() => {
        if (!!viewState.selectedActivity) {
            const activityCopy = viewState.selectedActivity;
            activityCopy.isActive = !activityCopy.isActive;
            patientStore.updateActivity({
                ...activityCopy,
                repeatDayFlags: activityCopy.hasRepetition ? activityCopy.repeatDayFlags : undefined,
                reminderTimeOfDay: activityCopy.hasReminder ? activityCopy.reminderTimeOfDay : undefined,
            });
            handleMoreClose();
        }
    });

    const handleDelete = action(() => {
        if (!!viewState.selectedActivity) {
            const activityCopy = viewState.selectedActivity;
            activityCopy.isDeleted = true;
            patientStore.updateActivity({
                ...activityCopy,
                repeatDayFlags: activityCopy.hasRepetition ? activityCopy.repeatDayFlags : undefined,
                reminderTimeOfDay: activityCopy.hasReminder ? activityCopy.reminderTimeOfDay : undefined,
            });
            handleMoreClose();
        }
    });

    return (
        <MainPage
            title={getString('Navigation_careplan')}
            action={
                <Button startIcon={<AddIcon />} component={Link} to={getFormLink(ParameterValues.form.addActivity)}>
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
                <div>
                    <Menu
                        id="activity-menu"
                        anchorEl={viewState.moreTargetEl}
                        keepMounted
                        open={Boolean(viewState.moreTargetEl)}
                        onClose={handleMoreClose}>
                        <MenuItem onClick={handleActivate}>
                            {getString(
                                viewState.selectedActivity?.isActive
                                    ? 'Careplan_activity_item_deactivate'
                                    : 'Careplan_activity_item_activate',
                            )}
                        </MenuItem>
                        <MenuItem onClick={handleDelete}>{getString('Careplan_activity_item_delete')}</MenuItem>
                    </Menu>
                    {activities.length > 0 ? (
                        Object.keys(groupedActivities).map((lifeareaId) => {
                            const activities = groupedActivities[lifeareaId];
                            const lifearea =
                                lifeAreas.find((la) => la.id == lifeareaId)?.name ||
                                getString('Careplan_activities_uncategorized');
                            return (
                                <Section title={lifearea} key={lifearea}>
                                    <CompactList aria-labelledby="nested-list-subheader">
                                        {activities.map((activity, idx) => (
                                            <Fragment key={activity.activityId}>
                                                <ListItem
                                                    alignItems="flex-start"
                                                    button
                                                    component={Link}
                                                    to={getFormLink(ParameterValues.form.editActivity, {
                                                        [Parameters.activityId as string]:
                                                            activity.activityId as string,
                                                    })}>
                                                    <ListItemText
                                                        style={{ opacity: activity.isActive ? 1 : 0.5 }}
                                                        secondaryTypographyProps={{
                                                            component: 'div',
                                                        }}
                                                        primary={<Typography noWrap>{activity.name}</Typography>}
                                                        secondary={
                                                            <Fragment>
                                                                <Typography variant="body2" component="div">
                                                                    {`${getString('Careplan_activity_item_value')}: ${
                                                                        activity.value
                                                                    }`}
                                                                </Typography>
                                                                <Typography variant="body2" component="span">
                                                                    {`${getString(
                                                                        'Careplan_activity_item_start_date',
                                                                    )} ${format(activity.startDateTime, 'MM/dd/yy')}`}
                                                                </Typography>
                                                                {activity.hasRepetition && activity.repeatDayFlags && (
                                                                    <Typography variant="body2" component="span">
                                                                        {`; ${getString(
                                                                            'Careplan_activity_item_repeat',
                                                                        )} ${getRepeatDateText(
                                                                            activity.repeatDayFlags,
                                                                        )}`}
                                                                    </Typography>
                                                                )}
                                                            </Fragment>
                                                        }
                                                    />

                                                    <ListItemSecondaryAction>
                                                        <IconButton
                                                            edge="end"
                                                            aria-label="more"
                                                            onClick={(e) => handleMoreClick(activity, e)}
                                                            size="large">
                                                            <MoreVertIcon />
                                                        </IconButton>
                                                    </ListItemSecondaryAction>
                                                </ListItem>
                                                {idx < activities.length - 1 && <Divider variant="middle" />}
                                            </Fragment>
                                        ))}
                                    </CompactList>
                                </Section>
                            );
                        })
                    ) : (
                        <Section title={getString('Careplan_add_activity')}>
                            <Typography variant="body2">{getString('Careplan_no_activities')}</Typography>
                        </Section>
                    )}
                </div>
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
        </MainPage>
    );
});

export default CarePlanPage;
