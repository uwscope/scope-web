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
import SettingsIcon from '@material-ui/icons/Settings';
import { GridCellParams, GridColDef, GridRowParams } from '@material-ui/x-grid';
import { compareAsc, format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import { GridDropdownField } from 'src/components/common/GridField';
import Questionnaire from 'src/components/common/Questionnaire';
import { Table } from 'src/components/common/Table';
import { AssessmentFrequency, assessmentFrequencyValues, DayOfWeek, daysOfWeekValues } from 'src/services/enums';
import { getString } from 'src/services/strings';
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
    assessment: IAssessment;
    canAdd?: boolean;
    useTime?: boolean;
}

export const AssessmentProgress: FunctionComponent<IAssessmentProgressProps> = observer((props) => {
    const currentPatient = usePatient();

    const { instruction, questions, options, assessment, maxValue, canAdd, useTime } = props;

    const state = useLocalObservable<{
        openEdit: boolean;
        openConfigure: boolean;
        assessmentDataId: string | undefined;
        patientSubmitted: boolean;
        frequency: AssessmentFrequency;
        dayOfWeek: DayOfWeek;
        dataId: string | undefined;
        data: AssessmentData;
        date: Date;
        totalOnly: boolean;
        total: number;
        comment: string;
    }>(() => ({
        openEdit: false,
        openConfigure: false,
        assessmentDataId: undefined,
        patientSubmitted: false,
        frequency: 'Every 2 weeks',
        dayOfWeek: 'Monday',
        dataId: undefined,
        data: {},
        date: new Date(),
        totalOnly: false,
        total: 0,
        comment: '',
    }));

    const handleClose = action(() => {
        state.openEdit = false;
        state.openConfigure = false;
    });

    const handleAddRecord = action(() => {
        state.assessmentDataId = undefined;
        state.patientSubmitted = false;
        state.openEdit = true;
        state.date = new Date();
        state.dataId = undefined;
        state.data = {};
        state.total = 0;
        state.totalOnly = false;
        state.comment = '';
    });

    const handleConfigure = action(() => {
        state.openConfigure = true;
        state.frequency = assessment.frequency || 'None';
        state.dayOfWeek = assessment.dayOfWeek || 'Monday';
    });

    const onSaveEditRecord = action(() => {
        const { data, date, dataId, total, comment } = state;
        currentPatient.updateAssessmentRecord({
            assessmentDataId: dataId,
            assessmentType: assessment.assessmentType,
            date,
            pointValues: data,
            comment: comment,
            totalScore: total,
        });
        state.openEdit = false;
    });

    const onSaveConfigure = action(() => {
        const { frequency, dayOfWeek } = state;
        var newAssessment = { ...assessment } as Partial<IAssessment>;
        newAssessment.frequency = frequency;
        newAssessment.dayOfWeek = dayOfWeek;
        currentPatient.updateAssessment(newAssessment);
        state.openConfigure = false;
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

    const onDayOfWeekChange = action((dow: DayOfWeek) => {
        state.dayOfWeek = dow;
    });

    const onCommentChange = action((comment: string) => {
        state.comment = comment;
    });

    const selectedValues = questions.map((q) => state.data[q.id]);
    const saveDisabled = state.totalOnly
        ? state.total == undefined
        : selectedValues.findIndex((v) => v == undefined) >= 0;

    const assessmentData = (assessment.data as IAssessmentDataPoint[])?.slice();

    const questionIds = questions.map((q) => q.id);

    const tableData = assessmentData
        ?.sort((a, b) => compareDesc(a.date, b.date))
        .map((a) => {
            return {
                date: format(a.date, 'MM/dd/yyyy'),
                total: getAssessmentScore(a.pointValues) || a.totalScore,
                id: a.assessmentDataId,
                ...a.pointValues,
                comment: a.comment,
            };
        });

    const recurrence = `${assessment.frequency} on ${assessment.dayOfWeek}s` || 'Not assigned';

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
        {
            field: 'comment',
            headerName: 'Comment',
            width: 120,
        },
    ];

    const onRowClick = action((param: GridRowParams) => {
        const id = param.getValue(param.id, 'id') as string;
        const data = assessmentData.find((a) => a.assessmentDataId == id);

        if (!!data) {
            state.assessmentDataId = data.assessmentDataId;
            state.patientSubmitted = data.patientSubmitted;
            state.openEdit = true;
            state.date = data.date;
            state.dataId = data.assessmentDataId;
            Object.assign(state.data, data.pointValues);
            state.total = data.totalScore;
            state.totalOnly = !!data.totalScore;
            state.comment = data.comment;
        }
    });

    return (
        <ActionPanel
            id={assessment.assessmentType.replace('-', '').replace(' ', '_').toLocaleLowerCase()}
            title={assessment.assessmentType}
            inlineTitle={recurrence}
            loading={currentPatient?.state == 'Pending'}
            actionButtons={
                canAdd
                    ? [
                          {
                              icon: <AddIcon />,
                              text: getString('patient_progress_assessment_action_add'),
                              onClick: handleAddRecord,
                          } as IActionButton,
                          {
                              icon: <SettingsIcon />,
                              text: getString('patient_progress_assessment_action_configure'),
                              onClick: handleConfigure,
                          } as IActionButton,
                      ]
                    : [
                          {
                              icon: <SettingsIcon />,
                              text: getString('patient_progress_assessment_action_configure'),
                              onClick: handleConfigure,
                          } as IActionButton,
                      ]
            }>
            <Grid container spacing={2} alignItems="stretch">
                {assessment.assessmentType != 'Mood Logging' && !!assessmentData && assessmentData.length > 0 && (
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
                        <AssessmentVis
                            data={assessmentData?.sort((a, b) => compareAsc(a.date, b.date))}
                            maxValue={maxValue}
                            useTime={useTime}
                        />
                    </Grid>
                )}
                {(!assessmentData || assessmentData.length == 0) && (
                    <Grid item xs={12}>
                        <Typography>{`There are no ${assessment.assessmentType} scores submitted for this patient`}</Typography>
                    </Grid>
                )}
            </Grid>

            <Dialog open={state.openEdit} onClose={handleClose} fullWidth maxWidth="lg">
                <DialogTitle>
                    {state.patientSubmitted
                        ? `Patient submitted ${assessment.assessmentType} record`
                        : state.assessmentDataId
                        ? `Edit ${assessment.assessmentType} record`
                        : `Add ${assessment.assessmentType} record`}
                </DialogTitle>
                <DialogContent>
                    <Questionnaire
                        readonly={state.patientSubmitted}
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
                        comment={state.comment}
                        onCommentChange={onCommentChange}
                    />
                </DialogContent>
                {state.patientSubmitted ? (
                    <DialogActions>
                        <Button onClick={handleClose} color="primary">
                            {getString('patient_progress_assessment_dialog_close_button')}
                        </Button>
                    </DialogActions>
                ) : (
                    <DialogActions>
                        <Button onClick={handleClose} color="primary">
                            {getString('patient_progress_assessment_dialog_cancel_button')}
                        </Button>
                        <Button onClick={onSaveEditRecord} color="primary" disabled={saveDisabled}>
                            {getString('patient_progress_assessment_dialog_save_button')}
                        </Button>
                    </DialogActions>
                )}
            </Dialog>
            <Dialog open={state.openConfigure} onClose={handleClose}>
                <DialogTitle>{getString('patient_progress_assessment_dialog_configure_title')}</DialogTitle>
                <DialogContent>
                    <Grid container spacing={2} alignItems="stretch">
                        <GridDropdownField
                            editable={true}
                            label={getString('patient_progress_assessment_dialog_configure_frequency_label')}
                            value={state.frequency}
                            options={assessmentFrequencyValues}
                            xs={12}
                            sm={12}
                            onChange={(text) => onFrequencyChange(text as AssessmentFrequency)}
                        />
                        <GridDropdownField
                            editable={true}
                            label={getString('patient_progress_assessment_dialog_configure_dayofweek_label')}
                            value={state.dayOfWeek}
                            options={daysOfWeekValues}
                            xs={12}
                            sm={12}
                            onChange={(text) => onDayOfWeekChange(text as DayOfWeek)}
                        />
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        {getString('dialog_action_cancel')}
                    </Button>
                    <Button onClick={onSaveConfigure} color="primary">
                        {getString('dialog_action_save')}
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default AssessmentProgress;
