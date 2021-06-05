import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { compareAsc, compareDesc } from 'date-fns';
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
import { SessionReviewTable } from 'src/components/PatientDetail/SessionReviewTable';
import { EntryType, referralStatusValues, sessionTypeValues } from 'src/services/enums';
import { ICaseReview, ISession, ISessionOrCaseReview } from 'src/services/types';
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

const defaultReview: ICaseReview = {
    reviewId: 'new',
    date: new Date(),
    consultingPsychiatrist: '',
    medicationChange: '',
    behavioralStrategyChange: '',
    referralsChange: '',
    otherRecommendations: '',
    reviewNote: '',
};

const state = observable<{
    open: boolean;
    isNew: boolean;
    dateAsc: boolean;
    entryType: EntryType;
    session: ISession;
    review: ICaseReview;
}>({
    open: false,
    isNew: false,
    dateAsc: false,
    session: defaultSession,
    review: defaultReview,
    entryType: 'Session',
});

const SessionEdit: FunctionComponent = observer(() => {
    const onValueChange = action((key: string, value: any) => {
        (state.session as any)[key] = value;
    });

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDateField
                editable={true}
                label="Session Date"
                value={state.session.date}
                onChange={(text) => onValueChange('date', text)}
            />
            <GridDropdownField
                editable={true}
                label="Session Type"
                value={state.session.sessionType}
                options={sessionTypeValues}
                onChange={(text) => onValueChange('sessionType', text)}
            />
            <GridTextField
                editable={true}
                label="Billable Minutes"
                value={state.session.billableMinutes}
                onChange={(text) => onValueChange('billableMinutes', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Medication changes"
                value={state.session.medicationChange}
                placeholder="Leave blank if no change in current medications"
                onChange={(text) => onValueChange('medicationChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Current medications"
                value={state.session.currentMedications}
                onChange={(text) => onValueChange('currentMedications', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                label="Behavioral Strategies"
                flags={state.session.behavioralStrategyChecklist}
                other={state.session.behavioralStrategyOther}
                onChange={(flags) => onValueChange('behavioralStrategyChecklist', flags)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                disabled={!state.session.behavioralStrategyChecklist['Behavioral Activation']}
                label="Behavioral Activation Checklist"
                flags={state.session.behavioralActivationChecklist}
                onChange={(flags) => onValueChange('behavioralActivationChecklist', flags)}
            />
            <GridMultiOptionsField
                sm={12}
                editable={true}
                label="Referrals"
                flags={state.session.referralStatus}
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
                value={state.session.otherRecommendations}
                onChange={(text) => onValueChange('otherRecommendations', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={10}
                label="Session Note"
                value={state.session.sessionNote}
                placeholder="Write session notes here"
                onChange={(text) => onValueChange('sessionNote', text)}
            />
        </Grid>
    );
});

const ReviewEdit: FunctionComponent = observer(() => {
    const onValueChange = action((key: string, value: any) => {
        (state.review as any)[key] = value;
    });

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDateField
                editable={true}
                label="Review Date"
                value={state.review.date}
                onChange={(text) => onValueChange('date', text)}
            />
            <GridTextField
                editable={true}
                label="Consulting Psychiatrist"
                value={state.review.consultingPsychiatrist}
                onChange={(text) => onValueChange('consultingPsychiatrist', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Medication changes"
                value={state.review.medicationChange}
                placeholder="Leave blank if no change in current medications"
                onChange={(text) => onValueChange('medicationChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Behavioral strategy changes"
                value={state.review.behavioralStrategyChange}
                placeholder="Leave blank if no change to behavioral strategies"
                onChange={(text) => onValueChange('behavioralStrategyChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Referral changes"
                value={state.review.referralsChange}
                placeholder="Leave blank if no change to referrals"
                onChange={(text) => onValueChange('referralsChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={4}
                label="Other recommendations / action items"
                value={state.review.otherRecommendations}
                onChange={(text) => onValueChange('otherRecommendations', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                maxLine={10}
                label="Review Note"
                value={state.review.reviewNote}
                placeholder="Write review notes here"
                onChange={(text) => onValueChange('reviewNote', text)}
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
        Object.assign(state.session, defaultSession);
        state.open = true;
        state.isNew = true;
        state.entryType = 'Session';
        state.session.sessionId = 'new';
    });

    const handleAddReview = action(() => {
        Object.assign(state.review, defaultReview);
        state.open = true;
        state.isNew = true;
        state.entryType = 'Case Review';
        state.review.reviewId = 'new';
    });

    const handleEditSession = action((sessionId: string) => {
        const session = currentPatient.sessions.find((s) => s.sessionId == sessionId);
        Object.assign(state.session, session);
        state.open = true;
        state.isNew = false;
        state.entryType = 'Session';
    });

    const handleEditReview = action((reviewId: string) => {
        const review = currentPatient.caseReviews.find((s) => s.reviewId == reviewId);
        Object.assign(state.review, review);
        state.open = true;
        state.isNew = false;
        state.entryType = 'Case Review';
    });

    const onSave = action(() => {
        const { session, review, entryType } = state;
        if (entryType == 'Session') {
            currentPatient.updateSession(session);
        } else if (entryType == 'Case Review') {
            currentPatient.updateCaseReview(review);
        }
        state.open = false;
    });

    const sortedSessionOrReviews = (currentPatient.sessions as ISessionOrCaseReview[])
        .concat(currentPatient.caseReviews)
        .slice()
        .sort((a, b) => (state.dateAsc ? compareAsc(a.date, b.date) : compareDesc(a.date, b.date)));

    return (
        <ActionPanel
            id="sessions"
            title="Sessions"
            loading={currentPatient.state == 'Pending'}
            actionButtons={[
                { icon: <AddIcon />, text: 'Add Case Review', onClick: handleAddReview } as IActionButton,
                { icon: <AddIcon />, text: 'Add Session', onClick: handleAddSession } as IActionButton,
            ]}>
            <SessionReviewTable
                sessionOrReviews={sortedSessionOrReviews}
                assessments={currentPatient.assessments}
                onReviewClick={handleEditReview}
                onSessionClick={handleEditSession}
            />
            <Dialog open={state.open} onClose={handleClose} maxWidth="md">
                <DialogTitle>{`${state.isNew ? 'Add' : 'Edit'} ${state.entryType} Information`}</DialogTitle>
                <DialogContent>{state.entryType == 'Session' ? <SessionEdit /> : <ReviewEdit />}</DialogContent>
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
