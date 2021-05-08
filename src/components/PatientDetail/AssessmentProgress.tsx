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
    TableCellProps,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    withTheme,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { compareAsc, format } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import Questionnaire from 'src/components/common/Questionnaire';
import { ClickableTableRow } from 'src/components/common/Table';
import { AssessmentData, IAssessment, IAssessmentDataPoint } from 'src/services/types';
import { usePatient } from 'src/stores/stores';
import { getAssessmentScore, getAssessmentScoreColorName } from 'src/utils/assessment';
import styled, { ThemedStyledProps } from 'styled-components';

const ColoredTabledCell = withTheme(
    styled(TableCell)((props: ThemedStyledProps<TableCellProps & { $color: string }, any>) => ({
        color: props.theme.customPalette.scoreColors[props.$color],
        fontWeight: 600,
    }))
);

export interface IAssessmentProgressProps {
    instruction?: string;
    questions: { question: string; id: string }[];
    options: { text: string; value: number }[];
    maxValue: number;
    assessment: IAssessment;
    onSaveAssessmentData?: (assessmentData: Partial<IAssessmentDataPoint>) => void;
}

export const AssessmentProgress: FunctionComponent<IAssessmentProgressProps> = observer((props) => {
    const currentPatient = usePatient();
    const { instruction, questions, options, assessment, maxValue, onSaveAssessmentData } = props;

    const state = useLocalObservable<{ open: boolean; dataId: string | undefined; data: AssessmentData; date: Date }>(
        () => ({
            open: false,
            dataId: undefined,
            data: {},
            date: new Date(),
        })
    );

    const handleClose = action(() => {
        state.open = false;
    });

    const handleAddRecord = action(() => {
        state.open = true;
        state.date = new Date();
        state.dataId = undefined;
        state.data = {};
    });

    const handleEditRecord = (data: IAssessmentDataPoint) =>
        action(() => {
            state.open = true;
            state.date = data.date;
            state.dataId = data.assessmentDataId;
            Object.assign(state.data, data.pointValues);
        });

    const onSave = action(() => {
        const { data, date, dataId } = state;
        onSaveAssessmentData &&
            onSaveAssessmentData({
                assessmentDataId: dataId,
                assessmentType: assessment.assessmentType,
                date,
                pointValues: data,
                comment: 'Submitted by CM',
            });
        state.open = false;
    });

    const onQuestionSelect = action((qid: string, value: number) => {
        state.data[qid] = value;
    });

    const onDateChange = action((date: Date) => {
        state.date = date;
    });

    const selectedValues = questions.map((q) => state.data[q.id]);
    const saveDisabled = selectedValues.findIndex((v) => v == undefined) >= 0;

    const assessmentData = (assessment?.data as IAssessmentDataPoint[])
        ?.slice()
        .sort((a, b) => compareAsc(a.date, b.date));

    const questionIds = questions.map((q) => q.id);

    return (
        <ActionPanel
            id={assessment.assessmentType.replace('-', '').replace(' ', '_').toLocaleLowerCase()}
            title={assessment.assessmentType}
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <AddIcon />, text: 'Add Record', onClick: handleAddRecord } as IActionButton]}>
            <Grid container spacing={2} alignItems="stretch">
                {!!assessmentData && assessmentData.length > 0 && (
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Date</TableCell>
                                    {questionIds.map((p) => (
                                        <TableCell key={p}>{p}</TableCell>
                                    ))}
                                    {questionIds.length > 1 ? <TableCell>Total</TableCell> : null}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {assessmentData.map((d, idx) => {
                                    const totalScore = getAssessmentScore(d.pointValues);
                                    const scoreColor = getAssessmentScoreColorName(d.assessmentType, totalScore);
                                    return (
                                        <ClickableTableRow hover key={idx} onClick={handleEditRecord(d)}>
                                            <TableCell component="th" scope="row">
                                                {format(d.date, 'MM/dd/yyyy')}
                                            </TableCell>
                                            {questionIds.map((p) => (
                                                <TableCell key={p}>{d.pointValues[p]}</TableCell>
                                            ))}
                                            {questionIds.length > 1 ? (
                                                <ColoredTabledCell $color={scoreColor}>{totalScore}</ColoredTabledCell>
                                            ) : null}
                                        </ClickableTableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
                {!!assessmentData && assessmentData.length > 0 && (
                    <Grid item xs={12}>
                        <AssessmentVis data={assessmentData} maxValue={maxValue} />
                    </Grid>
                )}
                {(!assessmentData || assessmentData.length == 0) && (
                    <Grid item xs={12}>
                        <Typography>{`There are no ${assessment.assessmentType} scores submitted for this patient`}</Typography>
                    </Grid>
                )}
            </Grid>

            <Dialog open={state.open} onClose={handleClose} fullWidth maxWidth="lg">
                <DialogTitle>{`Add a new ${assessment.assessmentType} record`}</DialogTitle>
                <DialogContent>
                    <Questionnaire
                        questions={questions}
                        options={options}
                        selectedValues={selectedValues}
                        selectedDate={state.date}
                        instruction={instruction}
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

export default AssessmentProgress;
