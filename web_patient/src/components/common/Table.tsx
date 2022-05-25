import { TableCell, TableRow } from '@mui/material';

import styled from 'styled-components';

export const ClickableTableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});

export const WordBreakTableCell = styled(TableCell)({
    wordBreak: 'break-word',
});
