import { IAssessment } from 'src/services/types';

export const phqInstruction =
    'Over the last 2 weeks, how often have you been bothered by any of the following problems?';

export const phqQuestions = [
    { question: 'Little interest or pleasure in doing things', id: 'Interest' },
    { question: 'Feeling down, depressed, or hopeless', id: 'Feeling' },
    { question: 'Trouble falling or staying asleep, or sleeping too much', id: 'Sleep' },
    { question: 'Feeling tired or having little energy', id: 'Tired' },
    { question: 'Poor appetite or overeating', id: 'Apetite' },
    {
        question: 'Feeling bad about yourself or that you are a failure or have let yourself or your family down',
        id: 'Failure',
    },
    {
        question: 'Trouble concentrating on things, such as reading the newspaper or watching television',
        id: 'Concentrating',
    },
    {
        question:
            'Moving or speaking so slowly that other people could have noticed. Or the opposite being so figety or restless that you have been moving around a lot more than usual',
        id: 'Slowness',
    },
    { question: 'Thoughts that you would be better off dead, or of hurting yourself', id: 'Suicide' },
];

export const phqOptions = [
    {
        text: 'Not at all',
        value: 0,
    },
    {
        text: 'Several days',
        value: 1,
    },
    {
        text: 'More than half the days',
        value: 2,
    },
    {
        text: 'Nearly every day',
        value: 3,
    },
];

export const phqMax = 3;

export const gadInstruction =
    'Over the last 2 weeks, how often have you been bothered by any of the following problems?';

export const gadQuestions = [
    { question: 'Feeling nervous, anxious or on edge', id: 'Anxious' },
    { question: 'Not being able to stop or control worrying', id: 'Constant worrying' },
    { question: 'Worrying too much about different things', id: 'Worrying too much' },
    { question: 'Trouble relaxing', id: 'Trouble relaxing' },
    { question: 'Being so restless that it is hard to sit still', id: 'Restless' },
    { question: 'Becoming easily annoyed or irritated', id: 'Irritable' },
    { question: 'Feeling afraid as if something awful might happen', id: 'Afraid' },
];

export const gadOptions = [
    {
        text: 'Not at all',
        value: 0,
    },
    {
        text: 'Several days',
        value: 1,
    },
    {
        text: 'More than half the days',
        value: 2,
    },
    {
        text: 'Nearly every day',
        value: 3,
    },
];

export const gadMax = 3;

export const moodQuestions = [{ question: 'Please rate your mood', id: 'Mood' }];

export const moodOptions = [
    {
        text: 'Awful',
        value: 1,
    },
    {
        text: 'Bad',
        value: 2,
    },
    {
        text: 'Okay',
        value: 3,
    },
    {
        text: 'Great',
        value: 4,
    },
    {
        text: 'Awesome',
        value: 5,
    },
];

export const moodMax = 5;

export const sortAssessment = (a: IAssessment, b: IAssessment) => {
    const getOrder = (assessment: IAssessment) => {
        switch (assessment.assessmentType) {
            case 'PHQ-9':
                return 1;
            case 'GAD-7':
                return 2;
            default:
                return 3;
        }
    };

    return getOrder(a) - getOrder(b);
};
