import AssignmentIcon from '@mui/icons-material/Assignment';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import SettingsIcon from '@mui/icons-material/Settings';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid, Typography } from '@mui/material';
import { GridColDef } from '@mui/x-data-grid';
import { format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { AssessmentFrequency, assessmentFrequencyValues, DayOfWeek, daysOfWeekValues } from 'shared/enums';
import { IAssessment, IAssessmentLog } from 'shared/types';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDropdownField } from 'src/components/common/GridField';
import { Table } from 'src/components/common/Table';
import { getString } from 'src/services/strings';
import { usePatient, useStores } from 'src/stores/stores';

export interface IMedicationProgressProps {
    assessment: IAssessment;
    assessmentLogs: IAssessmentLog[];
}

export const MedicationProgress: FunctionComponent<IMedicationProgressProps> = observer((props) => {
    const currentPatient = usePatient();
    const rootStore = useStores();

    const { assessment, assessmentLogs } = props;

    const assessmentContent = rootStore.getAssessmentContent(assessment.assessmentId);

    const state = useLocalObservable<{
        openConfigure: boolean;
        frequency: AssessmentFrequency;
        dayOfWeek: DayOfWeek;
    }>(() => ({
        openConfigure: false,
        frequency: 'Every 2 weeks',
        dayOfWeek: 'Monday',
    }));

    const handleClose = action(() => {
        state.openConfigure = false;
    });

    // const handleConfigure = action(() => {
    //     state.openConfigure = true;
    //     state.frequency = assessment.frequency || 'Every 2 weeks';
    //     state.dayOfWeek = assessment.dayOfWeek || 'Monday';
    // });

    const onSaveConfigure = action(() => {
        const { frequency, dayOfWeek } = state;
        var newAssessment = { ...assessment, frequency, dayOfWeek };
        currentPatient.updateAssessment(newAssessment);
        state.openConfigure = false;
    });

    const onFrequencyChange = action((freq: AssessmentFrequency) => {
        state.frequency = freq;
    });

    const onDayOfWeekChange = action((dow: DayOfWeek) => {
        state.dayOfWeek = dow;
    });

    const sortedLogs = assessmentLogs?.slice().sort((a, b) => compareDesc(a.recordedDateTime, b.recordedDateTime));

    const tableData = sortedLogs?.map((a) => {
        return {
            date: format(a.recordedDateTime, 'MM/dd/yy'),
            adherence:
                a.pointValues['Adherence'] == 1
                    ? getString('patient_progress_medication_adherence_yes')
                    : getString('patient_progress_medication_adherence_no'),
            id: a.assessmentLogId,
            comment: a.comment,
        };
    });

    const columns: GridColDef[] = [
        {
            field: 'date',
            headerName: getString('patient_progress_medication_header_date'),
            width: 65,
            sortable: true,
            hideSortIcons: false,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'adherence',
            headerName: getString('patient_progress_medication_header_adherence'),
            minWidth: 180,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'comment',
            headerName: getString('patient_progress_medication_header_comment'),
            width: 300,
            flex: 1,
            align: 'left',
            headerAlign: 'center',
        },
    ];

    const recurrence =
        assessment.assigned && assessment.assignedDateTime
            ? `${assessment.frequency} on ${assessment.dayOfWeek}s, assigned on ${format(
                  assessment.assignedDateTime,
                  'MM/dd/yyyy',
              )}`
            : 'Not assigned';

    return (
        <ActionPanel
            id={assessment.assessmentId}
            title={assessmentContent?.name || 'Unknown assessment'}
            inlineTitle={recurrence}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadAssessmentLogsState.pending}
            error={currentPatient?.loadAssessmentLogsState.error}
            actionButtons={[
                {
                    icon: assessment.assigned ? <AssignmentTurnedInIcon /> : <AssignmentIcon />,
                    text: assessment.assigned
                        ? getString('patient_progress_assessment_assigned_button')
                        : getString('patient_progress_assessment_assign_button'),
                    // Temporarily disable assignment
                    // onClick: assessment.assigned
                    //     ? undefined
                    //     : () => currentPatient?.assignAssessment(assessment.assessmentId),
                } as IActionButton,
            ].concat(
                assessment.assigned
                    ? [
                          {
                              icon: <SettingsIcon />,
                              text: getString('patient_progress_assessment_action_configure'),
                              // Temporarily disable assignment
                              //   onClick: handleConfigure,
                          } as IActionButton,
                      ]
                    : [],
            )}>
            <Grid container alignItems="stretch">
                {!!sortedLogs && sortedLogs.length > 0 && (
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
                        headerHeight={28}
                        rowHeight={24}
                        autoHeight={true}
                        isRowSelectable={() => false}
                        pagination
                    />
                )}
                {(!sortedLogs || sortedLogs.length == 0) && (
                    <Grid item xs={12}>
                        <Typography>{getString('patient_progress_medication_empty')}</Typography>
                    </Grid>
                )}
            </Grid>
            <Dialog open={state.openConfigure} onClose={handleClose}>
                <DialogTitle>{getString('patient_progress_assessment_dialog_configure_title')}</DialogTitle>
                <DialogContent dividers>
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

export default MedicationProgress;
