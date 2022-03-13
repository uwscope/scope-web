import AddIcon from '@mui/icons-material/Add';
import { Grid } from '@mui/material';
import { compareAsc, compareDesc } from 'date-fns';
import { action, runInAction } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
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
import { usePatient, useStores } from 'src/stores/stores';
import { getAssessmentScoreFromPointValues } from 'src/utils/assessment';

const getDefaultSession = () =>
    ({
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
    } as ISession);

const getDefaultReview = () =>
    ({
        date: clearTime(new Date()),
        consultingPsychiatrist: { providerId: '', name: '' },
        medicationChange: '',
        behavioralStrategyChange: '',
        referralsChange: '',
        otherRecommendations: '',
        reviewNote: '',
    } as ICaseReview);

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

const getDefaultState = () =>
    ({
        open: false,
        isNew: false,
        dateAsc: false,
        session: getDefaultSession(),
        review: getDefaultReview(),
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
    } as IState);

interface ISessionEditProps {
    session: ISession;
    referralStatusFlags: ReferralStatusFlags;
    otherReferralFlags: KeyedMap<ReferralStatus>;
    onSessionValueChange: (key: string, value: any) => void;
    onReferralStatusFlagsChange: (flags: ReferralStatusFlags) => void;
    onOtherReferralFlagsChange: (flags: KeyedMap<ReferralStatus>) => void;
}

