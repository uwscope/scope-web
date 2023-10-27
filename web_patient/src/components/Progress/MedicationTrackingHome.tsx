import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { format } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { IAssessmentLog } from 'shared/types';
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

export const MedicationTrackingHome: FunctionComponent<{ assessmentType: string }> = observer((props) => {
    const { assessmentType } = props;
    const navigate = useNavigate();
    const rootStore = useStores();
    const { patientStore } = rootStore;

    const viewState = useLocalObservable<{ selectedLog?: IAssessmentLog; isOpen: boolean }>(() => ({
        selectedLog: undefined,
        isOpen: false,
    }));

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const handleLogClick = action((log: IAssessmentLog) => {
        viewState.selectedLog = log;
        viewState.isOpen = true;
    });

    const handleClose = action(() => {
        viewState.selectedLog = undefined;
        viewState.isOpen = false;
    });

    const title = 'Progress_medication_tracking_title';
    const assessmentContent = rootStore.getAssessmentContent(assessmentType);

    const logs = patientStore.assessmentLogs.filter((a) => a.assessmentId.toLowerCase() == assessmentType);

    return (
        <DetailPage title={getString(title)} onBack={handleGoBack}>
            <ContentLoader
                state={patientStore.loadAssessmentLogsState}
                name={`${assessmentContent?.name} logs`}
                onRetry={() => patientStore.loadAssessmentLogs()}>
                {logs.length > 0 ? (
                    <Fragment>
                        <Table size="small" aria-label="a dense table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>{getString('Assessment_progress_column_date')}</TableCell>
                                    <TableCell>{getString('Medication_progress_adherence')}</TableCell>
                                    <TableCell>{getString('Medication_progress_note')}</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {logs.map((log, idx) => (
                                    <TableRow key={idx} hover onClick={() => handleLogClick(log)}>
                                        <TableCell component="th" scope="row">
                                            {`${format(log.recordedDateTime, 'MM/dd')}`}
                                        </TableCell>
                                        <TableCell>{log.adherence == 1 ? 'Yes' : 'No'}</TableCell>
                                        <TableCell>{log.medicationNote}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                        {viewState.selectedLog && (
                            <ProgressDialog
                                isOpen={viewState.isOpen}
                                title={getString('Progress_medication_assessment_detail_title')}
                                content={
                                    <Table size="small" aria-label="a dense table">
                                        <TableBody>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Assessment_progress_column_date')}
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
                                                    {getString('Medication_progress_adherence')}
                                                </TableCell>
                                                <TableCell>
                                                    {viewState.selectedLog?.adherence == 1 ? 'Yes' : 'No'}
                                                </TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Medication_progress_note')}
                                                </TableCell>
                                                <TableCell>{viewState.selectedLog?.medicationNote}</TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                }
                                onClose={handleClose}
                            />
                        )}
                    </Fragment>
                ) : (
                    <Typography>{getString('Assessment_progress_no_data')}</Typography>
                )}
            </ContentLoader>
        </DetailPage>
    );
});

export default MedicationTrackingHome;
