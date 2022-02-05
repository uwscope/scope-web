import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { format } from 'date-fns';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { useNavigate } from 'react-router';
import { IAssessmentLog } from 'shared/types';
import { DetailPage } from 'src/components/common/DetailPage';
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

    const viewState = useLocalObservable<{ selectedLog?: IAssessmentLog }>(() => ({}));

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const handleLogClick = action((log: IAssessmentLog) => {
        viewState.selectedLog = log;
    });

    const handleClose = action(() => {
        viewState.selectedLog = undefined;
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
                                        {`${format(log.recordedDate, 'MM/dd')}`}
                                    </TableCell>
                                    <TableCell>{getAssessmentScore(log.pointValues)}</TableCell>
                                    <TableCell>{log.comment}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>

                    <ProgressDialog
                        isOpen={!!viewState.selectedLog}
                        title={getString(detail_title)}
                        content={
                            <Table size="small" aria-label="a dense table">
                                <TableBody>
                                    <TableRow>
                                        <TableCell component="th" scope="row">
                                            {getString('Assessment_progress_column_date')}
                                        </TableCell>
                                        <TableCell>{`${
                                            viewState.selectedLog?.recordedDate &&
                                            format(viewState.selectedLog.recordedDate, 'MM/dd')
                                        }`}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell component="th" scope="row">
                                            {getString('Assessment_progress_column_total')}
                                        </TableCell>
                                        <TableCell>
                                            {!!viewState.selectedLog?.pointValues
                                                ? getAssessmentScore(viewState.selectedLog?.pointValues)
                                                : -1}
                                        </TableCell>
                                    </TableRow>
                                    {viewState.selectedLog &&
                                        Object.keys(viewState.selectedLog.pointValues).map((key) => (
                                            <TableRow key={key}>
                                                <TableCell component="th" scope="row">
                                                    {key}
                                                </TableCell>
                                                <TableCell>
                                                    {getValueString(viewState.selectedLog?.pointValues[key])}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    <TableRow>
                                        <TableCell component="th" scope="row">
                                            {getString('Assessment_progress_column_comment')}
                                        </TableCell>
                                        <TableCell>{viewState.selectedLog?.comment}</TableCell>
                                    </TableRow>
                                </TableBody>
                            </Table>
                        }
                        onClose={handleClose}
                    />
                </Fragment>
            ) : (
                <Typography>{getString('Assessment_progress_no_data')}</Typography>
            )}
        </DetailPage>
    );
});

export default AssessmentHome;
