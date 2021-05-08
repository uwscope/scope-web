import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import {
    GridDateField,
    GridDropdownField,
    GridMultiOptionsField,
    GridMultiSelectField,
    GridTextField,
} from 'src/components/common/GridField';
import { ClickableTableRow } from 'src/components/common/Table';
import { referralStatusValues, sessionTypeValues } from 'src/services/enums';
import { ISession } from 'src/services/types';
import { usePatient } from 'src/stores/stores';

const defaultSession: ISession = {
    sessionId: 'new',
    date: new Date(),
    sessionType: 'In person at clinic',
    billableMinutes: 0,
    medicationChange: '',
    currentMedications: '',
    behavioralStrategyChecklist: {
        'Behavioral Activation': false,
        'Motivational Interviewing': false,
        'Problem Solving Therapy': false,
        'Cognitive Therapy': false,
        'Mindfulness Strategies': false,
        'Supportive Therapy': false,
        Other: false,
    },
    behavioralStrategyOther: '',
    behavioralActivationChecklist: {
        'Review of the BA model': false,
        'Values and goals assessment': false,
        'Activity scheduling': false,
        'Mood and activity monitoring': false,
        Relaxation: false,
        'Contingency management': false,
        'Managing avoidance behaviors': false,
        'Problem-solving': false,
    },
    referralStatus: {
        Psychiatry: 'Not Referred',
        Psychology: 'Not Referred',
        'Patient Navigation': 'Not Referred',
        'Integrative Medicine': 'Not Referred',
        'Spiritual Care': 'Not Referred',
        'Palliative Care': 'Not Referred',
        Other: 'Not Referred',
    },
    referralOther: '',
    otherRecommendations: '',
    sessionNote: '',
};

const state = observable<{ open: boolean; isNew: boolean } & ISession>({
    open: false,
    isNew: false,
    ...defaultSession,
});

const SessionEdit: FunctionComponent = observer(() => {
    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDateField
                editable={true}
                label="Session Date"
                value={state.date}
                onChange={(text) => onValueChange('date', text)}
            />
            <GridDropdownField
                editable={true}
                label="Session Type"
                value={state.sessionType}
                options={sessionTypeValues}
                onChange={(text) => onValueChange('sessionType', text)}
            />
            <GridTextField
                editable={true}
                label="Billable Minutes"
                value={state.billableMinutes}
                onChange={(text) => onValueChange('billableMinutes', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Medication changes"
                value={state.medicationChange}
                placeholder="Leave blank if no change in current medications"
                onChange={(text) => onValueChange('medicationChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Current medications"
                value={state.currentMedications}
                onChange={(text) => onValueChange('currentMedications', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                label="Behavioral Strategies"
                flags={state.behavioralStrategyChecklist}
                other={state.behavioralStrategyOther}
                onChange={(flags) => onValueChange('behavioralStrategyChecklist', flags)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                disabled={!state.behavioralStrategyChecklist['Behavioral Activation']}
                label="Behavioral Activation Checklist"
                flags={state.behavioralActivationChecklist}
                onChange={(flags) => onValueChange('behavioralActivationChecklist', flags)}
            />
            <GridMultiOptionsField
                sm={12}
                editable={true}
                label="Referrals"
                flags={state.referralStatus}
                options={referralStatusValues.filter((r) => r != 'Not Referred')}
                notOption="Not Referred"
                onChange={(flags) => onValueChange('referralStatus', flags)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Other recommendations / action items"
                value={state.otherRecommendations}
                onChange={(text) => onValueChange('otherRecommendations', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={10}
                label="Session Note"
                value={state.sessionNote}
                placeholder="Write session notes here"
                onChange={(text) => onValueChange('sessionNote', text)}
            />
        </Grid>
    );
});

export const SessionInfo: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const handleClose = action(() => {
        state.open = false;
    });

    const handleAddSession = action(() => {
        Object.assign(state, defaultSession);
        state.open = true;
        state.isNew = true;
        state.sessionId = 'new';
    });

    const handleEditSession = action((session: ISession) => {
        Object.assign(state, session);
        state.open = true;
        state.isNew = false;
    });

    const onSave = action(() => {
        const { open, ...sessionData } = { ...state };
        currentPatient?.updateSession(sessionData);
        state.open = false;
    });

    return (
        <ActionPanel
            id="sessions"
            title="Sessions"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={[{ icon: <AddIcon />, text: 'Add Session', onClick: handleAddSession } as IActionButton]}>
            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Session Id</TableCell>
                            <TableCell>Date</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Billable Minutes</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {currentPatient?.sessions.map((session, idx) => (
                            <ClickableTableRow hover key={session.sessionId} onClick={() => handleEditSession(session)}>
                                <TableCell component="th" scope="row">
                                    {idx == 0 ? 'Initial assessment' : `${idx}`}
                                </TableCell>
                                <TableCell>{format(session.date, 'MM/dd/yyyy')}</TableCell>
                                <TableCell>{session.sessionType}</TableCell>
                                <TableCell>{session.billableMinutes}</TableCell>
                            </ClickableTableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <Dialog open={state.open} onClose={handleClose} maxWidth="md">
                <DialogTitle>{`${state.isNew ? 'Add' : 'Edit'} Session Information`}</DialogTitle>
                <DialogContent>
                    <SessionEdit />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={onSave} color="primary">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default SessionInfo;
