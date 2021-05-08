import { styled, Typography, withTheme } from '@material-ui/core';
import React, { FunctionComponent } from 'react';

const Label = withTheme(
    styled(Typography)((props) => ({
        ...props.theme.typography.body2,
        textTransform: 'uppercase',
        display: 'inline',
        fontWeight: 500,
        lineHeight: 1,
        color: props.theme.customPalette.label,
    }))
);

const Value = withTheme(
    styled(Typography)((props) => ({
        ...props.theme.typography.body2,
        display: 'inline',
        lineHeight: 1,
        color: props.theme.customPalette.label,
    }))
);

export interface ILabeledFieldProps {
    label: string;
    value: string | number | undefined;
}

export const LabeledField: FunctionComponent<ILabeledFieldProps> = (props) => {
    const { label, value } = props;
    return (
        <div>
            <Label>{label}</Label>
            {`: `}
            <Value>{value}</Value>
        </div>
    );
};

export default LabeledField;
