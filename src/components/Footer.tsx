import { Container, Typography } from '@material-ui/core';
import { styled, withTheme } from '@material-ui/core/styles';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';

const Disclaimer = styled(Typography)({
    flexGrow: 1,
});

const FooterContainer = withTheme(
    styled(Container)((props) => ({
        height: 80,
        borderTop: 'solid 1px #eee',
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
