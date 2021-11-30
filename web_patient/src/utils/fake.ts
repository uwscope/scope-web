import { addDays } from 'date-fns';
import { flatten, random } from 'lodash';
import { LoremIpsum } from 'lorem-ipsum';
import { getRandomBoolean, getRandomItem } from 'src/services/random';
import {
    DayOfWeekFlags,
    dueTypeValues,
    IActivity,
    IAssessmentDataPoint,
    ILifeAreaValue,
    ILifeAreaValueActivity,
    IPatientConfig,
    IScheduledTaskItem,
} from 'src/services/types';

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

export const getFakeLifeareaValues = (): ILifeAreaValue[] => {
    return [
        {
            id: 'inventory-value-1',
            lifeareaId: 'education',
            name: 'some inventory value',
            activities: getFakeLifeareaValueActivities('education'),
        } as ILifeAreaValue,
    ];
};

export const getFakeLifeareaValueActivities = (lifeareaId: string): ILifeAreaValueActivity[] => {
    return [
        {
            id: 'inventory-activity',
            name: 'some inventory activity',
            valueId: 'inventory-value-1',
            lifeareaId,
            enjoyment: 5,
            importance: 6,
        } as ILifeAreaValueActivity,
    ];
};

export const getFakeActivities = (): IActivity[] => {
    return [
        {
            id: 'some-activity',
            name: 'Some activity education no reminder repeat M/W',
            value: 'Some value',
            lifeareaId: 'education',
            startDate: new Date(),
            timeOfDay: 9,
            hasReminder: false,
            hasRepetition: true,
            repeatDayFlags: DayOfWeekFlags.Monday | DayOfWeekFlags.Wednesday,
            isActive: true,
        } as IActivity,
        {
            id: 'some-activity2',
            name: 'Some activity relationship has reminder no repeat',
            value: 'Some value',
            lifeareaId: 'relationship',
            startDate: new Date(),
            timeOfDay: 12,
            hasReminder: true,
            hasRepetition: false,
            repeatDayFlags: DayOfWeekFlags.None,
            isActive: true,
        } as IActivity,
        {
            id: 'some-activity3',
            name: 'Some activity relationship repeat F inactive',
            value: 'Some value',
            lifeareaId: 'relationship',
            startDate: new Date(),
            timeOfDay: 12,
            hasReminder: false,
            hasRepetition: true,
            repeatDayFlags: DayOfWeekFlags.Friday,
            isActive: false,
        } as IActivity,
    ];
};

export const getFakeScheduledItems = (daysBefore: number, daysAfter: number): IScheduledTaskItem[] => {
    const today = new Date();

    const items = flatten(
        [...Array(daysBefore + daysAfter).keys()].map((idx) => {
            const date = addDays(today, idx - daysBefore);
            const itemCount = random(0, 3);

            return [...Array(itemCount).keys()].map(
                () =>
                    ({
                        sourceId: 'some-activity',
                        id: (date.getTime() + random(10000)).toString(),
                        dueType: getRandomItem(dueTypeValues),
                        due: date,
                        name: lorem.generateWords(random(2, 5)),
                        taskType: 'Activity',
                        reminder: date,
                        completed: random(0, 5) < 1,
                    } as IScheduledTaskItem)
            );
        })
    );

    return items;
};

export const getFakeInspirationalQuotes = (maxCount: number) => {
    return [...Array(maxCount).keys()].map((_) => lorem.generateSentences(random(1, 2)));
};

export const getFakePatientConfig = () => {
    return {
        needsInventory: getRandomBoolean(),
        needsSafetyPlan: getRandomBoolean(),
        requiredAssessments: ['phq-9', 'gad-7'],
    } as IPatientConfig;
};

export const getFakeAssessmentLog = () => {
    return {
        assessmentDataId: random(10000).toString(),
        assessmentId: 'phq-9',
        date: new Date(),
        pointValues: {
            Interest: random(0, 3),
            Feeling: random(0, 3),
            Sleep: random(0, 3),
            Tired: random(0, 3),
            Apetite: random(0, 3),
            Failure: random(0, 3),
            Concentrating: random(0, 3),
            Slowness: random(0, 3),
            Suicide: random(0, 3),
        },
        comment: 'This is fake generated comment',
    } as IAssessmentDataPoint;
};
