import { Stack } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

export interface IFormSectionProps {
    prompt: string;
    subPrompt?: string;
    help?: string | React.ReactNode;
    addPaddingTop?: boolean;
    content: string | React.ReactElement;
}

export const Container = withTheme(
    styled.div<{ $addPaddingTop: boolean }>((props) => ({
        paddingTop: props.$addPaddingTop ? props.theme.spacing(4) : 0,
    })),
);

export const ContentContainer = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(0, 0),
    })),
);

export const HeaderText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.h5.fontSize,
        fontWeight: props.theme.typography.fontWeightBold,
        lineHeight: 1.1,
    })),
);

export const SubHeaderText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.body1.fontSize,
        fontWeight: props.theme.typography.fontWeightBold,
        lineHeight: 1.1,
        color: props.theme.palette.primary.dark,
    })),
);

export const HelperText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.body2.fontSize,
        color: props.theme.palette.text.secondary,
        lineHeight: 1,
        fontStyle: 'italic',
    })),
);

export const FormSection: FunctionComponent<IFormSectionProps> = (props) => {
    const { prompt, subPrompt, help, content, addPaddingTop } = props;

    return (
        <Container $addPaddingTop={addPaddingTop}>
            <Stack spacing={1}>
                <HeaderText>{prompt}</HeaderText>
                {subPrompt && <SubHeaderText>{subPrompt}</SubHeaderText>}
                {help && <HelperText>{help}</HelperText>}
                {content}
            </Stack>
        </Container>
    );
};

export default FormSection;
