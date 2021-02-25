import { Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@material-ui/core';
import { format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel from 'src/components/common/ActionPanel';
import { MoodMap } from 'src/services/types';
import { useStores } from 'src/stores/stores';
import { last, mean } from 'src/utils/array';

export const BAActivities: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    return (
        <ActionPanel id="activities" title="Activities" loading={currentPatient?.state == 'Pending'} actionButtons={[]}>
            <Grid container spacing={2} alignItems="stretch">
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Activity</TableCell>
                                <TableCell>Mood pattern</TableCell>
                                <TableCell>Average mood</TableCell>
                                <TableCell>Completion rate</TableCell>
                                <TableCell>Last completed</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {currentPatient?.activities.map((activity) => {
                                const moodAvg = mean(activity.moodData.map((m) => (m.pointValues as MoodMap)['Mood']));
                                return (
                                    <TableRow key={activity.activityId}>
                                        <TableCell component="th" scope="row">
                                            {activity.activityName}
                                        </TableCell>
                                        <TableCell>TBD</TableCell>
                                        <TableCell>{activity.moodData.length > 0 ? moodAvg : 'NA'}</TableCell>
                                        <TableCell>TBD</TableCell>
                                        <TableCell>
                                            {activity.moodData.length > 0
                                                ? format(last(activity.moodData)?.date as Date, 'MM/dd/yyyy')
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

export default BAActivities;
