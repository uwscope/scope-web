import {
    Avatar,
    Divider,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Typography,
    withTheme,
} from '@material-ui/core';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { Link, useHistory } from 'react-router-dom';
import { MainPage } from 'src/components/common/MainPage';
import ScheduledListItem from 'src/components/common/ScheduledListItem';
import Section from 'src/components/common/Section';
import { getImage } from 'src/services/images';
import { getFormLink, getFormPath, Parameters, ParameterValues, Routes } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { IAssessmentContent, IScheduledTaskItem } from 'src/services/types';
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
    const history = useHistory();
    const { todayItems, config } = rootStore.patientStore;

    const onTaskClick = action((item: IScheduledTaskItem) => () => {
        history.push(
            getFormPath(ParameterValues.form.activityLog, {
                [Parameters.activityId]: item.sourceId,
                [Parameters.taskId]: item.id,
            })
        );
    });

    const assessments =
        config.requiredAssessments &&
        (config.requiredAssessments
            .map((assessmentId) => rootStore.getAssessmentContent(assessmentId))
            .filter((c) => !!c) as IAssessmentContent[]);

    return (
        <MainPage title={getGreeting(new Date())}>
            {!!rootStore.inspirationalQuote ? (
                <Section title={getString('Home_quote_title')}>
                    <Typography variant="body2">{rootStore.inspirationalQuote}</Typography>
                </Section>
            ) : null}
            <Section title={getString('Home_things_title')}>
                <CompactList>
                    {!!config.needsInventory && (
                        <ListItem button component={Link} to={Routes.valuesInventory}>
                            <ListItemAvatar>
                                <Avatar
                                    alt={getString('Home_values_button_text')}
                                    src={getImage('Home_values_button_image')}
                                />
                            </ListItemAvatar>
                            <ListItemText primary={getString('Home_values_button_text')} />
                        </ListItem>
                    )}
                    {config.needsInventory && config.needsSafetyPlan && <Divider variant="middle" />}
                    {!!config.needsSafetyPlan && (
                        <ListItem button>
                            <ListItemAvatar>
                                <Avatar
                                    alt={getString('Home_safety_button_text')}
                                    src={getImage('Home_safety_button_image')}
                                />
                            </ListItemAvatar>
                            <ListItemText primary={getString('Home_safety_button_text')} />
                        </ListItem>
                    )}
                    {(config.needsInventory || config.needsSafetyPlan) && <Divider variant="middle" />}
                    {assessments &&
                        assessments.length > 0 &&
                        assessments.map((assessment) => (
                            <Fragment>
                                <ListItem
                                    button
                                    component={Link}
                                    to={getFormPath(ParameterValues.form.assessmentLog, {
                                        [Parameters.assessmentId]: assessment.id,
                                    })}>
                                    <ListItemAvatar>
                                        <Avatar
                                            alt={getString('Home_assessment_button_text').replace(
                                                '${assessment}',
                                                assessment.name
                                            )}
                                            src={getImage('Home_safety_button_image')}
                                        />
                                    </ListItemAvatar>
                                    <ListItemText
                                        primary={getString('Home_assessment_button_text').replace(
                                            '${assessment}',
                                            assessment.name
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
                            <Fragment>
                                <ScheduledListItem key={item.id} item={item} onClick={onTaskClick(item)} />
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
