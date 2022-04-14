import { differenceInYears } from 'date-fns';
import { action, computed, makeAutoObservable, toJS } from 'mobx';
import {
    behavioralActivationChecklistValues,
    behavioralStrategyChecklistValues,
    cancerTreatmentRegimenValues,
    discussionFlagValues,
    patientRaceValues,
} from 'shared/enums';
import { getLogger } from 'shared/logger';
import { getPatientServiceInstance, IPatientService } from 'shared/patientService';
import { IPromiseQueryState, PromiseQuery } from 'shared/promiseQuery';
import { getLoadAndLogQuery, onArrayConflict, onSingletonConflict } from 'shared/stores';
import {
    IActivity,
    IActivityLog,
    IAssessment,
    IAssessmentLog,
    ICaseReview,
    IClinicalHistory,
    IMoodLog,
    IPatient,
    IPatientProfile,
    ISafetyPlan,
    IScheduledActivity,
    IScheduledAssessment,
    ISession,
    IValuesInventory,
} from 'shared/types';

const logger = getLogger('PatientStore');

export interface IPatientStore extends IPatient {
    readonly recordId: string;
    readonly name: string;
    readonly age: number;

    readonly loadPatientState: IPromiseQueryState;

    readonly loadValuesInventoryState: IPromiseQueryState;
    readonly loadProfileState: IPromiseQueryState;
    readonly loadClinicalHistoryState: IPromiseQueryState;
    readonly loadSafetyPlanState: IPromiseQueryState;

    readonly loadSessionsState: IPromiseQueryState;
    readonly loadCaseReviewsState: IPromiseQueryState;

    readonly loadAssessmentsState: IPromiseQueryState;
    readonly loadActivitiesState: IPromiseQueryState;

    readonly loadScheduledAssessmentsState: IPromiseQueryState;
    readonly loadScheduledActivitiesState: IPromiseQueryState;

    readonly loadMoodLogsState: IPromiseQueryState;
    readonly loadAssessmentLogsState: IPromiseQueryState;
    readonly loadActivityLogsState: IPromiseQueryState;

    readonly latestSession: ISession | undefined;

    load(getToken?: () => string | undefined, onUnauthorized?: () => void): void;

    updateProfile(profile: IPatientProfile): Promise<void>;
    updateClinicalHistory(history: IClinicalHistory): Promise<void>;

    assignValuesInventory(): void;
    assignSafetyPlan(): void;
    assignAssessment(assessmentId: string): void;

    assignSafetyPlan(): void;

    addSession(session: ISession): void;
    updateSession(session: ISession): void;

    addCaseReview(caseReview: ICaseReview): void;
    updateCaseReview(caseReview: ICaseReview): void;

    updateAssessment(assessment: IAssessment): void;

    addAssessmentLog(assessmentLog: IAssessmentLog): void;
    updateAssessmentLog(assessmentLog: IAssessmentLog): void;
}

export class PatientStore implements IPatientStore {
    private readonly patientService: IPatientService;

    private readonly loadPatientDataQuery: PromiseQuery<IPatient>;
    private readonly loadValuesInventoryQuery: PromiseQuery<IValuesInventory>;
    private readonly loadProfileQuery: PromiseQuery<IPatientProfile>;
    private readonly loadClinicalHistoryQuery: PromiseQuery<IClinicalHistory>;
    private readonly loadSafetyPlanQuery: PromiseQuery<ISafetyPlan>;

    private readonly loadSessionsQuery: PromiseQuery<ISession[]>;
    private readonly loadCaseReviewsQuery: PromiseQuery<ICaseReview[]>;

    private readonly loadAssessmentsQuery: PromiseQuery<IAssessment[]>;
    private readonly loadActivitiesQuery: PromiseQuery<IActivity[]>;

    private readonly loadScheduledActivitiesQuery: PromiseQuery<IScheduledActivity[]>;
    private readonly loadScheduledAssessmentsQuery: PromiseQuery<IScheduledAssessment[]>;

    private readonly loadMoodLogsQuery: PromiseQuery<IMoodLog[]>;
    private readonly loadAssessmentLogsQuery: PromiseQuery<IAssessmentLog[]>;
    private readonly loadActivityLogsQuery: PromiseQuery<IActivityLog[]>;

    private loadAndLogQuery: <T>(
        queryCall: () => Promise<T>,
        promiseQuery: PromiseQuery<T>,
        onConflict?: (responseData?: any) => T,
    ) => Promise<void>;

