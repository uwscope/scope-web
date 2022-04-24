import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { format } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { IMoodLog } from 'shared/types';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import { DetailPage } from 'src/components/common/DetailPage';
import { WordBreakTableCell } from 'src/components/common/Table';
import ProgressDialog from 'src/components/Progress/ProgressDialog';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

export const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

export const MoodTrackingHome: FunctionComponent = observer(() => {
    const navigate = useNavigate();
    const { patientStore } = useStores();

    const viewState = useLocalObservable<{ selectedLog?: IMoodLog; isOpen: boolean }>(() => ({
        selectedLog: undefined,
        isOpen: false,
    }));

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const handleLogClick = action((log: IMoodLog) => {
        viewState.selectedLog = log;
        viewState.isOpen = true;
    });

    const handleClose = action(() => {
        viewState.selectedLog = undefined;
        viewState.isOpen = false;
    });

    return (
        <DetailPage title={getString('Progress_mood_tracking_title')} onBack={handleGoBack}>
            <ContentLoader
                state={patientStore.loadMoodLogsState}
                name="mood logs"
                onRetry={() => patientStore.loadMoodLogs()}>
                {patientStore.moodLogs.length > 0 ? (
                    <Fragment>
                        <Table size="small" aria-label="a dense table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>{getString('Mood_tracking_column_date')}</TableCell>
                                    <TableCell>{getString('Mood_tracking_column_mood')}</TableCell>
                                    <TableCell>{getString('Mood_tracking_column_comment')}</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {patientStore.moodLogs.map((log, idx) => (
                                    <TableRow key={idx} hover onClick={() => handleLogClick(log)}>
                                        <TableCell component="th" scope="row">
                                            {`${format(log.recordedDateTime, 'MM/dd')}`}
                                        </TableCell>
                                        <WordBreakTableCell>{log.mood}</WordBreakTableCell>
                                        <WordBreakTableCell>{log.comment}</WordBreakTableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                        {viewState.selectedLog && (
                            <ProgressDialog
                                isOpen={viewState.isOpen}
                                title={getString('Mood_tracking_detail_title')}
                                content={
                                    <Table size="small" aria-label="a dense table">
                                        <TableBody>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Mood_tracking_column_date')}
                                                </TableCell>
                                                <WordBreakTableCell>{`${
                                                    viewState.selectedLog?.recordedDateTime &&
                                                    format(
                                                        viewState.selectedLog.recordedDateTime,
                                                        'MM/dd/yyyy h:mm aaa',
                                                    )
                                                }`}</WordBreakTableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Mood_tracking_column_mood')}
                                                </TableCell>
                                                <WordBreakTableCell>{viewState.selectedLog?.mood}</WordBreakTableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Mood_tracking_column_comment')}
                                                </TableCell>
                                                <WordBreakTableCell>
                                                    {viewState.selectedLog?.comment}
                                                </WordBreakTableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                }
                                onClose={handleClose}
                            />
                        )}
                    </Fragment>
                ) : (
                    <Typography>{getString('Mood_tracking_no_data')}</Typography>
                )}
            </ContentLoader>
        </DetailPage>
    );
});

export default MoodTrackingHome;
