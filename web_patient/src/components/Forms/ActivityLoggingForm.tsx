import { FormControl, FormControlLabel, Radio, RadioGroup, Slider, Stack, TextField } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { ActivitySuccessType, activitySuccessTypeValues } from 'shared/enums';
import { IActivityLog } from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { logError } from 'src/services/logger';
import { getRouteParameter, Parameters } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

export interface IActivityLoggingFormProps extends IFormProps {}

const SliderContainer = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(8, 2),
    })),
);

const PageSuccess: FunctionComponent<{
    activityName: string;
    successValue?: ActivitySuccessType;
    alternate?: string;
    onSuccessChange: (type: ActivitySuccessType) => void;
    onAlternateChange: (val: string) => void;
}> = (props) => {
    const { activityName, successValue, alternate, onSuccessChange, onAlternateChange } = props;

    const getSuccessString = (v: ActivitySuccessType) => {
        switch (v) {
            case 'Yes':
                return getString('Form_activity_log_success_yes');
            case 'No':
                return getString('Form_activity_log_success_no');
            case 'SomethingElse':
            default:
                return getString('Form_activity_log_success_something_else');
        }
    };

    const showAlternative = successValue == 'SomethingElse';

    return (
        <Stack spacing={4}>
            <FormSection
                prompt={getString('Form_activity_log_success_prompt')}
                subPrompt={activityName}
                content={
                    <FormControl component="fieldset">
                        <RadioGroup
                            aria-label={`${activityName}-success`}
                            name={`${activityName}-success`}
                            value={successValue == undefined ? '' : successValue}
                            onChange={(_, val) => onSuccessChange(val)}>
                            {activitySuccessTypeValues.map((v) => {
                                return (
                                    <FormControlLabel
                                        key={`${v}`}
                                        value={v}
                                        control={<Radio />}
                                        label={getSuccessString(v)}
                                    />
                                );
                            })}
                        </RadioGroup>
                    </FormControl>
                }
            />
            {showAlternative && (
                <div>
                    <FormSection
                        prompt={getString('Form_activity_log_alternative_propmpt')}
                        content={
                            <div>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={3}
                                    value={alternate}
                                    onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                                        onAlternateChange(event.target.value)
                                    }
                                    variant="outlined"
                                />
                            </div>
                        }
                    />
                </div>
            )}
        </Stack>
    );
};

const PageRating: FunctionComponent<{
    instruction: string;
    help: string;
    rating?: number;
    onRatingChange: (rating: number) => void;
}> = (props) => {
    const { instruction, help, rating, onRatingChange } = props;

    return (
        <FormSection
            prompt={instruction}
            help={help}
            content={
                <SliderContainer>
                    <Slider
                        value={rating}
                        getAriaValueText={(v) => v.toString()}
                        valueLabelDisplay="on"
                        step={1}
                        marks={[
                            {
                                value: 0,
                                label: getString('Form_activity_log_rating_low'),
                            },
                            {
                                value: 5,
                                label: getString('Form_activity_log_rating_moderate'),
                            },
                            {
                                value: 10,
                                label: getString('Form_activity_log_rating_high'),
                            },
                        ]}
                        min={0}
                        max={10}
                        onChange={(_: any, newValue: number | number[]) => onRatingChange(newValue as number)}
                    />
                </SliderContainer>
            }
        />
    );
};

export const ActivityLoggingForm: FunctionComponent<IActivityLoggingFormProps> = observer(() => {
    const activityId = getRouteParameter(Parameters.activityId);
    const taskId = getRouteParameter(Parameters.taskId);

    if (!activityId || !taskId) {
        return null;
    }

    const rootStore = useStores();
    const { patientStore } = rootStore;
    const activity = patientStore.getActivityById(activityId);
    const task = patientStore.getTaskById(taskId);

    if (!activity || !task) {
        logError('ActivityForm', `Activity or task not found: activity=${activityId}, task=${taskId}`);
        return null;
    }

    if (task.activityId != activityId) {
        logError('ActivityForm', `Activity and task mismatch: activity=${activityId}, taskSource=${task.activityId}`);
        return null;
    }

    const viewState = useLocalObservable<{ hasData: boolean }>(() => ({
        hasData: false,
    }));

    const dataState = useLocalObservable<IActivityLog>(() => ({
        activityId,
        scheduledActivityId: task.scheduledActivityId,
        alternative: '',
        comment: '',
        pleasure: 5,
        accomplishment: 5,
        activityName: activity.name,
        recordedDateTime: new Date(),
        success: '',
    }));

    const handleSubmit = action(async () => {
        try {
            // Some cleaning up of the log data based on completion state
            if (dataState.success == 'No') {
                const { pleasure, accomplishment, ...logData } = dataState;
                await patientStore.completeScheduledActivity({ ...logData });
            } else if (dataState.success == 'Yes') {
                const { alternative, ...logData } = dataState;
                await patientStore.completeScheduledActivity({ ...logData });
            } else {
                await patientStore.completeScheduledActivity({ ...dataState });
            }
            return !patientStore.loadActivityLogsState.error;
        } catch {
            return false;
        }
    });

    const handleValueChange = action((key: string, value: any) => {
        (dataState as any)[key] = value;
    });

    const getActivityLogPages = () => {
        const successPage = {
            content: (
                <PageSuccess
                    activityName={activity.name}
                    alternate={dataState.alternative}
                    successValue={dataState.success}
                    onAlternateChange={(v) => handleValueChange('alternative', v)}
                    onSuccessChange={(v) => handleValueChange('success', v)}
                />
            ),
            canGoNext: dataState.success == 'SomethingElse' ? !!dataState.alternative : dataState.success != undefined,
        };

        const pleasurePage = {
            content: (
                <PageRating
                    instruction={getString('Form_activity_log_pleasure_prompt')}
                    help={getString('Form_activity_log_pleasure_help')}
                    rating={dataState.pleasure != undefined ? dataState.pleasure : 5}
                    onRatingChange={(v) => handleValueChange('pleasure', v)}
                />
            ),
            canGoNext: dataState.pleasure != undefined,
        };

        const accomplishmentPage = {
            content: (
                <PageRating
                    instruction={getString('Form_activity_log_accomplishment_prompt')}
                    help={getString('Form_activity_log_accomplishment_help')}
                    rating={dataState.accomplishment != undefined ? dataState.accomplishment : 5}
                    onRatingChange={(v) => handleValueChange('accomplishment', v)}
                />
            ),
            canGoNext: dataState.accomplishment != undefined,
        };

        const commentPage = {
            content: (
                <FormSection
                    prompt={getString('Form_activity_log_comment_prompt')}
                    help={getString('Form_activity_log_comment_help')}
                    content={
                        <TextField
                            fullWidth
                            value={dataState.comment}
                            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                                handleValueChange('comment', event.target.value)
                            }
                            variant="outlined"
                            multiline
                            rows={10}
                        />
                    }
                />
            ),
            canGoNext: true,
        };

        const pages = [successPage];

        if (dataState.success == 'Yes' || dataState.success == 'SomethingElse') {
            pages.push(pleasurePage);
            pages.push(accomplishmentPage);
        }

        pages.push(commentPage);

        return pages;
    };

    return (
        <FormDialog
            title={getString('Form_activity_logging_title')}
            isOpen={true}
            canClose={!viewState.hasData}
            loading={patientStore.loadActivityLogsState.pending}
            pages={getActivityLogPages()}
            onSubmit={handleSubmit}
            submitToast={getString('Form_activity_log_submit_success')}
        />
    );
});

export default ActivityLoggingForm;
