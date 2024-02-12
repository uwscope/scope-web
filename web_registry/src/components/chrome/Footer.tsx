import React, { FunctionComponent } from "react";

import { Box, Typography } from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import styled from "styled-components";

const Disclaimer = styled(Typography)({
  flexGrow: 1,
});

const FooterContainer = withTheme(
  styled(Box)((props) => ({
    minHeight: props.theme.customSizes.footerHeight,
    borderTop: `solid 1px ${props.theme.customPalette.subtle}`,
    alignItems: "center",
    display: "flex",
    padding: props.theme.spacing(1, 3),
    backgroundColor: "white",
  })),
);

export const Footer: FunctionComponent = () => {
  return (
    <footer style={{ position: "fixed", bottom: 0, width: "100%" }}>
      <FooterContainer>
        <Disclaimer>Prototype by UW</Disclaimer>
      </FooterContainer>
    </footer>
  );
};

export default Footer;
