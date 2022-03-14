import { DatePicker } from '@mui/lab';
import {
    Checkbox,
    FormControl,
    FormControlLabel,
    FormControlProps,
    FormHelperText,
    Grid,
    GridSize,
    IconButton,
    Input,
    InputLabel,
    MenuItem,
    Radio,
    RadioGroup,
    Select,
    SelectProps,
    Switch,
    TextField,
    Typography,
} from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { format } from 'date-fns';
import { action } from 'mobx';
import React, { FunctionComponent, useState } from 'react';
import { KeyedMap } from 'shared/types';
import styled, { CSSObject, ThemedStyledProps } from 'styled-components';
import CloseIcon from '@mui/icons-material/Close';
import { clearTime } from 'shared/time';

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
        } as CSSObject),
    ),
);

const SelectField = withTheme(
    styled(Select)(
        (props: ThemedStyledProps<SelectProps & { $editable: boolean }, any>) =>
        ({
            '>.MuiSelect-icon': {
                display: props.$editable ? undefined : 'none',
            },
        } as CSSObject),
    ),
);

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
    required?: boolean;
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
    type?: string;
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
        type,
        helperText = '',
        required,
    } = props;

    const handleChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onChange) {
            onChange(event.target.value);
        }
    });

    return (
        <Grid item xs={xs || 12} sm={sm || 6}>
            <EditableFormControl fullWidth $editable={editable}>
                <InputLabel shrink>{`${label}${editable && required ? '*' : ''}`}</InputLabel>
                <Input
                    required={required}
                    type={type}
                    multiline={multiline}
                    minRows={minLine}
                    maxRows={maxLine}
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
    const { editable, label, value, options, onChange, xs, sm, required } = props;

    const handleChange = action((event: React.ChangeEvent<{ name?: string; value: unknown }>) => {
        if (!!onChange) {
            onChange(event.target.value as string);
        }
    });

    return (
        <Grid item xs={xs || 12} sm={sm || 6}>
            <EditableFormControl fullWidth $editable={editable}>
                <InputLabel shrink>{`${label}${editable && required ? '*' : ''}`}</InputLabel>
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

export interface IGridDateFieldProps extends IGridFieldProps { }

export const GridDateField: FunctionComponent<IGridDateFieldProps> = (props) => {
    const { editable, label, value, onChange, xs, sm, required } = props;

    const handleChange = action((date: Date | null) => {
        if (!!onChange) {
            onChange(!!date ? clearTime(date) : '');
        }
    });

    if (editable) {
        return (
            <Grid item xs={xs || 12} sm={sm || 6}>
                <DatePicker
                    label={`${label}${required ? '*' : ''}`}
                    value={value}
                    onChange={handleChange}
                    renderInput={(params) => (
                        <TextField
                            variant="outlined"
                            fullWidth
                            {...params}
                            InputLabelProps={{
                                shrink: true,
                                sx: { position: 'relative' },
                            }}
                        />
                    )}
                />
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
    const { editable, label, flags, flagOrder, other, onChange, onOtherChange, xs, sm, maxLine, disabled, required } =
        props;

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
                        <InputLabel shrink>{`${label}${required ? '*' : ''}`}</InputLabel>
                        <Grid container>
                            {(flagOrder || Object.keys(flags))
                                .filter((f) => f != 'Other')
                                .map((key) => {
                                    return (
                                        <Grid item xs={6} key={key}>
                                            <FormControlLabel
                                                sx={{ marginLeft: 0 }}
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
                                        sx={{ marginLeft: 0 }}
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
    otherFlags?: KeyedMap<string> | undefined;
    options: readonly string[];
    notOption: string;
    defaultOption: string;
    onChange?: (flags: KeyedMap<string>) => void;
    onOtherChange?: (flags: KeyedMap<string>) => void;
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
        otherFlags = {},
        notOption,
        defaultOption,
        onChange,
        onOtherChange,
        xs,
        sm,
        maxLine,
        disabled,
        required,
    } = props;

    const [other, setOther] = useState<string>('');

    const _handleFlagsChange = (flag: string, flags?: KeyedMap<string>, onChange?: (flags: KeyedMap<string>) => void) =>
        action((event: React.MouseEvent<HTMLButtonElement>) => {
            if (!!onChange && !!flags) {
                const newValue = (event.target as HTMLButtonElement).value;
                const prevValue = flags[flag];

                const newFlags: KeyedMap<string> = {};
                Object.assign(newFlags, flags);

                // If the flag was selected when it was previously on, toggle it off to notOption
                newFlags[flag] = newValue == prevValue ? notOption : newValue;
                onChange(newFlags);
            }
        });

    const handleFlagsChange = (flag: string) => _handleFlagsChange(flag, flags, onChange);

    const handleOtherFlagsChange = (flag: string) => _handleFlagsChange(flag, otherFlags, onOtherChange);

    const handleOtherChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setOther(event.target.value);
    };

    const handleOtherAdd = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            const trimOther = other.trim();
            if (!!onOtherChange && !!trimOther && !(trimOther in otherFlags)) {
                const newFlags: KeyedMap<string> = {};
                Object.assign(newFlags, otherFlags);
                newFlags[trimOther] = defaultOption;
                setOther('');
                onOtherChange(newFlags);
            }
        }
    };

    const handleOtherDelete = (key: string) => () => {
        if (key in otherFlags) {
            if (!!onOtherChange) {
                const newFlags: KeyedMap<string> = {};
                Object.assign(newFlags, otherFlags);
                delete newFlags[key];
                onOtherChange(newFlags);
            }
        }
    };

    const visibleOptions = options.filter((o) => o != notOption);

    if (!!flags) {
        if (editable) {
            return (
                <Grid item xs={xs || 12} sm={sm || 6}>
                    <EditableFormControl disabled={disabled} fullWidth $editable={true}>
                        <InputLabel shrink>{`${label}${required ? '*' : ''}`}</InputLabel>
                        {(flagOrder || Object.keys(flags)).map((key) => (
                            <Grid container key={key} alignItems="center">
                                <Grid item xs={4}>
                                    <RadioLabel>{key}</RadioLabel>
                                </Grid>

                                <Grid item xs={8}>
                                    <RadioGroup row aria-label="gender" name="gender1" value={flags[key]}>
                                        {visibleOptions.map((option) => (
                                            <FormControlLabel
                                                key={option}
                                                value={option}
                                                control={<Radio onClick={handleFlagsChange(key)} />}
                                                label={option}
                                            />
                                        ))}
                                    </RadioGroup>
                                </Grid>
                            </Grid>
                        ))}
                        {(otherFlags && Object.keys(otherFlags)).map((key) => (
                            <Grid container key={key} alignItems="center">
                                <Grid
                                    item
                                    xs={4}
                                    container
                                    direction="row"
                                    justifyContent="flex-start"
                                    flexWrap="nowrap">
                                    <RadioLabel
                                        sx={{
                                            textOverflow: 'ellipsis',
                                            overflow: 'hidden',
                                            whiteSpace: 'nowrap',
                                        }}>
                                        {key}
                                    </RadioLabel>
                                    <IconButton
                                        sx={{ padding: 0, paddingLeft: 2 }}
                                        size="small"
                                        aria-label="delete"
                                        onClick={handleOtherDelete(key)}>
                                        <CloseIcon fontSize="small" />
                                    </IconButton>
                                </Grid>

                                <Grid item xs={8}>
                                    <RadioGroup
                                        sx={{ justifyContent: 'space-evenly' }}
                                        row
                                        aria-label="gender"
                                        name="gender1"
                                        value={otherFlags[key]}>
                                        {visibleOptions.map((option) => (
                                            <FormControlLabel
                                                key={option}
                                                value={option}
                                                control={<Radio onClick={handleOtherFlagsChange(key)} />}
                                                label={option}
                                            />
                                        ))}
                                    </RadioGroup>
                                </Grid>
                            </Grid>
                        ))}
                        <FormControl fullWidth>
                            <Input
                                placeholder="Add other referral (type out the referral then press enter to add)"
                                margin="none"
                                multiline={false}
                                value={other}
                                onChange={handleOtherChange}
                                onKeyPress={handleOtherAdd}
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
    const { editable, label, on, onChange, xs, sm, required } = props;

    const handleChange = action((event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onChange) {
            const on = (event.target as HTMLInputElement).checked;
            onChange(on);
        }
    });

    return (
        <Grid item xs={xs || 12} sm={sm || 6}>
            <FormControlLabel
                sx={{ marginLeft: 0 }}
                control={<Switch checked={on} onChange={handleChange} name={label} disabled={!editable} />}
                label={`${label}${editable && required ? '*' : ''}`}
            />
        </Grid>
    );
};
