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
    Switch,
    Typography,
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
                '>.MuiFormLabel-root.Mui-focused': {},
                '>.MuiInput-underline:hover:not(.Mui-disabled):before': {
                    border: props.$editable ? undefined : 'none',
                },
                '>.MuiInput-underline:after': {
                    border: props.$editable ? undefined : 'none',
                },
                '>.MuiFormHelperText-root': {
                    lineHeight: 1,
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
    'label + .MuiInput-formControl': {
        marginTop: 20,
    },
});

const OtherGrid = styled(Grid)({
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
});

const RadioLabel = styled(Typography)({
    paddingLeft: 12,
    alignSelf: 'center',
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
    helperText?: string;
}

export interface IGridTextFieldProps extends IGridFieldProps {
    multiline?: boolean;
    maxLine?: number;
    minLine?: number;
}

export const GridTextField: FunctionComponent<IGridTextFieldProps> = (props) => {
    const {
        editable,
        label,
        value,
        multiline = false,
        minLine,
        maxLine,
        onChange,
        placeholder = 'No data',
        xs,
        sm,
        helperText = '',
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
                <Input
                    multiline={multiline}
                    rows={minLine}
                    rowsMax={maxLine}
                    readOnly={!editable}
                    value={value}
                    onChange={handleChange}
                    fullWidth
                    placeholder={placeholder}
                />
                {!!helperText ? <FormHelperText>{helperText}</FormHelperText> : null}
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
                xs={xs}
                sm={sm}
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
    flagOrder?: string[];
}

export const GridMultiSelectField: FunctionComponent<IGridMultiSelectFieldProps> = (props) => {
    const { editable, label, flags, flagOrder, other, onChange, onOtherChange, xs, sm, maxLine, disabled } = props;

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
                            {(flagOrder || Object.keys(flags))
                                .filter((f) => f != 'Other')
                                .map((key) => {
                                    return (
                                        <Grid item xs={6} key={key}>
                                            <FormControlLabel
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
                                    <FormControlLabel
                                        control={
                                            <Checkbox
                                                checked={flags['Other']}
                                                onChange={handleChange('Other')}
                                                name="Other"
                                            />
                                        }
                                        label="Other"
                                    />
                                    <Input
                                        multiline={false}
                                        value={other}
                                        onChange={handleOtherChange}
                                        fullWidth
                                        disabled={!flags['Other']}
                                        margin="none"
                                        style={{ margin: 0 }}
                                    />
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
    flagOrder?: string[];
}

export const GridMultiOptionsField: FunctionComponent<IGridMultiOptionsFieldProps> = (props) => {
    const {
        editable,
        label,
        flags,
        flagOrder,
        options,
        other,
        notOption,
        onChange,
        onOtherChange,
        xs,
        sm,
        maxLine,
        disabled,
    } = props;

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
                        {(flagOrder || Object.keys(flags)).map((key) => (
                            <Grid container key={key} alignItems="center">
                                <Grid item xs={4}>
                                    <RadioLabel>{key}</RadioLabel>
                                </Grid>

                                <Grid item xs={8}>
                                    <RadioGroup
                                        row
                                        aria-label="gender"
                                        name="gender1"
                                        value={flags[key]}
                                        onChange={handleChange(key)}>
                                        {options.map((option) => (
                                            <FormControlLabel
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
                            <Input
                                margin="none"
                                multiline={false}
                                value={other}
                                onChange={handleOtherChange}
                                fullWidth
                            />
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

export interface IGridSwitchFieldProps extends IGridFieldBaseProps {
    on: boolean;
    onChange?: (on: boolean) => void;
}

export const GridSwitchField: FunctionComponent<IGridSwitchFieldProps> = (props) => {
    const { editable, label, on, onChange, xs, sm } = props;

    const handleChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onChange) {
            const on = (event.target as HTMLInputElement).checked;
            onChange(on);
        }
    });

    return (
        <Grid item xs={xs || 12} sm={sm || 6}>
            <FormControlLabel
                control={<Switch checked={on} onChange={handleChange} name={label} disabled={!editable} />}
                label={label}
            />
        </Grid>
    );
};
