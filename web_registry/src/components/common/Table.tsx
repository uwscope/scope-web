import React from "react";

import { TableRow } from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import {
  DataGrid,
  GridCellParams,
  GridCellValue,
  GridValueFormatterParams,
} from "@mui/x-data-grid";
import { formatDateOnly } from "shared/time";
import styled from "styled-components";

export const NA = "--";

export const TableRowHeight_2RowsNoScroll = 42;
export const TableRowHeight_3RowsNoScroll = 63;
export const TableRowHeight_5RowsNoScroll = 105;

export const ClickableTableRow = styled(TableRow)({
  "&:hover": {
    cursor: "pointer",
  },
});

export const Table = withTheme(
  styled(DataGrid)(() => ({
    ".MuiDataGrid-columnHeaders": {
      backgroundColor: "rgba(0,0,0,0.05)",
    },
    ".MuiDataGrid-columnHeader": {
      paddingLeft: 4,
      paddingRight: 4,
    },
    ".MuiDataGrid-columnHeaderTitleContainer": {
      padding: 0,
    },
    ".MuiDataGrid-cell": {
      paddingLeft: 4,
      paddingRight: 4,
    },
    ".MuiDataGrid-cell:focus": {
      outline: "none",
    },
    ".MuiDataGrid-row:hover": {
      cursor: "pointer",
    },
    ".MuiDataGrid-footerContainer": {
      maxHeight: 24,
      minHeight: 24,
      backgroundColor: "rgba(0,0,0,0.05)",
      overflow: "hidden",
    },
    // Based on MUI colors:
    // https://mui.com/material-ui/customization/color/
    //
    // Primary color, and the color of our "New" badges, is currently "indigo 500", which is #3f51b5
    //
    // To indicate a new row, use "indigo 100", which is #c5cae9
    ".recentEntryRow": {
      backgroundColor: "rgba(197, 202, 233, 1)",
    },
    // To indicate a new row with a hover, use "indigo 200", which is #9fa8da
    ".recentEntryRow:hover": {
      backgroundColor: "rgba(159, 168, 218, 1)",
    },
  })),
);

export const MultilineCell = withTheme(
  styled.div((props) => ({
    whiteSpace: "initial",
    lineHeight: "1rem",
    overflowY: "auto",
    maxHeight: "100%",
    padding: props.theme.spacing(1, 0),
  })),
);

export const renderMultilineCell = (props: GridCellParams) => (
  <MultilineCell>{props.value}</MultilineCell>
);

export const dateFormatter: (params: GridValueFormatterParams) => string = (
  params,
) => {
  return formatDateOnly(params.value as Date, "MM/dd/yy");
};

export const nullUndefinedFormatter: (
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
