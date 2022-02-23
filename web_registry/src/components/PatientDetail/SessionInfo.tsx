import AddIcon from '@mui/icons-material/Add';
import { Grid } from '@mui/material';
import { compareAsc, compareDesc } from 'date-fns';
import { action, observable, runInAction } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import {
    behavioralActivationChecklistValues,
    behavioralStrategyChecklistValues,
    EntryType,
    Referral,
    ReferralStatus,
    ReferralStatusFlags,
    referralStatusValues,
    sessionTypeValues,
} from 'shared/enums';
import { toLocalDateOnly, toUTCDateOnly, clearTime } from 'shared/time';
import { ICaseReview, IReferralStatus, ISession, ISessionOrCaseReview, KeyedMap } from 'shared/types';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import {
    GridDateField,
    GridDropdownField,
    GridMultiOptionsField,
    GridMultiSelectField,
    GridTextField,
} from 'src/components/common/GridField';
import { SessionProgressVis } from 'src/components/common/SessionProgressVis';
import StatefulDialog from 'src/components/common/StatefulDialog';
import { SessionReviewTable } from 'src/components/PatientDetail/SessionReviewTable';
import { usePatient } from 'src/stores/stores';
import { getAssessmentScore } from 'src/utils/assessment';

const defaultSession: ISession = {
    date: clearTime(new Date()),
    sessionType: 'In person',
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
        'Positive reinforcement': false,
        'Managing avoidance behaviors': false,
        'Problem-solving': false,
    },

    referrals: [],

    otherRecommendations: '',
    sessionNote: '',
};

const defaultReview: ICaseReview = {
    date: clearTime(new Date()),
    consultingPsychiatrist: { identityId: '', name: '' },
    medicationChange: '',
    behavioralStrategyChange: '',
    referralsChange: '',
    otherRecommendations: '',
    reviewNote: '',
};

interface IState {
    open: boolean;
    isNew: boolean;
    dateAsc: boolean;
    entryType: EntryType;
    session: ISession;
    review: ICaseReview;
    referralStatusFlags: ReferralStatusFlags;
    otherReferralFlags: KeyedMap<ReferralStatus>;
}

const defaultState: IState = {
    open: false,
    isNew: false,
    dateAsc: false,
    session: defaultSession,
    review: defaultReview,
    entryType: 'Session',
    referralStatusFlags: {
        Psychiatry: 'Not Referred',
        Psychology: 'Not Referred',
        'Patient Navigation': 'Not Referred',
        'Integrative Medicine': 'Not Referred',
        'Spiritual Care': 'Not Referred',
        'Palliative Care': 'Not Referred',
    },
    otherReferralFlags: {},
};

const state = observable<IState>(defaultState);

