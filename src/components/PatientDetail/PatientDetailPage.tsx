import { Divider, Paper, Typography, withTheme } from '@material-ui/core';
import { action } from 'mobx';
import React, { FunctionComponent } from 'react';
import { ContentsMenu, IContentItem } from 'src/components/common/ContentsMenu';
import BAInformation from 'src/components/PatientDetail/BAInformation';
import PatientInformation from 'src/components/PatientDetail/PatientInformation';
import ProgressInformation from 'src/components/PatientDetail/ProgressInformation';
import { useStores } from 'src/stores/stores';
import styled from 'styled-components';

const DetailPageContainer = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'stretch',
        height: '100%',
        overflow: 'hidden',
    })
);

const LeftPaneContainer = withTheme(
    styled(Paper)({
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'stretch',
        height: '100%',
        overflow: 'hidden',
    })
);

const PatientCard = withTheme(
    styled.div((props) => ({
        padding: props.theme.spacing(2.5),
    }))
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

export const PatientDetailPage: FunctionComponent = () => {
    const rootStore = useStores();
    const { currentPatient } = rootStore;

    React.useEffect(
        action(() => {
            rootStore.currentPatient?.getPatientData();
        }),
        []
    );

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
            content: <ProgressInformation />,
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
            content: <BAInformation />,
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
            <LeftPaneContainer elevation={3} square>
                <PatientCard>
                    <Typography variant="h5">{currentPatient?.name}</Typography>
                    <Typography variant="body1">{`MRN: ${currentPatient?.MRN}`}</Typography>
                </PatientCard>
                <Divider variant="middle" />
                <ContentsMenu contents={contents} contentId="#scroll-content" />
            </LeftPaneContainer>
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
};

export default PatientDetailPage;
