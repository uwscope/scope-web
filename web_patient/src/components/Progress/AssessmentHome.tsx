import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { format } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { IAssessmentLog } from 'shared/types';
import ContentLoader from 'src/components/Chrome/ContentLoader';
import { DetailPage } from 'src/components/common/DetailPage';
import { WordBreakTableCell } from 'src/components/common/Table';
import ProgressDialog from 'src/components/Progress/ProgressDialog';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';
import { getAssessmentScore } from 'src/utils/assessment';
import styled from 'styled-components';

export const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

export const AssessmentHome: FunctionComponent<{ assessmentType: string }> = observer((props) => {
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

    const title = assessmentType == 'phq-9' ? 'Progress_phq_assessment_title' : 'Progress_gad_assessment_title';
    const detail_title =
        assessmentType == 'phq-9' ? 'Progress_phq_assessment_detail_title' : 'Progress_gad_assessment_detail_title';
    const assessmentContent = rootStore.getAssessmentContent(assessmentType);

    const logs = patientStore.assessmentLogs.filter((a) => a.assessmentId.toLowerCase() == assessmentType);

    const getValueString = (pointValue: number | undefined) => {
        return `${assessmentContent?.options.find((o) => o.value == pointValue)?.text} (${pointValue})`;
    };

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
                                    <TableCell>{getString('Assessment_progress_column_total')}</TableCell>
                                    <TableCell>{getString('Assessment_progress_column_comment')}</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {logs.map((log, idx) => (
                                    <TableRow key={idx} hover onClick={() => handleLogClick(log)}>
                                        <TableCell component="th" scope="row">
                                            {`${format(log.recordedDateTime, 'MM/dd')}`}
                                        </TableCell>
                                        <WordBreakTableCell>
                                            {log.totalScore != undefined && log.totalScore >= 0
                                                ? log.totalScore
                                                : getAssessmentScore(log.pointValues)}
                                        </WordBreakTableCell>
                                        <WordBreakTableCell>{log.comment}</WordBreakTableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                        {viewState.selectedLog && (
                            <ProgressDialog
                                isOpen={viewState.isOpen}
                                title={getString(detail_title)}
                                content={
                                    <Table size="small" aria-label="a dense table">
                                        <TableBody>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Assessment_progress_column_date')}
                                                </TableCell>
                                                <WordBreakTableCell>{`${
                                                    viewState.selectedLog?.recordedDateTime &&
                                                    format(viewState.selectedLog.recordedDateTime, 'MM/dd')
                                                }`}</WordBreakTableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Assessment_progress_column_total')}
                                                </TableCell>
                                                <WordBreakTableCell>
                                                    {viewState.selectedLog?.totalScore != undefined &&
                                                    viewState.selectedLog?.totalScore >= 0
                                                        ? viewState?.selectedLog.totalScore
                                                        : !!viewState.selectedLog?.pointValues
                                                        ? getAssessmentScore(viewState.selectedLog?.pointValues)
                                                        : -1}
                                                </WordBreakTableCell>
                                            </TableRow>
                                            {viewState.selectedLog &&
                                                viewState.selectedLog.pointValues &&
                                                Object.keys(viewState.selectedLog.pointValues).map((key) => (
                                                    <TableRow key={key}>
                                                        <TableCell component="th" scope="row">
                                                            {key}
                                                        </TableCell>
                                                        <WordBreakTableCell>
                                                            {getValueString(viewState.selectedLog?.pointValues[key])}
                                                        </WordBreakTableCell>
                                                    </TableRow>
                                                ))}
                                            <TableRow>
                                                <TableCell component="th" scope="row">
                                                    {getString('Assessment_progress_column_comment')}
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
                    <Typography>{getString('Assessment_progress_no_data')}</Typography>
                )}
            </ContentLoader>
        </DetailPage>
    );
});

export default AssessmentHome;
