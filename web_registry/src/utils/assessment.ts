import { compareDesc } from 'date-fns';
import { sum } from 'lodash';
import { AssessmentData, IAssessment, IAssessmentContent, IAssessmentLog } from 'src/services/types';

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
    return getOrder(a.assessmentId) - getOrder(b.assessmentId);
};

export const sortAssessmentContent = (a: IAssessmentContent, b: IAssessmentContent) => {
    return getOrder(a.name) - getOrder(b.name);
};

export const getAssessmentScore = (pointValues: AssessmentData) => {
    return sum(Object.keys(pointValues).map((k) => pointValues[k] || 0));
};

export const getLatestScore = (assessmentLogs: IAssessmentLog[], assessmentName: string) => {
    const filteredAssessmentLogs = assessmentLogs.filter((a) => a.assessmentName == assessmentName);
    if (filteredAssessmentLogs.length > 0) {
        const sortedAssessments = assessmentLogs.slice().sort((a, b) => compareDesc(a.recordedDate, b.recordedDate));
        const latest = sortedAssessments[0];

        if (!!latest.totalScore) {
            return latest.totalScore;
        } else {
            return getAssessmentScore(latest.pointValues);
        }
    }

    return -1;
};

export const getAssessmentScoreColorName = (assessmentId: string, totalScore: number) => {
    if (assessmentId == 'PHQ-9' || assessmentId == 'GAD-7') {
        if (totalScore > 15) {
            return 'bad';
        } else if (totalScore > 10) {
            return 'warning';
        } else if (totalScore >= 0) {
            return 'good';
        }
    }

    if (assessmentId == 'Mood Logging') {
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
