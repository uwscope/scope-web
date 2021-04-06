import { Grid } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import AssessmentProgress from 'src/components/PatientDetail/AssessmentProgress';
import { IAssessmentContent, KeyedMap } from 'src/services/types';
import { useStores } from 'src/stores/stores';
import { contains } from 'src/utils/array';

export const ProgressInformation: FunctionComponent = observer(() => {
    const {
        currentPatient,
        appConfig: { assessments },
    } = useStores();

    const validAssessments = assessments.reduce(
        (prev, curr) => ({ ...prev, [curr.name]: curr }),
        {}
    ) as KeyedMap<IAssessmentContent>;
    const validAssessmentNames = Object.keys(validAssessments);
    const patientAssessments = currentPatient?.assessments.filter((a) =>
        contains(validAssessmentNames, a.assessmentType)
    );

    if (!!patientAssessments) {
        return (
            <Grid container spacing={3} alignItems="stretch" direction="row">
                {patientAssessments.map((a) => {
                    const assessmentContent = validAssessments[a.assessmentType];
                    const assessmentMax = Math.max(...assessmentContent.options.map((o) => o.value));
                    return (
                        <Grid item xs={12} sm={12} key={a.assessmentType}>
                            <AssessmentProgress
                                assessment={a}
                                instruction={assessmentContent.instruction}
                                questions={assessmentContent.questions}
                                options={assessmentContent.options}
                                maxValue={assessmentMax}
                                onSaveAssessmentData={(assessmentData) =>
                                    currentPatient?.updateAssessmentRecord(assessmentData)
                                }
                            />
                        </Grid>
                    );
                })}
            </Grid>
        );
    }

    return null;
});

export default ProgressInformation;
