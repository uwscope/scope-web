import { TableRow } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { DataGrid, GridCellParams } from '@mui/x-data-grid';
import React from 'react';
import styled from 'styled-components';

export const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

export const Table = withTheme(
    styled(DataGrid)(() => ({
        '.MuiDataGrid-columnHeaders': {
            backgroundColor: 'rgba(0,0,0,0.05)',
        },
        '.MuiDataGrid-columnHeader': {
            paddingLeft: 4,
            paddingRight: 4,
        },
        '.MuiDataGrid-columnHeaderTitleContainer': {
            padding: 0,
        },
        '.MuiDataGrid-cell': {
            paddingLeft: 4,
            paddingRight: 4,
        },
        '.MuiDataGrid-cell:focus': {
            outline: 'none',
        },
        '.MuiDataGrid-row:hover': {
            cursor: 'pointer',
        },
        '.MuiDataGrid-footerContainer': {
            maxHeight: 24,
            minHeight: 24,
            backgroundColor: 'rgba(0,0,0,0.05)',
            overflow: 'hidden',
        },
    })),
);

export const MultilineCell = withTheme(
    styled.div((props) => ({
        whiteSpace: 'initial',
        lineHeight: '1rem',
        overflowY: 'auto',
        height: '100%',
        padding: props.theme.spacing(1, 0),
    })),
);

export const renderMultilineCell = (props: GridCellParams) => <MultilineCell>{props.value}</MultilineCell>;
