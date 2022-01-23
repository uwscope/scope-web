import { Grid } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { GridCellParams, GridColDef, GridColumnHeaderParams, GridRowParams } from '@mui/x-data-grid';
import { format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { CaseReviewEntryType, SessionType } from 'shared/enums';
import { ICaseReview, IReferralStatus, ISession, ISessionOrCaseReview, isSession, KeyedMap } from 'shared/types';
import { Table } from 'src/components/common/Table';
import styled from 'styled-components';

const ColumnHeader = styled.div({
    whiteSpace: 'initial',
    fontWeight: 500,
    lineHeight: '1rem',
    textAlign: 'center',
});

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
    medications: string;
    behavioralStrategies: string;
    referrals: string;
    otherRecommendations: string;
    note: string;
}

export interface ISessionReviewTableProps {
    sessionOrReviews: ReadonlyArray<ISessionOrCaseReview>;
    onSessionClick?: (sessionId: string) => void;
    onReviewClick?: (reviewId: string) => void;
}

export const SessionReviewTable: FunctionComponent<ISessionReviewTableProps> = observer((props) => {
    const { sessionOrReviews, onSessionClick, onReviewClick } = props;

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

    const generateFlagText = (flags: KeyedMap<boolean | string>, other: string) => {
        var concatValues = Object.keys(flags)
            .filter((k) => flags[k] && k != 'Other')
            .join(', ');
        if (flags['Other']) {
            concatValues = [concatValues, other || 'Other'].join(', ');
        }

        return concatValues;
    };

    const generateReferralText = (referrals: IReferralStatus[]) => {
        return referrals.map((ref) => (ref.referralType == 'Other' ? ref.referralOther : ref.referralType)).join(', ');
    };

    const getSessionData = (session: ISession): ISessionTableData => ({
        id: session.sessionId,
        date: `${format(session.date, 'MM/dd/yy')}`,
        type: session.sessionType,
        billableMinutes: session.billableMinutes,
        flag: 'TBD',
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
                isRowSelectable={() => false}
                pagination
            />
        </Grid>
    );
});

export default SessionReviewTable;
