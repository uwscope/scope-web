import { Avatar, Divider, List, ListItem, ListItemAvatar, ListItemText, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { IScheduledActivity } from 'shared/types';
import { MainPage } from 'src/components/common/MainPage';
import ScheduledListItem from 'src/components/common/ScheduledListItem';
import Section from 'src/components/common/Section';
import { getImage } from 'src/services/images';
import { getFormLink, getFormPath, Parameters, ParameterValues, Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import { getGreeting } from 'src/utils/schedule';
import styled from 'styled-components';

const CompactList = withTheme(
    styled(List)((props) => ({
        marginLeft: props.theme.spacing(-2),
        marginRight: props.theme.spacing(-2),
        'li>.MuiListItemIcon-root': {
            minWidth: 36,
        },
    }))
);

export const HomePage: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const navigate = useNavigate();
    const { todayItems, config, scheduledAssessments } = rootStore.patientStore;

    const onTaskClick = action((item: IScheduledActivity) => () => {
        navigate(
            getFormPath(ParameterValues.form.activityLog, {
                [Parameters.activityId]: item.activityId,
                [Parameters.taskId]: item.scheduleId,
            })
        );
    });

    const onSafetyPlanClick = action(() => {
        navigate(Routes.resources);
        navigate(getFormPath(ParameterValues.form.safetyPlan));
    });

    const onValuesInventoryClick = action(() => {
        navigate(Routes.resources);
        navigate(`${Routes.resources}/${Routes.valuesInventory}`);
    });

    console.log(rootStore.inspirationalQuote);

    return (
        <MainPage title={getGreeting(new Date())}>
            {!!rootStore.inspirationalQuote ? (
                <Section title={getString('Home_quote_title')}>
                    <Typography variant="body2">{rootStore.inspirationalQuote}</Typography>
                </Section>
            ) : null}
            <Section title={getString('Home_things_title')}>
                <CompactList>
                    {!!config.assignedValuesInventory && (
                        <ListItem button onClick={onValuesInventoryClick}>
                            <ListItemAvatar>
                                <Avatar
                                    alt={getString('Home_values_button_text')}
                                    src={getImage('Home_values_button_image')}
                                />
                            </ListItemAvatar>
                            <ListItemText primary={getString('Home_values_button_text')} />
                        </ListItem>
                    )}
                    {config.assignedValuesInventory && config.assignedSafetyPlan && <Divider variant="middle" />}
                    {!!config.assignedSafetyPlan && (
                        <ListItem button onClick={onSafetyPlanClick}>
                            <ListItemAvatar>
                                <Avatar
                                    alt={getString('Home_safety_button_text')}
                                    src={getImage('Home_safety_button_image')}
                                />
                            </ListItemAvatar>
                            <ListItemText primary={getString('Home_safety_button_text')} />
                        </ListItem>
                    )}
                    {(config.assignedValuesInventory || config.assignedSafetyPlan) && <Divider variant="middle" />}
                    {scheduledAssessments &&
                        scheduledAssessments.length > 0 &&
                        scheduledAssessments.map((assessment) => (
                            <Fragment key={assessment.scheduleId}>
                                <ListItem
                                    button
                                    component={Link}
                                    to={getFormPath(ParameterValues.form.assessmentLog, {
                                        [Parameters.taskId]: assessment.scheduleId,
                                        [Parameters.assessmentId]: assessment.assessmentId,
                                    })}>
                                    <ListItemAvatar>
                                        <Avatar
                                            alt={getString('Home_assessment_button_text').replace(
                                                '${assessment}',
                                                assessment.assessmentName
                                            )}
                                            src={getImage('Home_safety_button_image')}
                                        />
                                    </ListItemAvatar>
                                    <ListItemText
                                        primary={getString('Home_assessment_button_text').replace(
                                            '${assessment}',
                                            assessment.assessmentName
                                        )}
                                    />
                                </ListItem>
                                <Divider variant="middle" />
                            </Fragment>
                        ))}
                    <ListItem button component={Link} to={getFormLink(ParameterValues.form.moodLog)}>
                        <ListItemAvatar>
                            <Avatar alt={getString('Home_mood_button_text')} src={getImage('Home_mood_button_image')} />
                        </ListItemAvatar>
                        <ListItemText primary={getString('Home_mood_button_text')} />
                    </ListItem>
                </CompactList>
            </Section>
            <Section title={getString('Home_plan_title')}>
                <CompactList>
                    {!!todayItems && todayItems.length > 0 ? (
                        todayItems.map((item, idx) => (
                            <Fragment key={item.scheduleId}>
                                <ScheduledListItem item={item} onClick={onTaskClick(item)} />
                                {idx < todayItems.length - 1 && <Divider variant="middle" />}
                            </Fragment>
                        ))
                    ) : (
                        <Typography variant="body2">{getString('Home_plan_done')}</Typography>
                    )}
                </CompactList>
            </Section>
        </MainPage>
    );
});

export default HomePage;
