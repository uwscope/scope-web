import { withTheme } from '@material-ui/core';
import { format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import LabeledField, { FlaggedField } from 'src/components/common/LabeledField';
import { DiscussionFlag } from 'src/services/enums';
import { usePatient } from 'src/stores/stores';
import styled from 'styled-components';

const Container = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(2.5),
    }))
);

const state = observable<{ open: boolean }>({
    open: false,
});

export const PatientCardExtended: FunctionComponent = observer((_) => {
    const patient = usePatient();

    const onToggleFlag = action((flag: DiscussionFlag, flagged: boolean) => {
        patient.discussionFlag[flag] = flagged;
        patient?.updatePatientData(patient);
        state.open = false;
    });

    const sessionCount = patient.sessions.length;
    const firstSession = sessionCount > 0 ? format(patient.sessions[0].date, 'MM/dd/yyyy') : '--';
    const lastSession = sessionCount > 0 ? format(patient.sessions[sessionCount - 1].date, 'MM/dd/yyyy') : '--';

    const flaggedForDiscussion = patient?.discussionFlag['Flag for discussion'];
    const flaggedForSafety = patient?.discussionFlag['Flag as safety risk'];

    return (
        <Container>
            {sessionCount > 0 ? (
                <div>
                    <LabeledField label="Session #" value={sessionCount} />
                    <LabeledField label="First Session" value={firstSession} />
                    <LabeledField label="Last Session" value={lastSession} />
                    <br />
                </div>
            ) : null}

            <LabeledField label="Flags" value="" />
            <FlaggedField
                label="Discussion"
                flagged={flaggedForDiscussion}
                onClick={() => onToggleFlag('Flag for discussion', !flaggedForDiscussion)}
            />
            <FlaggedField
                label="Safety risk"
                flagged={flaggedForSafety}
                onClick={() => onToggleFlag('Flag as safety risk', !flaggedForSafety)}
            />
        </Container>
    );
});

export default PatientCardExtended;
