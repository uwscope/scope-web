import { Grid, Typography } from '@material-ui/core';
import { GridColDef } from '@material-ui/x-grid';
import { compareAsc, format, isBefore } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { ActivitySuccessType } from 'shared/enums';
import { IActivityLog } from 'shared/types';
import ActionPanel from 'src/components/common/ActionPanel';
import { Table } from 'src/components/common/Table';
import { getString } from 'src/services/strings';
import { usePatient } from 'src/stores/stores';

export const ActivityProgress: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const logMap = new Map<string, IActivityLog>();

    currentPatient.activityLogs
        ?.slice()
        .sort((a, b) => compareAsc(a.recordedDate, b.recordedDate))
        .forEach((log) => logMap.set(log.scheduleId, log));

    const logs = currentPatient.scheduledActivities
        ?.slice()
        .filter((a) => isBefore(a.dueDate, new Date()))
        .sort((a, b) => compareDesc(a.dueDate, b.dueDate))
        .map((scheduledActivity) => ({
            ...scheduledActivity,
            ...logMap.get(scheduledActivity.scheduleId),
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
            id: log.scheduleId,
            name: log.activityName,
            dueDate: format(log.dueDate, 'MM/dd/yyyy'),
            recordedDate: log.completed && log.recordedDate ? format(log.recordedDate, 'MM/dd/yyyy') : '--',
            completed: log.completed && log.success ? getCompleted(log.success) : '--',
            pleasure: log.completed ? log.pleasure : '--',
            accomplishment: log.completed ? log.accomplishment : '--',
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
            field: 'recordedDate',
            headerName: getString('patient_progress_activity_header_submitted_date'),
            width: 100,
            sortable: true,
            hideSortIcons: false,
        },
        {
            field: 'name',
            headerName: getString('patient_progress_activity_header_activity'),
            width: 300,
        },
        {
            field: 'completed',
            headerName: getString('patient_progress_activity_header_success'),
            width: 200,
            sortable: true,
            hideSortIcons: false,
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
        },
    ];

    return (
        <ActionPanel
            id={getString('patient_progress_activity_hash')}
            title={getString('patient_progress_activity_name')}
            loading={currentPatient?.state == 'Pending'}>
            <Grid container spacing={2} alignItems="stretch">
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
                        autoPageSize
                        autoHeight={true}
                        isRowSelectable={(_) => false}
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
