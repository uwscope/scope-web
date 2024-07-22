// NOTE: This component increases transparency by displaying the most recent patient interaction details. Final implementation may vary.

import React, { FunctionComponent } from "react";

import { Grid } from "@mui/material";
import { observer } from "mobx-react";
import ActionPanel from "src/components/common/ActionPanel";
import { GridTextField } from "src/components/common/GridField";
import { usePatient } from "src/stores/stores";

export const RecentInteraction: FunctionComponent = observer(() => {
  const currentPatient = usePatient();

  const loading =
    currentPatient?.loadPatientState.pending ||
    currentPatient?.loadActivitiesState.pending ||
    currentPatient?.loadActivityLogsState.pending ||
    currentPatient?.loadSessionsState.pending ||
    currentPatient?.loadAssessmentLogsState.pending;
  const error =
    currentPatient?.loadActivitiesState.error ||
    currentPatient?.loadActivityLogsState.error ||
    currentPatient?.loadSessionsState.error ||
    currentPatient?.loadAssessmentLogsState.error;

  return (
    <ActionPanel
      id="recent-interaction"
      title="Recent Patient Interaction"
      loading={loading}
      error={error}
    >
      <Grid container spacing={2} alignItems="stretch">
        <GridTextField
          sm={12}
          label="Patient Interaction Date"
          value={currentPatient.recentInteractionCutoffDateTime}
        />
        <GridTextField
          sm={3}
          label="Activities Count"
          value={
            currentPatient.recentActivities
              ? currentPatient.recentActivities.length
              : "No Recent Activities"
          }
        />
        <GridTextField
          sm={3}
          label="Activities"
          value={currentPatient.recentActivities
            ?.map((activity) => activity.name)
            .join(", ")}
          multiline={true}
        />
        <GridTextField
          sm={3}
          label="Values Count"
          value={
            currentPatient.recentValues
              ? currentPatient.recentValues.length
              : "No Recent Values"
          }
        />
        <GridTextField
          sm={3}
          label="Values"
          value={currentPatient.recentValues
            ?.map((value) => value.name)
            .join(", ")}
          multiline={true}
        />
        <GridTextField
          sm={3}
          label="Activity Logs Counts"
          value={
            currentPatient.recentActivityLogsSortedByDateAndTimeDescending
              ?.length
          }
        />
        <GridTextField
          sm={3}
          label="Assessment Logs Count"
          value={
            currentPatient.recentAssessmentLogsSortedByDateAndTimeDescending
              ?.length
          }
        />
        <GridTextField
          sm={3}
          label="Mood Logs Count"
          value={
            currentPatient.recentMoodLogsSortedByDateAndTimeDescending?.length
          }
        />
        <GridTextField
          sm={3}
          label="Mood Log Scores"
          value={currentPatient.recentMoodLogsSortedByDateAndTimeDescending
            ?.map((moodLog) => moodLog.mood)
            .join(", ")}
          multiline={true}
        />
        <GridTextField
          sm={3}
          label="Safety Plan Update"
          value={
            currentPatient.recentSafetyPlan
              ? currentPatient.recentSafetyPlan.lastUpdatedDateTime
              : "No Recent Update on Safety Plan"
          }
        />
      </Grid>
    </ActionPanel>
  );
});

export default RecentInteraction;
