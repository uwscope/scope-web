import { action, computed, makeAutoObservable } from 'mobx';
import {
    IActivity,
    IActivityLog,
    IAssessmentLog,
    IMoodLog,
    IPatientConfig,
    ISafetyPlan,
    IScheduledActivity,
    IScheduledAssessment,
    IValuesInventory,
} from 'shared/types';
import { IPatientService } from 'shared/patientService';
import { IPromiseQueryState, PromiseQuery, PromiseState } from 'shared/promiseQuery';
import { getLogger } from 'shared/logger';
import { isScheduledForDay } from 'src/utils/schedule';

export interface IPatientStore {
    readonly taskItems: IScheduledActivity[];
    readonly todayItems: IScheduledActivity[];
    readonly scheduledAssessments: IScheduledAssessment[];

    readonly config: IPatientConfig;
    readonly activities: IActivity[];
    readonly valuesInventory: IValuesInventory;
    readonly safetyPlan: ISafetyPlan;

    readonly activityLogs: IActivityLog[];
    readonly assessmentLogs: IAssessmentLog[];
    readonly moodLogs: IMoodLog[];

    // UI states
    loadState: PromiseState;
    loadActivitiesState: PromiseState;
    loadScheduledActivitiesState: PromiseState;
    loadScheduledAssessmentsState: PromiseState;
    loadConfigState: PromiseState;
    loadSafetyPlanState: PromiseState;
    loadActivityLogsState: PromiseState;
    loadAssessmentLogsState: PromiseState;
    loadMoodLogsState: PromiseState;

    // Helpers
    getTaskById: (taskId: string) => IScheduledActivity | undefined;
    getScheduledAssessmentById: (schedulId: string) => IScheduledAssessment | undefined;
    getActivityById: (activityId: string) => IActivity | undefined;

    // Data load/save
    load: () => Promise<void>;
    completeScheduledActivity: (scheduledItem: IScheduledActivity, activityLog: IActivityLog) => Promise<boolean>;
    saveMoodLog: (moodLog: IMoodLog) => Promise<boolean>;
    saveAssessmentLog: (assessmentData: IAssessmentLog) => Promise<boolean>;

    updateSafetyPlan: (safetyPlan: ISafetyPlan) => Promise<void>;

    addActivity: (activity: IActivity) => Promise<boolean>;
    updateActivity: (activity: IActivity) => Promise<boolean>;

    // Values inventory
    loadValuesInventoryState: IPromiseQueryState;
    loadValuesInventory: () => Promise<void>;
    updateValuesInventory: (inventory: IValuesInventory) => Promise<void>;
    resetLoadValuesInventoryState: () => void;
}

const logger = getLogger('PatientStore');

export class PatientStore implements IPatientStore {
    private readonly loadQuery: PromiseQuery<any[]>;
    private readonly loadActivitiesQuery: PromiseQuery<IActivity[]>;
    private readonly loadScheduledActivitiesQuery: PromiseQuery<IScheduledActivity[]>;
    private readonly loadScheduledAssessmentsQuery: PromiseQuery<IScheduledAssessment[]>;
    private readonly loadConfigQuery: PromiseQuery<IPatientConfig>;
    private readonly loadValuesInventoryQuery: PromiseQuery<IValuesInventory>;
    private readonly loadSafetyPlanQuery: PromiseQuery<ISafetyPlan>;
    private readonly loadActivityLogsQuery: PromiseQuery<IActivityLog[]>;
    private readonly loadAssessmentLogsQuery: PromiseQuery<IAssessmentLog[]>;
    private readonly loadMoodLogsQuery: PromiseQuery<IMoodLog[]>;

    private readonly patientService: IPatientService;

