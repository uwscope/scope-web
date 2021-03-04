import { Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@material-ui/core';
import { format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel from 'src/components/common/ActionPanel';
import { useStores } from 'src/stores/stores';
import { last } from 'src/utils/array';

export const AssessmentInfo: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    return (
        <ActionPanel
            id="assessments"
            title="Assessments"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[]}>
            <Grid container spacing={2} alignItems="stretch">
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Assessment</TableCell>
                                <TableCell>Frequency</TableCell>
                                <TableCell>Last completed</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {currentPatient?.assessments.map((a) => {
                                return (
                                    <TableRow hover key={a.assessmentType}>
                                        <TableCell component="th" scope="row">
                                            {a.assessmentType}
                                        </TableCell>
                                        <TableCell>{a.frequency}</TableCell>
                                        <TableCell>
                                            {a.data.length > 0
                                                ? format(last(a.data)?.date as Date, 'MM/dd/yyyy')
                                                : 'NA'}
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Grid>
        </ActionPanel>
    );
});

export default AssessmentInfo;
