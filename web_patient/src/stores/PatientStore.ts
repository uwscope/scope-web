import { flatten, remove } from 'lodash';
import { action, computed, makeAutoObservable, toJS } from 'mobx';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import {
    IActivity,
    IActivityLog,
    IAssessmentDataPoint,
    ILifeAreaValue,
    ILifeAreaValueActivity,
    IMoodLog,
    IPatientConfig,
    IScheduledTaskItem,
} from 'src/services/types';
import { isScheduledForDay } from 'src/utils/schedule';

export interface IPatientStore {
    readonly taskItems: IScheduledTaskItem[];
    readonly todayItems: IScheduledTaskItem[];
    readonly config: IPatientConfig;
    readonly activities: IActivity[];
    readonly values: ILifeAreaValue[];
    readonly valueActivities: ILifeAreaValueActivity[];
    readonly activityLogs: IActivityLog[];
    readonly assessmentLogs: IAssessmentDataPoint[];

    // UI states
    loadState: PromiseState;

    // Helpers
    getTaskById: (taskId: string) => IScheduledTaskItem | undefined;
    getActivityById: (activityId: string) => IActivity | undefined;
    getValueById: (valueId: string) => ILifeAreaValue | undefined;

    // Data load/save
    load: () => Promise<void>;
    completeTaskItem: (item: IScheduledTaskItem) => Promise<boolean>;
    saveMoodLog: (moodLog: IMoodLog) => Promise<boolean>;
    saveAssessment: (assessmentData: IAssessmentDataPoint) => Promise<boolean>;
    saveActivityLog: (activityLog: Partial<IActivityLog>) => Promise<boolean>;

    addValueToLifearea: (lifeareaId: string, value: string) => void;
    deleteValueFromLifearea: (lifeareaId: string, valueId: string) => void;
    addActivityToValue: (valueId: string, activity: string, enjoyment: number, importance: number) => void;
    updateActivityInValue: (
        valueId: string,
        activityId: string,
        activity: string,
        enjoyment: number,
        importance: number
    ) => void;
    deleteActivityFromValue: (valueId: string, activityId: string) => void;

    updateActivity: (activity: IActivity) => Promise<boolean>;
}

export class PatientStore implements IPatientStore {
    private readonly loadQuery: PromiseQuery<any[]>;
    private readonly loadActivitiesQuery: PromiseQuery<IActivity[]>;
    private readonly loadScheduleQuery: PromiseQuery<IScheduledTaskItem[]>;
    private readonly loadConfigQuery: PromiseQuery<IPatientConfig>;
    private readonly loadLifeareaValuesQuery: PromiseQuery<ILifeAreaValue[]>;
    private readonly loadActivityLogsQuery: PromiseQuery<IActivityLog[]>;
    private readonly loadAssessmentLogsQuery: PromiseQuery<IAssessmentDataPoint[]>;

    constructor() {
        this.loadScheduleQuery = new PromiseQuery<IScheduledTaskItem[]>([], 'loadScheduleQuery');
        this.loadConfigQuery = new PromiseQuery<IPatientConfig>(undefined, 'loadConfigQuery');
        this.loadQuery = new PromiseQuery<PromiseSettledResult<any>[]>([], 'loadQuery');
        this.loadActivitiesQuery = new PromiseQuery<IActivity[]>([], 'loadActivitiesQuery');
        this.loadLifeareaValuesQuery = new PromiseQuery<ILifeAreaValue[]>([], 'loadLifeareaValuesQuery');
        this.loadActivityLogsQuery = new PromiseQuery<IActivityLog[]>([], 'loadActivityLogsQuery');
        this.loadAssessmentLogsQuery = new PromiseQuery<IAssessmentDataPoint[]>([], 'loadAssessmentLogsQuery');

        makeAutoObservable(this);
    }

    @computed public get loadState() {
        return this.loadQuery.state;
    }

