import React, { FunctionComponent } from "react";

import { Grid, Typography } from "@mui/material";
import {
  GridColDef,
  GridRowHeightParams,
  GridRowParams,
} from "@mui/x-data-grid";
import { format } from "date-fns";
import { observer } from "mobx-react";
import { IAssessment, IMoodLog } from "shared/types";
import ActionPanel from "src/components/common/ActionPanel";
import { AssessmentVis } from "src/components/common/AssessmentVis";
import { renderMultilineCell, Table } from "src/components/common/Table";
import { getString } from "src/services/strings";
import { usePatient, useStores } from "src/stores/stores";

export interface IMoodProgressProps {
  assessment: IAssessment;
  maxValue: number;
  moodLogsSortedByDateAndTime: IMoodLog[];
  moodLogsSortedByDateAndTimeDescending: IMoodLog[];
}

export const MoodProgress: FunctionComponent<IMoodProgressProps> = observer(
  (props) => {
    const currentPatient = usePatient();
    const rootStore = useStores();

    const {
      moodLogsSortedByDateAndTime,
      moodLogsSortedByDateAndTimeDescending,
      assessment,
      maxValue,
    } = props;

    const assessmentContent = rootStore.getAssessmentContent(
      assessment.assessmentId,
    );

    const tableData = moodLogsSortedByDateAndTimeDescending?.map((a) => {
      return {
        date: format(a.recordedDateTime, "MM/dd/yy"),
        time: format(a.recordedDateTime, "hh:mm aa"),
        rating: a.mood,
        id: a.moodLogId,
        comment: a.comment,
      };
    });

    const columns: GridColDef[] = [
      {
        field: "date",
        headerName: "Date",
        width: 65,
        align: "center",
        headerAlign: "center",
      },
      {
        field: "time",
        headerName: "Time",
        width: 65,
        align: "center",
        headerAlign: "center",
      },
      {
        field: "rating",
        headerName: getString("patient_progress_mood_header_mood"),
        width: 60,
        align: "center",
        headerAlign: "center",
      },
      {
        field: "comment",
        headerName: getString("patient_progress_mood_header_comment"),
        width: 300,
        flex: 1,
        align: "left",
        headerAlign: "center",
        renderCell: renderMultilineCell,
      },
    ];

    const getRowClassName = React.useCallback((param: GridRowParams) => {
      const id = param.row["id"] as string;
      const data = currentPatient.getRecentEntryMoodLogById(id);
      if (!!data) {
        return "recentEntryRow";
      } else {
        return "";
      }
    }, []);

    const getRowHeight = React.useCallback((param: GridRowHeightParams) => {
      const id = param.id as string;
      const data = currentPatient.getMoodLogById(id);

      if (!!data && !!data.comment && data.comment.length >= 200) {
        return 60;
      }

      return undefined;
    }, []);

    return (
      <ActionPanel
        id={assessment.assessmentId}
        title={assessmentContent?.name || "Mood"}
        loading={
          currentPatient?.loadPatientState.pending ||
          currentPatient?.loadMoodLogsState.pending
        }
        error={currentPatient?.loadMoodLogsState.error}
      >
        <Grid container alignItems="stretch">
          {!!moodLogsSortedByDateAndTime &&
            moodLogsSortedByDateAndTime.length > 0 && (
              <Table
                rows={tableData}
                columns={columns.map((c) => ({
                  sortable: false,
                  filterable: false,
                  editable: false,
                  hideSortIcons: true,
                  disableColumnMenu: true,
                  ...c,
                }))}
                // These heights are similar to a 'density' of 'compact'.
                // But density is multiplied against these, so do not also apply it.
                headerHeight={36}
                // Row height of 40 allows display of 2 rows of text.
                rowHeight={40}
                // getRowHeight aims to detect situations where more height is needed.
                getRowHeight={getRowHeight}
                autoHeight={true}
                isRowSelectable={() => false}
                pagination
                rowsPerPageOptions={[10, 25, 50, 100]}
                initialState={{
                  pagination: {
                    pageSize: 25,
                  },
                }}
                getRowClassName={getRowClassName}
              />
            )}
          {!!moodLogsSortedByDateAndTime &&
            moodLogsSortedByDateAndTime.length > 0 && (
              <Grid item xs={12}>
                <AssessmentVis
                  data={moodLogsSortedByDateAndTime.map((log) => ({
                    recordedDateTime: log.recordedDateTime,
                    pointValues: { Mood: log.mood },
                  }))}
                  maxValue={maxValue}
                  useTime={true}
                />
              </Grid>
            )}
          {(!moodLogsSortedByDateAndTime ||
            moodLogsSortedByDateAndTime.length == 0) && (
            <Grid item xs={12}>
              <Typography>
                {getString("patient_progress_mood_empty")}
              </Typography>
            </Grid>
          )}
        </Grid>
      </ActionPanel>
    );
  },
);

export default MoodProgress;
