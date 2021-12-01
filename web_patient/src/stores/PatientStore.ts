import { flatten, remove } from 'lodash';
import { action, computed, makeAutoObservable } from 'mobx';
import {
    IActivity,
    IActivityLog,
    IAssessmentLog,
    ILifeAreaValue,
    ILifeAreaValueActivity,
    IMoodLog,
    IPatientConfig,
    IScheduledActivity,
    IScheduledAssessment,
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
    readonly values: ILifeAreaValue[];
    readonly valueActivities: ILifeAreaValueActivity[];
    readonly activityLogs: IActivityLog[];
    readonly assessmentLogs: IAssessmentLog[];
    readonly moodLogs: IMoodLog[];

    // UI states
    loadState: PromiseState;

    // Helpers
    getTaskById: (taskId: string) => IScheduledActivity | undefined;
    getScheduledAssessmentById: (schedulId: string) => IScheduledAssessment | undefined;
    getActivityById: (activityId: string) => IActivity | undefined;
    getValueById: (valueId: string) => ILifeAreaValue | undefined;

    // Data load/save
    load: () => Promise<void>;
    completeScheduledActivity: (scheduledItem: IScheduledActivity, activityLog: IActivityLog) => Promise<boolean>;
    saveMoodLog: (moodLog: IMoodLog) => Promise<boolean>;
    saveAssessmentLog: (assessmentData: IAssessmentLog) => Promise<boolean>;

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

    addActivity: (activity: IActivity) => Promise<boolean>;
    updateActivity: (activity: IActivity) => Promise<boolean>;
}

export class PatientStore implements IPatientStore {
    private readonly loadQuery: PromiseQuery<any[]>;
    private readonly loadActivitiesQuery: PromiseQuery<IActivity[]>;
    private readonly loadScheduledActivitiesQuery: PromiseQuery<IScheduledActivity[]>;
    private readonly loadScheduledAssessmentsQuery: PromiseQuery<IScheduledAssessment[]>;
    private readonly loadConfigQuery: PromiseQuery<IPatientConfig>;
    private readonly loadLifeareaValuesQuery: PromiseQuery<ILifeAreaValue[]>;
    private readonly loadActivityLogsQuery: PromiseQuery<IActivityLog[]>;
    private readonly loadAssessmentLogsQuery: PromiseQuery<IAssessmentLog[]>;
    private readonly loadMoodLogsQuery: PromiseQuery<IMoodLog[]>;

    constructor() {
        this.loadScheduledActivitiesQuery = new PromiseQuery<IScheduledActivity[]>([], 'loadScheduledActivitiesQuery');
        this.loadScheduledAssessmentsQuery = new PromiseQuery<IScheduledAssessment[]>(
            [],
            'loadScheduledActivitiesQuery'
        );
        this.loadConfigQuery = new PromiseQuery<IPatientConfig>(undefined, 'loadConfigQuery');
        this.loadQuery = new PromiseQuery<PromiseSettledResult<any>[]>([], 'loadQuery');
        this.loadActivitiesQuery = new PromiseQuery<IActivity[]>([], 'loadActivitiesQuery');
        this.loadLifeareaValuesQuery = new PromiseQuery<ILifeAreaValue[]>([], 'loadLifeareaValuesQuery');
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

    @action.bound
    public getValueById(valueId: string) {
        return this.values.find((v) => v.id == valueId);
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
                this.loadLifeareaValuesQuery.fromPromise(patientService.getValuesInventory()),
                this.loadActivityLogsQuery.fromPromise(patientService.getActivityLogs()),
                this.loadAssessmentLogsQuery.fromPromise(patientService.getAssessmentLogs()),
            ])
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
    public async saveValuesInventory(inventory: ILifeAreaValue[]) {
        const { patientService } = useServices();

        await this.loadLifeareaValuesQuery.fromPromise(patientService.updateValuesInventory(inventory));
    }

    @action.bound
    public async addValueToLifearea(lifeareaId: string, value: string) {
        const newValue = {
            id: '',
            name: value,
            dateCreated: new Date(),
            dateEdited: new Date(),
            lifeareaId,
            activities: [],
        } as ILifeAreaValue;

        const prevValues = this.values.slice();
        prevValues.push(newValue);

        await this.updateValuesInventory(prevValues);
    }

    @action.bound
    public async deleteValueFromLifearea(lifeareaId: string, valueId: string) {
        const foundValue = this.values.find((v) => v.id == valueId);

        if (!!foundValue && foundValue.lifeareaId == lifeareaId) {
            const prevValues = this.values.slice();

            remove(prevValues, (v) => v.id == valueId);

            await this.updateValuesInventory(prevValues);
        } else {
            console.assert(true, `Lifearea value not found: ${lifeareaId} - ${valueId}`);
        }
    }

    @action.bound
    public async addActivityToValue(valueId: string, activity: string, enjoyment: number, importance: number) {
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

            await this.updateValuesInventory(prevValues);
        } else {
            console.assert(true, `Lifearea value not found: ${valueId}`);
        }
    }

    @action.bound
    public async updateActivityInValue(
        valueId: string,
        activityId: string,
        activity: string,
        enjoyment: number,
        importance: number
    ) {
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

                await this.updateValuesInventory(prevValues);
            }
        } else {
            console.assert(foundValueIndex >= 0, `Lifearea value and activity not found: ${valueId} ${activityId}`);
        }
    }

    @action.bound
    public async deleteActivityFromValue(valueId: string, activityId: string) {
        const foundActivity = this.valueActivities.findIndex((a) => a.id == activityId);
        const foundValue = this.values.findIndex((v) => v.id == valueId);

        if (foundActivity >= 0 && foundValue >= 0) {
            const prevValues = this.values.slice();
            const value = prevValues[foundValue];

            remove(value.activities, (a) => a.id == activityId);

            await this.updateValuesInventory(prevValues);
        } else {
            console.assert(foundActivity >= 0, `Activity not found: ${activityId}`);
            console.assert(foundValue >= 0, `Value not found: ${valueId}`);
        }
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

    private async updateValuesInventory(values: ILifeAreaValue[]) {
        const { patientService } = useServices();

        await this.loadLifeareaValuesQuery.fromPromise(patientService.updateValuesInventory(values));
    }
}
