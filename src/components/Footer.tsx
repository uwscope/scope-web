import { Container, Typography } from '@material-ui/core';
import { withTheme } from '@material-ui/core/styles';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const Disclaimer = styled(Typography)({
    flexGrow: 1,
});

const FooterContainer = withTheme(
    styled(Container)((props) => ({
        minHeight: props.theme.customSizes.footerHeight,
        borderTop: `solid 1px ${props.theme.customPalette.subtle}`,
        alignItems: 'center',
        display: 'flex',
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
