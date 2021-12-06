import { AssessmentData } from 'shared/types';
import { sum } from 'src/utils/array';

export const getAssessmentScore = (pointValues: AssessmentData) => {
    return sum(Object.keys(pointValues).map((k) => pointValues[k] || 0));
};
