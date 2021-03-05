import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    styled,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { compareAsc, format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import Questionnaire from 'src/components/common/Questionnaire';
import { phq9ItemValues } from 'src/services/enums';
import { AssessmentData, IAssessmentDataPoint } from 'src/services/types';
import { useStores } from 'src/stores/stores';
import { getAssessmentScore } from 'src/utils/assessment';

const phqInstruction = 'Over the last 2 weeks, how often have you been bothered by any of the following problems?';
const phqQuestions = [
    { question: 'Little interest or pleasure in doing things', id: 'Interest' },
    { question: 'Feeling down, depressed, or hopeless', id: 'Feeling' },
    { question: 'Trouble falling or staying asleep, or sleeping too much', id: 'Sleep' },
    { question: 'Feeling tired or having little energy', id: 'Tired' },
    { question: 'Poor appetite or overeating', id: 'Apetite' },
    {
        question: 'Feeling bad about yourself or that you are a failure or have let yourself or your family down',
        id: 'Failure',
    },
    {
        question: 'Trouble concentrating on things, such as reading the newspaper or watching television',
        id: 'Concentrating',
    },
    {
        question:
            'Moving or speaking so slowly that other people could have noticed. Or the opposite being so figety or restless that you have been moving around a lot more than usual',
        id: 'Slowness',
    },
    { question: 'Thoughts that you would be better off dead, or of hurting yourself', id: 'Suicide' },
];
const phqOptions = [
    {
        text: 'Not at all',
        value: 0,
    },
    {
        text: 'Several days',
        value: 1,
    },
    {
        text: 'More than half the days',
        value: 2,
    },
    {
        text: 'Nearly every day',
        value: 3,
    },
];

const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

const defaultPHQ: AssessmentData = {
    Interest: undefined,
    Feeling: undefined,
    Sleep: undefined,
    Tired: undefined,
    Apetite: undefined,
    Failure: undefined,
    Concentrating: undefined,
    Slowness: undefined,
    Suicide: undefined,
};

const state = observable<{ open: boolean; dataId: string | undefined; phq: AssessmentData; date: Date }>({
    open: false,
    dataId: undefined,
    phq: defaultPHQ,
    date: new Date(),
});

export const PHQProgress: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const phqAssessment = currentPatient?.assessments.find((a) => a.assessmentType == 'PHQ-9');

    const handleClose = action(() => {
        state.open = false;
    });

    const handleAddRecord = action(() => {
        state.open = true;
        state.date = new Date();
        state.dataId = undefined;
        Object.assign(state.phq, defaultPHQ);
    });

    const handleEditRecord = (data: IAssessmentDataPoint) =>
        action(() => {
            state.open = true;
            state.date = data.date;
            state.dataId = data.assessmentDataId;
            Object.assign(state.phq, data.pointValues);
        });

    const onSave = action(() => {
        const { phq, date, dataId } = state;
        currentPatient?.updateAssessmentRecord({
            assessmentDataId: dataId,
            assessmentType: 'PHQ-9',
            date,
            pointValues: phq,
            comment: 'Submitted by CM',
        });
        state.open = false;
    });

    const onQuestionSelect = action((qid: string, value: number) => {
        state.phq[qid] = value;
    });

    const onDateChange = action((date: Date) => {
        state.date = date;
    });

    const selectedValues = phqQuestions.map((q) => state.phq[q.id]);
    const saveDisabled = selectedValues.findIndex((v) => v == undefined) >= 0;

    const phqData = (phqAssessment?.data as IAssessmentDataPoint[])?.slice().sort((a, b) => compareAsc(a.date, b.date));

    return (
        <ActionPanel
            id="phq9"
            title="PHQ-9"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <AddIcon />, text: 'Add Record', onClick: handleAddRecord } as IActionButton]}>
            <Grid container spacing={2} alignItems="stretch">
                {!!phqData && (
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Date</TableCell>
                                    <TableCell>Score</TableCell>
                                    {phq9ItemValues.map((p) => (
                                        <TableCell key={p}>{p}</TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {phqData.map((d, idx) => {
                                    return (
                                        <ClickableTableRow hover key={idx} onClick={handleEditRecord(d)}>
                                            <TableCell component="th" scope="row">
                                                {format(d.date, 'MM/dd/yyyy')}
                                            </TableCell>
                                            <TableCell>{getAssessmentScore(d.pointValues)}</TableCell>
                                            {phq9ItemValues.map((p) => (
                                                <TableCell key={p}>{d.pointValues[p]}</TableCell>
                                            ))}
                                        </ClickableTableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
                {!!phqData && phqData.length > 0 && (
                    <Grid item xs={12}>
                        <AssessmentVis data={phqData} />
                    </Grid>
                )}
                {(!phqData || phqData.length == 0) && (
                    <Grid item xs={12}>
                        <Typography>There are no PHQ-9 scores submitted for this patient</Typography>
                    </Grid>
                )}
            </Grid>

            <Dialog open={state.open} onClose={handleClose} fullWidth maxWidth="lg">
                <DialogTitle>{'Add a new PHQ-9 record'}</DialogTitle>
                <DialogContent>
                    <Questionnaire
                        questions={phqQuestions}
                        options={phqOptions}
                        selectedValues={selectedValues}
                        selectedDate={state.date}
                        instruction={phqInstruction}
                        onSelect={onQuestionSelect}
                        onDateChange={onDateChange}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={onSave} color="primary" disabled={saveDisabled}>
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default PHQProgress;
