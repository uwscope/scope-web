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
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
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

    // Helpers
    getTaskById: (taskId: string) => IScheduledActivity | undefined;
    getScheduledAssessmentById: (schedulId: string) => IScheduledAssessment | undefined;
    getActivityById: (activityId: string) => IActivity | undefined;

    // Data load/save
    load: () => Promise<void>;
    completeScheduledActivity: (scheduledItem: IScheduledActivity, activityLog: IActivityLog) => Promise<boolean>;
    saveMoodLog: (moodLog: IMoodLog) => Promise<boolean>;
    saveAssessmentLog: (assessmentData: IAssessmentLog) => Promise<boolean>;

    updateValuesInventory: (inventory: IValuesInventory) => Promise<void>;
    updateSafetyPlan: (safetyPlan: ISafetyPlan) => Promise<void>;

    addActivity: (activity: IActivity) => Promise<boolean>;
    updateActivity: (activity: IActivity) => Promise<boolean>;
}

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

    constructor() {
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
        const { patientService } = useServices();
        await this.loadQuery.fromPromise(
            Promise.allSettled([
                this.loadScheduledActivitiesQuery.fromPromise(patientService.getScheduledActivities()),
                this.loadScheduledAssessmentsQuery.fromPromise(patientService.getScheduledAssessments()),
                this.loadConfigQuery.fromPromise(patientService.getPatientConfig()),
                this.loadActivitiesQuery.fromPromise(patientService.getActivities()),
                this.loadValuesInventoryQuery.fromPromise(patientService.getValuesInventory()),
                this.loadActivityLogsQuery.fromPromise(patientService.getActivityLogs()),
                this.loadAssessmentLogsQuery.fromPromise(patientService.getAssessmentLogs()),
                this.loadSafetyPlanQuery.fromPromise(patientService.getSafetyPlan()),
            ]),
        );
    }

    @action.bound
    public async completeScheduledActivity(scheduledItem: IScheduledActivity, activityLog: IActivityLog) {
        const { patientService } = useServices();

        const promise = patientService.addActivityLog(activityLog).then((addedLog) => {
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
        const { patientService } = useServices();

        const promise = patientService.addMoodLog(moodLog).then((addedLog) => {
            const newLogs = this.moodLogs.slice() || [];
            newLogs.push(addedLog);
            return newLogs;
        });

        await this.loadMoodLogsQuery.fromPromise(promise);

        return true;
    }

    @action.bound
    public async saveAssessmentLog(assessmentLog: IAssessmentLog) {
        const { patientService } = useServices();

        const promise = patientService.addAssessmentLog(assessmentLog).then((addedLog) => {
            const newLogs = this.assessmentLogs.slice() || [];
            newLogs.push(addedLog);
            return newLogs;
        });

        await this.loadAssessmentLogsQuery.fromPromise(promise);
        console.log('TODO: Mark assessment as done on the server and reload client config');

        await this.loadConfigQuery.fromPromise(patientService.getPatientConfig());
        return true;
    }

    @action.bound
    public async updateValuesInventory(inventory: IValuesInventory) {
        const { patientService } = useServices();

        await this.loadValuesInventoryQuery.fromPromise(patientService.updateValuesInventory(inventory));
    }

    @action.bound
    public async updateSafetyPlan(safetyPlan: ISafetyPlan) {
        const { patientService } = useServices();

        const promise = patientService.updateSafetyPlan(safetyPlan);
        await this.loadSafetyPlanQuery.fromPromise(promise);
    }

    @action.bound
    public async addActivity(activity: IActivity) {
        const { patientService } = useServices();

        const promise = patientService.addActivity(activity).then((addedActivity) => {
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
            const { patientService } = useServices();

            const promise = patientService.updateActivity(activity).then((updatedActivity) => {
                prevActivities[found] = updatedActivity;
                return prevActivities;
            });
            await this.loadActivitiesQuery.fromPromise(promise);

            return true;
        }

        return false;
    }
}
