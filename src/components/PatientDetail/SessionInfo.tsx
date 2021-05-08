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
    TableCellProps,
    TableHead,
    TableRow,
    withTheme,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { compareDesc, format } from 'date-fns';
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
import { ISession, KeyedMap } from 'src/services/types';
import { usePatient } from 'src/stores/stores';
import styled, { ThemedStyledProps } from 'styled-components';

const SizableTableCell = withTheme(
    styled(TableCell)((props: ThemedStyledProps<TableCellProps & { $width: number }, any>) => ({
        minWidth: props.$width,
    }))
);

const HorizontalScrollTable = styled(Table)({
    overflowX: 'auto',
    width: '100%',
    display: 'block',
});

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
        currentPatient.updateSession(sessionData);
        state.open = false;
    });

    const generateFlagText = (flags: KeyedMap<boolean | string>, other: string) => {
        var concatValues = Object.keys(flags)
            .filter((k) => flags[k] && k != 'Other')
            .join('\n');
        if (flags['Other']) {
            concatValues = [concatValues, other].join('\n');
        }

        return concatValues;
    };

    const sortedSessions = currentPatient.sessions.slice().sort((a, b) => compareDesc(a.date, b.date));

    return (
        <ActionPanel
            id="sessions"
            title="Sessions"
            loading={currentPatient.state == 'Pending'}
            actionButtons={[{ icon: <AddIcon />, text: 'Add Session', onClick: handleAddSession } as IActionButton]}>
            <Grid container alignItems="stretch">
                <HorizontalScrollTable size="small">
                    <TableHead>
                        <TableRow>
                            <SizableTableCell $width={80}>Date</SizableTableCell>
                            <SizableTableCell $width={80}>Type</SizableTableCell>
                            <SizableTableCell $width={80}>Billable Minutes</SizableTableCell>
                            <SizableTableCell $width={120}>Medications</SizableTableCell>
                            <SizableTableCell $width={200}>Behavioral Strategies</SizableTableCell>
                            <SizableTableCell $width={200}>Referrals</SizableTableCell>
                            <SizableTableCell $width={200}>Other Reco/Action Items</SizableTableCell>
                            <SizableTableCell $width={300}>Notes</SizableTableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {sortedSessions.map((session, idx) => (
                            <ClickableTableRow hover key={idx} onClick={() => handleEditSession(session)}>
                                <TableCell>{format(session.date, 'MM/dd/yyyy')}</TableCell>
                                <TableCell>{session.sessionType}</TableCell>
                                <TableCell>{session.billableMinutes}</TableCell>
                                <TableCell>{session.medicationChange}</TableCell>
                                <TableCell>
                                    {generateFlagText(
                                        session.behavioralStrategyChecklist,
                                        session.behavioralStrategyOther
                                    )}
                                </TableCell>
                                <TableCell>{generateFlagText(session.referralStatus, session.referralOther)}</TableCell>
                                <TableCell>{session.otherRecommendations}</TableCell>
                                <TableCell>{session.sessionNote}</TableCell>
                            </ClickableTableRow>
                        ))}
                    </TableBody>
                </HorizontalScrollTable>
            </Grid>
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
