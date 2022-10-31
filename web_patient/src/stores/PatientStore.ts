import { action, computed, makeAutoObservable, toJS } from 'mobx';
import {
    IActivity,
    IActivityLog,
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
import { IPatientService } from 'shared/patientService';
import { IPromiseQueryState, PromiseQuery } from 'shared/promiseQuery';
import { getLogger } from 'shared/logger';
import { isScheduledForDay } from 'src/utils/schedule';
// TODO Activity Refactor
// import { daysOfWeekValues } from 'shared/enums';
import { getLoadAndLogQuery, onArrayConflict, onSingletonConflict } from 'shared/stores';
import _ from 'lodash';
import { compareDesc } from 'date-fns';

export interface IPatientStore {
    readonly taskItems: IScheduledActivity[];
    readonly todayItems: IScheduledActivity[];
    readonly assessmentsToComplete: IScheduledAssessment[];

    readonly config: IPatientConfig;
    readonly activities: IActivity[];
    readonly values: IValue[];
    readonly valuesInventory: IValuesInventory;
    readonly safetyPlan: ISafetyPlan;

    readonly activityLogs: IActivityLog[];
    readonly assessmentLogs: IAssessmentLog[];
    readonly moodLogs: IMoodLog[];

    // UI states
    loadPatientState: IPromiseQueryState;

    loadActivitiesState: IPromiseQueryState;
    loadActivityLogsState: IPromiseQueryState;
    loadAssessmentLogsState: IPromiseQueryState;
    loadConfigState: IPromiseQueryState;
    loadMoodLogsState: IPromiseQueryState;
    loadSafetyPlanState: IPromiseQueryState;
    loadScheduledActivitiesState: IPromiseQueryState;
    loadValuesState: IPromiseQueryState;
    loadValuesInventoryState: IPromiseQueryState;

    // Helpers
    getActivityById: (activityId: string) => IActivity | undefined;
    getActivitiesByLifeAreaId: (lifeAreaId: string) => IActivity[];
    getActivitiesByValueId: (valueId: string) => IActivity[];
    getActivitiesWithoutValueId: () => IActivity[];
    getScheduledAssessmentById: (schedulId: string) => IScheduledAssessment | undefined;
    getTaskById: (taskId: string) => IScheduledActivity | undefined;
    getValueById: (valueId: string) => IValue | undefined;
    getValuesByLifeAreaId: (lifeAreaId: string) => IValue[];

    // Data load/save
    load: () => Promise<void>;

    loadActivityLogs: () => Promise<void>;
    loadMoodLogs: () => Promise<void>;
    loadValuesInventory: () => Promise<void>;

    // Activities
    addActivity: (activity: IActivity) => Promise<void>;
    updateActivity: (activity: IActivity) => Promise<void>;

    // Activity logs
    completeScheduledActivity: (activityLog: IActivityLog) => Promise<void>;

    // Assessments
    saveAssessmentLog: (assessmentData: IAssessmentLog) => Promise<void>;
    loadAssessmentLogs: () => Promise<void>;

    // Mood logs
    saveMoodLog: (moodLog: IMoodLog) => Promise<void>;

    // Safety Plan
    updateSafetyPlan: (safetyPlan: ISafetyPlan) => Promise<void>;

    // Values
    addValue: (value: IValue) => Promise<void>;
    updateValue: (value: IValue) => Promise<void>;

    // Values inventory
    updateValuesInventory: (inventory: IValuesInventory) => Promise<void>;
}

const logger = getLogger('PatientStore');

export class PatientStore implements IPatientStore {
    private readonly loadPatientQuery: PromiseQuery<IPatient>;
    private readonly loadActivitiesQuery: PromiseQuery<IActivity[]>;
    private readonly loadScheduledActivitiesQuery: PromiseQuery<IScheduledActivity[]>;
    private readonly loadScheduledAssessmentsQuery: PromiseQuery<IScheduledAssessment[]>;
    private readonly loadConfigQuery: PromiseQuery<IPatientConfig>;
    private readonly loadValuesQuery: PromiseQuery<IValue[]>;
    private readonly loadValuesInventoryQuery: PromiseQuery<IValuesInventory>;
    private readonly loadSafetyPlanQuery: PromiseQuery<ISafetyPlan>;
    private readonly loadActivityLogsQuery: PromiseQuery<IActivityLog[]>;
    private readonly loadAssessmentLogsQuery: PromiseQuery<IAssessmentLog[]>;
    private readonly loadMoodLogsQuery: PromiseQuery<IMoodLog[]>;

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
        this.loadActivityLogsQuery = new PromiseQuery<IActivityLog[]>([], 'loadActivityLogsQuery');
        this.loadAssessmentLogsQuery = new PromiseQuery<IAssessmentLog[]>([], 'loadAssessmentLogsQuery');
        this.loadConfigQuery = new PromiseQuery<IPatientConfig>(undefined, 'loadConfigQuery');
        this.loadMoodLogsQuery = new PromiseQuery<IMoodLog[]>([], 'loadMoodLogsQuery');
        this.loadSafetyPlanQuery = new PromiseQuery<ISafetyPlan>(undefined, 'loadSafetyPlan');
        this.loadScheduledActivitiesQuery = new PromiseQuery<IScheduledActivity[]>([], 'loadScheduledActivitiesQuery');
        this.loadScheduledAssessmentsQuery = new PromiseQuery<IScheduledAssessment[]>([], 'loadScheduledAssessmentsQuery');
        this.loadValuesQuery = new PromiseQuery<IValue[]>([], 'loadValuesQuery');
        this.loadValuesInventoryQuery = new PromiseQuery<IValuesInventory>(undefined, 'loadValuesInventoryQuery');

        makeAutoObservable(this);
    }

    @computed public get loadPatientState() {
        return this.loadPatientQuery;
    }

    @computed public get loadActivitiesState() {
        return this.loadActivitiesQuery;
    }

    @computed public get loadActivityLogsState() {
        return this.loadActivityLogsQuery;
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

    @computed public get taskItems() {
        return this.loadScheduledActivitiesQuery.value || [];
    }

    @computed public get todayItems() {
        return this.taskItems.filter((i) => isScheduledForDay(i, new Date()));
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

    @computed public get config() {
        const config = this.loadConfigQuery.value
        || {
            // Default value before initial load
            assignedValuesInventory: true,
            assignedSafetyPlan: true,
            assignedScheduledAssessments: [],
        };

        return config;
    }

    @computed public get activities() {
        return this.loadActivitiesQuery.value || [];
    }

    /* TODO Activity Refactor
    @computed public get activitySchedules() {
        return (this.loadActivitySchedulesQuery.value || [])
            .map(
                (a) =>
                    ({
                        ...a,
                        repeatDayFlags: Object.assign(
                            {},
                            ...daysOfWeekValues.map((x) => ({
                                [x]: !!a?.repeatDayFlags?.[x],
                            })),
                        ),
                    } as IActivity),
            );
    }
    */

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
        return this.taskItems.find((t) => t.scheduledActivityId == taskId);
    }

    @action.bound
    public getScheduledAssessmentById(scheduleId: string) {
        return this.loadScheduledAssessmentsQuery.value?.find((t) => t.scheduledAssessmentId == scheduleId);
    }

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
            return (!a.valueId);
        });
    }

    @action.bound getValueById(valueId: string) {
        return this.values.find((v) => v.valueId == valueId);
    }

    @action.bound getValuesByLifeAreaId(lifeAreaId: string) {
        return this.values.filter((v) => {
            return v.lifeAreaId == lifeAreaId;
        });
    }

    @action
    public async load() {
        const initialLoad = () =>
            this.patientService.getPatient().then((patient) => {
                this.loadActivitiesQuery.fromPromise(Promise.resolve(patient.activities));
                this.loadActivityLogsQuery.fromPromise(Promise.resolve(patient.activityLogs));
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

    @action.bound
    public async completeScheduledActivity(activityLog: IActivityLog) {
        const promise = this.patientService
            .addActivityLog({ ...activityLog, completed: true, recordedDateTime: new Date() })
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

    @action.bound
    public async addActivity(activity: IActivity) {
        const promise = this.patientService.addActivity(activity).then((addedActivity) => {
            const newActivities = this.activities.slice() || [];
            newActivities.push(addedActivity);
            return newActivities;
        });

        await this.loadAndLogQuery<IActivity[]>(
            () => promise,
            this.loadActivitiesQuery,
            onArrayConflict('activity', 'activityId', () => this.activities, logger),
        );

        await this.loadAndLogQuery<IScheduledActivity[]>(
            this.patientService.getScheduledActivities,
            this.loadScheduledActivitiesQuery,
        );
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

            await this.loadAndLogQuery<IScheduledActivity[]>(
                this.patientService.getScheduledActivities,
                this.loadScheduledActivitiesQuery,
            );
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

    @action.bound
    public async addValue(value: IValue) {
        const promise = this.patientService.addValue(value).
        then((addedValue) => {
            const newValues = this.values.slice() || [];
            newValues.push(addedValue);
            return newValues;
        });

        await this.loadAndLogQuery<IValue[]>(
            () => promise,
            this.loadValuesQuery,
            onArrayConflict('value', 'valueId', () => this.values, logger),
        );
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

    @action.bound
    public async loadActivities() {
        await this.loadAndLogQuery<IActivity[]>(
            this.patientService.getActivities,
            this.loadActivitiesQuery
        );
    }

    @action.bound
    public async loadActivityLogs() {
        await this.loadAndLogQuery<IActivityLog[]>(
            this.patientService.getActivityLogs,
            this.loadActivityLogsQuery
        );
    }

    @action.bound
    public async loadAssessmentLogs() {
        await this.loadAndLogQuery<IAssessmentLog[]>(
            this.patientService.getAssessmentLogs,
            this.loadAssessmentLogsQuery,
        );
    }

    @action.bound
    public async loadMoodLogs() {
        await this.loadAndLogQuery<IMoodLog[]>(
            this.patientService.getMoodLogs,
            this.loadMoodLogsQuery
        );
    }
}
