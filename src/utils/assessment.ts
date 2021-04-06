import { AssessmentData, IAssessment } from 'src/services/types';
import { sum } from 'src/utils/array';

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

export const getAssessmentScore = (pointValues: AssessmentData) => {
    return sum(Object.keys(pointValues).map((k) => pointValues[k] || 0));
};
