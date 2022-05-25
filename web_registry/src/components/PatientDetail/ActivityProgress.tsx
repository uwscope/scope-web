import { Grid, Typography } from '@mui/material';
import { GridColDef } from '@mui/x-data-grid';
import { compareAsc, format, isBefore } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { ActivitySuccessType } from 'shared/enums';
import { IActivityLog } from 'shared/types';
import ActionPanel from 'src/components/common/ActionPanel';
import { renderMultilineCell, Table } from 'src/components/common/Table';
import { getString } from 'src/services/strings';
import { usePatient } from 'src/stores/stores';

export const ActivityProgress: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const logMap = new Map<string, IActivityLog>();

    currentPatient.activityLogs
        ?.slice()
        .sort((a, b) => compareAsc(a.recordedDateTime, b.recordedDateTime))
        .forEach((log) => logMap.set(log.scheduledActivityId, log));

    const logs = currentPatient.scheduledActivities
        ?.slice()
        .filter((a) => isBefore(a.dueDateTime, new Date()) || a.completed)
        .sort((a, b) => compareDesc(a.dueDateTime, b.dueDateTime))
        .map((scheduledActivity) => ({
            ...scheduledActivity,
            ...logMap.get(scheduledActivity.scheduledActivityId),
        }));

    const getCompleted = (success: ActivitySuccessType) => {
        switch (success) {
            case 'Yes':
                return getString('patient_progress_activity_success_yes');
            case 'No':
                return getString('patient_progress_activity_success_no');
            default:
                return getString('patient_progress_activity_success_maybe');
        }
    };

    const tableData = logs?.map((log) => {
        return {
            id: log.scheduledActivityId,
            name: log.activityName,
            dueDate: format(log.dueDateTime, 'MM/dd/yyyy'),
            recordedDateTime: log.completed && log.recordedDateTime ? format(log.recordedDateTime, 'MM/dd/yyyy') : '--',
            completed: log.completed && log.success ? getCompleted(log.success) : '--',
            alternative: log.alternative || '--',
            pleasure: log.completed && log.success != 'No' ? log.pleasure : '--',
            accomplishment: log.completed && log.success != 'No' ? log.accomplishment : '--',
            comment: log.completed ? log.comment : '--',
        };
    });

    const columns: GridColDef[] = [
        {
            field: 'dueDate',
            headerName: getString('patient_progress_activity_header_due_date'),
            width: 100,
            sortable: true,
            hideSortIcons: false,
        },
        {
            field: 'recordedDateTime',
            headerName: getString('patient_progress_activity_header_submitted_date'),
            width: 100,
            sortable: true,
            hideSortIcons: false,
        },
        {
            field: 'name',
            headerName: getString('patient_progress_activity_header_activity'),
            width: 300,
            renderCell: renderMultilineCell,
        },
        {
            field: 'completed',
            headerName: getString('patient_progress_activity_header_success'),
            width: 200,
            sortable: true,
            hideSortIcons: false,
        },
        {
            field: 'alternative',
            headerName: getString('patient_progress_activity_header_alternative'),
            width: 200,
            sortable: false,
            hideSortIcons: false,
            renderCell: renderMultilineCell,
        },
        {
            field: 'pleasure',
            headerName: getString('patient_progress_activity_header_pleasure'),
            width: 100,
        },
        {
            field: 'accomplishment',
            headerName: getString('patient_progress_activity_header_accomplishment'),
            width: 100,
        },
        {
            field: 'comment',
            headerName: getString('patient_progress_activity_header_comment'),
            width: 200,
            renderCell: renderMultilineCell,
        },
    ];

    return (
        <ActionPanel
            id={getString('patient_progress_activity_hash')}
            title={getString('patient_progress_activity_name')}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadActivityLogsState.pending}
            error={currentPatient?.loadActivityLogsState.error}>
            <Grid container alignItems="stretch">
                {!!logs && logs.length > 0 && (
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
                        isRowSelectable={() => false}
                        pagination
                    />
                )}
                {(!logs || logs.length == 0) && (
                    <Grid item xs={12}>
                        <Typography>{getString('patient_progress_activity_empty')}</Typography>
                    </Grid>
                )}
            </Grid>
        </ActionPanel>
    );
});

export default ActivityProgress;
