import withTheme from '@mui/styles/withTheme';
import { GridCellParams, GridColDef, GridColumnHeaderParams, GridRowParams } from '@mui/x-data-grid';
import { addWeeks, compareAsc, differenceInWeeks, format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { getFollowupWeeks } from 'shared/time';
import { Table } from 'src/components/common/Table';
import { IPatientStore } from 'src/stores/PatientStore';
import { getAssessmentScore, getAssessmentScoreColorName } from 'src/utils/assessment';
import styled from 'styled-components';

const TableContainer = styled.div({
    flexGrow: 1,
});

const ColumnHeader = styled.div({
    whiteSpace: 'initial',
    fontWeight: 500,
    lineHeight: '1rem',
    textAlign: 'center',
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
        { field: 'MRN', headerName: 'MRN', minWidth: 50, align: 'center', headerAlign: 'center' },
        {
            field: 'depressionTreatmentStatus',
            headerName: 'Tx Status',
            minWidth: 120,
            align: 'center',
            headerAlign: 'center',
        },
        { field: 'name', headerName: 'Name', minWidth: 120, align: 'center', headerAlign: 'center' },
        {
            field: 'clinicCode',
            headerName: 'Clinic Code',
            minWidth: 120,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'initialSession',
            headerName: 'Initial Session',
            minWidth: 80,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
        },
        {
            field: 'recentSession',
            headerName: 'Last Session',
            minWidth: 80,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
        },
        {
            field: 'nextSessionDue',
            headerName: 'Follow-up Due',
            minWidth: 80,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
        },
        {
            field: 'totalSessions',
            headerName: 'Total Sess',
            width: 50,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
        },
        {
            field: 'treatmentWeeks',
            headerName: 'Wks in Tx',
            width: 50,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
        },
        {
            field: 'initialPHQ',
            headerName: 'Initial PHQ-9',
            width: 50,
            renderHeader,
            renderCell: renderPHQCell,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'lastPHQ',
            headerName: 'Last PHQ-9',
            width: 50,
            renderHeader,
            renderCell: renderPHQCell,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'changePHQ',
            headerName: 'Change',
            width: 60,
            renderHeader,
            renderCell: renderChangeCell,
            align: 'center',
            headerAlign: 'center',
        },
        { field: 'lastPHQDate', headerName: 'Last PHQ-9 Date', minWidth: 120, align: 'center', headerAlign: 'center' },
        {
            field: 'initialGAD',
            headerName: 'Initial GAD-7',
            width: 50,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'lastGAD',
            headerName: 'Last GAD-7',
            width: 50,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'changeGAD',
            headerName: 'Change',
            width: 60,
            renderHeader,
            renderCell: renderChangeCell,
            align: 'center',
            headerAlign: 'center',
        },
        { field: 'lastGADDate', headerName: 'Last GAD-7 Date', minWidth: 120, align: 'center', headerAlign: 'center' },
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
            initialSession: initialSessionDate ? format(initialSessionDate, 'MM/dd/yy') : NA,
            recentSession: recentSessionDate ? format(recentSessionDate, 'MM/dd/yy') : NA,
            nextSessionDue:
                recentSessionDate && p.profile.followupSchedule
                    ? format(addWeeks(recentSessionDate, getFollowupWeeks(p.profile.followupSchedule)), 'MM/dd/yy')
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
                headerHeight={36}
                rowHeight={36}
                onRowClick={onRowClick}
                autoHeight={true}
                isRowSelectable={false}
                pagination
                disableColumnMenu
            />
        </TableContainer>
    );
});

export default CaseloadTable;
