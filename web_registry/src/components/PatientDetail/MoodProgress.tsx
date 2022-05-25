import { Grid, Typography } from '@mui/material';
import { GridColDef } from '@mui/x-data-grid';
import { compareAsc, format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { IAssessment, IMoodLog } from 'shared/types';
import ActionPanel from 'src/components/common/ActionPanel';
import { AssessmentVis } from 'src/components/common/AssessmentVis';
import { renderMultilineCell, Table } from 'src/components/common/Table';
import { getString } from 'src/services/strings';
import { usePatient, useStores } from 'src/stores/stores';

export interface IMoodProgressProps {
    assessment: IAssessment;
    maxValue: number;
    moodLogs: IMoodLog[];
}

export const MoodProgress: FunctionComponent<IMoodProgressProps> = observer((props) => {
    const currentPatient = usePatient();
    const rootStore = useStores();

    const { moodLogs, assessment, maxValue } = props;

    const assessmentContent = rootStore.getAssessmentContent(assessment.assessmentId);

    const sortedMoodLogs = moodLogs?.slice().sort((a, b) => compareDesc(a.recordedDateTime, b.recordedDateTime));

    const tableData = sortedMoodLogs?.map((a) => {
        return {
            date: format(a.recordedDateTime, 'MM/dd/yy'),
            time: format(a.recordedDateTime, 'hh:mm aa'),
            rating: a.mood,
            id: a.moodLogId,
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
            renderCell: renderMultilineCell,
        },
    ];

    console.log(
        `loadpatient=${currentPatient?.loadPatientState.pending}, loadmood=${currentPatient?.loadMoodLogsState.pending}`,
    );

    return (
        <ActionPanel
            id={assessment.assessmentId}
            title={assessmentContent?.name || 'Mood'}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadMoodLogsState.pending}
            error={currentPatient?.loadMoodLogsState.error}>
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
                        headerHeight={36}
                        autoHeight={true}
                        isRowSelectable={() => false}
                        pagination
                    />
                )}
                {!!sortedMoodLogs && sortedMoodLogs.length > 0 && (
                    <Grid item xs={12}>
                        <AssessmentVis
                            data={moodLogs
                                .slice()
                                .sort((a, b) => compareAsc(a.recordedDateTime, b.recordedDateTime))
                                .map((log) => ({
                                    recordedDateTime: log.recordedDateTime,
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
});

export default MoodProgress;
