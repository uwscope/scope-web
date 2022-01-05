import { Grid } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { GridCellParams, GridColDef, GridColumnHeaderParams, GridRowParams } from '@mui/x-data-grid';
import { format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import compareAsc from 'date-fns/esm/fp/compareAsc/index.js';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { CaseReviewEntryType, SessionType } from 'shared/enums';
import {
    IAssessmentLog,
    ICaseReview,
    IReferralStatus,
    ISession,
    ISessionOrCaseReview,
    isSession,
    KeyedMap,
} from 'shared/types';
import { Table } from 'src/components/common/Table';
import { getAssessmentScore, getAssessmentScoreColorName } from 'src/utils/assessment';
import styled from 'styled-components';

const ColumnHeader = styled.div({
    whiteSpace: 'initial',
    fontWeight: 500,
    lineHeight: '1rem',
    textAlign: 'center',
});

const PHQCell = withTheme(
    styled.div<{ score: number }>((props) => ({
        width: 'calc(100% + 16px)',
        marginLeft: -8,
        marginRight: -8,
        backgroundColor: props.theme.customPalette.scoreColors[getAssessmentScoreColorName('PHQ-9', props.score)],
    }))
);

const GADCell = withTheme(
    styled.div<{ score: number }>((props) => ({
        width: 'calc(100% + 16px)',
        marginLeft: -8,
        marginRight: -8,
        backgroundColor: props.theme.customPalette.scoreColors[getAssessmentScoreColorName('GAD-7', props.score)],
    }))
);

const MultilineCell = withTheme(
    styled.div<{ score: number }>((props) => ({
        whiteSpace: 'initial',
        lineHeight: '1rem',
        overflowY: 'auto',
        height: '100%',
        padding: props.theme.spacing(1, 0),
    }))
);

const renderHeader = (props: GridColumnHeaderParams) => <ColumnHeader>{props.colDef.headerName}</ColumnHeader>;

const renderPHQCell = (props: GridCellParams) => <PHQCell score={props.value as number}>{props.value}</PHQCell>;

const renderGADCell = (props: GridCellParams) => <GADCell score={props.value as number}>{props.value}</GADCell>;

const renderMultilineCell = (props: GridCellParams) => (
    <MultilineCell score={props.value as number}>{props.value}</MultilineCell>
);

const NA = '--';

interface ISessionTableData {
    id: string;
    date: string;
    type: SessionType | CaseReviewEntryType;
    billableMinutes: number | string;
    flag: string;
    phq9: number | string;
    gad7: number | string;
    medications: string;
    behavioralStrategies: string;
    referrals: string;
    otherRecommendations: string;
    note: string;
}

export interface ISessionReviewTableProps {
    sessionOrReviews: ReadonlyArray<ISessionOrCaseReview>;
    assessmentLogs: ReadonlyArray<IAssessmentLog>;
    onSessionClick?: (sessionId: string) => void;
    onReviewClick?: (reviewId: string) => void;
}

export const SessionReviewTable: FunctionComponent<ISessionReviewTableProps> = observer((props) => {
    const { sessionOrReviews, assessmentLogs, onSessionClick, onReviewClick } = props;

    const onRowClick = (param: GridRowParams) => {
        const id = param.getValue(param.id, 'id') as string;

        if (param.getValue(param.id, 'type') == 'Case Review') {
            onReviewClick && onReviewClick(id);
        } else {
            onSessionClick && onSessionClick(id);
        }
    };

    // Column names map to IPatientStore property names
    const columns: GridColDef[] = [
        {
            field: 'id',
            headerName: 'Id',
            renderHeader,
            hide: true,
            headerAlign: 'center',
        },
        {
            field: 'date',
            headerName: 'Date',
            width: 65,
            renderHeader,
            sortable: true,
            hideSortIcons: false,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'type',
            headerName: 'Type',
            width: 70,
            renderHeader,
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'billableMinutes',
            headerName: 'Bill Min',
            width: 25,
            renderHeader,
            align: 'center',
            type: 'number',
            headerAlign: 'center',
        },
        {
            field: 'phq9',
            headerName: 'PHQ',
            width: 25,
            renderHeader,
            renderCell: renderPHQCell,
            align: 'center',
            type: 'number',
            headerAlign: 'center',
        },
        {
            field: 'gad7',
            headerName: 'GAD',
            width: 25,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
            type: 'number',
            headerAlign: 'center',
        },
        {
            field: 'medications',
            headerName: 'Medications',
            width: 150,
            renderHeader,
            renderCell: renderMultilineCell,
            headerAlign: 'center',
        },
        {
            field: 'behavioralStrategies',
            headerName: 'Behavioral Strategies',
            width: 150,
            renderHeader,
            renderCell: renderMultilineCell,
            headerAlign: 'center',
        },
        {
            field: 'referrals',
            headerName: 'Referrals',
            width: 150,
            renderHeader,
            renderCell: renderMultilineCell,
            headerAlign: 'center',
        },
        {
            field: 'otherRecommendations',
            headerName: 'Other Rec / Action Items',
            width: 150,
            renderHeader,
            renderCell: renderMultilineCell,
            headerAlign: 'center',
        },
        {
            field: 'note',
            headerName: 'Note',
            minWidth: 150,
            flex: 1,
            renderHeader,
            renderCell: renderMultilineCell,
            headerAlign: 'center',
        },
    ];

    const phq9 = assessmentLogs
        ?.filter((a) => a.assessmentId == 'phq-9')
        ?.slice()
        .sort((a, b) => compareDesc(a.recordedDate, b.recordedDate));
    const gad7 = assessmentLogs
        ?.filter((a) => a.assessmentId == 'gad-7')
        ?.slice()
        .sort((a, b) => compareDesc(a.recordedDate, b.recordedDate));

    const getLastAvailableAssessment = (assessmentLogs: IAssessmentLog[] | undefined, date: Date) => {
        var dataPoint = assessmentLogs?.find((p) => compareAsc(p.recordedDate, date) >= 0);

        if (!!dataPoint) {
            return getAssessmentScore(dataPoint.pointValues);
        }

        return NA;
    };

    const generateFlagText = (flags: KeyedMap<boolean | string>, other: string) => {
        var concatValues = Object.keys(flags)
            .filter((k) => flags[k] && k != 'Other')
            .join('\n');
        if (flags['Other']) {
            concatValues = [concatValues, other].join('\n');
        }

        return concatValues;
    };

    const generateReferralText = (referrals: IReferralStatus[]) => {
        return referrals.map((ref) => ref.referralType).join('\n');
    };

    const getSessionData = (session: ISession): ISessionTableData => ({
        id: session.sessionId,
        date: `${format(session.date, 'MM/dd/yy')}`,
        type: session.sessionType,
        billableMinutes: session.billableMinutes,
        flag: 'TBD',
        phq9: getLastAvailableAssessment(phq9, session.date),
        gad7: getLastAvailableAssessment(gad7, session.date),
        medications: session.medicationChange,
        behavioralStrategies: generateFlagText(session.behavioralStrategyChecklist, session.behavioralStrategyOther),
        referrals: generateReferralText(session.referrals),
        otherRecommendations: session.otherRecommendations,
        note: session.sessionNote,
    });

    const getReviewData = (review: ICaseReview): ISessionTableData => ({
        id: review.reviewId,
        date: `${format(review.date, 'MM/dd')}\n${format(review.date, 'yyyy')}`,
        type: 'Case Review',
        billableMinutes: NA,
        flag: 'TBD',
        phq9: getLastAvailableAssessment(phq9, review.date),
        gad7: getLastAvailableAssessment(gad7, review.date),
        medications: review.medicationChange,
        behavioralStrategies: review.behavioralStrategyChange,
        referrals: review.referralsChange,
        otherRecommendations: review.otherRecommendations,
        note: review.reviewNote,
    });

    const data = sessionOrReviews.map((p) => {
        if (isSession(p)) {
            return getSessionData(p);
        } else {
            return getReviewData(p as ICaseReview);
        }
    });

    return (
        <Grid container alignItems="stretch">
            <Table
                rows={data}
                columns={columns.map((c) => ({
                    sortable: false,
                    filterable: false,
                    editable: false,
                    hideSortIcons: true,
                    disableColumnMenu: true,
                    ...c,
                }))}
                headerHeight={36}
                onRowClick={onRowClick}
                autoHeight={true}
                isRowSelectable={false}
                pagination
            />
        </Grid>
    );
});

export default SessionReviewTable;
