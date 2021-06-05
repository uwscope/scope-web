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
    TableHead,
    TableRow,
    Typography,
    withTheme,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import EditIcon from '@material-ui/icons/Edit';
import { format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import { GridDropdownField } from 'src/components/common/GridField';
import Questionnaire from 'src/components/common/Questionnaire';
import { ClickableTableRow } from 'src/components/common/Table';
import { AssessmentFrequency, assessmentFrequencyValues } from 'src/services/enums';
import { AssessmentData, IAssessment, IAssessmentDataPoint } from 'src/services/types';
import { usePatient } from 'src/stores/stores';
import { getAssessmentScore, getAssessmentScoreColorName } from 'src/utils/assessment';
import styled, { ThemedStyledProps } from 'styled-components';

const CenteredTableCell = styled(TableCell)({
    minWidth: 120,
    textAlign: 'center',
});

const ColoredTabledCell = withTheme(
    styled(CenteredTableCell)((props: ThemedStyledProps<TableCellProps & { $color: string }, any>) => ({
        color: props.theme.customPalette.scoreColors[props.$color],
        fontWeight: 600,
    }))
);

const HorizontalScrollTable = styled(Table)({
    overflowX: 'auto',
    width: '100%',
    display: 'block',
});

export interface IAssessmentProgressProps {
    instruction?: string;
    questions: { question: string; id: string }[];
    options: { text: string; value: number }[];
    maxValue: number;
    assessmentType: string;
    assessment?: IAssessment;
}

export const AssessmentProgress: FunctionComponent<IAssessmentProgressProps> = observer((props) => {
    const currentPatient = usePatient();

    const { instruction, questions, options, assessmentType, assessment, maxValue } = props;

    const state = useLocalObservable<{
        openEdit: boolean;
        openFreq: boolean;
        frequency: AssessmentFrequency;
        dataId: string | undefined;
        data: AssessmentData;
        date: Date;
    }>(() => ({
        openEdit: false,
        openFreq: false,
        frequency: 'Every 2 weeks',
        dataId: undefined,
        data: {},
        date: new Date(),
    }));

    const handleClose = action(() => {
        state.openEdit = false;
        state.openFreq = false;
    });

    const handleAddRecord = action(() => {
        state.openEdit = true;
        state.date = new Date();
        state.dataId = undefined;
        state.data = {};
    });

    const handleEditRecord = (data: IAssessmentDataPoint) =>
        action(() => {
            state.openEdit = true;
            state.date = data.date;
            state.dataId = data.assessmentDataId;
            Object.assign(state.data, data.pointValues);
        });

    const handleEditFrequecy = action(() => {
        state.openFreq = true;
        state.frequency = assessment?.frequency || 'None';
    });

    const onSaveEditRecord = action(() => {
        const { data, date, dataId } = state;
        currentPatient.updateAssessmentRecord({
            assessmentDataId: dataId,
            assessmentType: assessmentType,
            date,
            pointValues: data,
            comment: 'Submitted by CM',
        });
        state.openEdit = false;
    });

    const onSaveEditFrequency = action(() => {
        const { frequency } = state;
        var newAssessment = assessment || ({ assessmentType: assessmentType } as Partial<IAssessment>);
        newAssessment.frequency = frequency;
        currentPatient.updateAssessment(newAssessment);
        state.openFreq = false;
    });

    const onQuestionSelect = action((qid: string, value: number) => {
        state.data[qid] = value;
    });

    const onDateChange = action((date: Date) => {
        state.date = date;
    });

    const onFrequencyChange = action((freq: AssessmentFrequency) => {
        state.frequency = freq;
    });

    const selectedValues = questions.map((q) => state.data[q.id]);
    const saveDisabled = selectedValues.findIndex((v) => v == undefined) >= 0;

    const assessmentData = (assessment?.data as IAssessmentDataPoint[])
        ?.slice()
        .sort((a, b) => compareDesc(a.date, b.date));

    const questionIds = questions.map((q) => q.id);

    const recurrence = assessment?.frequency || 'Not assigned';

    return (
        <ActionPanel
            id={assessmentType.replace('-', '').replace(' ', '_').toLocaleLowerCase()}
            title={`${assessmentType} (${recurrence})`}
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[
                { icon: <AddIcon />, text: 'Add Record', onClick: handleAddRecord } as IActionButton,
                { icon: <EditIcon />, text: 'Edit Frequency', onClick: handleEditFrequecy } as IActionButton,
            ]}>
            <Grid container spacing={2} alignItems="stretch">
                {assessmentType != 'Mood Logging' && !!assessmentData && assessmentData.length > 0 && (
                    <HorizontalScrollTable size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell>Date</TableCell>
                                {questionIds.length > 1 ? <CenteredTableCell>Total</CenteredTableCell> : null}
                                {questionIds.map((p) => (
                                    <CenteredTableCell key={p}>{p}</CenteredTableCell>
                                ))}
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
                                        {questionIds.length > 1 ? (
                                            <ColoredTabledCell $color={scoreColor}>{totalScore}</ColoredTabledCell>
                                        ) : null}
                                        {questionIds.map((p) => (
                                            <CenteredTableCell key={p}>{d.pointValues[p]}</CenteredTableCell>
                                        ))}
                                    </ClickableTableRow>
                                );
                            })}
                        </TableBody>
                    </HorizontalScrollTable>
                )}
                {!!assessmentData && assessmentData.length > 0 && (
                    <Grid item xs={12}>
                        <AssessmentVis data={assessmentData} maxValue={maxValue} />
                    </Grid>
                )}
                {(!assessmentData || assessmentData.length == 0) && (
                    <Grid item xs={12}>
                        <Typography>{`There are no ${assessmentType} scores submitted for this patient`}</Typography>
                    </Grid>
                )}
            </Grid>

            <Dialog open={state.openEdit} onClose={handleClose} fullWidth maxWidth="lg">
                <DialogTitle>{`Add a new ${assessmentType} record`}</DialogTitle>
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
                    <Button onClick={onSaveEditRecord} color="primary" disabled={saveDisabled}>
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
            <Dialog open={state.openFreq} onClose={handleClose}>
                <DialogTitle>Edit Assessment Frequency</DialogTitle>
                <DialogContent>
                    <Grid container spacing={2} alignItems="stretch">
                        <GridDropdownField
                            editable={true}
                            label="Assessment Frequency"
                            value={state.frequency}
                            options={assessmentFrequencyValues}
                            xs={12}
                            sm={12}
                            onChange={(text) => onFrequencyChange(text as AssessmentFrequency)}
                        />
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={onSaveEditFrequency} color="primary">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default AssessmentProgress;