    constructor(patientService: IPatientService) {
        this.patientService = patientService;

        this.loadScheduledActivitiesQuery = new PromiseQuery<IScheduledActivity[]>([], 'loadScheduledActivitiesQuery');
        this.loadScheduledAssessmentsQuery = new PromiseQuery<IScheduledAssessment[]>(
            [],
            'loadScheduledActivitiesQuery',
        );
        this.loadConfigQuery = new PromiseQuery<IPatientConfig>(undefined, 'loadConfigQuery');
        this.loadQuery = new PromiseQuery<PromiseSettledResult<any>[]>([], 'loadQuery');
        this.loadActivitiesQuery = new PromiseQuery<IActivity[]>([], 'loadActivitiesQuery');
        this.loadValuesInventoryQuery = new PromiseQuery<IValuesInventory>(undefined, 'loadValuesInventoryQuery');
        this.loadSafetyPlanQuery = new PromiseQuery<ISafetyPlan>(undefined, 'loadSafetyPlan');
        this.loadActivityLogsQuery = new PromiseQuery<IActivityLog[]>([], 'loadActivityLogsQuery');
        this.loadAssessmentLogsQuery = new PromiseQuery<IAssessmentLog[]>([], 'loadAssessmentLogsQuery');
        this.loadMoodLogsQuery = new PromiseQuery<IMoodLog[]>([], 'loadMoodLogsQuery');

        makeAutoObservable(this);
    }

    @computed public get loadState() {
        return this.loadQuery.state;
    }

    @computed public get loadValuesInventoryState() {
        return this.loadValuesInventoryQuery;
    }

    @computed public get loadActivitiesState() {
        return this.loadActivitiesQuery.state;
    }

    @computed public get loadScheduledActivitiesState() {
        return this.loadScheduledActivitiesQuery.state;
    }

    @computed public get loadScheduledAssessmentsState() {
        return this.loadScheduledAssessmentsQuery.state;
    }

    @computed public get loadConfigState() {
        return this.loadConfigQuery.state;
    }

    @computed public get loadSafetyPlanState() {
        return this.loadSafetyPlanQuery.state;
    }

    @computed public get loadActivityLogsState() {
        return this.loadActivityLogsQuery.state;
    }

    @computed public get loadAssessmentLogsState() {
        return this.loadAssessmentLogsQuery.state;
    }

    @computed public get loadMoodLogsState() {
        return this.loadMoodLogsQuery.state;
    }

    @computed public get taskItems() {
        return this.loadScheduledActivitiesQuery.value || [];
    }

    @computed public get todayItems() {
        return this.taskItems.filter((i) => isScheduledForDay(i, new Date()));
    }

    @computed public get scheduledAssessments() {
        return (this.loadScheduledAssessmentsQuery.value || []).filter((i) => isScheduledForDay(i, new Date()));
    }

    @computed public get config() {
        return (
            this.loadConfigQuery.value || {
                assignedValuesInventory: false,
                assignedSafetyPlan: false,
                assignedAssessmentIds: ['phq-9', 'gad-7'],
            }
        );
    }

    @computed public get activities() {
        return (this.loadActivitiesQuery.value || []).filter((a) => !a.isDeleted);
    }

    @computed public get valuesInventory() {
        return (
            this.loadValuesInventoryQuery.value || {
                assigned: false,
            }
        );
    }

    @computed public get safetyPlan() {
        return this.loadSafetyPlanQuery.value || { assigned: false };
    }

    @computed public get activityLogs() {
        return this.loadActivityLogsQuery.value || [];
    }

    @computed public get assessmentLogs() {
        return this.loadAssessmentLogsQuery.value || [];
    }

    @computed public get moodLogs() {
        return this.loadMoodLogsQuery.value || [];
    }

    @action.bound
    public getTaskById(taskId: string) {
        return this.taskItems.find((t) => t.scheduleId == taskId);
    }

    @action.bound
    public getScheduledAssessmentById(scheduleId: string) {
        return this.scheduledAssessments.find((t) => t.scheduleId == scheduleId);
    }

    @action.bound
    public getActivityById(activityId: string) {
        return this.activities.find((a) => a.activityId == activityId);
    }

    @action
    public async load() {
        console.log('load called');
        if (!this.loadQuery.pending) {
            await this.loadQuery.fromPromise(
                Promise.allSettled([
                    // this.loadScheduledActivitiesQuery.fromPromise(patientService.getScheduledActivities()),
                    // this.loadScheduledAssessmentsQuery.fromPromise(patientService.getScheduledAssessments()),
                    this.loadConfigQuery.fromPromise(this.patientService.getPatientConfig()),
                    // this.loadActivitiesQuery.fromPromise(patientService.getActivities()),
                    // this.loadValuesInventoryQuery.fromPromise(patientService.getValuesInventory()),
                    // this.loadActivityLogsQuery.fromPromise(patientService.getActivityLogs()),
                    // this.loadAssessmentLogsQuery.fromPromise(patientService.getAssessmentLogs()),
                    // this.loadSafetyPlanQuery.fromPromise(patientService.getSafetyPlan()),
                ]),
            );
        }

        await this.loadValuesInventory();
    }

