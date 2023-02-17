import { compareDesc } from 'date-fns';
import _ from 'lodash';
import { action, computed, makeAutoObservable, toJS } from 'mobx';
import { getLogger } from 'shared/logger';
import { IPatientService } from 'shared/patientService';
import { IPromiseQueryState, PromiseQuery } from 'shared/promiseQuery';
import { getLoadAndLogQuery, onArrayConflict, onSingletonConflict } from 'shared/stores';
import {
    IActivity,
    IActivityLog,
    IActivitySchedule,
    IAssessmentLog,
    IMoodLog,
    IPatient,
    IPatientConfig,
    ISafetyPlan,
    IScheduledActivity,
    IScheduledAssessment,
    IValue,
    IValuesInventory,
} from 'shared/types';

import { isScheduledForDay } from 'src/utils/schedule';

export interface IPatientStore {
    readonly activities: IActivity[];
    readonly activityLogs: IActivityLog[];
    readonly activitySchedules: IActivitySchedule[];
    readonly assessmentsToComplete: IScheduledAssessment[];
    readonly assessmentLogs: IAssessmentLog[];
    readonly config: IPatientConfig;
    readonly moodLogs: IMoodLog[];
    readonly safetyPlan: ISafetyPlan;
    readonly taskItems: IScheduledActivity[];
    readonly todayItems: IScheduledActivity[];
    readonly values: IValue[];
    readonly valuesInventory: IValuesInventory;

    // UI states
    readonly loadPatientState: IPromiseQueryState;

    readonly loadActivitiesState: IPromiseQueryState;
    readonly loadActivityLogsState: IPromiseQueryState;
    readonly loadActivitySchedulesState: IPromiseQueryState;
    readonly loadAssessmentLogsState: IPromiseQueryState;
    readonly loadConfigState: IPromiseQueryState;
    readonly loadMoodLogsState: IPromiseQueryState;
    readonly loadSafetyPlanState: IPromiseQueryState;
    readonly loadScheduledActivitiesState: IPromiseQueryState;
    readonly loadValuesState: IPromiseQueryState;
    readonly loadValuesInventoryState: IPromiseQueryState;

    // Helpers
    getActivityById: (activityId: string) => IActivity | undefined;
    getActivitiesByLifeAreaId: (lifeAreaId: string) => IActivity[];
    getActivitiesByValueId: (valueId: string) => IActivity[];
    getActivitiesWithoutValueId: () => IActivity[];
    getActivityScheduleById: (activityScheduleId: string) => IActivitySchedule | undefined;
    getActivitySchedulesByActivityId: (activityId: string) => IActivitySchedule[];
    getScheduledAssessmentById: (scheduleId: string) => IScheduledAssessment | undefined;
    getTaskById: (taskId: string) => IScheduledActivity | undefined;
    getValueById: (valueId: string) => IValue | undefined;
    getValuesByLifeAreaId: (lifeAreaId: string) => IValue[];

    // Data load/save
    load: () => Promise<void>;

    // Activities
    addActivity: (activity: IActivity) => Promise<IActivity | null>;
    deleteActivity: (activity: IActivity) => Promise<void>;
    loadActivities: () => Promise<void>;
    updateActivity: (activity: IActivity) => Promise<void>;

    // Activity logs
    completeScheduledActivity: (activityLog: IActivityLog) => Promise<void>;
    loadActivityLogs: () => Promise<void>;

    // Activity schedules
    addActivitySchedule: (activitySchedule: IActivitySchedule) => Promise<void>;
    deleteActivitySchedule: (activitySchedule: IActivitySchedule) => Promise<void>;
    updateActivitySchedule: (activitySchedule: IActivitySchedule) => Promise<void>;

    // Assessment logs
    loadAssessmentLogs: () => Promise<void>;
    saveAssessmentLog: (assessmentData: IAssessmentLog) => Promise<void>;

    // Mood logs
    loadMoodLogs: () => Promise<void>;
    saveMoodLog: (moodLog: IMoodLog) => Promise<void>;

    // Safety Plan
    updateSafetyPlan: (safetyPlan: ISafetyPlan) => Promise<void>;

    // Values
    addValue: (value: IValue) => Promise<IValue | null>;
    deleteValue: (value: IValue) => Promise<void>;
    updateValue: (value: IValue) => Promise<void>;

