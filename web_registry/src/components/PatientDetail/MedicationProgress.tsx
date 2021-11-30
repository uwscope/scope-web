import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid, Typography } from '@material-ui/core';
import SettingsIcon from '@material-ui/icons/Settings';
import { GridColDef } from '@material-ui/x-grid';
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
import { usePatient } from 'src/stores/stores';

export interface IMedicationProgressProps {
    assessment: IAssessment;
    assessmentLogs: IAssessmentLog[];
}

export const MedicationProgress: FunctionComponent<IMedicationProgressProps> = observer((props) => {
    const currentPatient = usePatient();

    const { assessment, assessmentLogs } = props;

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

    const handleConfigure = action(() => {
        state.openConfigure = true;
        state.frequency = assessment.frequency || 'None';
        state.dayOfWeek = assessment.dayOfWeek || 'Monday';
    });

    const onSaveConfigure = action(() => {
        const { frequency, dayOfWeek } = state;
        var newAssessment = { ...assessment } as Partial<IAssessment>;
        newAssessment.frequency = frequency;
        newAssessment.dayOfWeek = dayOfWeek;
        currentPatient.updateAssessment(newAssessment);
        state.openConfigure = false;
    });

    const onFrequencyChange = action((freq: AssessmentFrequency) => {
        state.frequency = freq;
    });

    const onDayOfWeekChange = action((dow: DayOfWeek) => {
        state.dayOfWeek = dow;
    });

    const sortedLogs = assessmentLogs?.slice().sort((a, b) => compareDesc(a.recordedDate, b.recordedDate));

    const tableData = sortedLogs?.map((a) => {
        return {
            date: format(a.recordedDate, 'MM/dd/yyyy'),
            adherence:
                a.pointValues['Adherence'] == 1
                    ? getString('patient_progress_medication_adherence_yes')
                    : getString('patient_progress_medication_adherence_no'),
            id: a.logId,
            comment: a.comment,
        };
    });

    const columns: GridColDef[] = [
        {
            field: 'date',
            headerName: getString('patient_progress_medication_header_date'),
            width: 100,
            sortable: true,
            hideSortIcons: false,
        },
        {
            field: 'adherence',
            headerName: getString('patient_progress_medication_header_adherence'),
            width: 80,
            align: 'center',
        },
        {
            field: 'comment',
            headerName: getString('patient_progress_medication_header_comment'),
            width: 200,
            align: 'left',
        },
    ];

    const recurrence = `${assessment.frequency} on ${assessment.dayOfWeek}s` || 'Not assigned';

    return (
        <ActionPanel
            id={assessment.assessmentId}
            title={assessment.assessmentName}
            inlineTitle={recurrence}
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[
                {
                    icon: <SettingsIcon />,
                    text: getString('patient_progress_assessment_action_configure'),
                    onClick: handleConfigure,
                } as IActionButton,
            ]}>
            <Grid container spacing={2} alignItems="stretch">
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
                        autoPageSize
                        autoHeight={true}
                        isRowSelectable={(_) => false}
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

export default MedicationProgress;
