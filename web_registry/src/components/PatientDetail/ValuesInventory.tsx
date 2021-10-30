import { Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@material-ui/core';
import AssignmentIcon from '@material-ui/icons/Assignment';
import AssignmentTurnedInIcon from '@material-ui/icons/AssignmentTurnedIn';
import { format } from 'date-fns';
import { observer } from 'mobx-react-lite';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { getString } from 'src/services/strings';
import { KeyedMap } from 'src/services/types';
import { usePatient, useStores } from 'src/stores/stores';

export const ValuesInventory: FunctionComponent = observer(() => {
    const {
        appConfig: { lifeAreas },
    } = useStores();
    const currentPatient = usePatient();
    const { valuesInventory } = currentPatient;
    const { assigned, assignedDate, values } = valuesInventory;

    const lifeareaMap = Object.assign({}, ...lifeAreas.map((la) => ({ [la.id]: la.name }))) as KeyedMap<string>;

    const activities = values
        .map((v) => {
            return v.activities.map((a) => {
                return {
                    id: a.id,
                    value: v.name,
                    lifearea: lifeareaMap[v.lifeareaId],
                    name: a.name,
                    enjoyment: a.enjoyment,
                    importance: a.importance,
                    lastEdited: a.dateEdited,
                };
            });
        })
        .reduce((a, b) => a.concat(b), []);

    return (
        <ActionPanel
            id={getString('patient_detail_subsection_values_inventory_hash')}
            title={getString('patient_detail_subsection_values_inventory_title')}
            inlineTitle={
                assigned
                    ? `${getString('patient_values_inventory_assigned_date')} ${format(assignedDate, 'MM/dd/yyyy')}`
                    : ''
            }
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[
                {
                    icon: assigned ? <AssignmentTurnedInIcon /> : <AssignmentIcon />,
                    text: assigned
                        ? getString('patient_values_inventory_assigned_button')
                        : getString('patient_values_inventory_assign_button'),
                    onClick: assigned ? undefined : () => currentPatient?.assignValuesInventory(),
                } as IActionButton,
            ]}>
            <Grid container spacing={2} alignItems="stretch">
                <TableContainer>
                    {!activities || activities.length == 0 ? (
                        <Grid item xs={12}>
                            <Typography>{getString('patient_values_inventory_empty')}</Typography>
                        </Grid>
                    ) : (
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>{getString('patient_values_inventory_activity_date_header')}</TableCell>
                                    <TableCell>{getString('patient_values_inventory_activity_name_header')}</TableCell>
                                    <TableCell>
                                        {getString('patient_values_inventory_activity_enjoyment_header')}
                                    </TableCell>
                                    <TableCell>
                                        {getString('patient_values_inventory_activity_importance_header')}
                                    </TableCell>
                                    <TableCell>
                                        {getString('patient_values_inventory_activity_lifearea_header')}
                                    </TableCell>
                                    <TableCell>{getString('patient_values_inventory_activity_value_header')}</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {activities.map((activity) => (
                                    <TableRow key={activity.id}>
                                        <TableCell component="th" scope="row">
                                            {format(activity.lastEdited, 'MM/dd/yyyy')}
                                        </TableCell>
                                        <TableCell>{activity.name}</TableCell>
                                        <TableCell>{activity.enjoyment}</TableCell>
                                        <TableCell>{activity.importance}</TableCell>
                                        <TableCell>{activity.lifearea}</TableCell>
                                        <TableCell>{activity.value}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </TableContainer>
            </Grid>
        </ActionPanel>
    );
});

export default ValuesInventory;
