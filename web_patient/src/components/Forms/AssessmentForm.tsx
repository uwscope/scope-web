import {
    FormControl,
    FormControlLabel,
    Radio,
    RadioGroup,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    TextField,
} from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { IAssessmentLog } from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection, { HelperText } from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getRouteParameter, Parameters } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import { getAssessmentScore } from 'src/utils/assessment';
import styled from 'styled-components';

export interface IAssessmentFormProps extends IFormProps {}

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
                                    label={`${resp.text} (${resp.value})`}
                                />
                            );
                        })}
                    </RadioGroup>
                </FormControl>
            }
        />
    );
};

const TotalScoreText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.h2.fontSize,
        fontWeight: props.theme.typography.fontWeightMedium,
        padding: props.theme.spacing(4),
        paddingBottom: 0,
        textAlign: 'center',
        lineHeight: 1,
    }))
);

const AssessmentText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.body1.fontSize,
        paddingBottom: props.theme.spacing(2),
        textAlign: 'center',
        lineHeight: 1,
    }))
);

export const AssessmentForm: FunctionComponent<IAssessmentFormProps> = observer(() => {
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

    const viewState = useLocalObservable<{ hasData: boolean }>(() => ({
        hasData: false,
    }));

    const dataState = useLocalObservable<IAssessmentLog>(() => ({
        scheduledAssessmentId: scheduledAssessment.scheduledAssessmentId,
        assessmentId: assessmentContent.id,

        completed: false,

        recordedDate: new Date(),
        pointValues: {},

        comment: '',
    }));

    const handleSelect = action((qid: string, value: number) => {
        dataState.pointValues[qid] = value;
        viewState.hasData = Object.keys(dataState.pointValues).length > 0;
    });

    const handleCommentChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        dataState.comment = event.target.value;
    });

    const handleSubmit = action(async () => {
        dataState.completed = true;
        return await patientStore.saveAssessmentLog(dataState);
    });

    const getAssessmentPages = () => {
        const questionPages = assessmentContent.questions.map((q) => ({
            content: (
                <QuestionForm
                    {...assessmentContent}
                    question={q.question}
                    questionId={q.id}
                    value={dataState.pointValues[q.id]}
                    onValueChange={(val) => handleSelect(q.id, val)}
                />
            ),
            canGoNext: dataState.pointValues[q.id] != undefined,
        }));

        const total = getAssessmentScore(dataState.pointValues);
        const assessment =
            assessmentContent.interpretationTable
                .slice()
                .sort((row) => row.max)
                .find((row) => total <= row.max)?.interpretation || '';

        const scorePage = {
            content: (
                <FormSection
                    prompt={`Your total ${assessmentContent.name} score is`}
                    content={
                        <div>
                            <TotalScoreText>{`${total}`}</TotalScoreText>
                            <AssessmentText>{`(${assessment})`}</AssessmentText>
                            <HelperText>{`How to interpret the ${assessmentContent.name} score:`}</HelperText>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>{getString('Form_assessment_score_column_name')}</TableCell>
                                        <TableCell>{assessmentContent.interpretationName}</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {assessmentContent.interpretationTable.map((int, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell component="th" scope="row">
                                                {int.score}
                                            </TableCell>
                                            <TableCell>{int.interpretation}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    }
                />
            ),
            canGoNext: true,
        };

        return [
            ...questionPages,
            scorePage,
            {
                content: (
                    <FormSection
                        prompt={getString('Form_assessment_comment_prompt')}
                        help={getString('Form_assessment_comment_help')}
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

    return (
        <FormDialog
            title={`${assessmentContent.name} ${getString('Form_assessment_checkin_title')}`}
            isOpen={true}
            canClose={!viewState.hasData}
            pages={getAssessmentPages()}
            onSubmit={handleSubmit}
            submitToast={getString('Form_assessment_submit_success')}
        />
    );
});

export default AssessmentForm;
