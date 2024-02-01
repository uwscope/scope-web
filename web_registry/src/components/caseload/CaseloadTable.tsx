import FlagIcon from '@mui/icons-material/Flag';
import { Tooltip } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import {
    GridCellParams,
    GridColDef,
    GridColumnHeaderParams,
    GridComparatorFn,
    GridRowParams,
    GridValueFormatterParams,
    gridDateComparator,
    gridNumberComparator,
} from '@mui/x-data-grid';
import { addWeeks, compareAsc, differenceInWeeks } from 'date-fns';
import React, { FunctionComponent } from 'react';
import { formatDateOnly, getFollowupWeeks } from 'shared/time';
import { Table } from 'src/components/common/Table';
import { IPatientStore } from 'src/stores/PatientStore';
import { getAssessmentScoreColorName, getAssessmentScoreFromAssessmentLog } from 'src/utils/assessment';
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
    styled.div<{ score: number; risk: boolean }>((props) => ({
        width: '100%',
        padding: props.theme.spacing(2),
        textAlign: 'center',
        backgroundColor: props.theme.customPalette.scoreColors[getAssessmentScoreColorName('PHQ-9', props.score)],
        border: props.risk ? `2px solid ${props.theme.customPalette.flagColors['safety']}` : 'none',
    })),
);

const GADCell = withTheme(
    styled.div<{ score: number }>((props) => ({
        width: '100%',
        padding: props.theme.spacing(2),
        textAlign: 'center',
        backgroundColor: props.theme.customPalette.scoreColors[getAssessmentScoreColorName('GAD-7', props.score)],
    })),
);

const ChangeCell = withTheme(
    styled.div<{ change: number }>((props) => ({
        width: '100%',
        padding: props.theme.spacing(2),
        textAlign: 'center',
        backgroundColor: props.change <= -50 && props.theme.customPalette.scoreColors['good'],
    })),
);

const RedFlag = withTheme(
    styled(FlagIcon)<{ $on: boolean }>((props) => ({
        color: props.theme.customPalette.flagColors[props.$on ? 'safety' : 'disabled'],
    })),
);

const YellowFlag = withTheme(
    styled(FlagIcon)<{ $on: boolean }>((props) => ({
        color: props.theme.customPalette.flagColors[props.$on ? 'discussion' : 'disabled'],
    })),
);

const dateValueComparator: GridComparatorFn = (v1, v2) => {
    if (v1 === null || v2 === null) {
        if (v1 !== null) {
            return -1;
        } else if (v2 !== null) {
            return 1;
        } else {
            return 0;
        }
    } else {
        const v1Date = v1 as Date;
        const v2Date = v2 as Date;

        return gridDateComparator(v1Date, v2Date);
    }
};

const dateValueFormatter = (params: GridValueFormatterParams) => {
    if (params.value === null) {
        return NA;
    }

    return formatDateOnly(params.value as Date, 'MM/dd/yy');
};

const numericValueComparator: GridComparatorFn = (v1, v2, cellParams1, cellParams2) => {
	if (v1 === NA || v2 === NA) {
		if (v1 !== NA) {
			return -1;
		} else if (v2 !== NA) {
			return 1;
		} else {
			return 0;
		}
	} else {
		const v1Number = v1 as Number;
		const v2Number = v2 as Number;

		return gridNumberComparator(v1Number, v2Number, cellParams1, cellParams2);
	}
};

const renderHeader = (props: GridColumnHeaderParams) => <ColumnHeader>{props.colDef.headerName}</ColumnHeader>;

const renderPHQCell = (props: GridCellParams, atRiskId: string) => (
    <PHQCell score={props.value as number} risk={!!props.row[atRiskId]}>
        {props.value}
    </PHQCell>
);

const renderGADCell = (props: GridCellParams) => <GADCell score={props.value as number}>{props.value}</GADCell>;

const renderChangeCell = (props: GridCellParams) => (
    <ChangeCell change={props.value as number}>{`${props.value}%`}</ChangeCell>
);

