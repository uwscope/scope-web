import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import Questionnaire from 'src/components/common/Questionnaire';
import { PHQ9Item, phq9ItemValues } from 'src/services/enums';
import { PHQ9Map } from 'src/services/types';
import { useStores } from 'src/stores/stores';
import { sum } from 'src/utils/array';

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

const defaultPHQ = {
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

const state = observable<{ open: boolean } & PHQ9Map>({
    open: false,
    ...defaultPHQ,
});

export const PHQProgress: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const phqAssessment = currentPatient?.assessments.find((a) => a.assessmentType == 'PHQ-9');
    const getPhqScore = (pointValues: PHQ9Map) => {
        return sum(Object.keys(pointValues).map((k) => pointValues[k as PHQ9Item] || 0));
    };

    const handleClose = action(() => {
        state.open = false;
    });

    const handleAddRecord = action(() => {
        state.open = true;
        Object.assign(state, defaultPHQ);
    });

    const onSave = action(() => {
        const { open, ...phqData } = { ...state };
        currentPatient?.addPHQ9Record(phqData);
        state.open = false;
    });

    const onQuestionSelect = action((qid: string, value: number) => {
        state[qid as PHQ9Item] = value;
    });

    const selectedValues = phqQuestions.map((q) => state[q.id as PHQ9Item]);
    const saveDisabled = selectedValues.findIndex((v) => v == undefined) >= 0;

    return (
        <ActionPanel
            id="phq9"
            title="PHQ-9"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <AddIcon />, text: 'Add Record', onClick: handleAddRecord } as IActionButton]}>
            <Grid container spacing={2} alignItems="stretch">
                {!!phqAssessment ? (
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Date</TableCell>
                                    <TableCell>Score</TableCell>
                                    {phq9ItemValues.map((p, idx) => (
                                        <TableCell key={p}>{`${idx + 1}. ${p}`}</TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {phqAssessment.data.map((d, idx) => {
                                    return (
                                        <TableRow key={idx}>
                                            <TableCell component="th" scope="row">
                                                {format(d.date, 'MM/dd/yyyy')}
                                            </TableCell>
                                            <TableCell>{getPhqScore(d.pointValues as PHQ9Map)}</TableCell>
                                            {phq9ItemValues.map((p) => (
                                                <TableCell key={p}>{(d.pointValues as PHQ9Map)[p]}</TableCell>
                                            ))}
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                ) : (
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
                        instruction={phqInstruction}
                        onSelect={onQuestionSelect}
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
