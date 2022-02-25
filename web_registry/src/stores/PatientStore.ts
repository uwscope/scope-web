import { differenceInYears } from 'date-fns';
import { action, computed, makeAutoObservable, toJS, when } from 'mobx';
import {
    behavioralActivationChecklistValues,
    behavioralStrategyChecklistValues,
    cancerTreatmentRegimenValues,
    discussionFlagValues,
    patientRaceValues,
} from 'shared/enums';
import { getLogger } from 'shared/logger';
import { getPatientServiceInstance, IPatientService } from 'shared/patientService';
import { IPromiseQueryState, PromiseQuery, PromiseState } from 'shared/promiseQuery';
import {
    IActivity,
    IActivityLog,
    IAssessment,
    IAssessmentLog,
    ICaseReview,
    IClinicalHistory,
    IMoodLog,
    IPatient,
    IPatientIdentity,
    IPatientProfile,
    ISafetyPlan,
    IScheduledActivity,
    IScheduledAssessment,
    ISession,
    IValuesInventory,
} from 'shared/types';
import { useServices } from 'src/services/services';

const logger = getLogger('PatientStore');

export interface IPatientStore extends IPatient {
    readonly recordId: string;
    readonly name: string;
    readonly age: number;
    readonly state: PromiseState;

    readonly loadValuesInventoryState: IPromiseQueryState;
    readonly loadProfileState: IPromiseQueryState;
    readonly loadClinicalHistoryState: IPromiseQueryState;

    readonly loadSessionsState: IPromiseQueryState;
    readonly loadCaseReviewsState: IPromiseQueryState;

    readonly latestSession: ISession | undefined;

    load(): void;

    updateProfile(profile: IPatientProfile): Promise<void>;
    updateClinicalHistory(history: IClinicalHistory): Promise<void>;

    assignValuesInventory(): void;
    assignSafetyPlan(): void;
    assignAssessment(assessmentId: string): void;

    addSession(session: ISession): void;
    updateSession(session: ISession): void;

    addCaseReview(caseReview: ICaseReview): void;
    updateCaseReview(caseReview: ICaseReview): void;

    updateAssessment(assessment: Partial<IAssessment>): void;

    addAssessmentLog(assessmentLog: IAssessmentLog): void;
    updateAssessmentLog(assessmentLog: IAssessmentLog): void;
}

export class PatientStore implements IPatientStore {
    public identity: IPatientIdentity;

    public safetyPlan: ISafetyPlan = {
        assigned: false,
        assignedDate: new Date(),
    };

    // Assessments
    public assessments: IAssessment[] = [];
    public scheduledAssessments: IScheduledAssessment[] = [];
    public assessmentLogs: IAssessmentLog[] = [];

    // Activities
    public activities: IActivity[] = [];
    public scheduledActivities: IScheduledActivity[] = [];
    public activityLogs: IActivityLog[] = [];

    // Mood logs
    public moodLogs: IMoodLog[] = [];

    private readonly patientService: IPatientService;

    private readonly loadPatientDataQuery: PromiseQuery<IPatient>;
    private readonly loadValuesInventoryQuery: PromiseQuery<IValuesInventory>;
    private readonly loadProfileQuery: PromiseQuery<IPatientProfile>;
    private readonly loadClinicalHistoryQuery: PromiseQuery<IClinicalHistory>;

    private readonly loadSessionsQuery: PromiseQuery<ISession[]>;
    private readonly loadCaseReviewsQuery: PromiseQuery<ICaseReview[]>;

