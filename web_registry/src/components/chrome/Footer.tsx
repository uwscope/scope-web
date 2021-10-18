import { Box, Typography } from '@material-ui/core';
import { withTheme } from '@material-ui/core/styles';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const Disclaimer = styled(Typography)({
    flexGrow: 1,
});

const FooterContainer = withTheme(
    styled(Box)((props) => ({
        minHeight: props.theme.customSizes.footerHeight,
        borderTop: `solid 1px ${props.theme.customPalette.subtle}`,
        alignItems: 'center',
        display: 'flex',
        padding: props.theme.spacing(1, 3),
        backgroundColor: 'white',
    }))
);

export const Footer: FunctionComponent = () => {
    return (
        <FooterContainer>
            <Disclaimer>Prototype by UW</Disclaimer>
        </FooterContainer>
    );
};

export default Footer;
