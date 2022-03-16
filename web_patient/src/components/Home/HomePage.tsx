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
    })),
);

export const HomePage: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const navigate = useNavigate();

    const onTaskClick = action((item: IScheduledActivity) => () => {
        navigate(
            getFormPath(ParameterValues.form.activityLog, {
                [Parameters.activityId]: item.activityId,
                [Parameters.taskId]: item.scheduledActivityId,
            }),
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

    return (
        <MainPage title={getGreeting(new Date())}>
            {!!rootStore.inspirationalQuote ? (
                <Section title={getString('Home_quote_title')}>
                    <Typography variant="body2">{rootStore.inspirationalQuote}</Typography>
                </Section>
            ) : null}
            <Section title={getString('Home_things_title')}>
                <CompactList>
                    {!!rootStore.patientStore.config.assignedValuesInventory && (
                        <ListItem button onClick={onValuesInventoryClick}>
                            <ListItemAvatar>
                                <Avatar
                                    variant="square"
                                    alt={getString('Home_values_button_text')}
                                    src={getImage('Home_values_button_image')}
                                />
                            </ListItemAvatar>
                            <ListItemText primary={getString('Home_values_button_text')} />
                        </ListItem>
                    )}
                    {rootStore.patientStore.config.assignedValuesInventory &&
                        rootStore.patientStore.config.assignedSafetyPlan && <Divider variant="middle" />}
                    {!!rootStore.patientStore.config.assignedSafetyPlan && (
                        <ListItem button onClick={onSafetyPlanClick}>
                            <ListItemAvatar>
                                <Avatar
                                    variant="square"
                                    alt={getString('Home_safety_button_text')}
                                    src={getImage('Home_safety_button_image')}
                                />
                            </ListItemAvatar>
                            <ListItemText primary={getString('Home_safety_button_text')} />
                        </ListItem>
                    )}
                    {(rootStore.patientStore.config.assignedValuesInventory ||
                        rootStore.patientStore.config.assignedSafetyPlan) && <Divider variant="middle" />}
                    {rootStore.patientStore.assessmentsToComplete &&
                        rootStore.patientStore.assessmentsToComplete.length > 0 &&
                        rootStore.patientStore.assessmentsToComplete.map((assessment) => {
                            const assessmentContent = rootStore.getAssessmentContent(assessment.assessmentId);

                            return (
                                <Fragment key={assessment.scheduledAssessmentId}>
                                    <ListItem
                                        button
                                        component={Link}
                                        to={getFormPath(ParameterValues.form.assessmentLog, {
                                            [Parameters.taskId]: assessment.scheduledAssessmentId,
                                            [Parameters.assessmentId]: assessment.assessmentId,
                                        })}>
                                        <ListItemAvatar>
                                            <Avatar
                                                variant="square"
                                                alt={getString('Home_assessment_button_text').replace(
                                                    '${assessment}',
                                                    assessmentContent?.name || 'Unknown assessment',
                                                )}
                                                src={getImage('Home_safety_button_image')}
                                            />
                                        </ListItemAvatar>
                                        <ListItemText
                                            primary={getString('Home_assessment_button_text').replace(
                                                '${assessment}',
                                                assessmentContent?.name || 'Unknown assessment',
                                            )}
                                        />
                                    </ListItem>
                                    <Divider variant="middle" />
                                </Fragment>
                            );
                        })}
                    <ListItem button component={Link} to={getFormLink(ParameterValues.form.moodLog)}>
                        <ListItemAvatar>
                            <Avatar
                                variant="square"
                                alt={getString('Home_mood_button_text')}
                                src={getImage('Home_mood_button_image')}
                            />
                        </ListItemAvatar>
                        <ListItemText primary={getString('Home_mood_button_text')} />
                    </ListItem>
                </CompactList>
            </Section>
            <Section title={getString('Home_plan_title')}>
                {!!rootStore.patientStore.todayItems && rootStore.patientStore.todayItems.length > 0 ? (
                    <CompactList>
                        {rootStore.patientStore.todayItems.map((item, idx) => (
                            <Fragment key={`${item.scheduledActivityId}-${idx}`}>
                                <ScheduledListItem item={item} onClick={onTaskClick(item)} />
                                {idx < rootStore.patientStore.todayItems.length - 1 && <Divider variant="middle" />}
                            </Fragment>
                        ))}
                    </CompactList>
                ) : (
                    <Typography variant="body2">{getString('Home_plan_done')}</Typography>
                )}
            </Section>
        </MainPage>
    );
});

export default HomePage;
