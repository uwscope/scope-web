import AddIcon from '@mui/icons-material/Add';
import AssignmentIcon from '@mui/icons-material/Assignment';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import SettingsIcon from '@mui/icons-material/Settings';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { GridCellParams, GridColDef, GridRowParams } from '@mui/x-data-grid';
import { compareAsc, format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { AssessmentFrequency, assessmentFrequencyValues, DayOfWeek, daysOfWeekValues } from 'shared/enums';
import { IAssessment, IAssessmentLog } from 'shared/types';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import { GridDropdownField } from 'src/components/common/GridField';
import Questionnaire from 'src/components/common/Questionnaire';
import StatefulDialog from 'src/components/common/StatefulDialog';
import { renderMultilineCell, Table } from 'src/components/common/Table';
import { getString } from 'src/services/strings';
import { usePatient, useStores } from 'src/stores/stores';
import { getAssessmentScoreColorName, getAssessmentScoreFromAssessmentLog } from 'src/utils/assessment';
import styled from 'styled-components';

const ScoreCell = withTheme(
    styled.div<{ score: number; assessmentId: string }>((props) => ({
        width: 'calc(100% + 16px)',
        display: 'flex',
        height: '100%',
        alignItems: 'center',
        justifyContent: 'center',
        marginLeft: -8,
        marginRight: -8,
        textAlign: 'center',
        padding: props.theme.spacing(1),
        backgroundColor:
            props.theme.customPalette.scoreColors[getAssessmentScoreColorName(props.assessmentId, props.score)],
    })),
);

const SuicideCell = withTheme(
    styled.div<{ score: number }>((props) => ({
        width: 'calc(100% + 16px)',
        display: 'flex',
        height: '100%',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: props.theme.spacing(0.5),
        border: props.score > 0 ? `2px solid ${props.theme.customPalette.flagColors['safety']}` : 'none',
    })),
);

export interface IAssessmentProgressProps {
    assessmentName: string;
    instruction?: string;
    questions: { question: string; id: string }[];
    options: { text: string; value: number }[];
    maxValue: number;
    assessment: IAssessment;
    assessmentLogs: IAssessmentLog[];
    canAdd?: boolean;
    useTime?: boolean;
}

export const AssessmentProgress: FunctionComponent<IAssessmentProgressProps> = observer((props) => {
    const {
        authStore: { currentUserIdentity },
    } = useStores();
    const currentPatient = usePatient();

    const { instruction, questions, options, assessment, assessmentName, assessmentLogs, maxValue, canAdd, useTime } =
        props;

    const maxTotal = maxValue * questions.length;

    const configureState = useLocalObservable<{
        openConfigure: boolean;
        frequency: AssessmentFrequency;
        dayOfWeek: DayOfWeek;
    }>(() => ({
        openConfigure: false,
        frequency: 'Every 2 weeks',
        dayOfWeek: 'Monday',
    }));

    const logState = useLocalObservable<{
        openEdit: boolean;
        totalOnly: boolean;
        totalScoreString: string;
        log: IAssessmentLog;
    }>(() => ({
        openEdit: false,
        totalOnly: false,
        totalScoreString: '',
        log: {
            assessmentId: assessment.assessmentId,
            recordedDateTime: new Date(),
            comment: '',
            pointValues: {},
            totalScore: -1,
        } as IAssessmentLog,
    }));

    const handleClose = action(() => {
        logState.openEdit = false;
        configureState.openConfigure = false;
    });

    const handleAddRecord = action(() => {
        logState.openEdit = true;
        logState.totalOnly = false;
        logState.log = {
            assessmentId: assessment.assessmentId,
            recordedDateTime: new Date(),
            comment: '',
            pointValues: {},
            totalScore: -1,
        } as IAssessmentLog;
    });

    const handleConfigure = action(() => {
        configureState.openConfigure = true;
        configureState.frequency = assessment.frequency || 'Every 2 weeks';
        configureState.dayOfWeek = assessment.dayOfWeek || 'Monday';
    });

    const onSaveEditRecord = action(() => {
        const { totalOnly, log } = logState;

        if (!!log.assessmentLogId) {
            currentPatient.updateAssessmentLog({
                ...log,
                assessmentId: assessment.assessmentId,
                patientSubmitted: false,
                submittedByProviderId: currentUserIdentity?.providerId,
                pointValues: totalOnly ? {} : { ...log.pointValues },
                totalScore: totalOnly ? log.totalScore : undefined,
            } as IAssessmentLog);
        } else {
            currentPatient.addAssessmentLog({
                ...log,
                scheduledAssessmentId: 'on-demand',
                assessmentId: assessment.assessmentId,
                patientSubmitted: false,
                submittedByProviderId: currentUserIdentity?.providerId,
                pointValues: totalOnly ? {} : { ...log.pointValues },
                totalScore: totalOnly ? log.totalScore : undefined,
            } as IAssessmentLog);
        }
        logState.openEdit = false;
    });

    const onSaveConfigure = action(() => {
        const { frequency, dayOfWeek } = configureState;
        assessment.assignedDateTime = new Date();
        var newAssessment = { ...assessment, frequency, dayOfWeek };
        currentPatient.updateAssessment(newAssessment);
        configureState.openConfigure = false;
    });

    const onQuestionSelect = action((qid: string, value: number) => {
        logState.log.pointValues[qid] = value;
    });

    const onDateChange = action((date: Date) => {
        logState.log.recordedDateTime = date;
    });

    const onTotalChange = action((value: string) => {
        logState.totalScoreString = value;

        if (!isNaN(Number(logState.totalScoreString))) {
            logState.log.totalScore = Number(logState.totalScoreString);
        }
    });

    const onToggleTotalOnly = action((value: boolean) => {
        logState.totalOnly = value;
    });

    const onFrequencyChange = action((freq: AssessmentFrequency) => {
        configureState.frequency = freq;
    });

    const onDayOfWeekChange = action((dow: DayOfWeek) => {
        configureState.dayOfWeek = dow;
    });

    const onCommentChange = action((comment: string) => {
        logState.log.comment = comment;
    });

    const selectedValues = questions.map((q) => logState.log.pointValues[q.id]);

    const saveDisabled = logState.totalOnly
        ? logState.log.totalScore == undefined || logState.log.totalScore < 0 || logState.log.totalScore > maxTotal
        : selectedValues.findIndex((v) => v == undefined) >= 0;

    const questionIds = questions.map((q) => q.id);

    const tableData = assessmentLogs
        .slice()
        .sort((a, b) => compareDesc(a.recordedDateTime, b.recordedDateTime))
        .map((a) => {
            return {
                date: format(a.recordedDateTime, 'MM/dd/yy'),
                total: getAssessmentScoreFromAssessmentLog(a),
                id: a.assessmentLogId,
                ...a.pointValues,
                comment: a.comment,
            };
        });

    const recurrence =
        assessment.assigned && assessment.assignedDateTime
            ? `${assessment.frequency} on ${assessment.dayOfWeek}s, assigned on ${format(
                  assessment.assignedDateTime,
                  'MM/dd/yyyy',
              )}`
            : 'Not assigned';

    const renderScoreCell = (props: GridCellParams) => (
        <ScoreCell score={props.value as number} assessmentId={assessment?.assessmentId}>
            {props.value}
        </ScoreCell>
    );

    const renderSuicideCell = (props: GridCellParams) => (
        <SuicideCell score={props.value as number}>{props.value}</SuicideCell>
    );

    const columns: GridColDef[] = [
        {
            field: 'date',
            headerName: 'Date',
            width: 65,
            sortable: true,
            hideSortIcons: false,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'total',
            headerName: 'Total',
            width: 60,
            renderCell: renderScoreCell,
            align: 'center',
            headerAlign: 'center',
        },
        ...questionIds.map(
            (q) =>
                ({
                    field: q,
                    headerName: q,
                    width: 60,
                    align: 'center',
                    headerAlign: 'center',
                    renderCell: q == 'Suicide' ? renderSuicideCell : undefined,
                } as GridColDef),
        ),
        {
            field: 'comment',
            headerName: 'Comment',
            minWidth: 300,
            flex: 1,
            headerAlign: 'center',
            renderCell: renderMultilineCell,
        },
    ];

    const onRowClick = action((param: GridRowParams) => {
        const id = param.row['id'] as string;
        const data = assessmentLogs.find((a) => a.assessmentLogId == id);
        if (!!data) {
            logState.openEdit = true;
            logState.log = { ...data };
            logState.log.pointValues = { ...data.pointValues };
            logState.totalOnly = data.totalScore != undefined && data.totalScore >= 0;
            logState.log.totalScore = data.totalScore != undefined && data.totalScore >= 0 ? data.totalScore : -1;
            logState.totalScoreString = `${logState.log.totalScore}`;
            logState.log.comment = data.comment || '';
        }
    });

    return (
        <ActionPanel
            id={assessment.assessmentId}
            title={assessmentName}
            inlineTitle={recurrence}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadAssessmentLogsState.pending}
            error={currentPatient?.loadAssessmentLogsState.error}
            actionButtons={[
                {
                    icon: assessment.assigned ? <AssignmentTurnedInIcon /> : <AssignmentIcon />,
                    text: assessment.assigned
                        ? getString('patient_progress_assessment_assigned_button')
                        : getString('patient_progress_assessment_assign_button'),
                    onClick: assessment.assigned
                        ? undefined
                        : () => currentPatient?.assignAssessment(assessment.assessmentId),
                } as IActionButton,
            ]
                .concat(
                    assessment.assigned
                        ? [
                              {
                                  icon: <SettingsIcon />,
                                  text: getString('patient_progress_assessment_action_configure'),
                                  onClick: handleConfigure,
                              } as IActionButton,
                          ]
                        : [],
                )
                .concat(
                    canAdd
                        ? [
                              {
                                  icon: <AddIcon />,
                                  text: getString('patient_progress_assessment_action_add'),
                                  onClick: handleAddRecord,
                              } as IActionButton,
                          ]
                        : [],
                )}>
            <Grid container alignItems="stretch">
                {assessment.assessmentId != 'mood' && assessmentLogs.length > 0 && (
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
                        headerHeight={36}
                        autoHeight={true}
                        onRowClick={onRowClick}
                        isRowSelectable={() => false}
                        pagination
                    />
                )}
                {assessmentLogs.length > 0 && (
                    <Grid item xs={12}>
                        <AssessmentVis
                            data={assessmentLogs
                                .slice()
                                .sort((a, b) => compareAsc(a.recordedDateTime, b.recordedDateTime))}
                            maxValue={maxValue}
                            useTime={useTime}
                            scaleOrder={questions.map((q) => q.id)}
                        />
                    </Grid>
                )}
                {assessmentLogs.length == 0 && (
                    <Grid item xs={12}>
                        <Typography>{`There are no ${assessmentName} scores submitted for this patient`}</Typography>
                    </Grid>
                )}
            </Grid>

            <StatefulDialog
                open={logState.openEdit}
                loading={currentPatient?.loadAssessmentLogsState.pending}
                error={currentPatient?.loadAssessmentLogsState.error}
                title={
                    logState.log.patientSubmitted
                        ? `Patient submitted ${assessmentName} record`
                        : !!logState.log.assessmentLogId
                        ? `Edit ${assessmentName} record`
                        : `Add ${assessmentName} record`
                }
                content={
                    <Questionnaire
                        readonly={logState.log.patientSubmitted}
                        questions={questions}
                        options={options}
                        selectedValues={selectedValues}
                        selectedDate={logState.log.recordedDateTime}
                        instruction={instruction}
                        onSelect={onQuestionSelect}
                        onDateChange={onDateChange}
                        onTotalChange={onTotalChange}
                        onToggleTotalOnly={onToggleTotalOnly}
                        totalOnly={logState.totalOnly}
                        totalScore={logState.totalScoreString}
                        maxTotal={maxTotal}
                        comment={logState.log.comment}
                        onCommentChange={onCommentChange}
                    />
                }
                handleCancel={handleClose}
                handleSave={onSaveEditRecord}
                disableSave={saveDisabled}
            />

            <Dialog open={configureState.openConfigure} onClose={handleClose}>
                <DialogTitle>{getString('patient_progress_assessment_dialog_configure_title')}</DialogTitle>
                <DialogContent dividers>
                    <Grid container spacing={2} alignItems="stretch">
                        <GridDropdownField
                            editable={true}
                            label={getString('patient_progress_assessment_dialog_configure_frequency_label')}
                            value={configureState.frequency}
                            options={assessmentFrequencyValues}
                            xs={12}
                            sm={12}
                            onChange={(text) => onFrequencyChange(text as AssessmentFrequency)}
                        />
                        <GridDropdownField
                            editable={true}
                            label={getString('patient_progress_assessment_dialog_configure_dayofweek_label')}
                            value={configureState.dayOfWeek}
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
