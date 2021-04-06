import DateFnsUtils from '@date-io/date-fns';
import {
    Checkbox,
    FormControl,
    FormControlLabel,
    FormControlProps,
    FormGroup,
    Grid,
    GridSize,
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
import { KeyedMap } from 'src/services/types';
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

interface IGridFieldBaseProps {
    editable?: boolean;
    label: string;
    xs?: GridSize;
    sm?: GridSize;
}

interface IGridFieldProps extends IGridFieldBaseProps {
    value: string | number | Date | undefined;
    onChange?: (text: string | number | Date) => void;
    placeholder?: string;
}

export interface IGridTextFieldProps extends IGridFieldProps {
    multiline?: boolean;
    maxLine?: number;
}

export const GridTextField: FunctionComponent<IGridTextFieldProps> = (props) => {
    const { editable, label, value, multiline = false, maxLine = 1, onChange, placeholder = 'No data', xs, sm } = props;

    const handleChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onChange) {
            onChange(event.target.value);
        }
    });

    return (
        <Grid item xs={xs || 12} sm={sm || 6} xl={4}>
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
    const { editable, label, value, options, onChange, xs, sm } = props;

    const handleChange = action((event: React.ChangeEvent<{ name?: string; value: unknown }>) => {
        if (!!onChange) {
            onChange(event.target.value as string);
        }
    });

    return (
        <Grid item xs={xs || 12} sm={sm || 6} xl={4}>
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

export interface IGridDateFieldProps extends IGridFieldProps {}

export const GridDateField: FunctionComponent<IGridDateFieldProps> = (props) => {
    const { editable, label, value, onChange, xs, sm } = props;

    const handleChange = action((date: Date | null) => {
        if (!!onChange && !!date) {
            onChange(date);
        }
    });

    if (editable) {
        return (
            <Grid item xs={xs || 12} sm={sm || 6} xl={4}>
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

export interface IGridMultiSelectFieldProps extends IGridFieldBaseProps {
    flags: KeyedMap<boolean> | undefined;
    onChange?: (flags: KeyedMap<boolean>) => void;
    other?: string | undefined;
    onOtherChange?: (other: string) => void;
}

export const GridMultiSelectField: FunctionComponent<IGridMultiSelectFieldProps> = (props) => {
    const { editable, label, flags, other, onChange, onOtherChange, xs, sm } = props;

    const handleChange = (flag: string) =>
        action((event: React.ChangeEvent<HTMLInputElement>) => {
            if (!!onChange && !!flags) {
                flags[flag] = event.target.checked;
                onChange(flags);
            }
        });

    const handleOtherChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onOtherChange) {
            onOtherChange(event.target.value);
        }
    });

    if (!!flags) {
        if (editable) {
            return (
                <Grid item xs={xs || 12} sm={sm || 6} xl={4}>
                    <FormGroup row>
                        {Object.keys(flags).map((key) => {
                            return (
                                <FormControlLabel
                                    key={key}
                                    control={<Checkbox checked={flags[key]} onChange={handleChange(key)} name={key} />}
                                    label={key}
                                />
                            );
                        })}
                        {flags['Other'] ?? (
                            <EditableTextField
                                $editable={editable}
                                multiline={false}
                                InputProps={{
                                    readOnly: !editable,
                                }}
                                label={label}
                                value={other}
                                onChange={handleOtherChange}
                                fullWidth
                            />
                        )}
                    </FormGroup>
                </Grid>
            );
        } else {
            var concatValues = Object.keys(flags)
                .filter((k) => flags[k] && k != 'Other')
                .join('; ');
            if (flags['Other']) {
                concatValues = [concatValues, other].join('; ');
            }

            return <GridTextField editable={false} label={label} value={concatValues} multiline={true} maxLine={2} />;
        }
    }

    return null;
};