    @computed public get taskItems() {
        return this.loadScheduleQuery.value || [];
    }

    @computed public get todayItems() {
        return this.taskItems.filter((i) => isScheduledForDay(i, new Date()));
    }

    @computed public get config() {
        return (
            this.loadConfigQuery.value || {
                needsInventory: false,
                needsSafetyPlan: false,
                requiredAssessments: ['phq-9', 'gad-7'],
            }
        );
    }

    @computed public get activities() {
        return (this.loadActivitiesQuery.value || []).filter((a) => !a.isDeleted);
    }

    @computed public get values() {
        return this.loadLifeareaValuesQuery.value || [];
    }

    @computed public get valueActivities() {
        return flatten(this.values.map((v) => v.activities));
    }

    @computed public get activityLogs() {
        return this.loadActivityLogsQuery.value || [];
    }

    @computed public get assessmentLogs() {
        return this.loadAssessmentLogsQuery.value || [];
    }

    @action.bound
    public getTaskById(taskId: string) {
        return this.taskItems.find((t) => t.id == taskId);
    }

    @action.bound
    public getActivityById(activityId: string) {
        return this.activities.find((a) => a.id == activityId);
    }

    @action.bound
    public getValueById(valueId: string) {
        return this.values.find((v) => v.id == valueId);
    }

    @action
    public async load() {
        const { patientService } = useServices();
        await this.loadQuery.fromPromise(
            Promise.allSettled([
                this.loadScheduleQuery.fromPromise(patientService.getTaskItems()),
                this.loadConfigQuery.fromPromise(patientService.getPatientConfig()),
                this.loadActivitiesQuery.fromPromise(patientService.getActivities()),
                this.loadLifeareaValuesQuery.fromPromise(patientService.getValuesInventory()),
                this.loadActivityLogsQuery.fromPromise(patientService.getActivityLogs()),
                this.loadAssessmentLogsQuery.fromPromise(patientService.getAssessmentLogs()),
            ])
        );
    }

    @action.bound
    public async completeTaskItem(item: IScheduledTaskItem) {
        console.log('TODO: save task completion to service', toJS(item));
        const found = this.taskItems.filter((i) => i.id == item.id)[0];
        if (!!found) {
            found.completed = await Promise.resolve(true);
        }

        return true;
    }

    @action.bound
    public saveMoodLog(moodLog: IMoodLog) {
        console.log('TODO: Save mood log to service', toJS(moodLog));
        return Promise.resolve(true);
    }

    @action.bound
    public async saveAssessment(assessmentData: IAssessmentDataPoint) {
        console.log('TODO: Save assessment to service', toJS(assessmentData));
        console.log('TODO: Mark assessment as done and reload client config');
        const prevLogs = this.assessmentLogs.slice();
        prevLogs.push(assessmentData);

        await this.loadAssessmentLogsQuery.fromPromise(Promise.resolve(prevLogs));

        return this.loadActivitiesQuery.state == 'Fulfilled';
    }

    @action.bound
    public async saveActivityLog(activityLog: Partial<IActivityLog>) {
        const prevLogs = this.activityLogs.slice();
        activityLog.id = Date.now().toString();
        activityLog.date = new Date();
        prevLogs.push(activityLog as IActivityLog);
        console.log('TODO: Save activity log to service', toJS(activityLog));

        await this.loadActivityLogsQuery.fromPromise(Promise.resolve(prevLogs));

        return this.loadActivityLogsQuery.state == 'Fulfilled';
    }

    @action.bound
    public saveValuesInventory(inventory: ILifeAreaValue[]) {
        console.log('TODO: Save values inventory to service', toJS(inventory));
        this.loadLifeareaValuesQuery.fromPromise(Promise.resolve(inventory));
    }

