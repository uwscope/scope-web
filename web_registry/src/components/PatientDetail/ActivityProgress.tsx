import { Grid, Typography } from '@material-ui/core';
import { GridColDef } from '@material-ui/x-grid';
import { format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel from 'src/components/common/ActionPanel';
import { Table } from 'src/components/common/Table';
import { ActivitySuccessType } from 'src/services/enums';
import { getString } from 'src/services/strings';
import { usePatient } from 'src/stores/stores';

export const ActivityProgress: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const logs = currentPatient.activityLogs?.slice().sort((a, b) => compareDesc(a.date, b.date));

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
            name: log.activityName,
            date: format(log.date, 'MM/dd/yyyy'),
            completed: getCompleted(log.success),
            pleasure: log.pleasure,
            accomplishment: log.accomplishment,
            comment: log.comment,
        };
    });

    const columns: GridColDef[] = [
        {
            field: 'name',
            headerName: getString('patient_progress_activity_header_activity'),
            width: 100,
        },
        {
            field: 'date',
            headerName: getString('patient_progress_activity_header_date'),
            width: 100,
            sortable: true,
            hideSortIcons: false,
        },
        {
            field: 'success',
            headerName: getString('patient_progress_activity_header_success'),
            width: 100,
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
            width: 120,
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