const SessionEdit: FunctionComponent = observer(() => {
    const onSessionValueChange = action((key: string, value: any) => {
        (state.session as any)[key] = value;
    });

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDateField
                editable={true}
                required={true}
                label="Session Date"
                value={state.session.date}
                onChange={(text) => onSessionValueChange('date', text)}
            />
            <GridDropdownField
                editable={true}
                required={true}
                label="Session Type"
                value={state.session.sessionType}
                options={sessionTypeValues}
                onChange={(text) => onSessionValueChange('sessionType', text)}
            />
            <GridTextField
                editable={true}
                label="Billable Minutes"
                value={state.session.billableMinutes}
                onChange={(text) => onSessionValueChange('billableMinutes', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Medication changes"
                value={state.session.medicationChange}
                placeholder="Leave blank if no change in current medications"
                onChange={(text) => onSessionValueChange('medicationChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Current medications"
                helperText="Psychotropic and other relevant medications (e.g., steroids, hormone therapies, opioids, etc.)"
                value={state.session.currentMedications}
                onChange={(text) => onSessionValueChange('currentMedications', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                label="Behavioral Strategies"
                flags={Object.assign(
                    {},
                    ...behavioralStrategyChecklistValues.map((x) => ({
                        [x]: !!state.session.behavioralStrategyChecklist?.[x],
                    })),
                )}
                flagOrder={[...behavioralStrategyChecklistValues]}
                other={state.session.behavioralStrategyOther}
                onChange={(flags) => onSessionValueChange('behavioralStrategyChecklist', flags)}
                onOtherChange={(text) => onSessionValueChange('behavioralStrategyOther', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                disabled={!state.session.behavioralStrategyChecklist['Behavioral Activation']}
                label="Behavioral Activation Checklist"
                flags={Object.assign(
                    {},
                    ...behavioralActivationChecklistValues.map((x) => ({
                        [x]: !!state.session.behavioralActivationChecklist?.[x],
                    })),
                )}
                flagOrder={[...behavioralActivationChecklistValues]}
                onChange={(flags) => onSessionValueChange('behavioralActivationChecklist', flags)}
            />
            <GridMultiOptionsField
                sm={12}
                editable={true}
                label="Referrals"
                flags={state.referralStatusFlags}
                otherFlags={state.otherReferralFlags}
                options={referralStatusValues}
                notOption="Not Referred"
                defaultOption="Pending"
                onChange={(flags) => onValueChange('referralStatusFlags', flags)}
                onOtherChange={(otherFlags) => onValueChange('otherReferralFlags', otherFlags)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Other recommendations / action items"
                value={state.session.otherRecommendations}
                onChange={(text) => onSessionValueChange('otherRecommendations', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={10}
                label="Session Note"
                value={state.session.sessionNote}
                placeholder="Write session notes here"
                onChange={(text) => onSessionValueChange('sessionNote', text)}
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
                value={state.review.consultingPsychiatrist.name}
                onChange={(text) => onValueChange('consultingPsychiatrist', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
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
                minLine={4}
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
                minLine={4}
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
                minLine={4}
                maxLine={4}
                label="Other recommendations / action items"
                value={state.review.otherRecommendations}
                onChange={(text) => onValueChange('otherRecommendations', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
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

        currentPatient.loadSessionsState.resetState();
        currentPatient.loadCaseReviewsState.resetState();
    });

    const _copySessionToState = (session: ISession | undefined) => {
        // Copy over current medications and referral status from the latest session
        if (!!session) {
            state.session.currentMedications = session.currentMedications;
            state.session.referrals = session.referrals;

            state.referralStatusFlags = {
                Psychiatry: 'Not Referred',
                Psychology: 'Not Referred',
                'Patient Navigation': 'Not Referred',
                'Integrative Medicine': 'Not Referred',
                'Spiritual Care': 'Not Referred',
                'Palliative Care': 'Not Referred',
            };

            var sessionReferralFlags = {} as any;
            var otherReferralFlags = {} as any;

            session.referrals.forEach((ref) => {
                if (ref.referralType != 'Other') {
                    sessionReferralFlags[ref.referralType] = ref.referralStatus;
                } else {
                    otherReferralFlags[ref.referralOther || ref.referralType] = ref.referralStatus;
                }
            });

            Object.assign(state.referralStatusFlags, sessionReferralFlags);
            state.otherReferralFlags = otherReferralFlags;
        }
    };

    const handleAddSession = action(() => {
        Object.assign(state, defaultState);
        state.open = true;
        state.isNew = true;
        state.entryType = 'Session';

        _copySessionToState(currentPatient.latestSession);
    });

    const handleAddReview = action(() => {
        Object.assign(state.review, defaultReview);
        state.open = true;
        state.isNew = true;
        state.entryType = 'Case Review';
    });

    const handleEditSession = action((sessionId: string) => {
        const session = currentPatient.sessions.find((s) => s.sessionId == sessionId);

        state.session = { ...defaultSession, ...session };
        state.open = true;
        state.isNew = false;
        state.entryType = 'Session';
        if (!!session && session.date) {
            state.session.date = toLocalDateOnly(session.date);
        }

        _copySessionToState(session);
    });

    const handleEditReview = action((caseReviewId: string) => {
        const review = currentPatient.caseReviews.find((s) => s.caseReviewId == caseReviewId);

        state.review = { ...defaultReview, ...review };
        state.open = true;
        state.isNew = false;
        state.entryType = 'Case Review';
        if (!!review && review.date) {
            state.review.date = toLocalDateOnly(review.date);
        }
    });

    const onSave = action(async () => {
        const { session, review, entryType, referralStatusFlags, otherReferralFlags } = state;

        if (entryType == 'Session') {
            // Organize referral flags
            const updatedSession = { ...session };
            updatedSession.referrals = Object.keys(referralStatusFlags)
                .map(
                    (flag) =>
                        ({
                            referralType: flag,
                            referralStatus: referralStatusFlags[flag as Referral],
                        } as IReferralStatus),
                )
                .concat(
                    Object.keys(otherReferralFlags).map(
                        (flag) =>
                            ({
                                referralType: 'Other',
                                referralOther: flag,
                                referralStatus: otherReferralFlags[flag as Referral],
                            } as IReferralStatus),
                    ),
                )
                .filter((rs) => rs.referralStatus != 'Not Referred');

            updatedSession.date = toUTCDateOnly(session.date);

            if (!updatedSession.sessionId) {
                await currentPatient.addSession(updatedSession);
            } else {
                await currentPatient.updateSession(updatedSession);
            }
        } else if (entryType == 'Case Review') {
            const updatedReview = { ...review };
            updatedReview.date = toUTCDateOnly(review.date);

            if (!updatedReview.caseReviewId) {
                await currentPatient.addCaseReview(updatedReview);
            } else {
                await currentPatient.updateCaseReview(updatedReview);
            }
        }

        runInAction(() => {
            if (!currentPatient.loadClinicalHistoryState.error && !currentPatient.loadCaseReviewsState.error) {
                state.open = false;
            }
        });
    });

    const sortedSessionOrReviews = (currentPatient.sessions as ISessionOrCaseReview[])
        .concat(currentPatient.caseReviews)
        .slice()
        .sort((a, b) => (state.dateAsc ? compareAsc(a.date, b.date) : compareDesc(a.date, b.date)));

    const phqScores = currentPatient.assessmentLogs
        .filter((log) => log.assessmentId == 'phq-9')
        .map((log) => ({
            date: log.recordedDate,
            score: log.totalScore || getAssessmentScore(log.pointValues),
        }));

    const gadScores = currentPatient.assessmentLogs
        .filter((log) => log.assessmentId == 'gad-7')
        .map((log) => ({
            date: log.recordedDate,
            score: log.totalScore || getAssessmentScore(log.pointValues),
        }));

    const sessionDates = currentPatient.sessions
        .filter((s) => !!s.sessionId)
        .map((s) => ({
            date: s.date,
            id: s.sessionId as string,
        }));

    const reviewDates = currentPatient.caseReviews
        .filter((r) => !!r.caseReviewId)
        .map((r) => ({
            date: r.date,
            id: r.caseReviewId as string,
        }));

    const loading = currentPatient?.loadSessionsState.pending || currentPatient?.loadCaseReviewsState.pending;
    const error = currentPatient?.loadSessionsState.error || currentPatient?.loadCaseReviewsState.error;

    return (
        <ActionPanel
            id="sessions"
            title="Sessions and Reviews"
            loading={loading}
            error={error}
            showSnackbar={!state.open}
            actionButtons={[
                {
                    icon: <AddIcon />,
                    text: 'Add Case Review',
                    onClick: handleAddReview,
                } as IActionButton,
                {
                    icon: <AddIcon />,
                    text: 'Add Session',
                    onClick: handleAddSession,
                } as IActionButton,
            ]}>
            <Grid container alignItems="stretch">
                <SessionReviewTable
                    sessionOrReviews={sortedSessionOrReviews}
                    onReviewClick={handleEditReview}
                    onSessionClick={handleEditSession}
                />
                {currentPatient.assessmentLogs.length > 0 && sortedSessionOrReviews.length > 0 && (
                    <Grid item xs={12}>
                        <SessionProgressVis
                            phqScores={phqScores}
                            gadScores={gadScores}
                            sessions={sessionDates}
                            reviews={reviewDates}
                            onSessionClick={handleEditSession}
                            onReviewClick={handleEditReview}
                        />
                    </Grid>
                )}
            </Grid>
            <StatefulDialog
                open={state.open}
                error={error}
                loading={loading}
                handleCancel={handleClose}
                handleSave={onSave}
                title={`${state.isNew ? 'Add' : 'Edit'} ${state.entryType} Information`}
                content={state.entryType == 'Session' ? <SessionEdit /> : <ReviewEdit />}
                disableSave={!(state.session || state.review).date || !(state.session || state.review).sessionType}
            />
        </ActionPanel>
    );
});

export default SessionInfo;
