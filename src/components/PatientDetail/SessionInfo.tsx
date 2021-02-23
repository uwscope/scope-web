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
import GridChecklist from 'src/components/common/GridChecklist';
import { GridDateField, GridDropdownField, GridTextField } from 'src/components/common/GridField';
import {
    BehavioralActivationChecklistItem,
    SessionType,
    sessionTypeValues,
    TreatmentChange,
    treatmentChangeValues,
    TreatmentPlan,
    treatmentPlanValues,
} from 'src/services/enums';
import { ISession } from 'src/services/types';
import { useStores } from 'src/stores/stores';

interface ISessionEditState {
    date: Date;
    sessionType: SessionType;
    billableMinutes: number;
    treatmentPlan: TreatmentPlan;
    treatmentChange: TreatmentChange;
    behavioralActivationChecklist: { [item in BehavioralActivationChecklistItem]: boolean };
    sessionNote: string;
}

const defaultSession: ISessionEditState = {
    date: new Date(),
    sessionType: 'In person at clinic',
    billableMinutes: 0,
    treatmentPlan: 'Maintain current treatment',
    treatmentChange: 'None',
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
    sessionNote: '',
};

const state = observable<{ open: boolean; isNew: boolean } & ISessionEditState>({
    open: false,
    isNew: false,
    ...defaultSession,
});

const SessionEdit: FunctionComponent = observer(() => {
    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    const onChecklistChange = action((key: string, value: boolean) => {
        state.behavioralActivationChecklist[key as BehavioralActivationChecklistItem] = value;
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
            <GridDropdownField
                editable={true}
                label="Treatment Plan"
                value={state.treatmentPlan}
                options={treatmentPlanValues}
                onChange={(text) => onValueChange('treatmentPlan', text)}
            />
            <GridDropdownField
                editable={true}
                label="Treatment Change"
                value={state.treatmentChange}
                options={treatmentChangeValues}
                onChange={(text) => onValueChange('treatmentChange', text)}
            />
            <GridTextField
                fullWidth={true}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Session Note"
                value={state.sessionNote}
                placeholder="Write session notes here"
                onChange={(text) => onValueChange('sessionNote', text)}
            />
            <GridChecklist
                fullWidth={true}
                editable={true}
                label="Behavioral Activation Checklist"
                values={state.behavioralActivationChecklist}
                onCheck={onChecklistChange}
            />
        </Grid>
    );
});

export const SessionInfo: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const handleClose = action(() => {
        state.open = false;
    });

    const handleAddSession = action(() => {
        Object.assign(state, defaultSession);
        state.open = true;
        state.isNew = true;
    });

    const handleEditSession = action((session: ISession) => {
        Object.assign(state, session);
        state.open = true;
        state.isNew = false;
    });

    const onSave = action(() => {
        const { open, ...sessionData } = { ...state };
        currentPatient?.addSession(sessionData);
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
                        {currentPatient?.sessions.map((session) => (
                            <TableRow key={session.sessionId} onClick={() => handleEditSession(session)}>
                                <TableCell component="th" scope="row">
                                    {session.sessionId}
                                </TableCell>
                                <TableCell>{format(session.date, 'MM/dd/yyyy')}</TableCell>
                                <TableCell>{session.sessionType}</TableCell>
                                <TableCell>{session.billableMinutes}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <Dialog open={state.open} onClose={handleClose}>
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
