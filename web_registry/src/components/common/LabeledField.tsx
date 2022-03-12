import FlagIcon from '@mui/icons-material/Flag';
import { IconButton, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

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

const NoPaddingIconButton = styled(IconButton)({
    padding: 0,
});

const ColoredFlag = withTheme(
    styled(FlagIcon)<{ customprops: { on: boolean; color: string } }>((props) => ({
        color: props.theme.customPalette.flagColors[props.customprops.on ? props.customprops.color : 'disabled'],
    })),
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

export interface IFlaggedFieldProps {
    label: string;
    flagged: boolean;
    color: string;
    onClick: () => void;
}

export const FlaggedField: FunctionComponent<IFlaggedFieldProps> = (props) => {
    const { label, flagged, color, onClick } = props;
    return (
        <div>
            <Value>{label}</Value>
            {`: `}
            <NoPaddingIconButton
                aria-label="flag"
                size="small"
                onClick={onClick}
            >
                <ColoredFlag
                    customprops={{ on: flagged, color: color }}
                    fontSize="small"
                />
            </NoPaddingIconButton>
        </div>
    );
};

export default LabeledField;