    // Values inventory
    loadValuesInventory: () => Promise<void>;
    updateValuesInventory: (inventory: IValuesInventory) => Promise<void>;
}

const logger = getLogger('PatientStore');

export class PatientStore implements IPatientStore {
    private readonly loadPatientQuery: PromiseQuery<IPatient>;
    private readonly loadActivitiesQuery: PromiseQuery<IActivity[]>;
    private readonly loadActivityLogsQuery: PromiseQuery<IActivityLog[]>;
    private readonly loadActivitySchedulesQuery: PromiseQuery<IActivitySchedule[]>;
    private readonly loadAssessmentLogsQuery: PromiseQuery<IAssessmentLog[]>;
    private readonly loadConfigQuery: PromiseQuery<IPatientConfig>;
    private readonly loadMoodLogsQuery: PromiseQuery<IMoodLog[]>;
    private readonly loadSafetyPlanQuery: PromiseQuery<ISafetyPlan>;
    private readonly loadScheduledActivitiesQuery: PromiseQuery<IScheduledActivity[]>;
    private readonly loadScheduledAssessmentsQuery: PromiseQuery<IScheduledAssessment[]>;
    private readonly loadValuesQuery: PromiseQuery<IValue[]>;
    private readonly loadValuesInventoryQuery: PromiseQuery<IValuesInventory>;

    private readonly patientService: IPatientService;

    private loadAndLogQuery: <T>(
        queryCall: () => Promise<T>,
        promiseQuery: PromiseQuery<T>,
        onConflict?: (responseData?: any) => T,
    ) => Promise<void>;

    constructor(patientService: IPatientService) {
        this.patientService = patientService;

        this.loadAndLogQuery = getLoadAndLogQuery(logger, this.patientService);

        this.loadPatientQuery = new PromiseQuery<IPatient>(undefined, 'loadPatientQuery');

        this.loadActivitiesQuery = new PromiseQuery<IActivity[]>([], 'loadActivitiesQuery');
        this.loadActivitySchedulesQuery = new PromiseQuery<IActivitySchedule[]>([], 'loadActivitySchedulesQuery');
        this.loadActivityLogsQuery = new PromiseQuery<IActivityLog[]>([], 'loadActivityLogsQuery');
        this.loadAssessmentLogsQuery = new PromiseQuery<IAssessmentLog[]>([], 'loadAssessmentLogsQuery');
        this.loadConfigQuery = new PromiseQuery<IPatientConfig>(undefined, 'loadConfigQuery');
        this.loadMoodLogsQuery = new PromiseQuery<IMoodLog[]>([], 'loadMoodLogsQuery');
        this.loadSafetyPlanQuery = new PromiseQuery<ISafetyPlan>(undefined, 'loadSafetyPlan');
        this.loadScheduledActivitiesQuery = new PromiseQuery<IScheduledActivity[]>([], 'loadScheduledActivitiesQuery');
        this.loadScheduledAssessmentsQuery = new PromiseQuery<IScheduledAssessment[]>(
            [],
            'loadScheduledAssessmentsQuery',
        );
        this.loadValuesQuery = new PromiseQuery<IValue[]>([], 'loadValuesQuery');
        this.loadValuesInventoryQuery = new PromiseQuery<IValuesInventory>(undefined, 'loadValuesInventoryQuery');

        makeAutoObservable(this);
    }

    @computed public get activities() {
        return this.loadActivitiesQuery.value || [];
    }

    @computed public get activityLogs() {
        return this.loadActivityLogsQuery.value || [];
    }

    @computed public get activitySchedules(): IActivitySchedule[] {
        return this.loadActivitySchedulesQuery.value || [];

        // TODO Activity Refactor: I don't think this is necessary?
        // return (this.loadActivitySchedulesQuery.value || [])
        //     .map(
        //         (as) =>
        //             ({
        //                 ...as,
        //                 repeatDayFlags: Object.assign(
        //                     {},
        //                     ...daysOfWeekValues.map((x) => ({
        //                         [x]: !!as?.repeatDayFlags?.[x],
        //                     })),
        //                 ),
        //             }),
        //     );
    }

    @computed public get assessmentsToComplete() {
        const scheduledAssessments = this.config?.assignedScheduledAssessments || [];
        // Returns deduped list of assessments to complete
        const latestAssessments: IScheduledAssessment[] = [];
        const assessmentGroups = _.groupBy(scheduledAssessments, (a) => a.assessmentId);

        for (var assessmentId in assessmentGroups) {
            const group = assessmentGroups[assessmentId];
            group.sort((a, b) => compareDesc(a.dueDateTime, b.dueDateTime));
            latestAssessments.push(group[0]);
        }

        return latestAssessments;
    }

