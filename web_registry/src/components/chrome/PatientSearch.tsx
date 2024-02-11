import React, { FunctionComponent } from "react";

import SearchIcon from "@mui/icons-material/Search";
import { alpha, Autocomplete, InputBase } from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import styled from "styled-components";

const SearchContainer = withTheme(
  styled.div((props) => ({
    position: "relative",
    borderRadius: props.theme.shape.borderRadius,
    backgroundColor: alpha(props.theme.palette.common.white, 0.15),
    "&:hover": {
      backgroundColor: alpha(props.theme.palette.common.white, 0.25),
    },
    marginRight: props.theme.spacing(2),
    marginLeft: 0,
    width: "100%",
    [props.theme.breakpoints.up("sm")]: {
      marginLeft: props.theme.spacing(3),
      width: "auto",
    },
  })),
);

const SearchIconContainer = withTheme(
  styled.div((props) => ({
    padding: props.theme.spacing(0, 2),
    height: "100%",
    position: "absolute",
    pointerEvents: "none",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  })),
);

const SearchInput = withTheme(
  styled(InputBase)((props) => ({
    padding: props.theme.spacing(1, 1, 1, 0),
    // vertical padding + font size from searchIcon
    paddingLeft: `calc(1em + ${props.theme.spacing(4)}px)`,
    transition: props.theme.transitions.create("width"),
    width: "100%",
    [props.theme.breakpoints.up("md")]: {
      width: "20ch",
    },
  })),
);

export interface IPatientSearchProps {
  options: string[];
  onSelect?: (option: string) => void;
}

export const PatientSearch: FunctionComponent<IPatientSearchProps> = (
  params,
) => {
  const onChange = (_: any, newValue: string | null) => {
    if (!!newValue && params.onSelect) {
      params.onSelect(newValue);
    }
  };

  return (
    <Autocomplete
      style={{ width: "300px" }}
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
};

export default PatientSearch;
