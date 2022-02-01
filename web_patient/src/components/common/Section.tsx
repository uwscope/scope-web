import { Paper, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const SectionContainer = withTheme(
    styled(Paper)((props) => ({
        borderRadius: props.theme.spacing(1),
        padding: props.theme.spacing(2),
        marginBottom: props.theme.spacing(3),
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: props.theme.customPalette.panel,
    }))
);

const SectionTitle = styled(Typography)({
    fontWeight: 600,
});

const SectionContent = styled.div({
    flexGrow: 1,
});

export interface ISectionProps {
    title?: string;
}

export const Section: FunctionComponent<ISectionProps> = (props) => {
    const { title } = props;

    return (
        <SectionContainer>
            {!!title ? <SectionTitle variant="overline">{title}</SectionTitle> : null}
            <SectionContent>{props.children}</SectionContent>
        </SectionContainer>
    );
};

export default Section;
