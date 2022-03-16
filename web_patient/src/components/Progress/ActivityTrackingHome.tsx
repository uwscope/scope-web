import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { format } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { ActivitySuccessType } from 'shared/enums';
import { IActivityLog } from 'shared/types';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import { DetailPage } from 'src/components/common/DetailPage';
import ProgressDialog from 'src/components/Progress/ProgressDialog';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

export const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

export const ActivityTrackingHome: FunctionComponent = observer(() => {
    const navigate = useNavigate();
    const { patientStore } = useStores();

    const viewState = useLocalObservable<{ selectedLog?: IActivityLog; isOpen: boolean }>(() => ({
        selectedLog: undefined,
        isOpen: false,
    }));

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const getSuccessString = (success?: ActivitySuccessType) => {
        switch (success) {
            case 'Yes':
                return getString('Activity_tracking_success_yes');
            case 'SomethingElse':
                return getString('Activity_tracking_success_no');
            case 'No':
                return getString('Activity_tracking_success_alt');
            default:
                return getString('Activity_tracking_success_none');
        }
    };

    const handleLogClick = action((log: IActivityLog) => {
        viewState.selectedLog = log;
        viewState.isOpen = true;
    });

    const handleClose = action(() => {
        viewState.selectedLog = undefined;
        viewState.isOpen = false;
    });

    return (
        <DetailPage title={getString('Progress_activity_tracking_title')} onBack={handleGoBack}>
            <ContentLoader
                state={patientStore.loadActivityLogsState}
                name="activity logs"
                onRetry={() => patientStore.loadActivityLogs()}>
                {patientStore.activityLogs.length > 0 ? (
                    <Fragment>
                        <Table size="small" aria-label="a dense table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>{getString('Activity_tracking_column_date')}</TableCell>
                                    <TableCell>{getString('Activity_tracking_column_name')}</TableCell>
                                    <TableCell>{getString('Activity_tracking_column_completed')}</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {patientStore.activityLogs.map((log, idx) => (
                                    <TableRow key={idx} hover onClick={() => handleLogClick(log)}>
                                        <TableCell component="th" scope="row">
                                            {`${format(log.recordedDateTime, 'MM/dd')}`}
                                        </TableCell>
                                        <TableCell>{log.activityName}</TableCell>
                                        <TableCell>{getSuccessString(log.success)}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                        {viewState.selectedLog && (
                            <ProgressDialog
                                isOpen={viewState.isOpen}
                                title={viewState.selectedLog?.activityName || 'Activity Log'}
                                content={
                                    <Table size="small" aria-label="a dense table">
                                        <TableBody>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_date')}
                                                </TableCell>
                                                <TableCell>{`${
                                                    viewState.selectedLog?.recordedDateTime &&
                                                    format(
                                                        viewState.selectedLog.recordedDateTime,
                                                        'MM/dd/yyyy h:mm aaa',
                                                    )
                                                }`}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_lifearea')}
                                                </TableCell>
                                                <TableCell>
                                                    {getString('Activity_tracking_log_lifearea_none')}
                                                </TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_value')}
                                                </TableCell>
                                                <TableCell>{getString('Activity_tracking_log_value_none')}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_completed')}
                                                </TableCell>
                                                <TableCell>
                                                    {viewState.selectedLog &&
                                                        getSuccessString(viewState.selectedLog.success)}
                                                </TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_pleasure')}
                                                </TableCell>
                                                <TableCell>{viewState.selectedLog?.pleasure}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_accomplishment')}
                                                </TableCell>
                                                <TableCell>{viewState.selectedLog?.accomplishment}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_comment')}
                                                </TableCell>
                                                <TableCell>{viewState.selectedLog?.comment}</TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                }
                                onClose={handleClose}
                            />
                        )}
                    </Fragment>
                ) : (
                    <Typography>{getString('Activity_tracking_no_data')}</Typography>
                )}
            </ContentLoader>
        </DetailPage>
    );
});

export default ActivityTrackingHome;
