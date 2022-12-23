import AssignmentIcon from '@mui/icons-material/Assignment';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import { Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import { compareDesc, format } from 'date-fns';
import { observer } from 'mobx-react-lite';
import React, { FunctionComponent } from 'react';
import { IActivity } from 'shared/types';

import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { getString } from 'src/services/strings';
import { usePatient, useStores } from 'src/stores/stores';

export const ValuesInventory: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const currentPatient = usePatient();
    const { values, valuesInventory } = currentPatient;
    const { assigned, assignedDateTime } = valuesInventory;
    var dateStrings: string[] = [];
    if (assigned && !!assignedDateTime) {
        dateStrings.push(
            `${getString('patient_values_inventory_assigned_date')} ${format(assignedDateTime, 'MM/dd/yyyy')}`,
        );
    }
    const activitiesWithValue = values
        ?.map((v) => {
            return currentPatient.getActivitiesByValueId(v.valueId as string);
        })
        .reduce((a, b) => a.concat(b), [])
        .sort((a, b) => compareDesc(a.editedDateTime, b.editedDateTime));

    // TODO: Sort on life area and value.

    if (activitiesWithValue.length !== 0) {
        dateStrings.push(
            `${getString('patient_values_inventory_activity_date_header')} ${format(
                activitiesWithValue[0].editedDateTime as Date,
                'MM/dd/yyyy',
            )}`,
        );
    }

    const otherActivites = currentPatient
        .getActivitiesWithoutValueId()
        .sort((a, b) => compareDesc(a.editedDateTime, b.editedDateTime));

    const activityWithValueTableRow = (activity: IActivity, idx: number): JSX.Element => {
        const value = currentPatient.getValueById(activity.valueId as string);
        const lifeAreaContent = rootStore.getLifeAreaContent(value?.lifeAreaId as string);

        return (
            <TableRow key={idx}>
                <TableCell>{lifeAreaContent?.name}</TableCell>
                <TableCell>{value?.name}</TableCell>
                <TableCell component="th" scope="row">
                    {!!activity.editedDateTime ? format(activity.editedDateTime, 'MM/dd/yyyy') : '--'}
                </TableCell>
                <TableCell>{activity.name}</TableCell>
                <TableCell>{activity.enjoyment}</TableCell>
                <TableCell>{activity.importance}</TableCell>
            </TableRow>
        );
    };

    const otherActivityTableRow = (activity: IActivity, idx: number): JSX.Element => {
        return (
            <TableRow key={idx}>
                <TableCell>-</TableCell> {/*NOTE: Should this be "Other"*/}
                <TableCell>-</TableCell>
                <TableCell component="th" scope="row">
                    {!!activity.editedDateTime ? format(activity.editedDateTime, 'MM/dd/yyyy') : '--'}
                </TableCell>
                <TableCell>{activity.name}</TableCell>
                <TableCell>{activity.enjoyment}</TableCell>
                <TableCell>{activity.importance}</TableCell>
            </TableRow>
        );
    };

    return (
        <ActionPanel
            id={getString('patient_detail_subsection_values_inventory_hash')}
            title={getString('patient_detail_subsection_values_inventory_title')}
            inlineTitle={dateStrings.join(', ')}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadValuesInventoryState.pending}
            error={currentPatient?.loadValuesInventoryState.error}
            actionButtons={[
                {
                    icon: assigned ? <AssignmentTurnedInIcon /> : <AssignmentIcon />,
                    text: assigned
                        ? getString('patient_values_inventory_assigned_button')
                        : getString('patient_values_inventory_assign_button'),
                    onClick: () => currentPatient?.assignValuesInventory(),
                } as IActionButton,
            ]}>
            <Grid container spacing={2} alignItems="stretch">
                {(!activitiesWithValue || activitiesWithValue.length == 0) &&
                (!otherActivites || otherActivites.length == 0) ? (
                    <Grid item xs={12}>
                        <Typography>{getString('patient_values_inventory_empty')}</Typography>
                    </Grid>
                ) : (
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>
                                        {getString('patient_values_inventory_activity_lifearea_header')}
                                    </TableCell>
                                    <TableCell>{getString('patient_values_inventory_activity_value_header')}</TableCell>
                                    <TableCell>{getString('patient_values_inventory_activity_date_header')}</TableCell>
                                    <TableCell>{getString('patient_values_inventory_activity_name_header')}</TableCell>
                                    <TableCell>
                                        {getString('patient_values_inventory_activity_enjoyment_header')}
                                    </TableCell>
                                    <TableCell>
                                        {getString('patient_values_inventory_activity_importance_header')}
                                    </TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {activitiesWithValue.map((activity, idx) => activityWithValueTableRow(activity, idx))}
                                {otherActivites.map((activity, idx) => otherActivityTableRow(activity, idx))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
            </Grid>
        </ActionPanel>
    );
});

export default ValuesInventory;