    @action.bound
    public async completeScheduledActivity(scheduledItem: IScheduledActivity, activityLog: IActivityLog) {
        const promise = this.patientService.addActivityLog(activityLog).then((addedLog) => {
            const newLogs = this.activityLogs.slice() || [];
            newLogs.push(addedLog);
            return newLogs;
        });

        await this.loadActivityLogsQuery.fromPromise(promise);

        const found = this.taskItems.filter((i) => i.scheduleId == scheduledItem.scheduleId)[0];
        if (!!found) {
            found.completed = true;
        }

        return true; // TODO: need to decide how to handle server errors
    }

    @action.bound
    public async saveMoodLog(moodLog: IMoodLog) {
        const promise = this.patientService.addMoodLog(moodLog).then((addedLog) => {
            const newLogs = this.moodLogs.slice() || [];
            newLogs.push(addedLog);
            return newLogs;
        });

        await this.loadMoodLogsQuery.fromPromise(promise);

        return true;
    }

    @action.bound
    public async saveAssessmentLog(assessmentLog: IAssessmentLog) {
        const promise = this.patientService.addAssessmentLog(assessmentLog).then((addedLog) => {
            const newLogs = this.assessmentLogs.slice() || [];
            newLogs.push(addedLog);
            return newLogs;
        });

        await this.loadAssessmentLogsQuery.fromPromise(promise);
        console.log('TODO: Mark assessment as done on the server and reload client config');

        await this.loadConfigQuery.fromPromise(this.patientService.getPatientConfig());
        return true;
    }

    @action.bound
    public async updateSafetyPlan(safetyPlan: ISafetyPlan) {
        const promise = this.patientService.updateSafetyPlan(safetyPlan);
        await this.loadSafetyPlanQuery.fromPromise(promise);
    }

    @action.bound
    public async addActivity(activity: IActivity) {
        const promise = this.patientService.addActivity(activity).then((addedActivity) => {
            const newActivities = this.activities.slice() || [];
            newActivities.push(addedActivity);
            return newActivities;
        });

        await this.loadActivitiesQuery.fromPromise(promise);

        return true;
    }

    @action.bound
    public async updateActivity(activity: IActivity) {
        const prevActivities = this.activities.slice() || [];
        const found = prevActivities.findIndex((a) => a.activityId == activity.activityId);

        console.assert(found >= 0, 'Activity to update not found');

        if (found >= 0) {
            const promise = this.patientService.updateActivity(activity).then((updatedActivity) => {
                prevActivities[found] = updatedActivity;
                return prevActivities;
            });
            await this.loadActivitiesQuery.fromPromise(promise);

            return true;
        }

        return false;
    }

    @action.bound
    public async loadValuesInventory() {
        await this.loadAndLogQuery<IValuesInventory>(
            this.patientService.getValuesInventory,
            this.loadValuesInventoryQuery,
        );
    }

    @action.bound
    public async updateValuesInventory(inventory: IValuesInventory) {
        const loggedCall = logger.logFunction<IValuesInventory>({ eventName: 'updateValuesInventory' })(() =>
            this.patientService.updateValuesInventory(inventory),
        );
        await this.loadValuesInventoryQuery.fromPromise(loggedCall);
    }

    @action.bound
    public resetLoadValuesInventoryState() {
        this.loadValuesInventoryQuery.state = this.loadActivitiesQuery.value != undefined ? 'Fulfilled' : 'Unknown';
    }

    private async loadAndLogQuery<T>(queryCall: () => Promise<T>, promiseQuery: PromiseQuery<T>) {
        const loggedCall = logger.logFunction<T>({ eventName: queryCall.name })(queryCall.bind(this.patientService));
        await promiseQuery.fromPromise(loggedCall);
    }
}
