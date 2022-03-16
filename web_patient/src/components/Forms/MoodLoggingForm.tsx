import { Slider, TextField } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { IMoodLog } from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

export interface IMoodLoggingFormProps extends IFormProps {}

const SliderContainer = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(8, 2),
    }))
);

export const MoodLoggingForm: FunctionComponent<IMoodLoggingFormProps> = observer(() => {
    const { patientStore } = useStores();

    const dataState = useLocalObservable<IMoodLog>(() => ({
        recordedDateTime: new Date(),
        mood: 5,
        comment: undefined,
    }));

    const handleMoodChange = action((_: any, newValue: number | number[]) => {
        dataState.mood = newValue as number;
    });

    const handleCommentChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        dataState.comment = event.target.value;
    });

    const getMoodLoggingPages = () => {
        return [
            {
                content: (
                    <FormSection
                        prompt={getString('Form_mood_logging_mood_prompt')}
                        help={getString('Form_mood_logging_mood_help')}
                        content={
                            <SliderContainer>
                                <Slider
                                    value={dataState.mood}
                                    getAriaValueText={(v) => v.toString()}
                                    aria-labelledby="mood-slider"
                                    valueLabelDisplay="on"
                                    step={1}
                                    marks={[
                                        {
                                            value: 0,
                                            label: getString('Form_mood_logging_mood_bad'),
                                        },
                                        {
                                            value: 5,
                                            label: getString('Form_mood_logging_mood_neutral'),
                                        },
                                        {
                                            value: 10,
                                            label: getString('Form_mood_logging_mood_good'),
                                        },
                                    ]}
                                    min={0}
                                    max={10}
                                    onChange={handleMoodChange}
                                />
                            </SliderContainer>
                        }
                    />
                ),
                canGoNext: true,
            },
            {
                content: (
                    <FormSection
                        prompt={getString('Form_mood_logging_comment_prompt')}
                        help={getString('Form_mood_logging_comment_help')}
                        content={
                            <TextField
                                fullWidth
                                value={dataState.comment}
                                onChange={handleCommentChange}
                                variant="outlined"
                                multiline
                                rows={10}
                            />
                        }
                    />
                ),
                canGoNext: true,
            },
        ];
    };

    const handleSubmit = action(async () => {
        try {
            await patientStore.saveMoodLog({ ...dataState });
            return !patientStore.loadMoodLogsState.error;
        } catch {
            return false;
        }
    });

    return (
        <FormDialog
            title={getString('Form_mood_logging_title')}
            isOpen={true}
            canClose={!dataState.mood && !dataState.comment}
            loading={patientStore.loadMoodLogsState.pending}
            pages={getMoodLoggingPages()}
            onSubmit={handleSubmit}
            submitToast={getString('Form_mood_submit_success')}
        />
    );
});

export default MoodLoggingForm;
