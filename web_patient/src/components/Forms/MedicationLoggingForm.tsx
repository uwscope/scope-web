import {
    FormControl,
    FormControlLabel,
    Radio,
    RadioGroup,
    SelectChangeEvent,
    Stack,
    TextField,
} from '@mui/material';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { IAssessmentLog } from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getRouteParameter, Parameters } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

export interface IMedicationLoggingFormProps extends IFormProps { }

interface IQuestionFormProps {
    instruction: string;
    question: string;
    questionId: string;
    value: number | undefined;
    options: { text: string; value: number }[];
    onValueChange: (newValue: number) => void;
}


const QuestionForm: FunctionComponent<IQuestionFormProps> = (props) => {
    const { instruction, question, questionId, value, options, onValueChange } = props;
    return (
        <FormSection
            prompt={instruction}
            subPrompt={question}
            content={
                <FormControl component="fieldset">
                    <RadioGroup
                        aria-label={questionId}
                        name={questionId}
                        value={value == undefined ? '' : value}
                        onChange={(_, val) => onValueChange(Number(val))}>
                        {options.map((resp, ridx) => {
                            return (
                                <FormControlLabel
                                    key={`${questionId}-${ridx}`}
                                    value={ridx}
                                    control={<Radio />}
                                    label={`${resp.text}`}
                                />
                            );
                        })}
                    </RadioGroup>
                </FormControl>
            }
        />
    );
};

export const MedicationLoggingForm: FunctionComponent<IMedicationLoggingFormProps> = observer(() => {
    const assessmentId = getRouteParameter(Parameters.assessmentId);
    const scheduleId = getRouteParameter(Parameters.taskId);

    if (!assessmentId || !scheduleId) {
        console.error(`Scheduled id or assessment id not found in query paramters: ${assessmentId} ${scheduleId}`);
        return null;
    }

    const rootStore = useStores();
    const { patientStore } = rootStore;
    const scheduledAssessment = patientStore.getScheduledAssessmentById(scheduleId);

    if (!scheduledAssessment) {
        console.error(`Scheduled assessment not found by schedule id: ${scheduleId}`);
        return null;
    }

    const assessmentContent = rootStore.getAssessmentContent(scheduledAssessment?.assessmentId);

    if (!assessmentContent) {
        return null;
    }


    const dataState = useLocalObservable<{ adherence: number | undefined, medicationQuestion: boolean, medicationNote: string | undefined }>(() => ({
        adherence: undefined,
        medicationQuestion: false,
        medicationNote: '',
    }));

    const handleAdherence = action((value: number) => {
        dataState.adherence = value as number;
    });

    const handleMedicationQuestion = action((event: SelectChangeEvent<boolean>) => {
        dataState.medicationQuestion = event.target.value == "true" ? true : false as boolean;
    });

    const handleMedicationNote = action((event: React.ChangeEvent<HTMLInputElement>) => {
        dataState.medicationNote = event.target.value;
    });

    const handleSubmit = action(async () => {
        const { scheduledAssessmentId, assessmentId } = scheduledAssessment;
        try {
            const log = {
                scheduledAssessmentId,
                assessmentId,
                patientSubmitted: true,
                recordedDateTime: new Date(),
                adherence: dataState.adherence,
                medicationQuestion: dataState.medicationQuestion,
                medicationNote: dataState.medicationQuestion ? dataState.medicationNote : undefined,
            } as IAssessmentLog;
            await patientStore.saveAssessmentLog(log);
            return !patientStore.loadAssessmentLogsState.error;
        } catch {
            return false;
        }
    });

    const getAssessmentPages = () => {
        let adherenceQuestion = assessmentContent.questions[0];
        const adherenceQuestionPage = {
            content: (
                <QuestionForm
                    {...assessmentContent}
                    question={adherenceQuestion.question}
                    questionId={adherenceQuestion.id}
                    value={dataState.adherence}
                    onValueChange={handleAdherence}
                />
            ),
            canGoNext: dataState.adherence != undefined,
        };

        const medicationQuestionPage = {
            content: (
                <Stack spacing={4}>
                    <FormSection
                        prompt={getString('Form_medication_logging_medication_question_prompt')}
                        content={
                            <FormControl>
                                <RadioGroup
                                    aria-labelledby="medication-prompt-label"
                                    value={dataState.medicationQuestion}
                                    name="medication-prompt-group"
                                    onChange={handleMedicationQuestion}
                                >
                                    <FormControlLabel value={true} control={<Radio />} label="Yes" />
                                    <FormControlLabel value={false} control={<Radio />} label="No" />
                                </RadioGroup>
                            </FormControl>
                        }
                    />
                    {dataState.medicationQuestion && (
                        <FormSection
                            prompt={getString(
                                'Form_medication_logging_medication_note_prompt'
                            )}
                            help={getString('Form_medication_logging_medication_note_subprompt')}
                            content={
                                <TextField
                                    fullWidth
                                    value={dataState.medicationNote}
                                    onChange={handleMedicationNote}
                                    variant="outlined"
                                    multiline
                                    rows={5}
                                    helperText={getString('Form_medication_logging_medication_note_subprompt_helper_text')}
                                />
                            }
                        />
                    )}
                </Stack>
            ),
            canGoNext: !dataState.medicationQuestion || (dataState.medicationNote != ''),
        };


        return [adherenceQuestionPage, medicationQuestionPage];
    };

    return (
        <FormDialog
            title={`${assessmentContent.name} ${getString('Form_assessment_checkin_title')}`}
            isOpen={true}
            canClose={true}
            loading={patientStore.loadAssessmentLogsState.pending}
            pages={getAssessmentPages()}
            onSubmit={handleSubmit}
            submitToast={getString('Form_assessment_submit_success')}
        />
    );
});

export default MedicationLoggingForm;