    @computed public get assessmentLogs() {
        return this.loadAssessmentLogsQuery.value || [];
    }

    @computed public get config() {
        const config = this.loadConfigQuery.value || {
            // Default value before initial load
            assignedValuesInventory: true,
            assignedSafetyPlan: true,
            assignedScheduledAssessments: [],
        };

        return config;
    }

    @computed public get moodLogs() {
        return this.loadMoodLogsQuery.value || [];
    }

    @computed public get safetyPlan() {
        return this.loadSafetyPlanQuery.value || { assigned: false };
    }

    @computed public get taskItems() {
        return this.loadScheduledActivitiesQuery.value || [];
    }

    @computed public get todayItems() {
        return this.taskItems.filter((i) => isScheduledForDay(i, new Date()));
    }

    @computed public get values() {
        return this.loadValuesQuery.value || [];
    }

    @computed public get valuesInventory() {
        return (
            this.loadValuesInventoryQuery.value || {
                assigned: false,
            }
        );
    }

    // UI states
    @computed public get loadPatientState() {
        return this.loadPatientQuery;
    }

    @computed public get loadActivitiesState() {
        return this.loadActivitiesQuery;
    }

    @computed public get loadActivityLogsState() {
        return this.loadActivityLogsQuery;
    }

    @computed public get loadActivitySchedulesState() {
        return this.loadActivitySchedulesQuery;
    }

    @computed public get loadAssessmentLogsState() {
        return this.loadAssessmentLogsQuery;
    }

    @computed public get loadConfigState() {
        return this.loadConfigQuery;
    }

    @computed public get loadMoodLogsState() {
        return this.loadMoodLogsQuery;
    }

    @computed public get loadSafetyPlanState() {
        return this.loadSafetyPlanQuery;
    }

    @computed public get loadScheduledActivitiesState() {
        return this.loadScheduledActivitiesQuery;
    }

    @computed public get loadValuesState() {
        return this.loadValuesQuery;
    }

    @computed public get loadValuesInventoryState() {
        return this.loadValuesInventoryQuery;
    }

    // Helpers
    @action.bound
    public getActivityById(activityId: string) {
        return this.activities.find((a) => a.activityId == activityId);
    }

    @action.bound
    public getActivitiesByLifeAreaId(lifeAreaId: string) {
        return this.activities.filter((a) => {
            if (!a.valueId) {
                return false;
            }

            const value = this.getValueById(a.valueId);
            if (!value) {
                return false;
            }

            return value.lifeAreaId == lifeAreaId;
        });
    }

    @action.bound
    public getActivitiesByValueId(valueId: string) {
        return this.activities.filter((a) => {
            if (!a.valueId) {
                return false;
            }

            return a.valueId == valueId;
        });
    }

    @action.bound
    public getActivitiesWithoutValueId() {
        return this.activities.filter((a) => {
            return !a.valueId;
        });
    }

    @action.bound
    public getActivityScheduleById(activityScheduleId: string) {
        return this.activitySchedules.find((as) => as.activityScheduleId == activityScheduleId);
    }

    @action.bound
    public getActivitySchedulesByActivityId(activityId: string): IActivitySchedule[] {
        return this.activitySchedules.filter((as) => {
            return as.activityId == activityId;
        });
    }

    @action.bound
    public getScheduledAssessmentById(scheduleId: string) {
        return this.loadScheduledAssessmentsQuery.value?.find((t) => t.scheduledAssessmentId == scheduleId);
    }

    @action.bound
    public getTaskById(taskId: string) {
        return this.taskItems.find((t) => t.scheduledActivityId == taskId);
    }

    @action.bound getValueById(valueId: string) {
        return this.values.find((v) => v.valueId == valueId);
    }

    @action.bound getValuesByLifeAreaId(lifeAreaId: string) {
        return this.values.filter((v) => {
            return v.lifeAreaId == lifeAreaId;
        });
    }

