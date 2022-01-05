import { Grid, Typography } from '@mui/material';
import { GridColDef } from '@mui/x-data-grid';
import { format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import React, { FunctionComponent } from 'react';
import { IAssessment, IMoodLog } from 'shared/types';
import ActionPanel from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import { Table } from 'src/components/common/Table';
import { getString } from 'src/services/strings';
import { usePatient } from 'src/stores/stores';

export interface IMoodProgressProps {
    assessment: IAssessment;
    maxValue: number;
    moodLogs: IMoodLog[];
}

export const MoodProgress: FunctionComponent<IMoodProgressProps> = (props) => {
    const currentPatient = usePatient();

    const { moodLogs, assessment, maxValue } = props;

    const sortedMoodLogs = moodLogs?.slice().sort((a, b) => compareDesc(a.recordedDate, b.recordedDate));

    const tableData = sortedMoodLogs?.map((a) => {
        return {
            date: format(a.recordedDate, 'MM/dd/yy'),
            time: format(a.recordedDate, 'hh:mm aa'),
            rating: a.mood,
            id: a.logId,
            comment: a.comment,
        };
    });

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
            field: 'time',
            headerName: 'Time',
            width: 65,
            sortable: true,
            hideSortIcons: false,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'rating',
            headerName: getString('patient_progress_mood_header_mood'),
            width: 60,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'comment',
            headerName: getString('patient_progress_mood_header_comment'),
            width: 300,
            flex: 1,
            align: 'left',
            headerAlign: 'center',
        },
    ];

    return (
        <ActionPanel
            id={assessment.assessmentId}
            title={assessment.assessmentName}
            loading={currentPatient?.state == 'Pending'}>
            <Grid container alignItems="stretch">
                {!!sortedMoodLogs && sortedMoodLogs.length > 0 && (
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
                        isRowSelectable={false}
                        pagination
                    />
                )}
                {!!sortedMoodLogs && sortedMoodLogs.length > 0 && (
                    <Grid item xs={12}>
                        <AssessmentVis
                            data={sortedMoodLogs.map((log) => ({
                                recordedDate: log.recordedDate,
                                pointValues: { Mood: log.mood },
                            }))}
                            maxValue={maxValue}
                            useTime={true}
                        />
                    </Grid>
                )}
                {(!sortedMoodLogs || sortedMoodLogs.length == 0) && (
                    <Grid item xs={12}>
                        <Typography>{getString('patient_progress_mood_empty')}</Typography>
                    </Grid>
                )}
            </Grid>
        </ActionPanel>
    );
};

export default MoodProgress;
