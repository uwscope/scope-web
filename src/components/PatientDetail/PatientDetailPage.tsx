import { Divider, Paper, Typography, withTheme } from '@material-ui/core';
import { action } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import { useParams } from 'react-router';
import { ContentsMenu, IContentItem } from 'src/components/common/ContentsMenu';
import BAInformation from 'src/components/PatientDetail/BAInformation';
import PatientCard from 'src/components/PatientDetail/PatientCard';
import PatientInformation from 'src/components/PatientDetail/PatientInformation';
import ProgressInformation from 'src/components/PatientDetail/ProgressInformation';
import SessionInformation from 'src/components/PatientDetail/SessionInformation';
import { PatientStoreProvider, useStores } from 'src/stores/stores';
import { sortAssessment } from 'src/utils/assessment';
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
    styled(Paper)((props) => ({
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'stretch',
        height: '100%',
        overflowY: 'auto',
        overflowX: 'hidden',
        width: props.theme.customSizes.contentsMenuWidth,
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

export const PatientDetailPage: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const { mrn } = useParams<{ mrn: string | undefined }>();
    const currentPatient = rootStore.getPatientByMRN(mrn);

    React.useEffect(
        action(() => {
            if (currentPatient) {
                currentPatient.getPatientData();
            }
        }),
        []
    );

    const contentMenu: IContent[] = [];

    const patientInfoMenu = [
        {
            hash: 'patient',
            label: 'Patient',
            top: true,
            content: <PatientInformation />,
        },
        {
            hash: 'clinical-history',
            label: 'Clinical History',
        },
        {
            hash: 'treatment',
            label: 'Treatment information',
        },
    ] as IContent[];
    contentMenu.push.apply(contentMenu, patientInfoMenu);

    const sessionInfoMenu = [
        {
            hash: 'session-info',
            label: 'Session Information',
            top: true,
            content: <SessionInformation />,
        },
        {
            hash: 'sessions',
            label: 'Sessions',
        },
    ] as IContent[];
    contentMenu.push.apply(contentMenu, sessionInfoMenu);

    if (currentPatient?.assessments && currentPatient?.assessments.length > 0) {
        const progressMenu = [
            {
                hash: 'progress',
                label: 'Progress',
                top: true,
                content: <ProgressInformation />,
            },
            {
                hash: 'assessments',
                label: 'Assessments',
            },
        ] as IContent[];

        progressMenu.push.apply(
            progressMenu,
            currentPatient?.assessments
                .slice()
                .sort(sortAssessment)
                .map(
                    (a) =>
                        ({
                            hash: a.assessmentType.replace('-', '').replace(' ', '_').toLocaleLowerCase(),
                            label: a.assessmentType,
                        } as IContent)
                )
        );
        contentMenu.push.apply(contentMenu, progressMenu);
    }

    const baMenu = [
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
    contentMenu.push.apply(contentMenu, baMenu);

    if (!!currentPatient) {
        return (
            <PatientStoreProvider patient={currentPatient}>
                <DetailPageContainer>
                    <LeftPaneContainer elevation={3} square>
                        <PatientCard loading={currentPatient.state == 'Pending'} />
                        <Divider variant="middle" />
                        <ContentsMenu contents={contentMenu} contentId="#scroll-content" />
                    </LeftPaneContainer>
                    <ContentContainer id="scroll-content">
                        {contentMenu
                            .filter((c) => c.top)
                            .map((c) => (
                                <Section id={c.hash} key={c.hash}>
                                    <SectionTitle variant="h6">{c.label}</SectionTitle>
                                    {c.content ? c.content : null}
                                </Section>
                            ))}
                    </ContentContainer>
                </DetailPageContainer>
            </PatientStoreProvider>
        );
    } else {
        return null;
    }
});

export default PatientDetailPage;
