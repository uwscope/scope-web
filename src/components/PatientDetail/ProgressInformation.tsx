import { Grid } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import AssessmentProgress from 'src/components/PatientDetail/AssessmentProgress';
import {
    gadInstruction,
    gadMax,
    gadOptions,
    gadQuestions,
    moodMax,
    moodOptions,
    moodQuestions,
    phqInstruction,
    phqMax,
    phqOptions,
    phqQuestions,
} from 'src/services/assessments';
import { useStores } from 'src/stores/stores';

export const ProgressInformation: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const phqProgress = currentPatient?.assessments.find((a) => a.assessmentType == 'PHQ-9');
    const gadProgress = currentPatient?.assessments.find((a) => a.assessmentType == 'GAD-7');
    const moodProgress = currentPatient?.assessments.find((a) => a.assessmentType == 'Mood Logging');

    return (
        <Grid container spacing={3} alignItems="stretch" direction="row">
            {!!phqProgress && (
                <Grid item xs={12} sm={12}>
                    <AssessmentProgress
                        assessment={phqProgress}
                        instruction={phqInstruction}
                        questions={phqQuestions}
                        options={phqOptions}
                        maxValue={phqMax}
                        onSaveAssessmentData={(assessmentData) =>
                            currentPatient?.updateAssessmentRecord(assessmentData)
                        }
                    />
                </Grid>
            )}
            {!!gadProgress && (
                <Grid item xs={12} sm={12}>
                    <AssessmentProgress
                        assessment={gadProgress}
                        instruction={gadInstruction}
                        questions={gadQuestions}
                        options={gadOptions}
                        maxValue={gadMax}
                        onSaveAssessmentData={(assessmentData) =>
                            currentPatient?.updateAssessmentRecord(assessmentData)
                        }
                    />
                </Grid>
            )}
            {!!moodProgress && (
                <Grid item xs={12} sm={12}>
                    <AssessmentProgress
                        assessment={moodProgress}
                        questions={moodQuestions}
                        options={moodOptions}
                        maxValue={moodMax}
                        onSaveAssessmentData={(assessmentData) =>
                            currentPatient?.updateAssessmentRecord(assessmentData)
                        }
                    />
                </Grid>
            )}
        </Grid>
    );
});

export default ProgressInformation;
