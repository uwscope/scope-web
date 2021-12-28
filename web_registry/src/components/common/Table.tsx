import { TableRow } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import styled from 'styled-components';

export const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

export const Table = styled(DataGrid)({
    '.MuiDataGrid-cell:focus': {
        outline: 'none',
    },
    '.MuiDataGrid-row:hover': {
        cursor: 'pointer',
    },
});
