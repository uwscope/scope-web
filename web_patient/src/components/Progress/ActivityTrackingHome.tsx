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
import { WordBreakTableCell } from 'src/components/common/Table';
import ProgressDialog from 'src/components/Progress/ProgressDialog';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

export const ActivityTrackingHome: FunctionComponent = observer(() => {
    const navigate = useNavigate();
    const rootStore = useStores();
    const { patientStore } = rootStore;

    const viewState = useLocalObservable<{
        selectedLog?: IActivityLog;
        isOpen: boolean;
        selectedLifeArea?: string;
        selectedValue?: string;
    }>(() => ({
        selectedLog: undefined,
        isOpen: false,
        selectedLifeArea: undefined,
        selectedValue: undefined,
    }));

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const getSuccessStringShort = (success?: ActivitySuccessType) => {
        switch (success) {
            case 'Yes':
                return getString('Activity_tracking_success_yes');
            case 'SomethingElse':
                return getString('Activity_tracking_success_alt');
            case 'No':
                return getString('Activity_tracking_success_no');
            default:
                return getString('Activity_tracking_success_none');
        }
    };

    const getSuccessString = (success?: ActivitySuccessType) => {
        switch (success) {
            case 'Yes':
                return getString('Form_activity_log_success_yes');
            case 'SomethingElse':
                return getString('Form_activity_log_success_something_else');
            case 'No':
                return getString('Form_activity_log_success_no');
            default:
                return getString('Activity_tracking_success_none');
        }
    };

    const handleLogClick = action((log: IActivityLog) => {
        viewState.selectedLog = log;
        viewState.isOpen = true;
        // TODO Activity Refactor: Activity Tracking
        const activity = patientStore.getActivityById(log.activity?.activityId as string);
        viewState.selectedValue =
            patientStore.getValueById(activity?.valueId as string)?.name ||
            getString('Activity_tracking_log_value_none');
        //viewState.selectedValue = getString('Activity_tracking_log_value_none');

        // const lifearea = activity && rootStore.getLifeAreaContent(activity?.lifeareaId);
        //viewState.selectedLifeArea = getString('Activity_tracking_log_lifearea_none');
        viewState.selectedLifeArea =
            (rootStore.getLifeAreaContent(patientStore.getValueById(activity?.valueId as string)?.lifeAreaId as string)
                ?.name as string) || getString('Activity_tracking_log_lifearea_none');
    });

    const handleClose = action(() => {
        viewState.selectedLog = undefined;
        viewState.isOpen = false;
        viewState.selectedLifeArea = undefined;
        viewState.selectedValue = undefined;
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
                                        {/* TODO: Remove ? from activity after database reset. */}
                                        <WordBreakTableCell>{log.activity?.name}</WordBreakTableCell>
                                        <WordBreakTableCell>{getSuccessStringShort(log.success)}</WordBreakTableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                        {viewState.selectedLog && (
                            <ProgressDialog
                                isOpen={viewState.isOpen}
                                // TODO: Remove ? from activity after database reset.
                                title={viewState.selectedLog?.activity?.name || 'Activity Log'}
                                content={
                                    <Table size="small" aria-label="a dense table">
                                        <TableBody>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_date')}
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
                                                    {getString('Activity_tracking_column_lifearea')}
                                                </TableCell>
                                                <WordBreakTableCell>{viewState.selectedLifeArea}</WordBreakTableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_value')}
                                                </TableCell>
                                                <WordBreakTableCell>{viewState.selectedValue}</WordBreakTableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_completed')}
                                                </TableCell>
                                                <WordBreakTableCell>
                                                    {viewState.selectedLog &&
                                                        getSuccessString(viewState.selectedLog.success)}
                                                </WordBreakTableCell>
                                            </TableRow>
                                            {viewState.selectedLog.success == 'SomethingElse' && (
                                                <TableRow>
                                                    <TableCell component="th" scope="row">
                                                        {getString('Activity_tracking_column_alternative')}
                                                    </TableCell>
                                                    <WordBreakTableCell>
                                                        {viewState.selectedLog?.alternative}
                                                    </WordBreakTableCell>
                                                </TableRow>
                                            )}
                                            {viewState.selectedLog.success != 'No' && (
                                                <TableRow>
                                                    <TableCell component="th" scope="row">
                                                        {getString('Activity_tracking_column_pleasure')}
                                                    </TableCell>
                                                    <WordBreakTableCell>
                                                        {viewState.selectedLog?.pleasure}
                                                    </WordBreakTableCell>
                                                </TableRow>
                                            )}
                                            {viewState.selectedLog.success != 'No' && (
                                                <TableRow>
                                                    <TableCell component="th" scope="row">
                                                        {getString('Activity_tracking_column_accomplishment')}
                                                    </TableCell>
                                                    <WordBreakTableCell>
                                                        {viewState.selectedLog?.accomplishment}
                                                    </WordBreakTableCell>
                                                </TableRow>
                                            )}
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Activity_tracking_column_comment')}
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
                    <Typography>{getString('Activity_tracking_no_data')}</Typography>
                )}
            </ContentLoader>
        </DetailPage>
    );
});

export default ActivityTrackingHome;