    constructor(patient: IPatient) {
        console.assert(!!patient.identity, 'Attempted to create a patient object without identity');
        console.assert(!!patient.identity.name, 'Attempted to create a patient object without a name');
        console.assert(!!patient.identity.patientId, 'Attempted to create a patient object without an id');

        this.patientService = getPatientServiceInstance(CLIENT_CONFIG.flaskBaseUrl, patient.identity.patientId);
        this.loadAndLogQuery = getLoadAndLogQuery(logger, this.patientService);

        this.loadPatientDataQuery = new PromiseQuery<IPatient>(patient, 'loadPatientData');
        this.loadValuesInventoryQuery = new PromiseQuery<IValuesInventory>(
            patient.valuesInventory,
            'loadValuesInventory',
        );
        this.loadProfileQuery = new PromiseQuery<IPatientProfile>(patient.profile, 'loadProfile');
        this.loadClinicalHistoryQuery = new PromiseQuery<IClinicalHistory>(
            patient.clinicalHistory,
            'loadClinicalHistory',
        );
        this.loadSafetyPlanQuery = new PromiseQuery<ISafetyPlan>(patient.safetyPlan, 'loadSafetyPlan');

        this.loadSessionsQuery = new PromiseQuery<ISession[]>(patient.sessions, 'loadSessions');
        this.loadCaseReviewsQuery = new PromiseQuery<ICaseReview[]>(patient.caseReviews, 'loadCaseReviews');

        this.loadAssessmentsQuery = new PromiseQuery<IAssessment[]>(patient.assessments, 'loadAssessments');
        this.loadActivitiesQuery = new PromiseQuery<IActivity[]>(patient.activities, 'loadActivities');

        this.loadScheduledAssessmentsQuery = new PromiseQuery<IScheduledAssessment[]>(
            patient.scheduledAssessments,
            'loadScheduledAssessments',
        );
        this.loadScheduledActivitiesQuery = new PromiseQuery<IScheduledActivity[]>(
            patient.scheduledActivities,
            'loadScheduledActivities',
        );

        this.loadAssessmentLogsQuery = new PromiseQuery<IAssessmentLog[]>(patient.assessmentLogs, 'loadAssessmentLogs');
        this.loadMoodLogsQuery = new PromiseQuery<IMoodLog[]>(patient.moodLogs, 'loadMoodLogs');
        this.loadActivityLogsQuery = new PromiseQuery<IActivityLog[]>(patient.activityLogs, 'loadActivityLogs');

        makeAutoObservable(this);
    }

    @computed get identity() {
        return this.loadPatientDataQuery.value?.identity || { name: 'Unknown', patientId: 'Unknown' };
    }

    @computed get recordId() {
        return this.identity.patientId;
    }

    @computed get name() {
        return this.profile.name || this.identity.name;
    }

    @computed get age() {
        return !!this.profile.birthdate ? differenceInYears(new Date(), this.profile.birthdate) : -1;
    }

    @computed get loadPatientState() {
        return this.loadPatientDataQuery;
    }

    @computed get loadValuesInventoryState() {
        return this.loadValuesInventoryQuery;
    }

    @computed get loadProfileState() {
        return this.loadProfileQuery;
    }

    @computed get loadClinicalHistoryState() {
        return this.loadClinicalHistoryQuery;
    }

    @computed get loadSafetyPlanState() {
        return this.loadSafetyPlanQuery;
    }

    @computed get loadSessionsState() {
        return this.loadSessionsQuery;
    }

    @computed get loadCaseReviewsState() {
        return this.loadCaseReviewsQuery;
    }

    @computed get loadMoodLogsState() {
        return this.loadMoodLogsQuery;
    }

    @computed get loadAssessmentLogsState() {
        return this.loadAssessmentLogsQuery;
    }

    @computed get loadAssessmentsState() {
        return this.loadAssessmentsQuery;
    }

    @computed get loadActivitiesState() {
        return this.loadActivitiesQuery;
    }

    @computed get loadActivityLogsState() {
        return this.loadActivityLogsQuery;
    }

    @computed get loadScheduledActivitiesState() {
        return this.loadScheduledActivitiesQuery;
    }

    @computed get loadScheduledAssessmentsState() {
        return this.loadScheduledAssessmentsQuery;
    }

    @computed get latestSession() {
        if (this.sessions.length > 0) {
            return this.sessions[this.sessions.length - 1];
        }

        return undefined;
    }

    @computed get valuesInventory() {
        return (
            this.loadValuesInventoryQuery.value || {
                assigned: false,
            }
        );
    }

    @computed get profile() {
        return (
            this.loadProfileQuery.value || {
                name: '',
                MRN: '',
            }
        );
    }

    @computed get clinicalHistory() {
        return this.loadClinicalHistoryQuery.value || {};
    }

