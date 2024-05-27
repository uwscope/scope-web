import React, { FunctionComponent } from "react";

import FlagIcon from "@mui/icons-material/Flag";
import { Tooltip } from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import {
  GridCellParams,
  GridCellValue,
  GridColDef,
  GridColumnHeaderParams,
  GridComparatorFn,
  gridDateComparator,
  gridNumberComparator,
  GridRenderCellParams,
  GridRowParams,
  GridSortModel,
  gridStringOrNumberComparator,
  GridValueFormatterParams,
} from "@mui/x-data-grid";
import {
  addWeeks,
  compareAsc,
  differenceInDays,
  differenceInMonths,
  differenceInWeeks,
} from "date-fns";
import { observer } from "mobx-react";
import { DiscussionFlags } from "shared/enums";
import { formatDateOnly, getFollowUpWeeks, toUTCDateOnly } from "shared/time";
import { Table } from "src/components/common/Table";
import { IPatientStore } from "src/stores/PatientStore";
import {
  getAssessmentScoreColorName,
  getAssessmentScoreFromAssessmentLog,
} from "src/utils/assessment";
import styled from "styled-components";

const TableContainer = styled.div({
  flexGrow: 1,
});

const ColumnHeader = styled.div({
  whiteSpace: "initial",
  fontWeight: 500,
  lineHeight: "1rem",
  textAlign: "center",
});

const PHQCell = withTheme(
  styled.div<{ score: number; risk: boolean }>((props) => ({
    width: "100%",
    padding: props.theme.spacing(2),
    textAlign: "center",
    backgroundColor:
      props.theme.customPalette.scoreColors[
        getAssessmentScoreColorName("PHQ-9", props.score)
      ],
    border: props.risk
      ? `2px solid ${props.theme.customPalette.flagColors["safety"]}`
      : "none",
  })),
);

const GADCell = withTheme(
  styled.div<{ score: number }>((props) => ({
    width: "100%",
    padding: props.theme.spacing(2),
    textAlign: "center",
    backgroundColor:
      props.theme.customPalette.scoreColors[
        getAssessmentScoreColorName("GAD-7", props.score)
      ],
  })),
);

const ChangeCell = withTheme(
  styled.div<{ change: number }>((props) => ({
    width: "100%",
    padding: props.theme.spacing(2),
    textAlign: "center",
    backgroundColor:
      props.change <= -50 && props.theme.customPalette.scoreColors["good"],
  })),
);

const HiglightedCell = withTheme(
  styled.div<{ scoreColorKey: string }>((props) => ({
    width: "100%",
    padding: props.theme.spacing(2),
    textAlign: "center",
    backgroundColor: props.theme.customPalette.scoreColors[props.scoreColorKey],
  })),
);

const RedFlag = withTheme(
  styled(FlagIcon)<{ $on: boolean }>((props) => ({
    color:
      props.theme.customPalette.flagColors[props.$on ? "safety" : "disabled"],
  })),
);

const YellowFlag = withTheme(
  styled(FlagIcon)<{ $on: boolean }>((props) => ({
    color:
      props.theme.customPalette.flagColors[
        props.$on ? "discussion" : "disabled"
      ],
  })),
);

const nullUndefinedComparator: (
  order: "first" | "last",
  comparator: GridComparatorFn,
) => GridComparatorFn = (order, comparator) => {
  // Grid's default comparators appear to sort undefined, but not null.
  // Direction of those comparators is also not configurable.
  // This wraps a provided comparator to configure sorting of both undefined and null.
  return (v1, v2, cellParams1, cellParams2) => {
    if (v1 === null || v1 === undefined || v2 === null || v2 === undefined) {
      // At least one value is not defined
      if (v1 !== null && v1 !== undefined) {
        // v1 is defined, but v2 is not
        if (order === "first") {
          return 1;
        } else {
          return -1;
        }
      } else if (v2 !== null && v2 !== undefined) {
        // v2 is defined, but v1 is not
        if (order === "first") {
          return -1;
        } else {
          return 1;
        }
      } else {
        // Neither value is defined
        return 0;
      }
    } else {
      // Both are defined
      return comparator(v1, v2, cellParams1, cellParams2);
    }
  };
};

