import { Box, Typography } from '@material-ui/core';
import { withTheme } from '@material-ui/core/styles';
import { observer } from 'mobx-react';
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
        marginLeft: props.theme.spacing(7) + 1,
        padding: props.theme.spacing(1, 3),
        backgroundColor: 'white',
        [props.theme.breakpoints.up('sm')]: {
            marginLeft: props.theme.spacing(9) + 1,
        },
    }))
);

export const Footer: FunctionComponent = observer(() => {
    return (
        <FooterContainer>
            <Disclaimer>Prototype by UW</Disclaimer>
        </FooterContainer>
    );
});

export default Footer;