    @action.bound
    public addValueToLifearea(lifeareaId: string, value: string) {
        console.log('TODO: Add value to life area', lifeareaId, value);
        const prevValues = this.values.slice();
        prevValues.push({
            lifeareaId,
            name: value,
            activities: [],
            id: Date.now().toString(),
        } as ILifeAreaValue);

        this.loadLifeareaValuesQuery.fromPromise(Promise.resolve(prevValues));

        console.log('TODO: Added value to life area', toJS(this.values));
    }

    @action.bound
    public deleteValueFromLifearea(lifeareaId: string, valueId: string) {
        console.log('TODO: Delete value', valueId);

        const foundValue = this.values.find((v) => v.id == valueId);

        if (!!foundValue && foundValue.lifeareaId == lifeareaId) {
            const prevValues = this.values.slice();
            remove(prevValues, (v) => v.id == valueId);

            this.loadLifeareaValuesQuery.fromPromise(Promise.resolve(prevValues));

            console.log('TODO: Deleted value', toJS(this.values));
        } else {
            console.error('Value not found');
        }
    }

    @action.bound
    public addActivityToValue(valueId: string, activity: string, enjoyment: number, importance: number) {
        console.log('TODO: Add activity to value', valueId, activity);
        const found = this.values.findIndex((v) => v.id == valueId);

        if (found >= 0) {
            const prevValues = this.values.slice();
            const foundValue = prevValues[found];

            foundValue.activities = foundValue.activities || [];
            foundValue.activities.push({
                id: Date.now().toString(),
                valueId: valueId,
                name: activity,
                enjoyment,
                importance,
            } as ILifeAreaValueActivity);

            this.loadLifeareaValuesQuery.fromPromise(Promise.resolve(prevValues));

            console.log('TODO: Added activity to value', toJS(this.values));
        } else {
            console.error('Value not found');
        }
    }

    @action.bound
    public updateActivityInValue(
        valueId: string,
        activityId: string,
        activity: string,
        enjoyment: number,
        importance: number
    ) {
        console.log('TODO: Update activity in value', valueId, activityId);
        const foundValueIndex = this.values.findIndex((v) => v.id == valueId);

        if (foundValueIndex >= 0) {
            const prevValues = this.values.slice();
            const foundValue = prevValues[foundValueIndex];
            const foundValueActivities = foundValue.activities || [];

            const foundActivity = foundValueActivities.find((a) => a.id == activityId && a.valueId == valueId);
            if (!!foundActivity) {
                foundActivity.name = activity;
                foundActivity.enjoyment = enjoyment;
                foundActivity.importance = importance;

                foundValue.activities = foundValueActivities;

                this.loadLifeareaValuesQuery.fromPromise(Promise.resolve(prevValues));

                console.log('TODO: Updated activity int value', toJS(this.values));
                return;
            }
        }
        console.error('Value not found');
    }

    @action.bound
    public deleteActivityFromValue(valueId: string, activityId: string) {
        console.log('TODO: Delete activity', activityId);

        const foundActivity = this.valueActivities.findIndex((a) => a.id == activityId);
        const foundValue = this.values.findIndex((v) => v.id == valueId);

        if (foundActivity >= 0 && foundValue >= 0) {
            const prevValues = this.values.slice();
            const value = prevValues[foundValue];

            remove(value.activities, (a) => a.id == activityId);

            this.loadLifeareaValuesQuery.fromPromise(Promise.resolve(prevValues));
        } else {
            console.error('Value or activity not found');
        }
    }

    @action.bound
    public async updateActivity(activity: IActivity) {
        console.log('TODO: Update activity', toJS(activity));

        const prevActivities = this.activities.slice();
        const found = prevActivities.findIndex((a) => a.id == activity.id);

        if (found >= 0) {
            prevActivities[found] = { ...activity };
        } else {
            activity.id = Date.now().toString();
            prevActivities.push(activity);
        }

        await this.loadActivitiesQuery.fromPromise(Promise.resolve(prevActivities));

        return this.loadActivitiesQuery.state == 'Fulfilled';
    }
}