    // Data load/save
    @action
    public async load() {
        const initialLoad = () =>
            this.patientService.getPatient().then((patient) => {
                this.loadActivitiesQuery.fromPromise(Promise.resolve(patient.activities));
                this.loadActivityLogsQuery.fromPromise(Promise.resolve(patient.activityLogs));
                this.loadActivitySchedulesQuery.fromPromise(Promise.resolve(patient.activitySchedules));
                this.loadAssessmentLogsQuery.fromPromise(Promise.resolve(patient.assessmentLogs));
                this.loadMoodLogsQuery.fromPromise(Promise.resolve(patient.moodLogs));
                this.loadSafetyPlanQuery.fromPromise(Promise.resolve(patient.safetyPlan));
                this.loadScheduledActivitiesQuery.fromPromise(Promise.resolve(patient.scheduledActivities));
                this.loadScheduledAssessmentsQuery.fromPromise(Promise.resolve(patient.scheduledAssessments));
                this.loadValuesQuery.fromPromise(Promise.resolve(patient.values));
                this.loadValuesInventoryQuery.fromPromise(Promise.resolve(patient.valuesInventory));
                return patient;
            });

        await Promise.allSettled([
            this.loadAndLogQuery<IPatient>(initialLoad, this.loadPatientQuery),
            this.loadAndLogQuery<IPatientConfig>(this.patientService.getPatientConfig, this.loadConfigQuery),
        ]);
    }

    // Activities
    @action.bound
    public async addActivity(activity: IActivity): Promise<IActivity | null> {
        let returnAddedActivity = null;

        const promise = this.patientService.addActivity(activity).then((addedActivity) => {
            returnAddedActivity = addedActivity;

            const newActivities = this.activities.slice() || [];
            newActivities.push(addedActivity);
            return newActivities;
        });

        await this.loadAndLogQuery<IActivity[]>(
            () => promise,
            this.loadActivitiesQuery,
            onArrayConflict('activity', 'activityId', () => this.activities, logger),
        );

        return returnAddedActivity;
    }

    @action.bound
    public async deleteActivity(activity: IActivity) {
        const prevActivities = this.activities.slice() || [];
        const foundIdx = prevActivities.findIndex((a) => a.activityId == activity.activityId);

        console.assert(foundIdx >= 0, `Activity to delete not found: ${activity.activityId}`);

        if (foundIdx >= 0) {
            const promise = this.patientService.deleteActivity(activity).then((_deletedActivity) => {
                prevActivities.splice(foundIdx, 1);
                return prevActivities;
            });

            await this.loadAndLogQuery<IActivity[]>(
                () => promise,
                this.loadActivitiesQuery,
                onArrayConflict('activity', 'activityId', () => this.activities, logger),
            );

            await this.loadAndLogQuery<IActivitySchedule[]>(
                this.patientService.getActivitySchedules,
                this.loadActivitySchedulesQuery,
            );
            await this.loadAndLogQuery<IScheduledActivity[]>(
                this.patientService.getScheduledActivities,
                this.loadScheduledActivitiesQuery,
            );
        }
    }

