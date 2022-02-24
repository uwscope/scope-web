import { addDays, format } from 'date-fns';
import { flatten, random, sample } from 'lodash';
import { LoremIpsum } from 'lorem-ipsum';
import { dueTypeValues } from 'shared/enums';
import {
    IActivity,
    IAssessmentLog,
    ILifeAreaValue,
    ILifeAreaValueActivity,
    IPatientConfig,
    ISafetyPlan,
    IScheduledActivity,
    IScheduledAssessment,
    IValuesInventory,
} from 'shared/types';

const lorem = new LoremIpsum({
    sentencesPerParagraph: {
        max: 8,
        min: 4,
    },
    wordsPerSentence: {
        max: 16,
        min: 4,
    },
});

export const getFakeValuesInventory = (): IValuesInventory => {
    return {
        assigned: true,
        assignedDateTime: new Date(),
        values: [
            {
                lifeareaId: 'education',
                name: 'some inventory value',
                activities: getFakeLifeareaValueActivities(),
            } as ILifeAreaValue,
        ],
    };
};

export const getFakeSafetyPlan = (): ISafetyPlan => {
    return {
        assigned: true,
        assignedDateTime: addDays(new Date(), -random(1, 14)),
    } as ISafetyPlan;
};

export const getFakeLifeareaValueActivities = (): ILifeAreaValueActivity[] => {
    return [
        {
            name: 'some inventory activity',
            enjoyment: 5,
            importance: 6,
        } as ILifeAreaValueActivity,
    ];
};

export const getFakeActivities = (): IActivity[] => {
    return [
        {
            activityId: 'some-activity',
            name: 'Some activity education no reminder repeat M/W',
            value: 'Some value',
            lifeareaId: 'education',
            startDate: new Date(),
            timeOfDay: 9,
            hasReminder: false,
            reminderTimeOfDay: 9,
            hasRepetition: true,
            repeatDayFlags: {},
            isActive: true,
            isDeleted: false,
        } as IActivity,
        {
            activityId: 'some-activity2',
            name: 'Some activity relationship has reminder no repeat',
            value: 'Some value',
            lifeareaId: 'relationship',
            startDate: new Date(),
            timeOfDay: 12,
            hasReminder: true,
            reminderTimeOfDay: 12,
            hasRepetition: false,
            repeatDayFlags: {},
            isActive: true,
            isDeleted: false,
        } as IActivity,
        {
            activityId: 'some-activity3',
            name: 'Some activity relationship repeat F inactive',
            value: 'Some value',
            lifeareaId: 'relationship',
            startDate: new Date(),
            timeOfDay: 12,
            hasReminder: false,
            reminderTimeOfDay: 12,
            hasRepetition: true,
            repeatDayFlags: {},
            isActive: false,
            isDeleted: false,
        } as IActivity,
    ];
};

export const getFakeScheduledActivities = (daysBefore: number, daysAfter: number): IScheduledActivity[] => {
    const today = new Date();

    const items = flatten(
        [...Array(daysBefore + daysAfter).keys()].map((idx) => {
            const date = addDays(today, idx - daysBefore);
            const itemCount = random(0, 3);

            return [...Array(itemCount).keys()].map(() => {
                const dueType = sample(dueTypeValues);
                const scheduleId = (date.getTime() + random(10000)).toString();
                return {
                    scheduleId,
                    activityId: 'some-activity',
                    activityName: `some-activity due on ${format(date, 'MM/dd/yyyy')} ${dueType} ${scheduleId}`,
                    dueType,
                    dueDate: date,
                    reminder: date,
                } as IScheduledActivity;
            });
        }),
    );

    return items;
};

export const getFakeScheduledAssessments = (): IScheduledAssessment[] => {
    const today = new Date();

    return [
        {
            scheduleId: (today.getTime() + random(10000)).toString(),
            assessmentId: 'phq-9',
            assessmentName: 'PHQ-9',
            dueDate: addDays(today, -random(0, 1)),
            dueType: 'Day',
        } as IScheduledAssessment,

        {
            scheduleId: (today.getTime() + random(10000)).toString(),
            assessmentId: 'gad-7',
            assessmentName: 'GAD-7',
            dueDate: addDays(today, -random(0, 1)),
            dueType: 'Day',
        } as IScheduledAssessment,
    ];
};

export const getFakeInspirationalQuotes = (maxCount: number) => {
    return [...Array(maxCount).keys()].map((_) => lorem.generateSentences(random(1, 2)));
};

export const getFakePatientConfig = () => {
    return {
        assignedValuesInventory: random(1) == 1,
        assignedSafetyPlan: random(1) == 1,
        assignedAssessmentIds: ['phq-9', 'gad-7'],
    } as IPatientConfig;
};

export const getFakeAssessmentLog = () => {
    return {
        logId: random(10000).toString(),
        recordedDate: new Date(),
        comment: 'This is fake generated comment',
        scheduleId: random(10000).toString(),
        assessmentId: 'phq-9',
        assessmentName: 'PHQ-9',
        completed: true,
        patientSubmitted: true,
        submittedBy: {
            identityId: 'patient-id',
            name: 'Some patient',
        },
        pointValues: {
            Interest: random(0, 3),
            Feeling: random(0, 3),
            Sleep: random(0, 3),
            Tired: random(0, 3),
            Appetite: random(0, 3),
            Failure: random(0, 3),
            Concentrating: random(0, 3),
            Slowness: random(0, 3),
            Suicide: random(0, 3),
        },
    } as IAssessmentLog;
};
