import AssignmentIcon from '@mui/icons-material/Assignment';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import { Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import { format } from 'date-fns';
import { observer } from 'mobx-react-lite';
import React, { FunctionComponent } from 'react';
import { KeyedMap } from 'shared/types';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { getString } from 'src/services/strings';
import { usePatient, useStores } from 'src/stores/stores';

export const ValuesInventory: FunctionComponent = observer(() => {
    const {
        appContentConfig: { lifeAreas },
    } = useStores();
    const currentPatient = usePatient();
    const { valuesInventory } = currentPatient;
    const { assigned, assignedDateTime, lastUpdatedDateTime, values } = valuesInventory;

    const lifeareaMap = Object.assign({}, ...lifeAreas.map((la) => ({ [la.id]: la.name }))) as KeyedMap<string>;

    const activities = values
        ?.map((v) => {
            return v.activities.map((a) => {
                return {
                    value: v.name,
                    lifearea: lifeareaMap[v.lifeareaId],
                    name: a.name,
                    enjoyment: a.enjoyment,
                    importance: a.importance,
                    lastEdited: a.editedDateTime,
                };
            });
        })
        .reduce((a, b) => a.concat(b), []);

    var dateStrings: string[] = [];
    if (assigned && !!assignedDateTime) {
        dateStrings.push(
            `${getString('patient_values_inventory_assigned_date')} ${format(assignedDateTime, 'MM/dd/yyyy')}`,
        );
    }

    if (!!lastUpdatedDateTime) {
        dateStrings.push(
            `${getString('patient_values_inventory_activity_date_header')} ${format(
                lastUpdatedDateTime,
                'MM/dd/yyyy',
            )}`,
        );
    }

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
                {!activities || activities.length == 0 ? (
                    <Grid item xs={12}>
                        <Typography>{getString('patient_values_inventory_empty')}</Typography>
                    </Grid>
                ) : (
                    <TableContainer>
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
                                {activities.map((activity, idx) => (
                                    <TableRow key={idx}>
                                        <TableCell component="th" scope="row">
                                            {!!activity.lastEdited ? format(activity.lastEdited, 'MM/dd/yyyy') : '--'}
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
                    </TableContainer>
                )}
            </Grid>
        </ActionPanel>
    );
});

export default ValuesInventory;
