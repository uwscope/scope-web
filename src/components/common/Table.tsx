import { TableRow } from '@material-ui/core';
import styled from 'styled-components';

export const ClickableRow = styled(TableRow)({
    '&:hover': {
        cursor: 'pointer',
    },
});
