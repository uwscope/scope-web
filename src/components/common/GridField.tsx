import {
    FormControl,
    FormControlProps,
    Grid,
    InputLabel,
    MenuItem,
    Select,
    SelectProps,
    TextField,
    TextFieldProps,
    withTheme,
} from '@material-ui/core';
import { action } from 'mobx';
import React, { FunctionComponent } from 'react';
import styled, { CSSObject, ThemedStyledProps } from 'styled-components';

const EditableTextField = withTheme(
    styled(TextField)(
        (props: ThemedStyledProps<TextFieldProps & { $editable: boolean }, any>) =>
            ({
                minWidth: 160,
                '>.MuiInput-underline:before': {
                    border: props.$editable ? undefined : 'none',
                },
                '>.MuiFormLabel-root': {
                    textTransform: 'uppercase',
                },
            } as CSSObject)
    )
);
const SelectForm = withTheme(
    styled(FormControl)(
        (props: ThemedStyledProps<FormControlProps & { $editable: boolean }, any>) =>
            ({
                width: '100%',
                minWidth: 160,
                '>.MuiInput-underline:before': {
                    border: props.$editable ? undefined : 'none',
                },
                '>.MuiFormLabel-root': {
                    textTransform: 'uppercase',
                },
            } as CSSObject)
    )
);

const SelectField = withTheme(
    styled(Select)(
        (props: ThemedStyledProps<SelectProps & { $editable: boolean }, any>) =>
            ({
                '>.MuiSelect-icon': {
                    display: props.$editable ? undefined : 'none',
                },
            } as CSSObject)
    )
);

interface IGridFieldProps {
    editable?: boolean;
    label: string;
    value: string | number | undefined;
    onChange?: (text: string) => void;
    fullWidth?: boolean;
}

export interface IGridTextFieldProps extends IGridFieldProps {
    multiline?: boolean;
    maxLine?: number;
}

export const GridTextField: FunctionComponent<IGridTextFieldProps> = (props) => {
    const { editable, label, value, multiline = false, maxLine = 1, fullWidth = false, onChange } = props;

    const handleChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onChange) {
            onChange(event.target.value);
        }
    });

    return (
        <Grid item xs={12} sm={fullWidth ? 12 : 6} xl={4}>
            <EditableTextField
                $editable={editable}
                multiline={multiline}
                rowsMax={maxLine}
                InputProps={{
                    readOnly: !editable,
                }}
                label={label}
                value={value}
                onChange={handleChange}
                fullWidth
            />
        </Grid>
    );
};

export interface IGridDropdownFieldProps extends IGridFieldProps {
    options: ReadonlyArray<string>;
}

export const GridDropdownField: FunctionComponent<IGridDropdownFieldProps> = (props) => {
    const { editable, label, value, options, onChange, fullWidth = false } = props;

    const handleChange = action((event: React.ChangeEvent<{ name?: string; value: unknown }>) => {
        if (!!onChange) {
            onChange(event.target.value as string);
        }
    });

    return (
        <Grid item xs={12} sm={fullWidth ? 12 : 6} xl={4}>
            <SelectForm $editable={editable}>
                <InputLabel>{label}</InputLabel>
                <SelectField
                    $editable={editable}
                    value={value}
                    label={label}
                    onChange={handleChange}
                    inputProps={{ readOnly: !editable }}>
                    {!!options
                        ? options.map((o) => (
                              <MenuItem key={o} value={o}>
                                  {o}
                              </MenuItem>
                          ))
                        : null}
                </SelectField>
            </SelectForm>
        </Grid>
    );
};
