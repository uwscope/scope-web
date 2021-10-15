import { TableRow } from '@material-ui/core';
import { XGrid } from '@material-ui/x-grid';
import styled from 'styled-components';

export const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

export const Table = styled(XGrid)({
    '.MuiDataGrid-cell:focus': {
        outline: 'none',
    },
    '.MuiDataGrid-row:hover': {
        cursor: 'pointer',
    },
});