const SessionEdit: FunctionComponent<ISessionEditProps> = observer((props) => {
    const {
        session,
        referralStatusFlags,
        otherReferralFlags,
        onSessionValueChange,
        onReferralStatusFlagsChange,
        onOtherReferralFlagsChange,
    } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDateField
                editable={true}
                required={true}
                label="Session Date"
                value={session.date}
                onChange={(text) => onSessionValueChange('date', text)}
            />
            <GridDropdownField
                editable={true}
                required={true}
                label="Session Type"
                value={session.sessionType}
                options={sessionTypeValues}
                onChange={(text) => onSessionValueChange('sessionType', text)}
            />
            <GridTextField
                editable={true}
                label="Billable Minutes"
                value={session.billableMinutes}
                onChange={(text) => onSessionValueChange('billableMinutes', Number.isNaN(Number(text)) ? 0 : text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Medication changes"
                value={session.medicationChange}
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
                value={session.currentMedications}
                onChange={(text) => onSessionValueChange('currentMedications', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                label="Behavioral Strategies"
                flags={Object.assign(
                    {},
                    ...behavioralStrategyChecklistValues.map((x) => ({
                        [x]: !!session.behavioralStrategyChecklist?.[x],
                    })),
                )}
                flagOrder={[...behavioralStrategyChecklistValues]}
                other={session.behavioralStrategyOther}
                onChange={(flags) => onSessionValueChange('behavioralStrategyChecklist', flags)}
                onOtherChange={(text) => onSessionValueChange('behavioralStrategyOther', text)}
            />
            <GridMultiSelectField
                sm={12}
                editable={true}
                disabled={!session.behavioralStrategyChecklist['Behavioral Activation']}
                label="Behavioral Activation Checklist"
                flags={Object.assign(
                    {},
                    ...behavioralActivationChecklistValues.map((x) => ({
                        [x]: !!session.behavioralActivationChecklist?.[x],
                    })),
                )}
                flagOrder={[...behavioralActivationChecklistValues]}
                onChange={(flags) => onSessionValueChange('behavioralActivationChecklist', flags)}
            />
            <GridMultiOptionsField
                sm={12}
                editable={true}
                label="Referrals"
                flags={referralStatusFlags}
                otherFlags={otherReferralFlags}
                options={referralStatusValues}
                notOption="Not Referred"
                defaultOption="Pending"
                onChange={(flags) => onReferralStatusFlagsChange(flags as ReferralStatusFlags)}
                onOtherChange={(otherFlags) => onOtherReferralFlagsChange(otherFlags as KeyedMap<ReferralStatus>)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Other recommendations / action items"
                value={session.otherRecommendations}
                onChange={(text) => onSessionValueChange('otherRecommendations', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={10}
                label="Session Note"
                value={session.sessionNote}
                placeholder="Write session notes here"
                onChange={(text) => onSessionValueChange('sessionNote', text)}
            />
        </Grid>
    );
});

interface IReviewEditProps {
    availablePsychiatristNames: string[];
    review: ICaseReview;
    onReviewValueChange: (key: string, value: any) => void;
    onConsultingPsychiatristChange: (name: string) => void;
}

const ReviewEdit: FunctionComponent<IReviewEditProps> = observer((props) => {
    const { review, availablePsychiatristNames, onReviewValueChange, onConsultingPsychiatristChange } = props;

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDateField
                editable={true}
                required={true}
                label="Review Date"
                value={review.date}
                onChange={(text) => onReviewValueChange('date', text)}
            />
            <GridDropdownField
                editable={true}
                required={true}
                label="Consulting Psychiatrist"
                value={review.consultingPsychiatrist.name}
                options={availablePsychiatristNames}
                onChange={(text) => onConsultingPsychiatristChange(`${text}`)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Medication changes"
                value={review.medicationChange}
                placeholder="Leave blank if no change in current medications"
                onChange={(text) => onReviewValueChange('medicationChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Behavioral strategy changes"
                value={review.behavioralStrategyChange}
                placeholder="Leave blank if no change to behavioral strategies"
                onChange={(text) => onReviewValueChange('behavioralStrategyChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Referral changes"
                value={review.referralsChange}
                placeholder="Leave blank if no change to referrals"
                onChange={(text) => onReviewValueChange('referralsChange', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={4}
                label="Other recommendations / action items"
                value={review.otherRecommendations}
                onChange={(text) => onReviewValueChange('otherRecommendations', text)}
            />
            <GridTextField
                sm={12}
                editable={true}
                multiline={true}
                minLine={4}
                maxLine={10}
                label="Review Note"
                value={review.reviewNote}
                placeholder="Write review notes here"
                onChange={(text) => onReviewValueChange('reviewNote', text)}
            />
        </Grid>
    );
});

export const SessionInfo: FunctionComponent = observer(() => {
    const currentPatient = usePatient();
    const { patientsStore } = useStores();

    const state = useLocalObservable<IState>(getDefaultState);

    const onSessionValueChange = action((key: string, value: any) => {
        (state.session as any)[key] = value;
    });

    const onReviewValueChange = action((key: string, value: any) => {
        (state.review as any)[key] = value;
    });

    const onReviewConsultingPsychiatristChange = action((name: string) => {
        const found = patientsStore.psychiatrists.find((p) => p.name == name);
        if (!!name && found) {
            state.review.consultingPsychiatrist = found;
        }
    });

    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

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
        Object.assign(state, getDefaultState());
        state.open = true;
        state.isNew = true;
        state.entryType = 'Session';

        _copySessionToState(currentPatient.latestSession);
    });

    const handleAddReview = action(() => {
        state.review = getDefaultReview();
        state.open = true;
        state.isNew = true;
        state.entryType = 'Case Review';
    });

    const handleEditSession = action((sessionId: string) => {
        const session = currentPatient.sessions.find((s) => s.sessionId == sessionId);

        state.session = { ...getDefaultSession(), ...session };
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

        state.review = { ...getDefaultReview(), ...review };
        state.open = true;
        state.isNew = false;
        state.entryType = 'Case Review';
        if (!!review && review.date) {
            state.review.date = toLocalDateOnly(review.date);
        }
    });

    const onSave = action(async () => {
        const { session, review, entryType, referralStatusFlags, otherReferralFlags, isNew } = state;

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
            updatedSession.billableMinutes = Number(session.billableMinutes);

            if (isNew) {
                await currentPatient.addSession(updatedSession);
            } else {
                await currentPatient.updateSession(updatedSession);
            }
        } else if (entryType == 'Case Review') {
            const updatedReview = { ...review };
            updatedReview.date = toUTCDateOnly(review.date);

            if (isNew) {
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
            date: log.recordedDateTime,
            score: log.totalScore || getAssessmentScoreFromPointValues(log.pointValues),
        }));

    const gadScores = currentPatient.assessmentLogs
        .filter((log) => log.assessmentId == 'gad-7')
        .map((log) => ({
            date: log.recordedDateTime,
            score: log.totalScore || getAssessmentScoreFromPointValues(log.pointValues),
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

    const loading =
        currentPatient?.loadPatientState.pending ||
        currentPatient?.loadSessionsState.pending ||
        currentPatient?.loadCaseReviewsState.pending;
    const error = currentPatient?.loadSessionsState.error || currentPatient?.loadCaseReviewsState.error;

    const availablePsychiatristNames = patientsStore.psychiatrists.map((p) => p.name);

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
                content={
                    state.entryType == 'Session' ? (
                        <SessionEdit
                            session={state.session}
                            referralStatusFlags={state.referralStatusFlags}
                            otherReferralFlags={state.otherReferralFlags}
                            onSessionValueChange={onSessionValueChange}
                            onReferralStatusFlagsChange={(flags) => onValueChange('referralStatusFlags', flags)}
                            onOtherReferralFlagsChange={(flags) => onValueChange('otherReferralFlags', flags)}
                        />
                    ) : (
                        <ReviewEdit
                            review={state.review}
                            availablePsychiatristNames={availablePsychiatristNames}
                            onReviewValueChange={onReviewValueChange}
                            onConsultingPsychiatristChange={onReviewConsultingPsychiatristChange}
                        />
                    )
                }
                disableSave={
                    state.entryType == 'Session'
                        ? !state.session.date || !state.session.sessionType
                        : !state.review.date ||
                          !state.review.consultingPsychiatrist ||
                          !state.review.consultingPsychiatrist.name
                }
            />
        </ActionPanel>
    );
});

export default SessionInfo;
