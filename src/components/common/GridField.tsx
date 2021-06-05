import DateFnsUtils from '@date-io/date-fns';
import {
    Checkbox,
    FormControl,
    FormControlLabel,
    FormControlProps,
    FormHelperText,
    Grid,
    GridSize,
    Input,
    InputLabel,
    MenuItem,
    Radio,
    RadioGroup,
    Select,
    SelectProps,
    withTheme,
} from '@material-ui/core';
import { KeyboardDatePicker, MuiPickersUtilsProvider } from '@material-ui/pickers';
import { format } from 'date-fns';
import { action } from 'mobx';
import React, { FunctionComponent } from 'react';
import { KeyedMap } from 'src/services/types';
import styled, { CSSObject, ThemedStyledProps } from 'styled-components';

const EditableFormControl = withTheme(
    styled(FormControl)(
        (props: ThemedStyledProps<FormControlProps & { $editable: boolean }, any>) =>
            ({
                minWidth: 160,
                '>.MuiInput-underline:before': {
                    border: props.$editable ? undefined : 'none',
                },
                '>.MuiFormLabel-root': {
                    position: 'relative',
                },
                '>.MuiFormLabel-root.Mui-focused': {
                    color: props.$editable ? undefined : 'rgba(0, 0, 0, 0.54)',
                },
                '>.MuiInput-underline:hover:not(.Mui-disabled):before': {
                    border: props.$editable ? undefined : 'none',
                },
                '>.MuiInput-underline:after': {
                    border: props.$editable ? undefined : 'none',
                },
                '>.MuiFormHelperText-root': {
                    lineHeight: 1,
                    margin: 0,
                },
                '>.MuiInput-root': {
                    margin: 0,
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
});

const OtherGrid = styled(Grid)({
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
});

const MultiSelectCheckbox = withTheme(
    styled(FormControlLabel)((props) => ({
        '>.MuiCheckbox-root': {
            padding: props.theme.spacing(0.5, 1),
        },
    }))
);

const MultiSelectRadio = withTheme(
    styled(FormControlLabel)((props) => ({
        '>.MuiRadio-root': {
            padding: props.theme.spacing(0.5, 1),
        },
    }))
);

interface IGridFieldBaseProps {
    editable?: boolean;
    label: string;
    helperText?: string;
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
    const {
        editable,
        label,
        value,
        multiline = false,
        maxLine,
        onChange,
        placeholder = 'No data',
        helperText,
        xs,
        sm,
    } = props;

    const handleChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onChange) {
            onChange(event.target.value);
        }
    });

    return (
        <Grid item xs={xs || 12} sm={sm || 6}>
            <EditableFormControl fullWidth $editable={editable}>
                <InputLabel shrink>{label}</InputLabel>
                {!!helperText ? <FormHelperText>{`(${helperText})`}</FormHelperText> : null}
                <Input
                    multiline={multiline}
                    rowsMax={maxLine}
                    readOnly={!editable}
                    value={value}
                    onChange={handleChange}
                    fullWidth
                    placeholder={placeholder}
                />
            </EditableFormControl>
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
        <Grid item xs={xs || 12} sm={sm || 6}>
            <EditableFormControl fullWidth $editable={editable}>
                <InputLabel shrink>{label}</InputLabel>
                {editable ? (
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
                ) : (
                    <Input readOnly value={value} fullWidth />
                )}
            </EditableFormControl>
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
            <Grid item xs={xs || 12} sm={sm || 6}>
                <MuiPickersUtilsProvider utils={DateFnsUtils}>
                    <DatePickerContainer
                        disableToolbar
                        variant="inline"
                        format="MM/dd/yyyy"
                        margin="normal"
                        label={label}
                        value={value}
                        onChange={handleChange}
                        InputLabelProps={{
                            shrink: true,
                        }}
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
    maxLine?: number;
    disabled?: boolean;
}

export const GridMultiSelectField: FunctionComponent<IGridMultiSelectFieldProps> = (props) => {
    const { editable, label, flags, other, onChange, onOtherChange, xs, sm, maxLine, disabled } = props;

    const handleChange = (flag: string) =>
        action((event: React.ChangeEvent<HTMLInputElement>) => {
            if (!!onChange && !!flags) {
                const newFlags: KeyedMap<boolean> = {};
                Object.assign(newFlags, flags);
                newFlags[flag] = event.target.checked;
                onChange(newFlags);
            }
        });

    const handleOtherChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onOtherChange) {
            onOtherChange(event.target.value);
        }
    });

    if (!!flags) {
        const showOther = Object.keys(flags).filter((f) => f == 'Other').length > 0;

        if (editable) {
            return (
                <Grid item xs={xs || 12} sm={sm || 6}>
                    <EditableFormControl disabled={disabled} fullWidth $editable={true}>
                        <InputLabel shrink>{label}</InputLabel>
                        <Grid container>
                            {Object.keys(flags)
                                .filter((f) => f != 'Other')
                                .map((key) => {
                                    return (
                                        <Grid item xs={6} key={key}>
                                            <MultiSelectCheckbox
                                                control={
                                                    <Checkbox
                                                        checked={flags[key]}
                                                        onChange={handleChange(key)}
                                                        name={key}
                                                    />
                                                }
                                                label={key}
                                            />
                                        </Grid>
                                    );
                                })}
                            {showOther ? (
                                <OtherGrid item xs={12} key={'Other'}>
                                    <MultiSelectCheckbox
                                        control={
                                            <Checkbox
                                                checked={flags['Other']}
                                                onChange={handleChange('Other')}
                                                name="Other"
                                            />
                                        }
                                        label="Other"
                                    />
                                    <FormControl fullWidth disabled={!flags['Other']}>
                                        <Input multiline={false} value={other} onChange={handleOtherChange} fullWidth />
                                    </FormControl>
                                </OtherGrid>
                            ) : null}
                        </Grid>
                    </EditableFormControl>
                </Grid>
            );
        } else {
            var concatValues = Object.keys(flags)
                .filter((k) => flags[k] && k != 'Other')
                .join('\n');
            if (flags['Other']) {
                concatValues = [concatValues, other].join('\n');
            }

            return (
                <GridTextField
                    xs={xs || 12}
                    sm={sm || 6}
                    editable={false}
                    label={label}
                    value={concatValues || 'None'}
                    multiline={true}
                    maxLine={maxLine}
                />
            );
        }
    }

    return null;
};

