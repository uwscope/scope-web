import { differenceInYears } from 'date-fns';
import { action, computed, makeAutoObservable, toJS, when } from 'mobx';
import { getLogger } from 'shared/logger';
import { getPatientServiceInstance, IPatientService } from 'shared/patientService';
import { PromiseQuery, PromiseState } from 'shared/promiseQuery';
import {
    IActivity,
    IActivityLog,
    IAssessment,
    IAssessmentLog,
    ICaseReview,
    IClinicalHistory,
    IIdentity,
    IMoodLog,
    IPatient,
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

    readonly latestSession: ISession | undefined;

    load(): void;

    updateProfile(profile: Partial<IPatientProfile>): void;
    updateClinicalHistory(history: Partial<IClinicalHistory>): void;

    assignValuesInventory(): void;
    assignSafetyPlan(): void;
    assignAssessment(assessmentId: string): void;

    addSession(session: Partial<ISession>): void;
    updateSession(session: Partial<ISession>): void;

    addCaseReview(caseReview: Partial<ICaseReview>): void;
    updateCaseReview(caseReview: Partial<ICaseReview>): void;

    updateAssessment(assessment: Partial<IAssessment>): void;

    addAssessmentLog(assessmentLog: IAssessmentLog): void;
    updateAssessmentLog(assessmentLog: IAssessmentLog): void;
}

export class PatientStore implements IPatientStore {
    public identity: IIdentity;

    // Patient info
    public profile: IPatientProfile = {
        name: '',
        MRN: '',
    };

    public clinicalHistory: IClinicalHistory = {};

    public safetyPlan: ISafetyPlan = {
        assigned: false,
        assignedDate: new Date(),
    };

    // Sessions
    public sessions: ISession[] = [];
    public caseReviews: ICaseReview[] = [];

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

    constructor(patient: IPatient) {
        console.assert(!!patient.identity, 'Attempted to create a patient object without identity');
        console.assert(!!patient.identity.name, 'Attempted to create a patient object without a name');
        console.assert(!!patient.identity.identityId, 'Attempted to create a patient object without an id');

        this.patientService = getPatientServiceInstance(CLIENT_CONFIG.flaskBaseUrl, patient.identity.identityId);

        this.identity = patient.identity;

        // Patient info
        this.profile = patient.profile || this.profile;
        this.clinicalHistory = patient.clinicalHistory || this.clinicalHistory;

        // Safety plan
        this.safetyPlan = patient.safetyPlan || this.safetyPlan;

        // Sessions
        this.sessions = patient.sessions || this.sessions;
        this.caseReviews = patient.caseReviews || this.caseReviews;

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

        makeAutoObservable(this);
    }

    @computed get recordId() {
        return this.identity.identityId;
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

    @computed get latestSession() {
        if (this.sessions.length > 0) {
            return this.sessions[this.sessions.length - 1];
        }

        return undefined;
    }

    @computed get valuesInventory() {
        return (
            this.loadValuesInventoryQuery.value ||
            this.loadPatientDataQuery.value?.valuesInventory || {
                assigned: false,
            }
        );
    }

    @action.bound
    public async load() {
        await this.loadAndLogQuery<IPatient>(this.patientService.getPatient, this.loadPatientDataQuery);
        await this.loadAndLogQuery<IValuesInventory>(
            this.patientService.getValuesInventory,
            this.loadValuesInventoryQuery,
        );
    }

    @action.bound
    public async updateProfile(patientProfile: Partial<IPatientProfile>) {
        const { registryService } = useServices();
        const promise = registryService.updatePatientProfile(this.recordId, patientProfile);

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public async updateClinicalHistory(clinicalHistory: Partial<IClinicalHistory>) {
        const { registryService } = useServices();
        const promise = registryService.updatePatientClinicalHistory(this.recordId, clinicalHistory);

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public async assignValuesInventory() {
        console.log('current values inventory', toJS(this.valuesInventory));
        const promise = this.patientService.updateValuesInventory({
            ...this.valuesInventory,
            assigned: true,
            assignedDateTime: new Date(),
        });

        await this.loadAndLogQuery<IValuesInventory>(() => promise, this.loadValuesInventoryQuery);
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
    public async addSession(session: Partial<ISession>) {
        const { registryService } = useServices();
        const promise = registryService.addPatientSession(this.recordId, session).then((session) => {
            // TODO: server should return appropriate id
            const addedSession = {
                ...session,
                sessionId: `session-${this.sessions.length}`,
            };

            this.sessions.push(addedSession);
            return this;
        });

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public async updateSession(session: Partial<ISession>) {
        const { registryService } = useServices();
        const promise = registryService.updatePatientSession(this.recordId, session).then((session) => {
            const existing = this.sessions.find((s) => s.sessionId == session.sessionId);
            console.assert(!!existing, 'Session not found when expected');

            if (!!existing) {
                Object.assign(existing, session);
                return this;
            }

            return this;
        });

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public async addCaseReview(caseReview: Partial<ICaseReview>) {
        const { registryService } = useServices();
        const promise = registryService.addPatientCaseReview(this.recordId, caseReview).then((caseReview) => {
            // TODO: server should return appropriate id
            const addedReview = {
                ...caseReview,
                reviewId: `caseReview-${this.caseReviews.length}`,
            };

            this.caseReviews.push(addedReview);
            return this;
        });

        this.runPromiseAfterLoad(promise);
    }

    @action.bound
    public async updateCaseReview(caseReview: Partial<ICaseReview>) {
        const { registryService } = useServices();
        const promise = registryService.updatePatientCaseReview(this.recordId, caseReview).then((caseReview) => {
            const existing = this.caseReviews.find((c) => c.reviewId == caseReview.reviewId);
            console.assert(!!existing, 'Case review not found when expected');

            if (!!existing) {
                Object.assign(existing, caseReview);
                return this;
            }

            return this;
        });

        this.runPromiseAfterLoad(promise);
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

    private async loadAndLogQuery<T>(queryCall: () => Promise<T>, promiseQuery: PromiseQuery<T>) {
        const effect = async () => {
            const loggedCall = logger.logFunction<T>({ eventName: queryCall.name })(
                queryCall.bind(this.patientService),
            );
            await promiseQuery.fromPromise(loggedCall);
        };

        if (promiseQuery.state == 'Pending') {
            when(() => {
                return promiseQuery.state != 'Pending';
            }, effect);
        } else {
            effect();
        }
    }
}