    @computed get safetyPlan() {
        return this.loadSafetyPlanQuery.value || { assigned: false };
    }

    @computed get sessions() {
        return this.loadSessionsQuery.value || [];
    }

    @computed get caseReviews() {
        return this.loadCaseReviewsQuery.value || [];
    }

    @computed get moodLogs() {
        return this.loadMoodLogsQuery.value || [];
    }

    @computed get assessmentLogs() {
        return this.loadAssessmentLogsQuery.value || [];
    }

    @computed get activityLogs() {
        return this.loadActivityLogsQuery.value || [];
    }

    @computed get assessments() {
        return this.loadAssessmentsQuery.value || [];
    }

    @computed get activities() {
        return this.loadActivitiesQuery.value || [];
    }

    @computed get scheduledAssessments() {
        return this.loadScheduledAssessmentsQuery.value || [];
    }

    @computed get scheduledActivities() {
        return this.loadScheduledActivitiesQuery.value || [];
    }

    @action.bound
    public async load(getToken?: () => string | undefined, onUnauthorized?: () => void) {
        if (getToken) {
            this.patientService.applyAuth(getToken, onUnauthorized);
        }

        // Don't load if it's already loading
        if (this.loadProfileState.pending) {
            return;
        }

        // Use this to make a single patient call to load everything
        const initialLoad = () =>
            this.patientService.getPatient().then((patient) => {
                this.loadProfileQuery.fromPromise(Promise.resolve(patient.profile));
                this.loadClinicalHistoryQuery.fromPromise(Promise.resolve(patient.clinicalHistory));
                this.loadValuesInventoryQuery.fromPromise(Promise.resolve(patient.valuesInventory));
                this.loadSafetyPlanQuery.fromPromise(Promise.resolve(patient.safetyPlan));
                this.loadSessionsQuery.fromPromise(Promise.resolve(patient.sessions));
                this.loadCaseReviewsQuery.fromPromise(Promise.resolve(patient.caseReviews));
                this.loadAssessmentsQuery.fromPromise(Promise.resolve(patient.assessments));
                this.loadActivitiesQuery.fromPromise(Promise.resolve(patient.activities));
                this.loadScheduledAssessmentsQuery.fromPromise(Promise.resolve(patient.scheduledAssessments));
                this.loadScheduledActivitiesQuery.fromPromise(Promise.resolve(patient.scheduledActivities));
                this.loadAssessmentLogsQuery.fromPromise(Promise.resolve(patient.assessmentLogs));
                this.loadMoodLogsQuery.fromPromise(Promise.resolve(patient.moodLogs));
                this.loadActivityLogsQuery.fromPromise(Promise.resolve(patient.activityLogs));
                return patient;
            });

        await this.loadAndLogQuery<IPatient>(initialLoad, this.loadPatientDataQuery);

        // Use this in case we want to call each document separately
        // await Promise.all([
        //     this.loadAndLogQuery<IPatient>(this.patientService.getPatient, this.loadPatientDataQuery),
        //     this.loadAndLogQuery<IPatientProfile>(this.patientService.getProfile, this.loadProfileQuery),
        //     this.loadAndLogQuery<IClinicalHistory>(
        //         this.patientService.getClinicalHistory,
        //         this.loadClinicalHistoryQuery,
        //     ),
        //     this.loadAndLogQuery<IValuesInventory>(
        //         this.patientService.getValuesInventory,
        //         this.loadValuesInventoryQuery,
        //     ),
        //     this.loadAndLogQuery<ISafetyPlan>(this.patientService.getSafetyPlan, this.loadSafetyPlanQuery),
        //     this.loadAndLogQuery<ISession[]>(this.patientService.getSessions, this.loadSessionsQuery),
        //     this.loadAndLogQuery<ICaseReview[]>(this.patientService.getCaseReviews, this.loadCaseReviewsQuery),
        //     this.loadAndLogQuery<IAssessment[]>(this.patientService.getAssessments, this.loadAssessmentsQuery),
        //     this.loadAndLogQuery<IActivity[]>(this.patientService.getActivities, this.loadActivitiesQuery),
        //     this.loadAndLogQuery<IScheduledAssessment[]>(
        //         this.patientService.getScheduledAssessments,
        //         this.loadScheduledAssessmentsQuery,
        //     ),
        //     this.loadAndLogQuery<IScheduledActivity[]>(
        //         this.patientService.getScheduledActivities,
        //         this.loadScheduledActivitiesQuery,
        //     ),
        //     this.loadAndLogQuery<IAssessmentLog[]>(this.patientService.getAssessmentLogs, this.loadAssessmentLogsQuery),
        //     this.loadAndLogQuery<IMoodLog[]>(this.patientService.getMoodLogs, this.loadMoodLogsQuery),
        //     this.loadAndLogQuery<IActivityLog[]>(this.patientService.getActivityLogs, this.loadActivityLogsQuery),
        // ]);
    }