const nullUndefinedFormatter: (
  formatter: (params: GridValueFormatterParams) => GridCellValue,
) => (params: GridValueFormatterParams) => GridCellValue = (formatter) => {
  return (params) => {
    if (params.value === null || params.value === undefined) {
      return NA;
    } else {
      return formatter(params);
    }
  };
};

const nullUndefinedRenderCell: (
  renderer: (params: GridRenderCellParams) => React.ReactNode,
) => (params: GridRenderCellParams) => React.ReactNode = (renderer) => {
  return (params: GridRenderCellParams) => {
    if (params.value === null || params.value === undefined) {
      return NA;
    } else {
      return renderer(params);
    }
  };
};

const flagsComparator: GridComparatorFn = (v1, v2) => {
  const v1FlaggedForSafety = !!(v1?.valueOf() as DiscussionFlags)?.[
    "Flag as safety risk"
  ];
  const v2FlaggedForSafety = !!(v2?.valueOf() as DiscussionFlags)?.[
    "Flag as safety risk"
  ];

  if (v1FlaggedForSafety && !v2FlaggedForSafety) {
    return -1;
  }
  if (v2FlaggedForSafety && !v1FlaggedForSafety) {
    return 1;
  }

  const v1FlaggedForDiscussion = !!(v1?.valueOf() as DiscussionFlags)?.[
    "Flag for discussion"
  ];
  const v2FlaggedForDiscussion = !!(v2?.valueOf() as DiscussionFlags)?.[
    "Flag for discussion"
  ];

  if (v1FlaggedForDiscussion && !v2FlaggedForDiscussion) {
    return -1;
  }
  if (v2FlaggedForDiscussion && !v1FlaggedForDiscussion) {
    return 1;
  }

  return 0;
};

const dateFormatter: (params: GridValueFormatterParams) => string = (
  params,
) => {
  return formatDateOnly(params.value as Date, "MM/dd/yy");
};

const stringOrNumberFormatter: (params: GridValueFormatterParams) => string = (
  params,
) => {
  return `${params.value}`;
};

const renderHeader = (props: GridColumnHeaderParams) => (
  <ColumnHeader>{props.colDef.headerName}</ColumnHeader>
);

const renderPHQCell = (props: GridCellParams, atRiskId: string) => (
  <PHQCell score={props.value as number} risk={!!props.row[atRiskId]}>
    {props.value}
  </PHQCell>
);

const renderGADCell = (props: GridCellParams) => (
  <GADCell score={props.value as number}>{props.value}</GADCell>
);

const renderChangeCell = (props: GridCellParams) => (
  <ChangeCell change={props.value as number}>{`${props.value}%`}</ChangeCell>
);

const renderCellFollowUpDue = (props: GridCellParams) => {
  const overdue = props.row["nextSessionOverdue"] as boolean;

  if (overdue) {
    return (
      <HiglightedCell scoreColorKey="warning">
        {props.formattedValue}
      </HiglightedCell>
    );
  } else {
    return props.formattedValue;
  }
};

const renderCellLastCaseReview = (props: GridCellParams) => {
  const overdue = props.row["recentCaseReviewOverdue"] as boolean;

  if (overdue) {
    return (
      <HiglightedCell scoreColorKey="warning">
        {props.formattedValue}
      </HiglightedCell>
    );
  } else {
    return props.formattedValue;
  }
};

const renderCellEnrollmentDate = (props: GridCellParams) => {
  const highlight = props.row["enrollmentDateHighlight"] as boolean;

  if (highlight) {
    return (
      <HiglightedCell scoreColorKey="warning">
        {props.formattedValue}
      </HiglightedCell>
    );
  } else {
    return props.formattedValue;
  }
};

const renderFlagCell = (props: GridCellParams) => {
  const flaggedForDiscussion = !!props.value?.["Flag for discussion"];
  const flaggedForSafety = !!props.value?.["Flag as safety risk"];

  return (
    <div>
      <Tooltip title="Flagged for safety">
        <RedFlag $on={flaggedForSafety} fontSize="small" />
      </Tooltip>
      <Tooltip title="Flagged for discussion">
        <YellowFlag $on={flaggedForDiscussion} fontSize="small" />
      </Tooltip>
    </div>
  );
};

