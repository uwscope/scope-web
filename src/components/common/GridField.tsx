import DateFnsUtils from '@date-io/date-fns';
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
import { KeyboardDatePicker, MuiPickersUtilsProvider } from '@material-ui/pickers';
import { format } from 'date-fns';
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

const DatePickerContainer = styled(KeyboardDatePicker)({
    width: '100%',
    margin: 0,
    '>.MuiFormLabel-root': {
        textTransform: 'uppercase',
    },
});

interface IGridFieldProps {
    editable?: boolean;
    label: string;
    value: string | number | Date | undefined;
    onChange?: (text: string | number | Date) => void;
    fullWidth?: boolean;
    placeholder?: string;
}

export interface IGridTextFieldProps extends IGridFieldProps {
    multiline?: boolean;
    maxLine?: number;
}

export const GridTextField: FunctionComponent<IGridTextFieldProps> = (props) => {
    const { editable, label, value, multiline = false, maxLine = 1, fullWidth = false, onChange, placeholder } = props;

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
                placeholder={placeholder}
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

export interface IGridDateField extends IGridFieldProps {}

export const GridDateField: FunctionComponent<IGridDateField> = (props) => {
    const { editable, label, value, onChange, fullWidth = false } = props;

    const handleChange = action((date: Date | null) => {
        if (!!onChange && !!date) {
            onChange(date);
        }
    });

    if (editable) {
        return (
            <Grid item xs={12} sm={fullWidth ? 12 : 6} xl={4}>
                <MuiPickersUtilsProvider utils={DateFnsUtils}>
                    <DatePickerContainer
                        disableToolbar
                        variant="inline"
                        format="MM/dd/yyyy"
                        margin="normal"
                        label={label}
                        value={value}
                        onChange={handleChange}
                    />
                </MuiPickersUtilsProvider>
            </Grid>
        );
    } else {
        return (
            <GridTextField
                editable={false}
                label={label}
                value={!!value ? format(value as Date, 'MM/dd/yyyy') : 'unknown'}
                onChange={onChange}
            />
        );
    }
};
