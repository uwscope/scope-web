import { Typography, withTheme } from '@material-ui/core';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import { ContentsMenu, IContentItem } from './common/ContentsMenu';
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
            hash: 'progress',
            label: 'Progress',
            top: true,
        },
    ] as IContent[];

    React.useLayoutEffect(() => {
        const handleScroll = () => {
            console.log('scroll');
        };

        window.addEventListener('scroll', handleScroll);

        return () => window.removeEventListener('scroll', handleScroll);
    });

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
