import React, { FunctionComponent } from "react";

import { Grid, Typography } from "@mui/material";
import {
  GridColDef,
  GridRowHeightParams,
  GridRowParams,
} from "@mui/x-data-grid";
import { isBefore } from "date-fns";
import compareDesc from "date-fns/compareDesc";
import { observer } from "mobx-react";
import { ActivitySuccessType } from "shared/enums";
import { IActivityLog } from "shared/types";
import ActionPanel from "src/components/common/ActionPanel";
import {
  dateFormatter,
  nullUndefinedFormatter,
  renderMultilineCell,
  Table,
  TableRowHeight_2RowsNoScroll,
  TableRowHeight_3RowsNoScroll,
} from "src/components/common/Table";
import { getString } from "src/services/strings";
import { usePatient } from "src/stores/stores";

export const ActivityProgress: FunctionComponent = observer(() => {
  const currentPatient = usePatient();

  const logMap = new Map<string, IActivityLog>();

  currentPatient.activityLogs?.slice().forEach((log) => {
    logMap.set(log.scheduledActivityId, log);
  });

  const logs = currentPatient.scheduledActivities
    ?.slice()
    .filter((a) => isBefore(a.dueDateTime, new Date()) || a.completed)
    .sort((a, b) => compareDesc(a.dueDateTime, b.dueDateTime))
    .map((scheduledActivity) => ({
      ...scheduledActivity,
    }));

  const getCompleted = (success: ActivitySuccessType) => {
    switch (success) {
      case "Yes":
        return getString("patient_progress_activity_success_yes");
      case "No":
        return getString("patient_progress_activity_success_no");
      default:
        return getString("patient_progress_activity_success_maybe");
    }
  };

  const tableData = logs?.map((log) => {
    const activityLog = logMap.get(log.scheduledActivityId);

    return {
      id: log.scheduledActivityId,
      name: log.dataSnapshot.activity.name,
      dueDate: log.dueDateTime,
      // format(log.dueDateTime, "MM/dd/yyyy"),
      recordedDateTime: log.completed
        ? activityLog?.recordedDateTime
        : undefined,
      // log.completed && activityLog?.recordedDateTime
      //   ? format(activityLog?.recordedDateTime, "MM/dd/yyyy")
      //   : "--",
      completed:
        log.completed && activityLog?.success
          ? getCompleted(activityLog?.success)
          : "--",
      alternative: activityLog?.alternative || "--",
      pleasure:
        log.completed && activityLog?.success != "No"
          ? activityLog?.pleasure
          : "--",
      accomplishment:
        log.completed && activityLog?.success != "No"
          ? activityLog?.accomplishment
          : "--",
      comment: log.completed ? activityLog?.comment : "--",
    };
  });

  const columns: GridColDef[] = [
    {
      field: "dueDate",
      headerName: getString("patient_progress_activity_header_due_date"),
      width: 65,
      align: "center",
      headerAlign: "center",
      valueFormatter: nullUndefinedFormatter(dateFormatter),
    },
    {
      field: "recordedDateTime",
      headerName: getString("patient_progress_activity_header_submitted_date"),
      width: 65,
      align: "center",
      headerAlign: "center",
      valueFormatter: nullUndefinedFormatter(dateFormatter),
    },
    {
      field: "name",
      headerName: getString("patient_progress_activity_header_activity"),
      width: 200,
      align: "left",
      headerAlign: "center",
      renderCell: renderMultilineCell,
    },
    {
      field: "completed",
      headerName: getString("patient_progress_activity_header_success"),
      width: 125,
      align: "left",
      headerAlign: "center",
      renderCell: renderMultilineCell,
    },
    {
      field: "alternative",
      headerName: getString("patient_progress_activity_header_alternative"),
      width: 150,
      align: "left",
      headerAlign: "center",
      renderCell: renderMultilineCell,
    },
    {
      field: "pleasure",
      headerName: getString("patient_progress_activity_header_pleasure"),
      width: 65,
      align: "center",
      headerAlign: "center",
    },
    {
      field: "accomplishment",
      headerName: getString("patient_progress_activity_header_accomplishment"),
      width: 65,
      align: "center",
      headerAlign: "center",
    },
    {
      field: "comment",
      headerName: getString("patient_progress_activity_header_comment"),
      width: 200,
      flex: 1,
      align: "left",
      headerAlign: "center",
      renderCell: renderMultilineCell,
    },
  ];

  const getRowClassName = React.useCallback((param: GridRowParams) => {
    const id = param.row["id"] as string;
    const data = currentPatient.getRecentEntryScheduledActivityById(id);
    if (!!data && data.completed) {
      return "recentEntryRow";
    } else {
      return "";
    }
  }, []);

  const getRowHeight = React.useCallback(
    (param: GridRowHeightParams) => {
      const id = param.id as string;

      const data = currentPatient.getScheduledActivityById(id);
      if (data) {
        const log = logMap.get(data.scheduledActivityId);

        if (data.dataSnapshot.activity.name.length > 100) {
          return TableRowHeight_3RowsNoScroll;
        }

        if (!!log && !!log.alternative && log.alternative.length >= 50) {
          return TableRowHeight_3RowsNoScroll;
        }

        if (!!log && !!log.comment && log.comment.length >= 50) {
          return TableRowHeight_3RowsNoScroll;
        }
      }

      return undefined;
    },
    [logMap],
  );

  return (
    <ActionPanel
      id={getString("patient_progress_activity_hash")}
      title={getString("patient_progress_activity_name")}
      loading={
        currentPatient?.loadPatientState.pending ||
        currentPatient?.loadActivityLogsState.pending
      }
      error={currentPatient?.loadActivityLogsState.error}
    >
      <Grid container alignItems="stretch">
        {!!logs && logs.length > 0 && (
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
            // Default to allow 2 rows.
            rowHeight={TableRowHeight_2RowsNoScroll}
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
        {(!logs || logs.length == 0) && (
          <Grid item xs={12}>
            <Typography>
              {getString("patient_progress_activity_empty")}
            </Typography>
          </Grid>
        )}
      </Grid>
    </ActionPanel>
  );
});

export default ActivityProgress;
