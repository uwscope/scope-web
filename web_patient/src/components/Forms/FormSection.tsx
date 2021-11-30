import { withTheme } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

export interface IFormSectionProps {
    prompt: string;
    subPrompt?: string;
    help?: string | React.ReactNode;
    addPaddingTop?: boolean;
    content: string | React.ReactElement;
}

const Container = withTheme(
    styled.div<{ $addPaddingTop: boolean }>((props) => ({
        paddingTop: props.$addPaddingTop ? props.theme.spacing(4) : 0,
    }))
);
const ContentContainer = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(0, 0),
    }))
);

const PromptText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.h6.fontSize,
        fontWeight: props.theme.typography.fontWeightBold,
        padding: props.theme.spacing(0, 0, 1, 0),
        lineHeight: 1,
    }))
);

const SubPromptText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.h6.fontSize,
        padding: props.theme.spacing(0, 0, 1, 0),
        lineHeight: 1,
        color: props.theme.palette.primary.dark,
    }))
);

export const HelperText = withTheme(
    styled.div((props) => ({
        fontSize: props.theme.typography.body1.fontSize,
        padding: props.theme.spacing(0, 0, 1, 0),
        color: props.theme.palette.text.secondary,
        lineHeight: 1,
        fontStyle: 'italic',
    }))
);

export const FormSection: FunctionComponent<IFormSectionProps> = (props) => {
    const { prompt, subPrompt, help, content, addPaddingTop } = props;

    return (
        <Container $addPaddingTop={addPaddingTop}>
            <PromptText>{prompt}</PromptText>
            {subPrompt && <SubPromptText>{subPrompt}</SubPromptText>}
            <ContentContainer>
                {help && <HelperText>{help}</HelperText>}
                {content}
            </ContentContainer>
        </Container>
    );
};

export default FormSection;