    constructor(patient: IPatient) {
        console.assert(!!patient.identity, 'Attempted to create a patient object without identity');
        console.assert(!!patient.identity.name, 'Attempted to create a patient object without a name');
        console.assert(!!patient.identity.patientId, 'Attempted to create a patient object without an id');

        this.patientService = getPatientServiceInstance(CLIENT_CONFIG.flaskBaseUrl, patient.identity.patientId);

        this.identity = patient.identity;

        // Safety plan
        this.safetyPlan = patient.safetyPlan || this.safetyPlan;

        // Assessments
        this.assessments = patient.assessments || this.assessments;
        this.scheduledAssessments = patient.scheduledAssessments || this.scheduledAssessments;
        this.assessmentLogs = patient.assessmentLogs || this.assessmentLogs;

        // Activities
        this.activities = patient.activities || this.activities;
        this.scheduledActivities = patient.scheduledActivities || this.scheduledActivities;
        this.activityLogs = patient.activityLogs || this.activityLogs;

        this.moodLogs = patient.moodLogs || this.moodLogs;

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

        this.loadSessionsQuery = new PromiseQuery<ISession[]>(patient.sessions, 'loadSessions');
        this.loadCaseReviewsQuery = new PromiseQuery<ICaseReview[]>(patient.caseReviews, 'loadCaseReviews');

        makeAutoObservable(this);
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

    @computed get state() {
        return this.loadPatientDataQuery.state;
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

    @computed get loadSessionsState() {
        return this.loadSessionsQuery;
    }

    @computed get loadCaseReviewsState() {
        return this.loadCaseReviewsQuery;
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

    @computed get sessions() {
        return this.loadSessionsQuery.value || [];
    }

    @computed get caseReviews() {
        return this.loadCaseReviewsQuery.value || [];
    }

    @action.bound
    public async load() {
        await this.loadAndLogQuery<IPatient>(this.patientService.getPatient, this.loadPatientDataQuery);
        await this.loadAndLogQuery<IPatientProfile>(this.patientService.getProfile, this.loadProfileQuery);
        await this.loadAndLogQuery<IClinicalHistory>(
            this.patientService.getClinicalHistory,
            this.loadClinicalHistoryQuery,
        );
        await this.loadAndLogQuery<IValuesInventory>(
            this.patientService.getValuesInventory,
            this.loadValuesInventoryQuery,
        );
        await this.loadAndLogQuery<ISession[]>(this.patientService.getSessions, this.loadSessionsQuery);
        await this.loadAndLogQuery<ICaseReview[]>(this.patientService.getCaseReviews, this.loadCaseReviewsQuery);
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
        });

        await this.loadAndLogQuery<IPatientProfile>(
            () => promise,
            this.loadProfileQuery,
            this.onSingletonConflict('profile'),
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
            this.onSingletonConflict('clinicalhistory'),
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
            this.onSingletonConflict('valuesinventory'),
        );
    }

    @action.bound
    public async assignSafetyPlan() {
        const { registryService } = useServices();
        const promise = registryService.updatePatientSafetyPlan(this.recordId, {
            assigned: true,
            assignedDate: new Date(),
        });

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public async assignAssessment(assessmentId: string) {
        const found = this.assessments.find((a) => a.assessmentId == assessmentId);

        console.assert(!!found, 'Assessment not found');

        if (!!found) {
            found.assigned = true;
            found.assignedDate = new Date();

            const { registryService } = useServices();

            const promise = registryService.updatePatientAssessment(this.recordId, found).then((newAssessment) => {
                const existing = this.assessments.find((c) => c.assessmentId == newAssessment.assessmentId);
                console.assert(!!existing, 'Assessment not found when expected');

                if (!!existing) {
                    Object.assign(existing, newAssessment);
                    return this;
                }

                return this;
            });

            this.runPromiseAfterLoad(promise);
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
    public async updateAssessment(assessment: Partial<IAssessment>) {
        const { registryService } = useServices();
        const promise = registryService.updatePatientAssessment(this.recordId, assessment).then((assessment) => {
            const existing = this.assessments.find((a) => a.assessmentId == assessment.assessmentId);
            console.assert(!!existing, 'Assessment not found when expected');

            if (!!existing) {
                Object.assign(existing, assessment);
                return this;
            }

            return this;
        });

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public addAssessmentLog(assessmentLog: IAssessmentLog) {
        const { registryService } = useServices();
        const promise = registryService.addPatientAssessmentLog(this.recordId, assessmentLog).then((assessmentLog) => {
            // TODO: server should return appropriate id
            const addedAssessmentLog = {
                ...assessmentLog,
                logId: `assessmentlog-${this.assessmentLogs.length}`,
            };

            this.assessmentLogs.push(addedAssessmentLog);
            return this;
        });

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public updateAssessmentLog(assessmentLog: IAssessmentLog) {
        const { registryService } = useServices();
        const promise = registryService
            .updatePatientAssessmentLog(this.recordId, assessmentLog)
            .then((assessmentLog) => {
                const existing = this.assessmentLogs.find((a) => a.logId == assessmentLog.logId);
                console.assert(!!existing, 'Assessment log not found when expected');

                if (!!existing) {
                    Object.assign(existing, assessmentLog);
                    return this;
                }

                return this;
            });

        this.runPromiseAfterLoad(promise);
    }

    private setPatientData(patient: IPatient) {
        Object.assign(this, patient);
    }

    private runAfterLoad(fn: () => void) {
        if (this.state == 'Pending') {
            when(() => {
                return this.state != 'Pending';
            }, fn);
        } else {
            fn();
        }
    }

    private runPromiseAfterLoad(promise: Promise<IPatient>) {
        const effect = () => {
            this.loadPatientDataQuery.fromPromise(promise).then((patientData) => {
                action(() => {
                    this.setPatientData(patientData);
                })();
            });
        };

        this.runAfterLoad(effect);
    }

    private async loadAndLogQuery<T>(
        queryCall: () => Promise<T>,
        promiseQuery: PromiseQuery<T>,
        onConflict?: (responseData?: any) => T,
    ) {
        const effect = async () => {
            const loggedCall = logger.logFunction<T>({ eventName: promiseQuery.name })(
                queryCall.bind(this.patientService),
            );
            await promiseQuery.fromPromise(loggedCall, onConflict);
        };

        if (promiseQuery.state == 'Pending') {
            when(
                () => {
                    return promiseQuery.state != 'Pending';
                },
                async () => {
                    await effect();
                },
            );
        } else {
            await effect();
        }
    }

    private onSingletonConflict =
        (fieldName: string) =>
        <T>(responseData?: any) => {
            return responseData?.[fieldName] as T;
        };

    private onSessionConflict = (responseData?: any) => {
        const updatedSession = responseData?.session;
        if (!!updatedSession) {
            const existing = this.sessions.find((s) => s.sessionId == updatedSession.sessionId);
            logger.assert(!!existing, 'Session not found when expected');

            if (!!existing) {
                Object.assign(existing, updatedSession);
                return this.sessions;
            } else {
                return this.sessions.slice().concat([updatedSession]);
            }
        }

        return this.sessions;
    };

    private onCaseReviewConflict = (responseData?: any) => {
        const updatedReview = responseData?.casereview;
        if (!!updatedReview) {
            const existing = this.caseReviews.find((r) => r.caseReviewId == updatedReview.caseReviewId);
            logger.assert(!!existing, 'Case review not found when expected');

            if (!!existing) {
                Object.assign(existing, updatedReview);
                return this.caseReviews;
            } else {
                return this.caseReviews.slice().concat([updatedReview]);
            }
        }

        return this.caseReviews;
    };
}
