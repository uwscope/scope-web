import { IAppContentConfig, IAssessmentContent, ILifeAreaContent } from 'shared/types';

const phq9Assessment: IAssessmentContent = {
    id: 'phq-9',
    name: 'PHQ-9',
    instruction: 'Over the last 2 weeks, how often have you been bothered by any of the following problems?',
    questions: [
        { question: 'Little interest or pleasure in doing things', id: 'Interest' },
        { question: 'Feeling down, depressed, or hopeless', id: 'Feeling' },
        {
            question: 'Trouble falling or staying asleep, or sleeping too much',
            id: 'Sleep',
        },
        { question: 'Feeling tired or having little energy', id: 'Tired' },
        { question: 'Poor appetite or overeating', id: 'Appetite' },
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
        {
            question: 'Thoughts that you would be better off dead, or of hurting yourself',
            id: 'Suicide',
        },
    ],
    options: [
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
    ],
    interpretationName: 'Depression severity',
    interpretationTable: [
        {
            score: '0-4',
            max: 4,
            interpretation: 'None/minimal',
        },
        {
            score: '5-9',
            max: 9,
            interpretation: 'Mild',
        },
        {
            score: '10-14',
            max: 14,
            interpretation: 'Moderate',
        },
        {
            score: '15-19',
            max: 19,
            interpretation: 'Moderately severe',
        },
        {
            score: '20-27',
            max: 27,
            interpretation: 'Severe',
        },
    ],
};

const gad7Assessment: IAssessmentContent = {
    id: 'gad-7',
    name: 'GAD-7',
    instruction: 'Over the last 2 weeks, how often have you been bothered by any of the following problems?',
    questions: [
        { question: 'Feeling nervous, anxious or on edge', id: 'Anxious' },
        {
            question: 'Not being able to stop or control worrying',
            id: 'Constant worrying',
        },
        {
            question: 'Worrying too much about different things',
            id: 'Worrying too much',
        },
        { question: 'Trouble relaxing', id: 'Trouble relaxing' },
        {
            question: 'Being so restless that it is hard to sit still',
            id: 'Restless',
        },
        { question: 'Becoming easily annoyed or irritated', id: 'Irritable' },
        {
            question: 'Feeling afraid as if something awful might happen',
            id: 'Afraid',
        },
    ],
    options: [
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
    ],
    interpretationName: 'Anxiety severity',
    interpretationTable: [
        {
            score: '0-5',
            max: 5,
            interpretation: 'None',
        },
        {
            score: '6-10',
            max: 10,
            interpretation: 'Mild',
        },
        {
            score: '11-15',
            max: 15,
            interpretation: 'Moderate',
        },
        {
            score: '16-21',
            max: 21,
            interpretation: 'Severe',
        },
    ],
};

const relationshipLifeArea = {
    id: 'relationship',
    name: 'Relationship/Social Life',
    examples: [
        {
            name: 'Being a loving parent',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being a caring partner',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being an attentive and supportive friend',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
    ],
} as ILifeAreaContent;

const educationLifeArea = {
    id: 'education',
    name: 'Education/Career/Contributing',
    examples: [
        {
            name: 'Being a loving parent',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being a caring partner',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being an attentive and supportive friend',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
    ],
} as ILifeAreaContent;

const recreationLifeArea = {
    id: 'recreation',
    name: 'Recreation/Interests/Creativity',
    examples: [
        {
            name: 'Being a loving parent',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being a caring partner',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being an attentive and supportive friend',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
    ],
} as ILifeAreaContent;

const mindBodyLifeArea = {
    id: 'mindbody',
    name: 'Mind/Body/Spirituality',
    examples: [
        {
            name: 'Being a loving parent',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being a caring partner',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being an attentive and supportive friend',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
    ],
} as ILifeAreaContent;

const responsibilitiesLifeArea = {
    id: 'responsibilities',
    name: 'Responsibilities',
    examples: [
        {
            name: 'Being a loving parent',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being a caring partner',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
        {
            name: 'Being an attentive and supportive friend',
            activities: [
                {
                    name: 'Tell my child I love them every day',
                },
                {
                    name: 'Make a special breakfast for my child on Saturday',
                },
                {
                    name: 'Take my child to the part on Saturday',
                },
                {
                    name: 'Pick up my child from school promptly each day',
                },
            ],
        },
    ],
} as ILifeAreaContent;

const resources = [
    {
        id: 'ba-model',
        name: 'Review of behavioral activation model',
        resources: [
            {
                name: 'Form A client education',
                filename: 'sample.pdf',
            },
            {
                name: 'Form B vicious cycle',
                filename: 'sample.pdf',
            },
        ],
    },
    {
        id: 'ba-monitor',
        name: 'Mood and activity monitoring',
        resources: [
            {
                name: 'Form A client education',
                filename: 'sample.pdf',
            },
            {
                name: 'Form B vicious cycle',
                filename: 'sample.pdf',
            },
        ],
    },
    {
        id: 'ba-values',
        name: 'Values and goals assessment',
        resources: [
            {
                name: 'Form A client education',
                filename: 'sample.pdf',
            },
            {
                name: 'Form B vicious cycle',
                filename: 'sample.pdf',
            },
        ],
    },
    {
        id: 'ba-schedule',
        name: 'Activity scheduling',
        resources: [
            {
                name: 'Form A client education',
                filename: 'sample.pdf',
            },
            {
                name: 'Form B vicious cycle',
                filename: 'sample.pdf',
            },
        ],
    },
];

export const defaultAppContentConfig: IAppContentConfig = {
    assessments: [phq9Assessment, gad7Assessment],
    lifeAreas: [
        relationshipLifeArea,
        educationLifeArea,
        recreationLifeArea,
        mindBodyLifeArea,
        responsibilitiesLifeArea,
    ],
    resources,
};