    @action.bound
    public async updateProfile(patientProfile: IPatientProfile) {
        const promise = this.patientService.updateProfile({
            ...toJS(this.profile),
            ...toJS(patientProfile),
            race: Object.assign({}, ...patientRaceValues.map((x) => ({ [x]: !!patientProfile.race?.[x] }))),
            discussionFlag: Object.assign(
                {},
                ...discussionFlagValues.map((x) => ({ [x]: !!patientProfile.discussionFlag?.[x] })),
            ),
            primaryCareManager: patientProfile.primaryCareManager
                ? {
                    name: patientProfile.primaryCareManager?.name,
                    providerId: patientProfile.primaryCareManager?.providerId,
                    role: patientProfile.primaryCareManager?.role,
                }
                : undefined,
        });

        await this.loadAndLogQuery<IPatientProfile>(
            () => promise,
            this.loadProfileQuery,
            onSingletonConflict('profile'),
        );
    }

    @action.bound
    public async updateClinicalHistory(clinicalHistory: IClinicalHistory) {
        const promise = this.patientService.updateClinicalHistory({
            ...toJS(this.clinicalHistory),
            ...toJS(clinicalHistory),
            currentTreatmentRegimen: Object.assign(
                {},
                ...cancerTreatmentRegimenValues.map((x) => ({ [x]: !!clinicalHistory.currentTreatmentRegimen?.[x] })),
            ),
        });

        await this.loadAndLogQuery<IClinicalHistory>(
            () => promise,
            this.loadClinicalHistoryQuery,
            onSingletonConflict('clinicalhistory'),
        );
    }

    @action.bound
    public async assignValuesInventory() {
        const promise = this.patientService.updateValuesInventory({
            ...toJS(this.valuesInventory),
            assigned: true,
            assignedDateTime: new Date(),
        });

        await this.loadAndLogQuery<IValuesInventory>(
            () => promise,
            this.loadValuesInventoryQuery,
            onSingletonConflict('valuesinventory'),
        );
    }

    @action.bound
    public async assignSafetyPlan() {
        const promise = this.patientService.updateSafetyPlan({
            ...toJS(this.safetyPlan),
            assigned: true,
            assignedDateTime: new Date(),
        });

        await this.loadAndLogQuery<ISafetyPlan>(
            () => promise,
            this.loadSafetyPlanQuery,
            onSingletonConflict('safetyplan'),
        );
    }

    @action.bound
    public async assignAssessment(assessmentId: string) {
        const found = this.assessments.find((a) => a.assessmentId == assessmentId);

        console.assert(!!found, 'Assessment not found');

        if (found) {
            return this.updateAssessment({
                ...toJS(found),
                assessmentId,
                assigned: true,
                assignedDateTime: new Date(),
                frequency: found.frequency || 'Every 2 weeks',
                dayOfWeek: found.dayOfWeek || 'Monday',
            });
        }
    }

    @action.bound
    public async addSession(session: ISession) {
        const promise = this.patientService.addSession(toJS(session)).then((addedSession) => {
            return this.sessions.slice().concat([addedSession]);
        });

        await this.loadAndLogQuery<ISession[]>(() => promise, this.loadSessionsQuery, this.onSessionConflict);
    }

    @action.bound
    public async updateSession(session: ISession) {
        const promise = this.patientService
            .updateSession({
                ...toJS(session),
                behavioralStrategyChecklist: Object.assign(
                    {},
                    ...behavioralStrategyChecklistValues.map((x) => ({
                        [x]: !!session.behavioralStrategyChecklist?.[x],
                    })),
                ),
                behavioralActivationChecklist: Object.assign(
                    {},
                    ...behavioralActivationChecklistValues.map((x) => ({
                        [x]: !!session.behavioralActivationChecklist?.[x],
                    })),
                ),
            })
            .then((updatedSession) => {
                const existing = this.sessions.find((s) => s.sessionId == updatedSession.sessionId);
                logger.assert(!!existing, 'Session not found when expected');

                if (!!existing) {
                    Object.assign(existing, updatedSession);
                    return this.sessions;
                } else {
                    return this.sessions.slice().concat([updatedSession]);
                }
            });

        await this.loadAndLogQuery<ISession[]>(() => promise, this.loadSessionsQuery, this.onSessionConflict);
    }

