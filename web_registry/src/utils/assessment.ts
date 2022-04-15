import { compareDesc } from 'date-fns';
import { sum } from 'lodash';
import { AssessmentData, IAssessment, IAssessmentContent, IAssessmentLog } from 'shared/types';

const getOrder = (assessment: string) => {
    switch (assessment.toLowerCase()) {
        case 'phq-9':
            return 1;
        case 'gad-7':
            return 2;
        default:
            return 3;
    }
};

export const sortAssessment = (a: IAssessment, b: IAssessment) => {
    return getOrder(a.assessmentId) - getOrder(b.assessmentId);
};

export const sortAssessmentIds = (a: string, b: string) => {
    return getOrder(a) - getOrder(b);
};

export const sortAssessmentContent = (a: IAssessmentContent, b: IAssessmentContent) => {
    return getOrder(a.id) - getOrder(b.id);
};

export const getAssessmentScoreFromAssessmentLog = (log: IAssessmentLog) => {
    if (log.totalScore != undefined && log.totalScore >= 0) {
        return log.totalScore;
    } else {
        return sum(Object.keys(log.pointValues).map((k) => log.pointValues[k] || 0));
    }
};

export const getAssessmentScoreFromPointValues = (pointValues: AssessmentData) => {
    return sum(Object.keys(pointValues).map((k) => pointValues[k] || 0));
};

export const getLatestScore = (assessmentLogs: IAssessmentLog[], assessmentId: string) => {
    const filteredAssessmentLogs = assessmentLogs.filter((a) => a.assessmentId == assessmentId);
    if (filteredAssessmentLogs.length > 0) {
        const sortedAssessments = filteredAssessmentLogs
            .slice()
            .sort((a, b) => compareDesc(a.recordedDateTime, b.recordedDateTime));
        const latest = sortedAssessments[0];

        if (!!latest.totalScore) {
            return latest.totalScore;
        } else {
            return getAssessmentScoreFromPointValues(latest.pointValues);
        }
    }

    return -1;
};

export const getAssessmentScoreColorName = (assessmentId: string, totalScore: number) => {
    const lowAssessmentId = assessmentId.toLowerCase();
    if (lowAssessmentId == 'phq-9' || lowAssessmentId == 'gad-7') {
        if (totalScore >= 15) {
            return 'bad';
        } else if (totalScore >= 10) {
            return 'warning';
        } else if (totalScore >= 0) {
            return 'good';
        }
    }

    if (lowAssessmentId == 'mood') {
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
