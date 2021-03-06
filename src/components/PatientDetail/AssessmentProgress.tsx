import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Typography,
    withTheme,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import EditIcon from '@material-ui/icons/Edit';
import { GridCellParams, GridColDef, GridRowParams } from '@material-ui/x-grid';
import { format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import { GridDropdownField } from 'src/components/common/GridField';
import Questionnaire from 'src/components/common/Questionnaire';
import { Table } from 'src/components/common/Table';
import { AssessmentFrequency, assessmentFrequencyValues } from 'src/services/enums';
import { AssessmentData, IAssessment, IAssessmentDataPoint } from 'src/services/types';
import { usePatient } from 'src/stores/stores';
import { getAssessmentScore, getAssessmentScoreColorName } from 'src/utils/assessment';
import styled from 'styled-components';

const ScoreCell = withTheme(
    styled.div<{ score: number; assessmentType: string }>((props) => ({
        width: 'calc(100% + 16px)',
        marginLeft: -8,
        marginRight: -8,
        padding: props.theme.spacing(1),
        backgroundColor:
            props.theme.customPalette.scoreColors[getAssessmentScoreColorName(props.assessmentType, props.score)],
    }))
);

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
        totalOnly: boolean;
        total: number;
    }>(() => ({
        openEdit: false,
        openFreq: false,
        frequency: 'Every 2 weeks',
        dataId: undefined,
        data: {},
        date: new Date(),
        totalOnly: false,
        total: 0,
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
        state.total = 0;
        state.totalOnly = false;
    });

    const handleEditFrequecy = action(() => {
        state.openFreq = true;
        state.frequency = assessment?.frequency || 'None';
    });

    const onSaveEditRecord = action(() => {
        const { data, date, dataId, total } = state;
        currentPatient.updateAssessmentRecord({
            assessmentDataId: dataId,
            assessmentType: assessmentType,
            date,
            pointValues: data,
            comment: 'Submitted by CM',
            totalScore: total,
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

    const onTotalChange = action((value: number) => {
        state.total = value;
    });

    const onToggleTotalOnly = action((value: boolean) => {
        state.totalOnly = value;
    });

    const onFrequencyChange = action((freq: AssessmentFrequency) => {
        state.frequency = freq;
    });

    const selectedValues = questions.map((q) => state.data[q.id]);
    const saveDisabled = state.totalOnly ? !state.total : selectedValues.findIndex((v) => v == undefined) >= 0;

    const assessmentData = (assessment?.data as IAssessmentDataPoint[])
        ?.slice()
        .sort((a, b) => compareDesc(a.date, b.date));

    const questionIds = questions.map((q) => q.id);

    const tableData = assessmentData?.map((a) => {
        return {
            date: format(a.date, 'MM/dd/yyyy'),
            total: getAssessmentScore(a.pointValues) || a.totalScore,
            id: a.assessmentDataId,
            ...a.pointValues,
        };
    });

    const recurrence = assessment?.frequency || 'Not assigned';

    const renderScoreCell = (props: GridCellParams) => (
        <ScoreCell score={props.value as number} assessmentType={assessment?.assessmentType}>
            {props.value}
        </ScoreCell>
    );
    const columns: GridColDef[] = [
        {
            field: 'date',
            headerName: 'Date',
            width: 100,
            sortable: true,
            hideSortIcons: false,
        },
        {
            field: 'total',
            headerName: 'Total',
            width: 80,
            renderCell: renderScoreCell,
            align: 'center',
        },
        ...questionIds.map(
            (q) =>
                ({
                    field: q,
                    headerName: q,
                    width: 80,
                    align: 'center',
                } as GridColDef)
        ),
    ];

    const onRowClick = action((param: GridRowParams) => {
        const id = param.getValue(param.id, 'id') as string;
        const data = assessmentData.find((a) => a.assessmentDataId == id);

        if (!!data) {
            state.openEdit = true;
            state.date = data.date;
            state.dataId = data.assessmentDataId;
            Object.assign(state.data, data.pointValues);
            state.total = data.totalScore;
            state.totalOnly = !!data.totalScore;
        }
    });

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
                    <Table
                        rows={tableData}
                        columns={columns.map((c) => ({
                            sortable: false,
                            filterable: false,
                            editable: false,
                            hideSortIcons: true,
                            disableColumnMenu: true,
                            ...c,
                        }))}
                        autoPageSize
                        onRowClick={onRowClick}
                        autoHeight={true}
                        isRowSelectable={(_) => false}
                    />
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
                        onTotalChange={onTotalChange}
                        onToggleTotalOnly={onToggleTotalOnly}
                        totalOnly={state.totalOnly}
                        totalScore={state.total}
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