    @action.bound
    public async addCaseReview(caseReview: ICaseReview) {
        const promise = this.patientService
            .addCaseReview({
                ...toJS(caseReview),
                consultingPsychiatrist: {
                    providerId: caseReview.consultingPsychiatrist.providerId,
                    name: caseReview.consultingPsychiatrist.name,
                    role: 'psychiatrist',
                },
            })
            .then((addedReview) => {
                return this.caseReviews.slice().concat([addedReview]);
            });

        await this.loadAndLogQuery<ICaseReview[]>(() => promise, this.loadCaseReviewsQuery, this.onCaseReviewConflict);
    }

    @action.bound
    public async updateCaseReview(caseReview: ICaseReview) {
        const promise = this.patientService
            .updateCaseReview({
                ...toJS(caseReview),
                consultingPsychiatrist: {
                    providerId: caseReview.consultingPsychiatrist.providerId,
                    name: caseReview.consultingPsychiatrist.name,
                    role: 'psychiatrist',
                },
            })
            .then((updatedReview) => {
                const existing = this.caseReviews.find((r) => r.caseReviewId == updatedReview.caseReviewId);
                logger.assert(!!existing, 'Case review not found when expected');

                if (!!existing) {
                    Object.assign(existing, updatedReview);
                    return this.caseReviews;
                } else {
                    return this.caseReviews.slice().concat([updatedReview]);
                }
            });

        await this.loadAndLogQuery<ICaseReview[]>(() => promise, this.loadCaseReviewsQuery, this.onCaseReviewConflict);
    }

    @action.bound
    public async updateAssessment(assessment: IAssessment) {
        const found = this.assessments.find((a) => a.assessmentId == assessment.assessmentId);

        console.assert(!!found, 'Assessment not found');

        if (found) {
            const promise = this.patientService
                .updateAssessment({
                    ...toJS(found),
                    ...assessment,
                })
                .then((updatedAssessment) => {
                    const existing = this.assessments.find((a) => a.assessmentId == updatedAssessment.assessmentId);
                    logger.assert(!!existing, 'Assessment not found when expected');

                    if (!!existing) {
                        Object.assign(existing, updatedAssessment);
                        return this.assessments;
                    } else {
                        return this.assessments.slice().concat([updatedAssessment]);
                    }
                });

            await this.loadAndLogQuery<IAssessment[]>(
                () => promise,
                this.loadAssessmentsQuery,
                this.onAssessmentConflict,
            );
        }
    }

    @action.bound
    public async addAssessmentLog(assessmentLog: IAssessmentLog) {
        const promise = this.patientService
            .addAssessmentLog({
                ...toJS(assessmentLog),
            })
            .then((addedLog) => {
                return this.assessmentLogs.slice().concat([addedLog]);
            });

        await this.loadAndLogQuery<IAssessmentLog[]>(
            () => promise,
            this.loadAssessmentLogsQuery,
            this.onAssessmentLogsConflict,
        );
    }

    @action.bound
    public async updateAssessmentLog(assessmentLog: IAssessmentLog) {
        const promise = this.patientService
            .updateAssessmentLog({
                ...toJS(assessmentLog),
            })
            .then((updatedAssessmentLog) => {
                const logsCopy = this.assessmentLogs.slice();
                const existingIdx = this.assessmentLogs.findIndex(
                    (r) => r.assessmentLogId == updatedAssessmentLog.assessmentLogId,
                );
                logger.assert(existingIdx >= 0, 'Assessment log not found when expected');

                if (existingIdx >= 0) {
                    logsCopy.splice(existingIdx, 1, updatedAssessmentLog);
                    return logsCopy;
                } else {
                    return this.assessmentLogs.slice().concat([updatedAssessmentLog]);
                }
            });

        await this.loadAndLogQuery<IAssessmentLog[]>(
            () => promise,
            this.loadAssessmentLogsQuery,
            this.onAssessmentLogsConflict,
        );
    }

    private onSessionConflict = (responseData?: any) => {
        return onArrayConflict('session', 'sessionId', () => this.sessions, logger)(responseData);
    };

    private onCaseReviewConflict = (responseData?: any) => {
        return onArrayConflict('casereview', 'caseReviewId', () => this.caseReviews, logger)(responseData);
    };

    private onAssessmentConflict = (responseData?: any) => {
        return onArrayConflict('assessment', 'assessmentId', () => this.assessments, logger)(responseData);
    };

    private onAssessmentLogsConflict = (responseData?: any) => {
        return onArrayConflict('assessmentlog', 'assessmentLogId', () => this.assessmentLogs, logger)(responseData);
    };
}
