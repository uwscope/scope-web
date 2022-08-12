import {
    FormControl,
    FormControlLabel,
    Link,
    Radio,
    RadioGroup,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    TextField,
} from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { action, ObservableMap } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { IAssessmentLog } from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getRouteParameter, Parameters } from 'src/services/routes';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import { getAssessmentScore } from 'src/utils/assessment';
import styled from 'styled-components';

export interface IAssessmentFormProps extends IFormProps { }

interface IQuestionFormProps {
    instruction: string;
    question: string;
    questionId: string;
    value: number | undefined;
    options: { text: string; value: number }[];
    onValueChange: (newValue: number) => void;
}

const ListDiv = styled.ul({
    marginBlockStart: '0.5em',
    marginBlockEnd: '0.5em',
    paddingInlineStart: 20,
});

const TotalScoreText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.h2.fontSize,
        fontWeight: props.theme.typography.fontWeightMedium,
        padding: props.theme.spacing(4),
        paddingBottom: 0,
        textAlign: 'center',
        lineHeight: 1,
    })),
);

const BodyText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.body1.fontSize,
        lineHeight: 1.1,
    })),
);

const CrisisContent: FunctionComponent = () => {
    return (
        <FormSection
            prompt={'Crisis resources'}
            content={
                <Stack spacing={2}>
                    <BodyText>
                        You indicated that you are having thoughts of death or suicide.
                    </BodyText>
                    <BodyText>If you need more help right away, here are some resources to try:</BodyText>
                    <ListDiv>
                        <li>
                            <BodyText>
                                Suicide & Crisis Lifeline - Call {' '}
                                <Link
                                    href="tel:988/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    988
                                </Link>
                                {' '} or {' '}
                                <Link
                                    href="tel:18002738255/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    1-800-273-TALK (8255)
                                </Link>
                            </BodyText>
                        </li>
                        <li>
                            <BodyText>
                                Lifeline Web Chat - {' '}
                                <Link
                                    href="https://suicidepreventionlifeline.org/chat/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    https://suicidepreventionlifeline.org/chat/
                                </Link>
                            </BodyText>
                        </li>
                        <li>
                            <BodyText>
                                Crisis Text Line - {' '}
                                <Link
                                    href="https://www.crisistextline.org/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    https://www.crisistextline.org/
                                </Link>
                                {' '} - Text {' '}
                                <Link
                                    href="sms:988/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    988
                                </Link>
                                {' '} or Text "HOME" to {' '}
                                <Link
                                    href="sms:741741/"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    741741
                                </Link>
                            </BodyText>
                        </li>
                        <li>
                            <BodyText>
                                If you need immediate medical attention, please call{' '}
                                <Link
                                    href="tel:911"
                                    target="_blank"
                                    sx={{ display: 'inline-block', overflowWrap: 'anywhere' }}>
                                    911
                                </Link>{' '}
                                or go to your nearest emergency room.
                            </BodyText>
                        </li>
                    </ListDiv>
                </Stack>
            }
        />
    );
};

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

    const dataState = useLocalObservable<{ pointValues: ObservableMap<string, number>; comment: string }>(() => ({
        pointValues: new ObservableMap(),
        comment: '',
    }));

    const handleSelect = action((qid: string, value: number) => {
        dataState.pointValues.set(qid, value);
        viewState.hasData = Object.keys(dataState.pointValues).length > 0;
    });

    const handleCommentChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        dataState.comment = event.target.value;
    });

    const handleSubmit = action(async () => {
        const { scheduledAssessmentId, assessmentId } = scheduledAssessment;
        try {
            const log = {
                scheduledAssessmentId,
                assessmentId,
                patientSubmitted: true,
                pointValues: Object.fromEntries(dataState.pointValues.entries()),
                recordedDateTime: new Date(),
                comment: dataState.comment,
            } as IAssessmentLog;
            await patientStore.saveAssessmentLog(log);
            return !patientStore.loadAssessmentLogsState.error;
        } catch {
            return false;
        }
    });

    const getAssessmentPages = () => {
        const questionPages = assessmentContent.questions.map((q) => ({
            content: (
                <QuestionForm
                    {...assessmentContent}
                    question={q.question}
                    questionId={q.id}
                    value={dataState.pointValues.get(q.id)}
                    onValueChange={(val) => handleSelect(q.id, val)}
                />
            ),
            canGoNext: dataState.pointValues.get(q.id) != undefined,
        }));

        const total = getAssessmentScore(Object.fromEntries(dataState.pointValues.entries()));
        const assessment =
            assessmentContent.interpretationTable
                .slice()
                .sort((row) => row.max)
                .find((row) => total <= row.max)?.interpretation || '';

        const scorePage = {
            content: (
                <Stack spacing={4}>
                    <FormSection
                        prompt={`Your ${assessmentContent.name} score is`}
                        content={
                            <div>
                                <TotalScoreText>{`${total}`}</TotalScoreText>
                                <BodyText>{`${assessment}`}</BodyText>
                            </div>
                        }
                    />
                    {assessmentId == 'phq-9' && !!dataState.pointValues.get('Suicide') && <CrisisContent />}

                    <FormSection
                        prompt={`How to interpret the ${assessmentContent.name} score:`}
                        content={
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
                        }
                    />
                </Stack>
            ),
            canGoNext: true,
        };

        const commentPage = {
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
        };

        if (assessmentContent.questions.length > 1) {
            return [...questionPages, scorePage, commentPage];
        } else {
            return [...questionPages, commentPage];
        }
    };

    return (
        <FormDialog
            title={`${assessmentContent.name} ${getString('Form_assessment_checkin_title')}`}
            isOpen={true}
            canClose={!viewState.hasData}
            loading={patientStore.loadAssessmentLogsState.pending}
            pages={getAssessmentPages()}
            onSubmit={handleSubmit}
            submitToast={getString('Form_assessment_submit_success')}
        />
    );
});

export default AssessmentForm;
