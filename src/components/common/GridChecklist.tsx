import { Checkbox, FormControlLabel, Grid, InputLabel, withTheme } from '@material-ui/core';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const ChecklistLabel = styled(InputLabel)({
    textTransform: 'uppercase',
    transform: 'translate(0, 1.5px) scale(0.75)',
});

const ChecklistItemGrid = withTheme(
    styled(Grid)((props) => ({
        padding: props.theme.spacing(0, 1),
        '&.MuiGrid-item': {
            padding: props.theme.spacing(0, 1),
        },
    }))
);

export interface IGridChecklistProps {
    editable?: boolean;
    label: string;
    values: { [key: string]: boolean };
    onCheck?: (key: string, value: boolean) => void;
    fullWidth?: boolean;
}

export const GridChecklist: FunctionComponent<IGridChecklistProps> = observer((props) => {
    const { onCheck, editable, label, values, fullWidth } = props;

    const handleChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onCheck) {
            onCheck(event.target.name, event.target.checked);
        }
    });

    return (
        <Grid item container spacing={2} alignItems="stretch" xs={12} sm={fullWidth ? 12 : 6} xl={4}>
            <Grid item xs={12}>
                <ChecklistLabel>{label}</ChecklistLabel>
            </Grid>
            {Object.keys(values).map((item) => {
                return (
                    <ChecklistItemGrid item xs={12} sm={6} xl={4} key={item}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={values[item]}
                                    onChange={handleChange}
                                    name={item}
                                    color="primary"
                                    inputProps={{
                                        readOnly: !editable,
                                    }}
                                />
                            }
                            label={item}
                        />
                    </ChecklistItemGrid>
                );
            })}
        </Grid>
    );
});

export default GridChecklist;
