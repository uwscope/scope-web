import { addDays } from 'date-fns';
import { LoremIpsum } from 'lorem-ipsum';
import {
    assessmentFrequencyValues,
    AssessmentType,
    assessmentTypeValues,
    behavioralActivationChecklistValues,
    clinicCodeValues,
    discussionFlagValues,
    followupScheduleValues,
    gad7ItemValues,
    patientSexValues,
    phq9ItemValues,
    referralValues,
    sessionTypeValues,
    treatmentChangeValues,
    treatmentPlanValues,
    treatmentRegimenValues,
    treatmentStatusValues,
} from 'src/services/enums';
import { IActivity, IAssessment, IAssessmentDataPoint, IPatient, ISession } from 'src/services/types';
import { getRandomFlags, getRandomInteger, getRandomItem, sample } from 'src/utils/random';

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

export const getRandomFakePatients = () => {
    const patientCount = getRandomInteger(3, 10);
    const patients = [...Array(patientCount).keys()].map((_) => getFakePatient());

    return patients;
};

const getFakePatient = () => {
    return {
        // Medical information
        MRN: getRandomInteger(10000, 1000000),
        firstName: getRandomItem(firstNames),
        lastName: getRandomItem(lastNames),
        birthdate: new Date(getRandomInteger(1930, 2000), getRandomInteger(0, 12), getRandomInteger(1, 28)),
        sex: getRandomItem(patientSexValues),
        clinicCode: getRandomItem(clinicCodeValues),
        treatmentRegimen: getRandomItem(treatmentRegimenValues),
        medicalDiagnosis: lorem.generateSentences(2),

        // Treatment information
        primaryCareManager: getRandomItem(careManagers),
        treatmentStatus: getRandomItem(treatmentStatusValues),
        followupSchedule: getRandomItem(followupScheduleValues),
        discussionFlag: getRandomItem(discussionFlagValues),
        referral: getRandomItem(referralValues),
        treatmentPlan: lorem.generateSentences(2),

        // Psychiatry
        psychHistory: lorem.generateSentences(3),
        substanceUse: lorem.generateSentences(1),
        psychMedications: lorem.generateSentences(2),
        psychDiagnosis: lorem.generateSentences(2),

        // Sessions
        sessions: getFakeSessions(),

        // Assessments
        assessments: getFakeAssessments(),

        // Activities
        activities: getFakeActivities(),
    } as IPatient;
};

const getFakeAssessments = () => {
    return sample(assessmentTypeValues, getRandomInteger(1, 3)).map(
        (a) =>
            ({
                assessmentId: a,
                assessmentType: a,
                frequency: getRandomItem(assessmentFrequencyValues),
                data: getAssessmentDataPoints(a),
            } as IAssessment)
    );
};

const getFakeAssessmentDataPoint = (assessmentType: AssessmentType) => {
    if (assessmentType == 'PHQ-9') {
        const points: { [key: string]: number } = {};
        phq9ItemValues.forEach((p) => (points[p] = getRandomInteger(0, 4)));
        return points;
    } else if (assessmentType == 'GAD-7') {
        const points: { [key: string]: number } = {};
        gad7ItemValues.forEach((p) => (points[p] = getRandomInteger(0, 4)));
        return points;
    } else {
        return { Mood: getRandomInteger(0, 5) };
    }
};

const getAssessmentDataPoints = (assessmentType: AssessmentType) => {
    return [...Array(getRandomInteger(5, 10)).keys()].map(
        (_, idx) =>
            ({
                assessmentDataId: `${assessmentType}-${idx}`,
                assessmentType: assessmentType,
                date: addDays(new Date(), -(getRandomInteger(0, 3) + idx * getRandomInteger(5, 8))),
                pointValues: getFakeAssessmentDataPoint(assessmentType),
                comment: lorem.generateSentences(1),
            } as IAssessmentDataPoint)
    );
};

const getFakeSessions = () => {
    const sessionCount = getRandomInteger(1, 10);

    return [...Array(sessionCount).keys()].map(
        (_, idx) =>
            ({
                sessionId: idx == 0 ? 'Initial assessment' : `session-${idx}`,
                date: addDays(new Date(), -(getRandomInteger(-2, 2) + (sessionCount - idx) * getRandomInteger(13, 18))),
                sessionType: getRandomItem(sessionTypeValues),
                billableMinutes: getRandomItem([30, 45, 60, 80]),
                treatmentPlan: getRandomItem(treatmentPlanValues),
                treatmentChange: getRandomItem(treatmentChangeValues),
                behavioralActivationChecklist: getRandomFlags(behavioralActivationChecklistValues),
                sessionNote: lorem.generateSentences(getRandomInteger(4, 7)),
            } as ISession)
    );
};

const getFakeActivities = () => {
    const activityCount = getRandomInteger(1, 3);

    return [...Array(activityCount).keys()].map(
        (idx) =>
            ({
                activityId: String(idx),
                activityName: lorem.generateWords(getRandomInteger(2, 5)),
                moodData: getAssessmentDataPoints('Mood logging'),
            } as IActivity)
    );
};

// Below are temporary TEST methods for generating fake data

const firstNames = [
    'Paisley',
    'Vince',
    'Prudence',
    'Floyd',
    'Marty',
    'Yvonne',
    'Russ',
    'Herb',
    'Hannah',
    'Melanie',
    'Dwayne',
    'Clifford',
    'Garth',
    'Rachel',
    'Phoebe',
    'Doug',
    'Mortimer',
    'Heath',
    'Iris',
    'Tony',
];

const lastNames = [
    'Lowe',
    'Dawson',
    'Porter',
    'Tomlinson',
    'Windrow',
    'Cook',
    'Wolfe',
    'Chapman',
    'Malone',
    'Green',
    'Fairbank',
    'Wood',
    'Miller',
    'Clayton',
    'Russell',
    'Atkinson',
    'Whitehead',
    'Greene',
    'Cannon',
    'Pope',
];

const careManagers = ['Luke Skywalker', 'Leia Organa', 'Han Solo', 'Padme Amidala'];