const rowDefaultComparator = (v1: { name: string }, v2: { name: string }) => {
  // This comparator is applied to sort rows before they are provided to the grid.
  // When no sort is selected in the grid, this controls the rendering order.
  // When a sort is selected in the grid, this becomes the secondary sorting criterion.
  return v1.name.localeCompare(v2.name);
};

const NA = "--";

export interface ICaseloadTableProps {
  patients: ReadonlyArray<IPatientStore>;
  onPatientClick?: (recordId: string) => void;
}

export const CaseloadTable: FunctionComponent<ICaseloadTableProps> = observer(
  (props) => {
    const { patients, onPatientClick } = props;

    const defaultSortModel: GridSortModel = [
      {
        field: "name",
        sort: "asc",
      },
    ];

    const [sortModel, setSortModel] =
      React.useState<GridSortModel>(defaultSortModel);

    const onRowClick = (param: GridRowParams) => {
      if (!!onPatientClick) {
        const mrn = param.row["MRN"];
        const found = patients.find((p) => p.profile.MRN == mrn);

        if (!!found) {
          onPatientClick(found.recordId);
        }
      }
    };

    const onSortModelChange: (sortModelUpdate: GridSortModel) => void = (
      sortModelUpdate,
    ) => {
      if (sortModelUpdate.length === 0) {
        sortModelUpdate = defaultSortModel;
      }

      setSortModel(sortModelUpdate);
    };

    // Column names map to IPatientStore property names
    const columns: GridColDef[] = [
      {
        field: "discussionFlags",
        headerName: "Flags",
        width: 25,
        align: "center",
        headerAlign: "center",
        sortComparator: flagsComparator,
        renderCell: renderFlagCell,
      },
      {
        field: "depressionTreatmentStatus",
        headerName: "Tx Status",
        minWidth: 120,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator(
          "last",
          gridStringOrNumberComparator,
        ),
        valueFormatter: nullUndefinedFormatter(stringOrNumberFormatter),
      },
      {
        field: "name",
        headerName: "Name",
        minWidth: 240,
        align: "center",
        headerAlign: "center",
        sortComparator: gridStringOrNumberComparator,
        valueFormatter: stringOrNumberFormatter,
      },
      {
        field: "clinicCode",
        headerName: "Clinic Code",
        minWidth: 120,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator(
          "last",
          gridStringOrNumberComparator,
        ),
        valueFormatter: nullUndefinedFormatter(stringOrNumberFormatter),
      },
      {
        field: "site",
        headerName: "Site",
        minWidth: 120,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator(
          "last",
          gridStringOrNumberComparator,
        ),
        valueFormatter: nullUndefinedFormatter(stringOrNumberFormatter),
      },
      {
        field: "initialSession",
        headerName: "Initial Session",
        width: 85,
        renderHeader,
        align: "center",
        headerAlign: "center",
        filterable: false,
        sortComparator: nullUndefinedComparator("last", gridDateComparator),
        valueFormatter: nullUndefinedFormatter(dateFormatter),
      },
      {
        field: "recentSession",
        headerName: "Last Session",
        width: 85,
        renderHeader,
        align: "center",
        headerAlign: "center",
        filterable: false,
        sortComparator: nullUndefinedComparator("last", gridDateComparator),
        valueFormatter: nullUndefinedFormatter(dateFormatter),
      },
      {
        field: "recentCaseReview",
        headerName: "Last Case Review",
        width: 85,
        renderHeader,
        align: "center",
        headerAlign: "center",
        filterable: false,
        sortComparator: nullUndefinedComparator("last", gridDateComparator),
        valueFormatter: nullUndefinedFormatter(dateFormatter),
        renderCell: renderCellLastCaseReview,
      },
      {
        field: "nextSessionDue",
        headerName: "Follow-Up Due",
        width: 85,
        renderHeader,
        align: "center",
        headerAlign: "center",
        filterable: false,
        sortComparator: nullUndefinedComparator("last", gridDateComparator),
        valueFormatter: nullUndefinedFormatter(dateFormatter),
        renderCell: renderCellFollowUpDue,
      },
      {
        field: "totalSessions",
        headerName: "Total Sess",
        width: 50,
        renderHeader,
        align: "center",
        headerAlign: "center",
        filterable: false,
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        valueFormatter: nullUndefinedFormatter(stringOrNumberFormatter),
      },
      {
        field: "treatmentWeeks",
        headerName: "Wks in Tx",
        width: 50,
        renderHeader,
        align: "center",
        headerAlign: "center",
        filterable: false,
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        valueFormatter: nullUndefinedFormatter(stringOrNumberFormatter),
      },
      {
        field: "initialPHQ",
        headerName: "Initial PHQ-9",
        width: 50,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        renderCell: nullUndefinedRenderCell((props) =>
          renderPHQCell(props, "initialAtRisk"),
        ),
      },
      {
        field: "recentPHQ",
        headerName: "Last PHQ-9",
        width: 50,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        renderCell: nullUndefinedRenderCell((props) =>
          renderPHQCell(props, "recentAtRisk"),
        ),
      },
      {
        field: "changePHQ",
        headerName: "Change",
        width: 60,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        renderCell: nullUndefinedRenderCell(renderChangeCell),
      },
      {
        field: "recentPHQDate",
        headerName: "Last PHQ-9 Date",
        width: 85,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridDateComparator),
        valueFormatter: nullUndefinedFormatter(dateFormatter),
      },
      {
        field: "initialGAD",
        headerName: "Initial GAD-7",
        width: 50,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        renderCell: nullUndefinedRenderCell(renderGADCell),
      },
      {
        field: "recentGAD",
        headerName: "Last GAD-7",
        width: 50,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        renderCell: nullUndefinedRenderCell(renderGADCell),
      },
      {
        field: "changeGAD",
        headerName: "Change",
        width: 60,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridNumberComparator),
        renderCell: nullUndefinedRenderCell(renderChangeCell),
      },
      {
        field: "recentGADDate",
        headerName: "Last GAD-7 Date",
        width: 85,
        renderHeader,
        align: "center",
        headerAlign: "center",
        sortComparator: nullUndefinedComparator("last", gridDateComparator),
        valueFormatter: nullUndefinedFormatter(dateFormatter),
      },
      {
        field: "enrollmentDate",
        headerName: "Enrollment Date",
        width: 85,
        renderHeader,
        align: "center",
        headerAlign: "center",
        filterable: false,
        sortComparator: nullUndefinedComparator("last", gridDateComparator),
        valueFormatter: nullUndefinedFormatter(dateFormatter),
        renderCell: renderCellEnrollmentDate,
      },
    ];

    const data = patients
      .map((p) => {
        const initialSessionDate =
          p.sessionsSortedByDate?.length > 0
            ? p.sessionsSortedByDate[0].date
            : undefined;
        const recentSessionDate = p.latestSession?.date;
        const recentReviewDate = p.latestCaseReview?.date;
        const nextSessionDueDate =
          recentSessionDate && p.profile.followupSchedule && p.profile.followupSchedule != "As needed"
            ? addWeeks(
                recentSessionDate,
                getFollowUpWeeks(p.profile.followupSchedule),
              )
            : undefined;

        const totalSessionsCount =
          p.sessionsSortedByDate && p.sessionsSortedByDate.length > 0
            ? p.sessionsSortedByDate.length
            : undefined;
        const treatmentWeeksCount =
          initialSessionDate && recentSessionDate
            ? differenceInWeeks(recentSessionDate, initialSessionDate) + 1
            : undefined;

        const phq9Entries = p.assessmentLogs
          ?.filter((a) => a.assessmentId == "phq-9")
          .slice()
          .sort((a, b) => compareAsc(a.recordedDateTime, b.recordedDateTime));
        const gad7Entries = p.assessmentLogs
          ?.filter((a) => a.assessmentId == "gad-7")
          .slice()
          .sort((a, b) => compareAsc(a.recordedDateTime, b.recordedDateTime));

        const initialPHQScore =
          phq9Entries && phq9Entries.length > 0
            ? getAssessmentScoreFromAssessmentLog(phq9Entries[0])
            : undefined;
        const recentPHQScore =
          phq9Entries && phq9Entries.length > 0
            ? getAssessmentScoreFromAssessmentLog(
                phq9Entries[phq9Entries.length - 1],
              )
            : undefined;
        const recentPHQDate =
          phq9Entries && phq9Entries?.length > 0
            ? phq9Entries[phq9Entries.length - 1].recordedDateTime
            : undefined;
        const changePHQ =
          initialPHQScore && recentPHQScore
            ? Math.round(
                ((recentPHQScore - initialPHQScore) / initialPHQScore) * 100,
              )
            : undefined;

        const initialGADScore =
          gad7Entries && gad7Entries.length > 0
            ? getAssessmentScoreFromAssessmentLog(gad7Entries[0])
            : undefined;
        const recentGADScore =
          gad7Entries && gad7Entries.length > 0
            ? getAssessmentScoreFromAssessmentLog(
                gad7Entries[gad7Entries.length - 1],
              )
            : undefined;
        const recentGADDate =
          gad7Entries && gad7Entries.length > 0
            ? gad7Entries[gad7Entries.length - 1].recordedDateTime
            : undefined;
        const changeGAD =
          initialGADScore && recentGADScore
            ? Math.round(
                ((recentGADScore - initialGADScore) / initialGADScore) * 100,
              )
            : undefined;

        const todayDateUtc = toUTCDateOnly(new Date());
        const recentReviewOverdue = ((): boolean => {
          if (p.profile.depressionTreatmentStatus === "CoCM") {
            // CoCM is overdue if no review or after 1 month
            return (
              !recentReviewDate ||
              differenceInMonths(todayDateUtc, recentReviewDate) >= 1
            );
          } else if (p.profile.depressionTreatmentStatus === "CoCM RP") {
            // CoCM RP is overdue if no review or after 2 months
            return (
              !recentReviewDate ||
              differenceInMonths(todayDateUtc, recentReviewDate) >= 2
            );
          }

          // Nothing else can be overdue
          return false;
        })();
        const nextSessionOverdue =
          nextSessionDueDate &&
          differenceInDays(todayDateUtc, nextSessionDueDate) >= 1;
        const initialAtRisk =
          phq9Entries &&
          phq9Entries.length > 0 &&
          phq9Entries[0].pointValues &&
          !!phq9Entries[0].pointValues["Suicide"];
        const recentAtRisk =
          phq9Entries &&
          phq9Entries.length > 0 &&
          phq9Entries[phq9Entries.length - 1].pointValues &&
          !!phq9Entries[phq9Entries.length - 1].pointValues["Suicide"];
        const enrollmentDateHighlight =
          p.profile.enrollmentDate &&
          differenceInMonths(todayDateUtc, p.profile.enrollmentDate) >= 9;

        return {
          //
          // Row ID used by Grid
          //
          id: p.profile.MRN,
          //
          // Needed for row click
          //
          MRN: p.profile.MRN,
          //
          // Rendered columns
          //
          discussionFlags: p.profile.discussionFlag,
          depressionTreatmentStatus: p.profile.depressionTreatmentStatus,
          name: p.profile.name,
          clinicCode: p.profile.clinicCode,
          site: p.profile.site,
          initialSession: initialSessionDate,
          recentSession: recentSessionDate,
          recentCaseReview: recentReviewDate,
          nextSessionDue: nextSessionDueDate,
          totalSessions: totalSessionsCount,
          treatmentWeeks: treatmentWeeksCount,
          initialPHQ: initialPHQScore,
          recentPHQ: recentPHQScore,
          recentPHQDate: recentPHQDate,
          changePHQ: changePHQ,
          initialGAD: initialGADScore,
          recentGAD: recentGADScore,
          changeGAD: changeGAD,
          recentGADDate: recentGADDate,
          enrollmentDate: p.profile.enrollmentDate,
          //
          // Not rendered, used by other columns
          //
          recentCaseReviewOverdue: recentReviewOverdue,
          nextSessionOverdue: nextSessionOverdue,
          initialAtRisk: initialAtRisk,
          recentAtRisk: recentAtRisk,
          enrollmentDateHighlight: enrollmentDateHighlight,
        };
      })
      .sort(rowDefaultComparator);

    return (
      <TableContainer>
        <Table
          rows={data}
          columns={columns}
          headerHeight={36}
          rowHeight={36}
          onRowClick={onRowClick}
          autoHeight={true}
          isRowSelectable={() => false}
          pagination
          disableColumnMenu
          sortModel={sortModel}
          onSortModelChange={onSortModelChange}
          sortingOrder={["asc", "desc", null]}
        />
      </TableContainer>
    );
  },
);

export default CaseloadTable;
