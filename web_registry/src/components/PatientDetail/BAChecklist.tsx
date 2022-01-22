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
import { compareAsc, format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { BehavioralActivationChecklistItem, behavioralActivationChecklistValues } from 'shared/enums';
import { IResourceItem, ISession, KeyedMap } from 'shared/types';
import ActionPanel from 'src/components/common/ActionPanel';
import { getString } from 'src/services/strings';
import { usePatient, useStores } from 'src/stores/stores';

export const BAChecklist: FunctionComponent = observer(() => {
    const {
        appConfig: { resources },
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

    const resourcesMap = Object.assign({}, ...resources.map((r) => ({ [r.id]: r.resources }))) as KeyedMap<
        IResourceItem[]
    >;

    const baComponents = behavioralActivationChecklistValues.map((ba) => ({
        id: ba,
        name: ba,
        completedDate: baCompletion[ba],
        resources: resourcesMap[ba],
    }));

    const getResourceLink = (filename: string) => {
        return `/resources/${filename}`;
    };

    return (
        <ActionPanel
            id={getString('patient_detail_subsection_checklist_hash')}
            title={getString('patient_detail_subsection_checklist_title')}
            loading={currentPatient?.state == 'Pending'}
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
                                            <FormHelperText>{`Last performed on ${format(
                                                component.completedDate as Date,
                                                'MM/dd/yyyy'
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
                                                component.resources.map((resource) => (
                                                    <ListItem dense disableGutters key={resource.name}>
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
                    </TableBody>
                </Table>
            </TableContainer>
        </ActionPanel>
    );
});

export default BAChecklist;
