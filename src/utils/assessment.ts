import { compareDesc } from 'date-fns';
import { AssessmentData, IAssessment, IAssessmentContent } from 'src/services/types';
import { sum } from 'src/utils/array';

const getOrder = (assessment: string) => {
    switch (assessment) {
        case 'PHQ-9':
            return 1;
        case 'GAD-7':
            return 2;
        default:
            return 3;
    }
};

export const sortAssessment = (a: IAssessment, b: IAssessment) => {
    return getOrder(a.assessmentType) - getOrder(b.assessmentType);
};

export const sortAssessmentContent = (a: IAssessmentContent, b: IAssessmentContent) => {
    return getOrder(a.name) - getOrder(b.name);
};

export const getAssessmentScore = (pointValues: AssessmentData) => {
    return sum(Object.keys(pointValues).map((k) => pointValues[k] || 0));
};

export const getLatestScore = (assessment: IAssessment) => {
    if (assessment?.data && assessment.data.length > 0) {
        const latest = assessment.data[assessment.data.length - 1];

        if (!!latest.totalScore) {
            return latest.totalScore;
        } else {
            return getAssessmentScore(assessment.data[assessment.data.length - 1].pointValues);
        }
    }

    return -1;
};

export const getLatestScores = (assessments: IAssessment[]) => {
    return assessments
        .filter((a) => a.data.length > 0)
        .map((a) => {
            return `${a.assessmentType}=${getAssessmentScore(
                a.data.slice().sort((a, b) => compareDesc(a.date, b.date))[0].pointValues
            )}`;
        })
        .join('; ');
};

export const getAssessmentScoreColorName = (assessmentType: string, totalScore: number) => {
    if (assessmentType == 'PHQ-9' || assessmentType == 'GAD-7') {
        if (totalScore > 15) {
            return 'bad';
        } else if (totalScore > 10) {
            return 'warning';
        } else if (totalScore >= 0) {
            return 'good';
        }
    }

    if (assessmentType == 'Mood Logging') {
        if (totalScore < 2) {
            return 'bad';
        } else if (totalScore < 4) {
            return 'warning';
        } else if (totalScore >= 0) {
            return 'good';
        }
    }

    return 'unknown';
};
