import { addDays } from 'date-fns';
import { flatten, random } from 'lodash';
import { LoremIpsum } from 'lorem-ipsum';
import { ILifeAreaValue, ILifeAreaValueActivity, IScheduledActivity } from 'shared/types';

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
            name: 'some inventory value 1',
            activities: getFakeLifeareaValueActivities('education', 'some inventory value 1'),
        } as ILifeAreaValue,
        {
            id: 'inventory-value-1',
            lifeareaId: 'recreation',
            name: 'some inventory value 2',
            activities: getFakeLifeareaValueActivities('recreation', 'some inventory value 2'),
        } as ILifeAreaValue,
    ];
};

export const getFakeLifeareaValueActivities = (lifeareaId: string, valueId: string): ILifeAreaValueActivity[] => {
    return [
        {
            id: `activity for ${lifeareaId}-${valueId} 1`,
            name: 'some inventory activity',
            valueId: valueId,
            lifeareaId,
            enjoyment: random(1, 10),
            importance: random(1, 10),
            dateCreated: new Date(),
            dateEdited: new Date(),
        } as ILifeAreaValueActivity,
        {
            id: `activity for ${lifeareaId}-${valueId} 2`,
            name: 'some inventory activity 2',
            valueId: valueId,
            lifeareaId,
            enjoyment: random(1, 10),
            importance: random(1, 10),
            dateCreated: new Date(),
            dateEdited: new Date(),
        } as ILifeAreaValueActivity,
    ];
};

// export const getFakeActivities = (): IActivity[] => {
//     return [
//         {
//             id: 'some-activity',
//             name: 'Some activity education no reminder repeat M/W',
//             value: 'Some value',
//             lifeareaId: 'education',
//             startDate: new Date(),
//             timeOfDay: 9,
//             hasReminder: false,
//             hasRepetition: true,
//             repeatDayFlags: DayOfWeekFlags.Monday | DayOfWeekFlags.Wednesday,
//             isActive: true,
//         } as IActivity,
//         {
//             id: 'some-activity2',
//             name: 'Some activity relationship has reminder no repeat',
//             value: 'Some value',
//             lifeareaId: 'relationship',
//             startDate: new Date(),
//             timeOfDay: 12,
//             hasReminder: true,
//             hasRepetition: false,
//             repeatDayFlags: DayOfWeekFlags.None,
//             isActive: true,
//         } as IActivity,
//         {
//             id: 'some-activity3',
//             name: 'Some activity relationship repeat F inactive',
//             value: 'Some value',
//             lifeareaId: 'relationship',
//             startDate: new Date(),
//             timeOfDay: 12,
//             hasReminder: false,
//             hasRepetition: true,
//             repeatDayFlags: DayOfWeekFlags.Friday,
//             isActive: false,
//         } as IActivity,
//     ];
// };

export const getFakeScheduledActivities = (daysBefore: number, daysAfter: number): IScheduledActivity[] => {
    const today = new Date();

    const items = flatten(
        [...Array(daysBefore + daysAfter).keys()].map((idx) => {
            const date = addDays(today, idx - daysBefore);
            const itemCount = random(0, 3);

            return [...Array(itemCount).keys()].map(
                () =>
                    ({
                        scheduleId: (date.getTime() + random(10000)).toString(),
                        activityId: (date.getTime() + random(10000)).toString(),
                        activityName: lorem.generateWords(random(2, 5)),
                        dueType: 'Day',
                        dueDate: date,
                        reminder: date,
                        // completed: getRandomBoolean(),
                        // recordedDate: addHours(date, getRandomInteger(3, 72)),
                        // success: getRandomItem(activitySuccessTypeValues),
                        // alternative: lorem.generateWords(random(2, 5)),
                        // pleasure: getRandomInteger(1, 11),
                        // accomplishment: getRandomInteger(1, 11),
                        // comment: lorem.generateWords(random(2, 10)),
                    } as IScheduledActivity)
            );
        })
    );

    return items;
};

// export const getFakeInspirationalQuotes = (maxCount: number) => {
//     return [...Array(maxCount).keys()].map((_) => lorem.generateSentences(random(1, 2)));
// };

// export const getFakePatientConfig = () => {
//     return {
//         needsInventory: getRandomBoolean(),
//         needsSafetyPlan: getRandomBoolean(),
//         requiredAssessments: ['phq-9', 'gad-7'],
//     } as IPatientConfig;
// };

// export const getFakeAssessmentLog = () => {
//     return {
//         assessmentDataId: random(10000).toString(),
//         assessmentId: 'phq-9',
//         date: new Date(),
//         pointValues: {
//             Interest: random(0, 3),
//             Feeling: random(0, 3),
//             Sleep: random(0, 3),
//             Tired: random(0, 3),
//             Appetite: random(0, 3),
//             Failure: random(0, 3),
//             Concentrating: random(0, 3),
//             Slowness: random(0, 3),
//             Suicide: random(0, 3),
//         },
//         comment: 'This is fake generated comment',
//     } as IAssessmentDataPoint;
// };
