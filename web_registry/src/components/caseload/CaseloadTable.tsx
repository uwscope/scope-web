import { withTheme } from '@material-ui/core';
import { GridCellParams, GridColDef, GridColumnHeaderParams, GridRowParams } from '@material-ui/x-grid';
import { addWeeks, compareAsc, differenceInWeeks, format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { Table } from 'src/components/common/Table';
import { IPatientStore } from 'src/stores/PatientStore';
import { getAssessmentScore, getAssessmentScoreColorName } from 'src/utils/assessment';
import { getFollowupWeeks } from 'src/utils/time';
import styled from 'styled-components';

const TableContainer = styled.div({
    flexGrow: 1,
});

const ColumnHeader = styled.div({
    whiteSpace: 'initial',
    fontWeight: 500,
    lineHeight: '1rem',
});

const PHQCell = withTheme(
    styled.div<{ score: number }>((props) => ({
        width: '100%',
        backgroundColor: props.theme.customPalette.scoreColors[getAssessmentScoreColorName('PHQ-9', props.score)],
    }))
);

const GADCell = withTheme(
    styled.div<{ score: number }>((props) => ({
        width: '100%',
        backgroundColor: props.theme.customPalette.scoreColors[getAssessmentScoreColorName('GAD-7', props.score)],
    }))
);

const ChangeCell = withTheme(
    styled.div<{ change: number }>((props) => ({
        width: '100%',
        backgroundColor: props.change <= -50 && props.theme.customPalette.scoreColors['good'],
    }))
);

const renderHeader = (props: GridColumnHeaderParams) => <ColumnHeader>{props.colDef.headerName}</ColumnHeader>;

const renderPHQCell = (props: GridCellParams) => <PHQCell score={props.value as number}>{props.value}</PHQCell>;

const renderGADCell = (props: GridCellParams) => <GADCell score={props.value as number}>{props.value}</GADCell>;

const renderChangeCell = (props: GridCellParams) => (
    <ChangeCell change={props.value as number}>{`${props.value}%`}</ChangeCell>
);

const NA = '--';

export interface ICaseloadTableProps {
    patients: ReadonlyArray<IPatientStore>;
    onPatientClick?: (recordId: string) => void;
}

export const CaseloadTable: FunctionComponent<ICaseloadTableProps> = observer((props) => {
    const { patients, onPatientClick } = props;

    const onRowClick = (param: GridRowParams) => {
        if (!!onPatientClick) {
            const mrn = param.getValue(param.id, 'MRN');
            const found = patients.find((p) => p.profile.MRN == mrn);

            if (!!found) {
                onPatientClick(found.recordId);
            }
        }
    };

    // Column names map to IPatientStore property names
    const columns: GridColDef[] = [
        { field: 'MRN', headerName: 'MRN', width: 150, renderHeader },
        {
            field: 'depressionTreatmentStatus',
            headerName: 'Treatment Status',
            width: 120,
            renderHeader,
        },
        { field: 'name', headerName: 'Name', width: 150, renderHeader },
        { field: 'clinicCode', headerName: 'Clinic Code', width: 150, renderHeader },
        {
            field: 'initialSession',
            headerName: 'Initial Session',
            width: 160,
            renderHeader,
        },
        {
            field: 'recentSession',
            headerName: 'Last Session',
            width: 160,
            renderHeader,
        },
        { field: 'nextSessionDue', headerName: 'Follow-up Due', width: 160, renderHeader },
        { field: 'totalSessions', headerName: 'Total Sessions', width: 120, renderHeader, align: 'center' },
        { field: 'treatmentWeeks', headerName: 'Weeks in Treatment', width: 120, renderHeader, align: 'center' },
        {
            field: 'initialPHQ',
            headerName: 'Initial PHQ-9',
            width: 120,
            renderHeader,
            renderCell: renderPHQCell,
            align: 'center',
        },
        {
            field: 'lastPHQ',
            headerName: 'Last PHQ-9',
            width: 120,
            renderHeader,
            renderCell: renderPHQCell,
            align: 'center',
        },
        {
            field: 'changePHQ',
            headerName: '% Change in PHQ-9',
            width: 150,
            renderHeader,
            renderCell: renderChangeCell,
            align: 'center',
        },
        { field: 'lastPHQDate', headerName: 'Last PHQ-9 Date', width: 150, renderHeader },
        {
            field: 'initialGAD',
            headerName: 'Initial GAD-7',
            width: 120,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
        },
        {
            field: 'lastGAD',
            headerName: 'Last GAD-7',
            width: 120,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
        },
        {
            field: 'changeGAD',
            headerName: '% Change in GAD-7',
            width: 150,
            renderHeader,
            renderCell: renderChangeCell,
            align: 'center',
        },
        { field: 'lastGADDate', headerName: 'Last GAD-7 Date', width: 150, renderHeader },
    ];

    const data = patients.map((p) => {
        const initialSessionDate = p.sessions?.length > 0 ? p.sessions[0].date : null;
        const recentSessionDate = p.sessions?.length > 0 ? p.sessions[p.sessions.length - 1].date : null;
        const phq9 = p.assessmentLogs
            ?.filter((a) => a.assessmentId == 'phq-9')
            .slice()
            .sort((a, b) => compareAsc(a.recordedDate, b.recordedDate));
        const gad7 = p.assessmentLogs
            ?.filter((a) => a.assessmentId == 'gad-7')
            .slice()
            .sort((a, b) => compareAsc(a.recordedDate, b.recordedDate));

        return {
            ...p,
            ...p.profile,
            id: p.profile.MRN,
            initialSession: initialSessionDate ? format(initialSessionDate, 'MM/dd/yyyy') : NA,
            recentSession: recentSessionDate ? format(recentSessionDate, 'MM/dd/yyyy') : NA,
            nextSessionDue:
                recentSessionDate && p.profile.followupSchedule
                    ? format(addWeeks(recentSessionDate, getFollowupWeeks(p.profile.followupSchedule)), 'MM/dd/yyyy')
                    : NA,
            totalSessions: p.sessions ? p.sessions.length : 0,
            treatmentWeeks:
                initialSessionDate && recentSessionDate
                    ? differenceInWeeks(recentSessionDate, initialSessionDate) + 1
                    : 0,
            initialPHQ: phq9 && phq9.length > 0 ? getAssessmentScore(phq9[0].pointValues) : NA,
            lastPHQ: phq9 && phq9.length > 0 ? getAssessmentScore(phq9[phq9.length - 1].pointValues) : NA,
            changePHQ:
                phq9 && phq9.length > 1
                    ? Math.round(
                          ((getAssessmentScore(phq9[phq9.length - 1].pointValues) -
                              getAssessmentScore(phq9[0].pointValues)) /
                              getAssessmentScore(phq9[0].pointValues)) *
                              100
                      )
                    : NA,
            lastPHQDate: phq9 && phq9?.length > 0 ? format(phq9[phq9.length - 1].recordedDate, 'MM/dd/yyyy') : NA,

            initialGAD: gad7 && gad7.length > 0 ? getAssessmentScore(gad7[0].pointValues) : NA,
            lastGAD: gad7 && gad7.length > 0 ? getAssessmentScore(gad7[gad7.length - 1].pointValues) : NA,
            changeGAD:
                gad7 && gad7.length > 1
                    ? Math.round(
                          ((getAssessmentScore(gad7[gad7.length - 1].pointValues) -
                              getAssessmentScore(gad7[0].pointValues)) /
                              getAssessmentScore(gad7[0].pointValues)) *
                              100
                      )
                    : NA,
            lastGADDate: gad7 && gad7.length > 0 ? format(gad7[gad7.length - 1].recordedDate, 'MM/dd/yyyy') : NA,
        };
    });

    return (
        <TableContainer>
            <Table
                rows={data}
                columns={columns}
                autoPageSize
                headerHeight={56}
                rowHeight={36}
                onRowClick={onRowClick}
                pagination={true}
            />
        </TableContainer>
    );
});

export default CaseloadTable;
