import {
    FormHelperText,
    Link,
    List,
    ListItem,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';
import { compareAsc } from 'date-fns';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { BehavioralActivationChecklistItem, behavioralActivationChecklistValues } from 'shared/enums';
import { formatDateOnly } from 'shared/time';
import { IResourceItem, ISession, KeyedMap } from 'shared/types';
import ActionPanel from 'src/components/common/ActionPanel';
import { getString } from 'src/services/strings';
import { usePatient, useStores } from 'src/stores/stores';

export const BAChecklist: FunctionComponent = observer(() => {
    const {
        appContentConfig: { registryresources },
    } = useStores();
    const currentPatient = usePatient();

    const baCompletion: { [key: string]: Date | undefined } = {};
    currentPatient?.sessions
        .slice()
        .sort((a, b) => compareAsc(a.date, b.date))
        .map((s) => s as ISession)
        .forEach((s) => {
            Object.keys(s.behavioralActivationChecklist).forEach((key) => {
                if (s.behavioralActivationChecklist[key as BehavioralActivationChecklistItem]) {
                    baCompletion[key] = s.date;
                }
            });
        });

    const resourcesMap = Object.assign({}, ...registryresources.map((r) => ({ [r.id]: r.resources }))) as KeyedMap<
        IResourceItem[]
    >;

    const baComponents = behavioralActivationChecklistValues.map((ba) => ({
        id: ba,
        name: ba,
        completedDate: baCompletion[ba],
        resources: resourcesMap[ba],
    }));

    const otherResources = resourcesMap[`Other`];

    const swResources = resourcesMap[`swresources`];

    const getResourceLink = (filename: string) => {
        return `/resources/${filename}`;
    };

    return (
        <ActionPanel
            id={getString('patient_detail_subsection_checklist_hash')}
            title={getString('patient_detail_subsection_checklist_title')}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadSessionsState.pending}
            error={currentPatient?.loadSessionsState.error}
            actionButtons={[]}>
            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>{getString('patient_behavioral_checklist_components_header')}</TableCell>
                            <TableCell>{getString('patient_behavioral_checklist_resources_header')}</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {baComponents.map((component) => (
                            <TableRow key={component.id}>
                                <TableCell component="th" scope="row" style={{ verticalAlign: 'top' }}>
                                    <Fragment>
                                        <div>{component.name}</div>
                                        {component.completedDate ? (
                                            <FormHelperText>{`Last performed on ${formatDateOnly(
                                                component.completedDate as Date,
                                                'MM/dd/yyyy',
                                            )}`}</FormHelperText>
                                        ) : (
                                            <FormHelperText>
                                                {getString('patient_behavioral_checklist_not_completed')}
                                            </FormHelperText>
                                        )}
                                    </Fragment>
                                </TableCell>
                                <TableCell>
                                    <Fragment>
                                        <List dense disablePadding>
                                            {component.resources &&
                                                component.resources.length > 0 &&
                                                component.resources.map((resource, idx) => (
                                                    <ListItem dense disableGutters key={`${resource.name}-${idx}`}>
                                                        <Link href={getResourceLink(resource.filename)} target="_blank">
                                                            {resource.name}
                                                        </Link>
                                                    </ListItem>
                                                ))}
                                        </List>
                                    </Fragment>
                                </TableCell>
                            </TableRow>
                        ))}
                        <TableRow>
                            <TableCell component="th" scope="row" style={{ verticalAlign: 'top' }}>
                                Other Patient Resources
                            </TableCell>
                            <TableCell>
                                <List dense disablePadding>
                                    {otherResources &&
                                        otherResources.length > 0 &&
                                        otherResources.map((resource, idx) => (
                                            <ListItem dense disableGutters key={`${resource.name}-${idx}`}>
                                                <Link href={getResourceLink(resource.filename)} target="_blank">
                                                    {resource.name}
                                                </Link>
                                            </ListItem>
                                        ))}
                                </List>
                            </TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell component="th" scope="row" style={{ verticalAlign: 'top' }}>
                                Social Worker Resources
                            </TableCell>
                            <TableCell>
                                <List dense disablePadding>
                                    {swResources &&
                                        swResources.length > 0 &&
                                        swResources.map((resource, idx) => (
                                            <ListItem dense disableGutters key={`${resource.name}-${idx}`}>
                                                <Link href={getResourceLink(resource.filename)} target="_blank">
                                                    {resource.name}
                                                </Link>
                                            </ListItem>
                                        ))}
                                </List>
                            </TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableContainer>
        </ActionPanel>
    );
});

export default BAChecklist;