export interface IGridMultiOptionsFieldProps extends IGridFieldBaseProps {
    flags: KeyedMap<string> | undefined;
    options: readonly string[];
    notOption: string;
    onChange?: (flags: KeyedMap<string>) => void;
    other?: string | undefined;
    onOtherChange?: (other: string) => void;
    maxLine?: number;
    disabled?: boolean;
}

export const GridMultiOptionsField: FunctionComponent<IGridMultiOptionsFieldProps> = (props) => {
    const { editable, label, flags, options, notOption, other, onChange, onOtherChange, xs, sm, maxLine, disabled } =
        props;

    const handleCheck = (flag: string) =>
        action((event: React.ChangeEvent<HTMLInputElement>) => {
            if (!!onChange && !!flags) {
                const newFlags: KeyedMap<string> = {};
                Object.assign(newFlags, flags);
                newFlags[flag] = (event.target as HTMLInputElement).checked ? options[0] : notOption;
                onChange(newFlags);
            }
        });

    const handleChange = (flag: string) =>
        action((event: React.ChangeEvent<HTMLInputElement>) => {
            if (!!onChange && !!flags) {
                const newFlags: KeyedMap<string> = {};
                Object.assign(newFlags, flags);
                newFlags[flag] = (event.target as HTMLInputElement).value;
                onChange(newFlags);
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
                <Grid item xs={xs || 12} sm={sm || 6}>
                    <EditableFormControl disabled={disabled} fullWidth $editable={true}>
                        <InputLabel shrink>{label}</InputLabel>
                        {Object.keys(flags).map((key) => (
                            <Grid container key={key}>
                                <Grid item xs={6}>
                                    <MultiSelectCheckbox
                                        control={
                                            <Checkbox
                                                checked={flags[key] != notOption}
                                                onChange={handleCheck(key)}
                                                name={key}
                                            />
                                        }
                                        label={key}
                                    />
                                </Grid>

                                <Grid item xs={6}>
                                    <RadioGroup
                                        row
                                        aria-label="gender"
                                        name="gender1"
                                        value={flags[key]}
                                        onChange={handleChange(key)}>
                                        {options.map((option) => (
                                            <MultiSelectRadio
                                                key={option}
                                                value={option}
                                                control={<Radio />}
                                                label={option}
                                            />
                                        ))}
                                    </RadioGroup>
                                </Grid>
                            </Grid>
                        ))}
                        <FormControl fullWidth disabled={flags['Other'] == notOption}>
                            <Input multiline={false} value={other} onChange={handleOtherChange} fullWidth />
                        </FormControl>
                    </EditableFormControl>
                </Grid>
            );
        } else {
            var concatValues = Object.keys(flags)
                .filter((k) => flags[k] && k != notOption)
                .map((k) => `${k}-${flags[k]}`)
                .join('\n');
            if (flags['Other'] != notOption) {
                concatValues = [concatValues, `${other}-${flags['Other']}`].join('\n');
            }

            return (
                <GridTextField
                    xs={xs || 12}
                    sm={sm || 6}
                    editable={false}
                    label={label}
                    value={concatValues || 'None'}
                    multiline={true}
                    maxLine={maxLine}
                />
            );
        }
    }

    return null;
};
