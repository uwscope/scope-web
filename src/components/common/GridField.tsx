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
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled, { CSSObject, ThemedStyledProps } from 'styled-components';

const EditableTextField = withTheme(
    styled(TextField)(
        (props: ThemedStyledProps<TextFieldProps & { $editable: boolean; $top: boolean }, any>) =>
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
        (props: ThemedStyledProps<FormControlProps & { $editable: boolean; $top: boolean }, any>) =>
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
        (props: ThemedStyledProps<SelectProps & { $editable: boolean; $top: boolean }, any>) =>
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
    defaultValue: string;
    onChange?: (text: string) => void;
    fullWidth?: boolean;
}

export interface IGridTextFieldProps extends IGridFieldProps {
    multiline?: boolean;
    maxLine?: number;
}

export const GridTextField: FunctionComponent<IGridTextFieldProps> = observer((props) => {
    const { editable, label, defaultValue, multiline = false, maxLine = 1, fullWidth = false, onChange } = props;

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onChange) {
            onChange(event.target.value);
        }
    };

    return (
        <Grid item xs={12} sm={fullWidth ? 12 : 6}>
            <EditableTextField
                $editable={editable}
                multiline={multiline}
                rowsMax={maxLine}
                InputProps={{
                    readOnly: !editable,
                }}
                label={label}
                defaultValue={defaultValue}
                onChange={handleChange}
                fullWidth
            />
        </Grid>
    );
});

export interface IGridDropdownFieldProps extends IGridFieldProps {
    options: string[];
}

export const GridDropdownField: FunctionComponent<IGridDropdownFieldProps> = observer((props) => {
    const { editable, label, defaultValue, options, onChange, fullWidth = false } = props;

    const handleChange = (event: React.ChangeEvent<{ name?: string; value: unknown }>) => {
        if (!!onChange) {
            onChange(event.target.value as string);
        }
    };

    return (
        <Grid item xs={12} sm={fullWidth ? 12 : 6}>
            <SelectForm>
                <InputLabel>{label}</InputLabel>
                <SelectField
                    $editable={editable}
                    defaultValue={defaultValue}
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
});
