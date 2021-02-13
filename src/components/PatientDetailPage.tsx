import { Typography, withTheme } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { ContentsMenu, IContentItem } from 'src/components/common/ContentsMenu';
import styled from 'styled-components';
import PatientInformation from './PatientDetail/PatientInformation';

const DetailPageContainer = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'stretch',
        height: '100%',
        overflow: 'hidden',
    })
);

const ContentContainer = withTheme(
    styled.div((props) => ({
        flex: 1,
        padding: props.theme.spacing(3),
        overflowX: 'hidden',
        overflowY: 'auto',
    }))
);

const Section = withTheme(
    styled.div((props) => ({
        marginBottom: props.theme.spacing(5),
        minHeight: 600,
    }))
);

const SectionTitle = styled(Typography)({
    minHeight: 48,
    textTransform: 'uppercase',
});

type IContent = IContentItem & { content?: React.ReactNode };

export const PatientDetailPage: FunctionComponent = observer(() => {
    const contents = [
        {
            hash: 'patient',
            label: 'Patient',
            top: true,
            content: <PatientInformation />,
        },
        {
            hash: 'medical',
            label: 'Medical information',
        },
        {
            hash: 'psychiatry',
            label: 'Psychiatry information',
        },
        {
            hash: 'treatment',
            label: 'Treatment information',
        },
        {
            hash: 'sessions',
            label: 'Sessions',
        },
        {
            hash: 'assessments',
            label: 'Assessments',
        },
        {
            hash: 'progress',
            label: 'Progress',
            top: true,
        },
        {
            hash: 'phq9',
            label: 'PHQ-9',
        },
        {
            hash: 'gad7',
            label: 'GAD-7',
        },
        {
            hash: 'mood',
            label: 'Mood Trends',
        },
        {
            hash: 'behavioral',
            label: 'Behavioral Activation',
            top: true,
        },
        {
            hash: 'checklist',
            label: 'Checklist',
        },
        {
            hash: 'activities',
            label: 'Activities',
        },
    ] as IContent[];

    return (
        <DetailPageContainer>
            <ContentsMenu contents={contents} contentId="#scroll-content" />
            <ContentContainer id="scroll-content">
                {contents
                    .filter((c) => c.top)
                    .map((c) => (
                        <Section id={c.hash} key={c.hash}>
                            <SectionTitle variant="h6">{c.label}</SectionTitle>
                            {c.content ? c.content : null}
                        </Section>
                    ))}
            </ContentContainer>
        </DetailPageContainer>
    );
});

export default PatientDetailPage;
