import { withTheme } from '@material-ui/core';
import { GridCellParams, GridColDef, GridColumnHeaderParams, GridRowParams } from '@material-ui/x-grid';
import { format } from 'date-fns';
import compareDesc from 'date-fns/compareDesc';
import compareAsc from 'date-fns/esm/fp/compareAsc/index.js';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import CaseloadTable from 'src/components/caseload/CaseloadTable';
import { Table } from 'src/components/common/Table';
import { CaseReviewEntryType, SessionType } from 'src/services/enums';
import {
    IAssessment,
    IAssessmentDataPoint,
    ICaseReview,
    ISession,
    ISessionOrCaseReview,
    isSession,
    KeyedMap,
} from 'src/services/types';
import { getAssessmentScore, getAssessmentScoreColorName } from 'src/utils/assessment';
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
    assessments: ReadonlyArray<IAssessment>;
    onSessionClick?: (sessionId: string) => void;
    onReviewClick?: (reviewId: string) => void;
}

export const SessionReviewTable: FunctionComponent<ISessionReviewTableProps> = observer((props) => {
    const { sessionOrReviews, assessments, onSessionClick, onReviewClick } = props;

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
        { field: 'id', headerName: 'Id', width: 150, renderHeader, hide: true },
        { field: 'date', headerName: 'Date', width: 150, renderHeader },
        { field: 'type', headerName: 'Type', width: 150, renderHeader },
        { field: 'billableMinutes', headerName: 'Billable Minutes', width: 150, renderHeader },
        { field: 'flag', headerName: 'Billable Flag', width: 150, renderHeader },
        {
            field: 'phq9',
            headerName: 'PHQ-9',
            width: 120,
            renderHeader,
            renderCell: renderPHQCell,
            align: 'center',
        },
        {
            field: 'gad7',
            headerName: 'GAD-7',
            width: 120,
            renderHeader,
            renderCell: renderGADCell,
            align: 'center',
        },
        { field: 'medications', headerName: 'Medications', width: 150, renderHeader, renderCell: renderMultilineCell },
        { field: 'behavioralStrategies', headerName: 'Behavioral Strategies', width: 150, renderHeader },
        { field: 'referrals', headerName: 'Referrals', width: 150, renderHeader },
        { field: 'otherRecommendations', headerName: 'Other Recommendations / Action Items', width: 150, renderHeader },
        { field: 'note', headerName: 'Note', width: 150, renderHeader, renderCell: renderMultilineCell },
    ];

    const phq9 = assessments
        ?.find((a) => a.assessmentType == 'PHQ-9')
        ?.data?.slice()
        .sort((a, b) => compareDesc(a.date, b.date));
    const gad7 = assessments
        ?.find((a) => a.assessmentType == 'GAD-7')
        ?.data?.slice()
        .sort((a, b) => compareDesc(a.date, b.date));

    const getLastAvailableAssessment = (assessmentData: IAssessmentDataPoint[] | undefined, date: Date) => {
        var dataPoint = assessmentData?.find((p) => compareAsc(p.date, date) >= 0);

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

    const getSessionData = (session: ISession): ISessionTableData => ({
        id: session.sessionId,
        date: format(session.date, 'MM/dd/yyyy'),
        type: session.sessionType,
        billableMinutes: session.billableMinutes,
        flag: 'TBD',
        phq9: getLastAvailableAssessment(phq9, session.date),
        gad7: getLastAvailableAssessment(gad7, session.date),
        medications: session.medicationChange,
        behavioralStrategies: generateFlagText(session.behavioralStrategyChecklist, session.behavioralStrategyOther),
        referrals: generateFlagText(session.referralStatus, session.referralOther),
        otherRecommendations: session.otherRecommendations,
        note: session.sessionNote,
    });

    const getReviewData = (review: ICaseReview): ISessionTableData => ({
        id: review.reviewId,
        date: format(review.date, 'MM/dd/yyyy'),
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
        <TableContainer>
            <Table
                rows={data}
                columns={columns}
                autoPageSize
                headerHeight={56}
                rowHeight={100}
                onRowClick={onRowClick}
                autoHeight={true}
            />
        </TableContainer>
    );
});

export default CaseloadTable;
