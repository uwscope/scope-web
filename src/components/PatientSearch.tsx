import { fade, InputBase, withTheme } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import { Autocomplete } from '@material-ui/lab';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const SearchContainer = withTheme(
    styled.div((props) => ({
        position: 'relative',
        borderRadius: props.theme.shape.borderRadius,
        backgroundColor: fade(props.theme.palette.common.white, 0.15),
        '&:hover': {
            backgroundColor: fade(props.theme.palette.common.white, 0.25),
        },
        marginRight: props.theme.spacing(2),
        marginLeft: 0,
        width: '100%',
        [props.theme.breakpoints.up('sm')]: {
            marginLeft: props.theme.spacing(3),
            width: 'auto',
        },
    }))
);

const SearchIconContainer = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(0, 2),
        height: '100%',
        position: 'absolute',
        pointerEvents: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    }))
);

const SearchInput = withTheme(
    styled(InputBase)((props) => ({
        padding: props.theme.spacing(1, 1, 1, 0),
        // vertical padding + font size from searchIcon
        paddingLeft: `calc(1em + ${props.theme.spacing(4)}px)`,
        transition: props.theme.transitions.create('width'),
        width: '100%',
        [props.theme.breakpoints.up('md')]: {
            width: '20ch',
        },
    }))
);

export interface IPatientSearchProps {
    options: string[];
    onSelect?: (option: string) => void;
}

export const PatientSearch: FunctionComponent<IPatientSearchProps> = observer((params) => {
    const onChange = (_: any, newValue: string | null) => {
        if (!!newValue && params.onSelect) {
            params.onSelect(newValue);
        }
    };

    return (
        <Autocomplete
            style={{ width: '300px' }}
            freeSolo
            disableClearable
            options={params.options}
            onChange={onChange}
            renderInput={(params) => {
                return (
                    <SearchContainer>
                        <SearchIconContainer>
                            <SearchIcon />
                        </SearchIconContainer>
                        <SearchInput
                            ref={params.InputProps.ref}
                            inputProps={params.inputProps}
                            placeholder="Search patient"
                        />
                    </SearchContainer>
                );
            }}
        />
    );
});

export default PatientSearch;
