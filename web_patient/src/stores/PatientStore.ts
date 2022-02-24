import { action, computed, makeAutoObservable, when } from 'mobx';
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
import { daysOfWeekValues } from 'shared/enums';

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
    loadScheduledActivitiesState: PromiseState;
    loadScheduledAssessmentsState: PromiseState;
    loadConfigState: PromiseState;
    loadSafetyPlanState: PromiseState;
    loadActivityLogsState: PromiseState;
    loadAssessmentLogsState: PromiseState;

    loadMoodLogsState: IPromiseQueryState;
    loadValuesInventoryState: IPromiseQueryState;
    loadActivitiesState: IPromiseQueryState;

    // Helpers
    getTaskById: (taskId: string) => IScheduledActivity | undefined;
    getScheduledAssessmentById: (schedulId: string) => IScheduledAssessment | undefined;
    getActivityById: (activityId: string) => IActivity | undefined;

    // Data load/save
    load: () => Promise<void>;
    completeScheduledActivity: (scheduledItem: IScheduledActivity, activityLog: IActivityLog) => Promise<boolean>;
    saveAssessmentLog: (assessmentData: IAssessmentLog) => Promise<boolean>;

    updateSafetyPlan: (safetyPlan: ISafetyPlan) => Promise<void>;

    // Activities
    addActivity: (activity: IActivity) => Promise<void>;
    updateActivity: (activity: IActivity) => Promise<void>;

    // Values inventory
    loadValuesInventory: () => Promise<void>;
    updateValuesInventory: (inventory: IValuesInventory) => Promise<void>;

    // Mood logs
    loadMoodLogs: () => Promise<void>;
    saveMoodLog: (moodLog: IMoodLog) => Promise<void>;
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
        return this.loadActivitiesQuery;
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
        return this.loadMoodLogsQuery;
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
                assignedValuesInventory: true,
                assignedSafetyPlan: true,
                assignedAssessmentIds: ['phq-9', 'gad-7'],
            }
        );
    }

    @computed public get activities() {
        return (this.loadActivitiesQuery.value || [])
            .filter((a) => !a.isDeleted)
            .map((a) => ({
                ...a,
                repeatDayFlags: Object.assign(
                    {},
                    ...daysOfWeekValues.map((x) => ({
                        [x]: !!a?.repeatDayFlags?.[x],
                    })),
                ),
            }));
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
        await this.loadMoodLogs();
        await this.loadActivities();
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

        await this.loadAndLogQuery<IMoodLog[]>(
            () => promise,
            this.loadMoodLogsQuery,
            this.onArrayConflict('moodlog', 'moodLogId', () => this.moodLogs),
        );
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
    public async loadActivities() {
        await this.loadAndLogQuery<IActivity[]>(this.patientService.getActivities, this.loadActivitiesQuery);
    }

    @action.bound
    public async addActivity(activity: IActivity) {
        const promise = this.patientService.addActivity(activity).then((addedActivity) => {
            const newActivities = this.activities.slice() || [];
            newActivities.push(addedActivity);
            return newActivities;
        });

        await this.loadActivitiesQuery.fromPromise(promise);
    }

    @action.bound
    public async updateActivity(activity: IActivity) {
        const prevActivities = this.activities.slice() || [];
        const found = prevActivities.findIndex((a) => a.activityId == activity.activityId);

        console.assert(found >= 0, `Activity to update not found: ${activity.activityId}`);

        if (found >= 0) {
            const promise = this.patientService.updateActivity(activity).then((updatedActivity) => {
                prevActivities[found] = updatedActivity;
                return prevActivities;
            });
            await this.loadActivitiesQuery.fromPromise(promise);
        }
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
        const loggedCall = logger.logFunction<IValuesInventory>({
            eventName: 'updateValuesInventory',
        })(() => this.patientService.updateValuesInventory(inventory));
        await this.loadValuesInventoryQuery.fromPromise(loggedCall, this.onSingletonConflict('valuesinventory'));
    }

    @action.bound
    public async loadMoodLogs() {
        await this.loadAndLogQuery<IMoodLog[]>(this.patientService.getMoodLogs, this.loadMoodLogsQuery);
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

    private onArrayConflict =
        <T>(itemName: string, idName: string, getArray: () => T[]) =>
        (responseData: any | undefined) => {
            const updatedLog = responseData?.[itemName];
            if (!!updatedLog) {
                const array = getArray();
                const existing = array.find((l) => (l as any)[idName] == updatedLog[idName]);
                logger.assert(!!existing, 'Log not found when expected');

                if (!!existing) {
                    Object.assign(existing, updatedLog);
                    return array;
                } else {
                    return array.slice().concat([updatedLog]);
                }
            }

            return getArray();
        };
}