const renderFlagCell = (props: GridCellParams) => {
    const flaggedForDiscussion = !!props.value?.['Flag for discussion'];
    const flaggedForSafety = !!props.value?.['Flag as safety risk'];
    return (
        <div>
            <Tooltip title="Flagged for safety">
                <RedFlag $on={flaggedForSafety} fontSize="small" />
            </Tooltip>
            <Tooltip title="Flagged for discussion">
                <YellowFlag $on={flaggedForDiscussion} fontSize="small" />
            </Tooltip>
        </div>
    );
};

const rowDefaultComparator = (v1: { name: string; }, v2: { name: string; }) => {
    return v1.name.localeCompare(v2.name);
}

const NA = '--';

export interface ICaseloadTableProps {
    patients: ReadonlyArray<IPatientStore>;
    onPatientClick?: (recordId: string) => void;
}

export const CaseloadTable: FunctionComponent<ICaseloadTableProps> = (props) => {
    const { patients, onPatientClick } = props;

    const onRowClick = (param: GridRowParams) => {
        if (!!onPatientClick) {
            const mrn = param.row['MRN'];
            const found = patients.find((p) => p.profile.MRN == mrn);

            if (!!found) {
                onPatientClick(found.recordId);
            }
        }
    };

    // Column names map to IPatientStore property names
    const columns: GridColDef[] = [
        {
            field: 'discussionFlag',
            headerName: 'Flags',
            width: 25,
            align: 'center',
            headerAlign: 'center',
            renderCell: renderFlagCell,
        },
        {
            field: 'depressionTreatmentStatus',
            headerName: 'Tx Status',
            minWidth: 120,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'name',
            headerName: 'Name',
            minWidth: 240,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'clinicCode',
            headerName: 'Clinic Code',
            minWidth: 120,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'site',
            headerName: 'Site',
            minWidth: 120,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'initialSession',
            headerName: 'Initial Session',
            width: 85,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
            sortComparator: dateValueComparator,
            valueFormatter: dateValueFormatter,
        },
        {
            field: 'recentSession',
            headerName: 'Last Session',
            width: 85,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
            sortComparator: dateValueComparator,
            valueFormatter: dateValueFormatter,
        },
        {
            field: 'recentCaseReview',
            headerName: 'Last Case Review',
            width: 85,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
            sortComparator: dateValueComparator,
            valueFormatter: dateValueFormatter,
        },
        {
            field: 'nextSessionDue',
            headerName: 'Follow-up Due',
            width: 85,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            filterable: false,
            sortComparator: dateValueComparator,
            valueFormatter: dateValueFormatter,
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
            renderCell: (props) => renderPHQCell(props, 'initialAtRisk'),
            align: 'center',
            headerAlign: 'center',
            sortComparator: numericValueComparator,
        },
        {
            field: 'lastPHQ',
            headerName: 'Last PHQ-9',
            width: 50,
            renderHeader,
            renderCell: (props) => renderPHQCell(props, 'lastAtRisk'),
            align: 'center',
            headerAlign: 'center',
            sortComparator: numericValueComparator,
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
        {
            field: 'lastPHQDate',
            headerName: 'Last PHQ-9 Date',
            width: 85,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            sortComparator: dateValueComparator,
            valueFormatter: dateValueFormatter,
        },
        {
            field: 'initialGAD',
            headerName: 'Initial GAD-7',
            width: 50,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
            headerAlign: 'center',
            sortComparator: numericValueComparator,
        },
        {
            field: 'lastGAD',
            headerName: 'Last GAD-7',
            width: 50,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
            headerAlign: 'center',
            sortComparator: numericValueComparator,
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
        {
            field: 'lastGADDate',
            headerName: 'Last GAD-7 Date',
            width: 85,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
            sortComparator: dateValueComparator,
            valueFormatter: dateValueFormatter,
        },
    ];

    const data = patients.map((p) => {
        const initialSessionDate = p.sessions?.length > 0 ? p.sessions[0].date : null;
        const recentSessionDate = p.sessions?.length > 0 ? p.sessions[p.sessions.length - 1].date : null;
        const recentReviewDate = p.caseReviews?.length > 0 ? p.caseReviews[p.caseReviews.length - 1].date : null;

        const phq9 = p.assessmentLogs
            ?.filter((a) => a.assessmentId == 'phq-9')
            .slice()
            .sort((a, b) => compareAsc(a.recordedDateTime, b.recordedDateTime));
        const gad7 = p.assessmentLogs
            ?.filter((a) => a.assessmentId == 'gad-7')
            .slice()
            .sort((a, b) => compareAsc(a.recordedDateTime, b.recordedDateTime));

        const initialAtRisk = phq9 && phq9.length > 0 && phq9[0].pointValues && !!phq9[0].pointValues['Suicide'];

        const lastAtRisk =
            phq9 &&
            phq9.length > 0 &&
            phq9[phq9.length - 1].pointValues &&
            !!phq9[phq9.length - 1].pointValues['Suicide'];

        const initialPHQScore = phq9 && phq9.length > 0 ? getAssessmentScoreFromAssessmentLog(phq9[0]) : undefined;
        const initialGADScore = gad7 && gad7.length > 0 ? getAssessmentScoreFromAssessmentLog(gad7[0]) : undefined;

        return {
            ...p,
            ...p.profile,
            id: p.profile.MRN,
            initialSession: initialSessionDate,
            recentSession: recentSessionDate,
            recentCaseReview: recentReviewDate,
            nextSessionDue: recentSessionDate && p.profile.followupSchedule
                ? addWeeks(recentSessionDate, getFollowupWeeks(p.profile.followupSchedule))
                : null,
            totalSessions: p.sessions ? p.sessions.length : 0,
            treatmentWeeks:
                initialSessionDate && recentSessionDate
                    ? differenceInWeeks(recentSessionDate, initialSessionDate) + 1
                    : 0,
            initialPHQ: phq9 && phq9.length > 0 ? initialPHQScore : NA,
            lastPHQ: phq9 && phq9.length > 0 ? getAssessmentScoreFromAssessmentLog(phq9[phq9.length - 1]) : NA,
            changePHQ:
                initialPHQScore && initialPHQScore
                    ? Math.round(
                          ((getAssessmentScoreFromAssessmentLog(phq9[phq9.length - 1]) - initialPHQScore) /
                              initialPHQScore) *
                              100,
                      )
                    : NA,
            lastPHQDate:
                phq9 && phq9?.length > 0 ? phq9[phq9.length - 1].recordedDateTime : null,

            initialGAD: gad7 && gad7.length > 0 ? initialGADScore : NA,
            lastGAD: gad7 && gad7.length > 0 ? getAssessmentScoreFromAssessmentLog(gad7[gad7.length - 1]) : NA,
            changeGAD:
                initialGADScore && initialGADScore > 0
                    ? Math.round(
                          ((getAssessmentScoreFromAssessmentLog(gad7[gad7.length - 1]) - initialGADScore) /
                              initialGADScore) *
                              100,
                      )
                    : NA,
            lastGADDate:
                gad7 && gad7.length > 0 ? gad7[gad7.length - 1].recordedDateTime : null,
            initialAtRisk,
            lastAtRisk,
        };
    }).sort(rowDefaultComparator);

    return (
        <TableContainer>
            <Table
                rows={data}
                columns={columns}
                headerHeight={36}
                rowHeight={36}
                onRowClick={onRowClick}
                autoHeight={true}
                isRowSelectable={() => false}
                pagination
                disableColumnMenu
                initialState={{
                    sorting: {
                        sortModel: [{ field: 'name', sort: 'asc'}]
                    }
                }}
            />
        </TableContainer>
    );
};

export default CaseloadTable;
