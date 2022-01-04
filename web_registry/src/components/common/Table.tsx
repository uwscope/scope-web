import { TableRow } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { DataGrid } from '@mui/x-data-grid';
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
        },
    }))
);
