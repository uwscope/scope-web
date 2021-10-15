import { Grid } from '@material-ui/core';
import { format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';
import { BehavioralStrategyChecklistItem, Referral } from 'src/services/enums';
import { BehavioralStrategyChecklistFlags } from 'src/services/types';
import { usePatient } from 'src/stores/stores';
import { getLatestScore } from 'src/utils/assessment';

export const TreatmentInfo: FunctionComponent = observer(() => {
    const currentPatient = usePatient();

    const latestPhQ = currentPatient?.assessments.find((a) => a.assessmentType == 'PHQ-9');
    const latestPhqScore = !!latestPhQ ? getLatestScore(latestPhQ) : -1;
    const latestGAD = currentPatient?.assessments.find((a) => a.assessmentType == 'GAD-7');
    const latestGadScore = !!latestGAD ? getLatestScore(latestGAD) : -1;

    const latestSessionDate = currentPatient.latestSession?.date;
    const currentMedications = currentPatient.latestSession?.currentMedications;
    const behavioralStrategiesUsedFlags: BehavioralStrategyChecklistFlags = {
        'Behavioral Activation': false,
        'Motivational Interviewing': false,
        'Problem Solving Therapy': false,
        'Cognitive Therapy': false,
        'Mindfulness Strategies': false,
        'Supportive Therapy': false,
        Other: false,
    };

    currentPatient.sessions.forEach((s) => {
        Object.keys(s.behavioralStrategyChecklist).forEach((k) => {
            if (!!s.behavioralStrategyChecklist[k as BehavioralStrategyChecklistItem]) {
                behavioralStrategiesUsedFlags[k as BehavioralStrategyChecklistItem] = true;
            }
        });
    });

    const behavioralStrategiesUsedList: string[] = [];
    Object.keys(behavioralStrategiesUsedFlags).forEach((k) => {
        if (!!behavioralStrategiesUsedFlags[k as BehavioralStrategyChecklistItem]) {
            behavioralStrategiesUsedList.push(k);
        }
    });

    const behavioralStrategiesUsed = behavioralStrategiesUsedList.join('\n');

    const latestReferralsFlags = currentPatient.latestSession?.referralStatus;
    const referralsList: string[] = [];
    if (!!latestReferralsFlags) {
        Object.keys(latestReferralsFlags).forEach((k) => {
            if (latestReferralsFlags[k as Referral] != 'Not Referred') {
                referralsList.push(`${k} - ${latestReferralsFlags[k as Referral]}`);
            }
        });
    }

    const referrals = referralsList.join('\n');

    return (
        <ActionPanel id="treatment" title="Ongoing Treatment Information">
            <Grid container spacing={2} alignItems="stretch">
                <GridTextField
                    sm={6}
                    label="Latest PHQ-9 Score"
                    value={latestPhqScore > 0 ? latestPhqScore : 'No data'}
                    helperText={
                        !!latestPhQ && latestPhQ.data.length > 0
                            ? `Updated: ${format(latestPhQ.data[0].date, 'MM/dd/yyyy')}`
                            : undefined
                    }
                />
                <GridTextField
                    sm={6}
                    label="Latest GAD-7 Score"
                    value={latestGadScore > 0 ? latestGadScore : 'No data'}
                    helperText={
                        !!latestGAD && latestGAD.data.length > 0
                            ? `Updated: ${format(latestGAD.data[0].date, 'MM/dd/yyyy')}`
                            : undefined
                    }
                />
                <GridTextField
                    sm={12}
                    label="Current medications"
                    value={currentMedications}
                    helperText={!!latestSessionDate ? `Updated: ${format(latestSessionDate, 'MM/dd/yyyy')}` : undefined}
                />
                <GridTextField
                    sm={12}
                    label="Behavioral Strategies Used"
                    value={behavioralStrategiesUsed}
                    multiline={true}
                    helperText={!!latestSessionDate ? `Updated: ${format(latestSessionDate, 'MM/dd/yyyy')}` : undefined}
                />
                <GridTextField
                    sm={12}
                    label="Referrals"
                    value={referrals}
                    multiline={true}
                    helperText={!!latestSessionDate ? `Updated: ${format(latestSessionDate, 'MM/dd/yyyy')}` : undefined}
                />
            </Grid>
        </ActionPanel>
    );
});

export default TreatmentInfo;