    @action.bound
    public async loadActivities() {
        await this.loadAndLogQuery<IActivity[]>(this.patientService.getActivities, this.loadActivitiesQuery);
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

            await this.loadAndLogQuery<IActivity[]>(
                () => promise,
                this.loadActivitiesQuery,
                onArrayConflict('activity', 'activityId', () => this.activities, logger),
            );
        }
    }

    // Activity Logs
    @action.bound
    public async completeScheduledActivity(activityLog: IActivityLog) {
        const promise = this.patientService
            //.addActivityLog({ ...activityLog, completed: true, recordedDateTime: new Date() }) TODO: Confirm if completed: true can be removed
            .addActivityLog({ ...activityLog, recordedDateTime: new Date() })
            .then((addedLog) => {
                const newLogs = this.activityLogs.slice() || [];
                newLogs.push(addedLog);
                return newLogs;
            });

        await this.loadAndLogQuery<IActivityLog[]>(
            () => promise,
            this.loadActivityLogsQuery,
            onArrayConflict('activitylog', 'activityLogId', () => this.activityLogs, logger),
        );

        await this.loadAndLogQuery<IScheduledActivity[]>(
            this.patientService.getScheduledActivities,
            this.loadScheduledActivitiesQuery,
        );
    }

    @action.bound
    public async loadActivityLogs() {
        await this.loadAndLogQuery<IActivityLog[]>(this.patientService.getActivityLogs, this.loadActivityLogsQuery);
    }

    // Activity schedules
    @action.bound
    public async addActivitySchedule(activitySchedule: IActivitySchedule) {
        const promise = this.patientService.addActivitySchedule(activitySchedule).then((addedActivitySchedule) => {
            const newActivitySchedules = this.activitySchedules.slice() || [];
            newActivitySchedules.push(addedActivitySchedule);
            return newActivitySchedules;
        });

        await this.loadAndLogQuery<IActivitySchedule[]>(
            () => promise,
            this.loadActivitySchedulesQuery,
            onArrayConflict('activitySchedule', 'activityScheduleId', () => this.activitySchedules, logger),
        );

        await this.loadAndLogQuery<IScheduledActivity[]>(
            this.patientService.getScheduledActivities,
            this.loadScheduledActivitiesQuery,
        );
    }

    @action.bound
    public async deleteActivitySchedule(activitySchedule: IActivitySchedule) {
        const prevActivitySchedules = this.activitySchedules.slice() || [];
        const foundIdx = prevActivitySchedules.findIndex(
            (as) => as.activityScheduleId == activitySchedule.activityScheduleId,
        );

        console.assert(foundIdx >= 0, `ActivitySchedule to delete not found: ${activitySchedule.activityScheduleId}`);

        if (foundIdx >= 0) {
            const promise = this.patientService
                .deleteActivitySchedule(activitySchedule)
                .then((_deletedActivitySchedule) => {
                    prevActivitySchedules.splice(foundIdx, 1);
                    return prevActivitySchedules;
                });

            await this.loadAndLogQuery<IActivitySchedule[]>(
                () => promise,
                this.loadActivitySchedulesQuery,
                onArrayConflict('activitySchedule', 'activityScheduleId', () => this.activitySchedules, logger),
            );

            await this.loadAndLogQuery<IScheduledActivity[]>(
                this.patientService.getScheduledActivities,
                this.loadScheduledActivitiesQuery,
            );
        }
    }

    @action.bound
    public async updateActivitySchedule(activitySchedule: IActivitySchedule) {
        const prevActivitySchedules = this.activitySchedules.slice() || [];
        const found = prevActivitySchedules.findIndex(
            (a) => a.activityScheduleId == activitySchedule.activityScheduleId,
        );

        console.assert(found >= 0, `ActivitySchedule to update not found: ${activitySchedule.activityScheduleId}`);

        if (found >= 0) {
            const promise = this.patientService
                .updateActivitySchedule(activitySchedule)
                .then((updatedActivitySchedule) => {
                    prevActivitySchedules[found] = updatedActivitySchedule;
                    return prevActivitySchedules;
                });

            await this.loadAndLogQuery<IActivitySchedule[]>(
                () => promise,
                this.loadActivitySchedulesQuery,
                onArrayConflict('activitySchedule', 'activityScheduleId', () => this.activitySchedules, logger),
            );

            await this.loadAndLogQuery<IScheduledActivity[]>(
                this.patientService.getScheduledActivities,
                this.loadScheduledActivitiesQuery,
            );
        }
    }

    // Assessment logs
    @action.bound
    public async loadAssessmentLogs() {
        await this.loadAndLogQuery<IAssessmentLog[]>(
            this.patientService.getAssessmentLogs,
            this.loadAssessmentLogsQuery,
        );
    }

    @action.bound
    public async saveAssessmentLog(assessmentLog: IAssessmentLog) {
        const promise = this.patientService
            .addAssessmentLog({ ...assessmentLog, recordedDateTime: new Date() })
            .then((addedLog) => {
                const newLogs = this.assessmentLogs.slice() || [];
                newLogs.push(addedLog);
                return newLogs;
            });

        await this.loadAndLogQuery<IAssessmentLog[]>(
            () => promise,
            this.loadAssessmentLogsQuery,
            onArrayConflict('assessmentlog', 'assessmentLogId', () => this.assessmentLogs, logger),
        );

        // Calling it outside of the promise query to avoid updating the flag.
        const newConfig = await this.patientService.getPatientConfig();
        await Promise.all([
            this.loadConfigQuery.fromPromise(Promise.resolve(newConfig)),
            this.loadAndLogQuery<IScheduledAssessment[]>(
                this.patientService.getScheduledAssessments,
                this.loadScheduledAssessmentsQuery,
            ),
        ]);
    }

    // Mood logs
    @action.bound
    public async loadMoodLogs() {
        await this.loadAndLogQuery<IMoodLog[]>(this.patientService.getMoodLogs, this.loadMoodLogsQuery);
    }

    @action.bound
    public async saveMoodLog(moodLog: IMoodLog) {
        const promise = this.patientService
            .addMoodLog({ ...moodLog, recordedDateTime: new Date() })
            .then((addedLog) => {
                const newLogs = this.moodLogs.slice() || [];
                newLogs.push(addedLog);
                return newLogs;
            });

        await this.loadAndLogQuery<IMoodLog[]>(
            () => promise,
            this.loadMoodLogsQuery,
            onArrayConflict('moodlog', 'moodLogId', () => this.moodLogs, logger),
        );
    }

    // Safety plan
    @action.bound
    public async updateSafetyPlan(safetyPlan: ISafetyPlan) {
        const promise = this.patientService.updateSafetyPlan({
            ...toJS(safetyPlan),
            lastUpdatedDateTime: new Date(),
        });

        await this.loadAndLogQuery<ISafetyPlan>(
            () => promise,
            this.loadSafetyPlanQuery,
            onSingletonConflict('safetyplan'),
        );

        // Calling it outside of the promise query to avoid updating the flag.
        const newConfig = await this.patientService.getPatientConfig();
        this.loadConfigQuery.fromPromise(Promise.resolve(newConfig));
    }

    // Values
    @action.bound
    public async addValue(value: IValue): Promise<IValue | null> {
        let returnAddedValue = null;

        const promise = this.patientService.addValue(value).then((addedValue) => {
            returnAddedValue = addedValue;

            const newValues = this.values.slice() || [];
            newValues.push(addedValue);
            return newValues;
        });

        await this.loadAndLogQuery<IValue[]>(
            () => promise,
            this.loadValuesQuery,
            onArrayConflict('value', 'valueId', () => this.values, logger),
        );

        return returnAddedValue;
    }

    @action.bound
    public async deleteValue(value: IValue) {
        const prevValues = this.values.slice() || [];
        const foundIdx = prevValues.findIndex((v) => v.valueId == value.valueId);

        console.assert(foundIdx >= 0, `Value to delete not found: ${value.valueId}`);

        if (foundIdx >= 0) {
            const promise = this.patientService.deleteValue(value).then((_deletedValue) => {
                prevValues.splice(foundIdx, 1);
                return prevValues;
            });

            await this.loadAndLogQuery<IValue[]>(
                () => promise,
                this.loadValuesQuery,
                onArrayConflict('value', 'valueId', () => this.values, logger),
            );

            await this.loadAndLogQuery<IActivity[]>(this.patientService.getActivities, this.loadActivitiesQuery);
            await this.loadAndLogQuery<IActivitySchedule[]>(
                this.patientService.getActivitySchedules,
                this.loadActivitySchedulesQuery,
            );
            await this.loadAndLogQuery<IScheduledActivity[]>(
                this.patientService.getScheduledActivities,
                this.loadScheduledActivitiesQuery,
            );
        }
    }

    @action.bound
    public async updateValue(value: IValue) {
        const prevValues = this.values.slice() || [];
        const foundIdx = prevValues.findIndex((v) => v.valueId == value.valueId);

        console.assert(foundIdx >= 0, `Value to update not found: ${value.valueId}`);

        if (foundIdx >= 0) {
            const promise = this.patientService.updateValue(value).then((updatedValue: IValue) => {
                prevValues[foundIdx] = updatedValue;

                return prevValues;
            });

            await this.loadAndLogQuery<IValue[]>(
                () => promise,
                this.loadValuesQuery,
                onArrayConflict('value', 'valueId', () => this.values, logger),
            );
        }
    }

    // Values inventory
    @action.bound
    public async loadValuesInventory() {
        await this.loadAndLogQuery<IValuesInventory>(
            this.patientService.getValuesInventory,
            this.loadValuesInventoryQuery,
        );
    }

    @action.bound
    public async updateValuesInventory(inventory: IValuesInventory) {
        const promise = this.patientService.updateValuesInventory({
            ...toJS(inventory),
        });

        await this.loadAndLogQuery<IValuesInventory>(
            () => promise,
            this.loadValuesInventoryQuery,
            onSingletonConflict('valuesinventory'),
        );

        // Calling it outside of the promise query to avoid updating the flag.
        const newConfig = await this.patientService.getPatientConfig();
        this.loadConfigQuery.fromPromise(Promise.resolve(newConfig));
    }
}
