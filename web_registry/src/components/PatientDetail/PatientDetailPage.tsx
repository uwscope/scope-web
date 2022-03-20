import { Divider, Grid, Paper, Typography } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { observer } from 'mobx-react';
import { runInAction } from 'mobx';
import React, { FunctionComponent, useEffect } from 'react';
import { useParams } from 'react-router';
import PageLoader from 'src/components/chrome/PageLoader';
import { ContentsMenu, IContentItem } from 'src/components/common/ContentsMenu';
import BehavioralInformation from 'src/components/PatientDetail/BehavioralInformation';
import PatientCard from 'src/components/PatientDetail/PatientCard';
import PatientCardExtended from 'src/components/PatientDetail/PatientCardExtended';
import PatientInformation from 'src/components/PatientDetail/PatientInformation';
import ProgressInformation from 'src/components/PatientDetail/ProgressInformation';
import SessionInformation from 'src/components/PatientDetail/SessionInformation';
import { getString } from 'src/services/strings';
import { PatientStoreProvider, useStores } from 'src/stores/stores';
import { sortAssessmentContent } from 'src/utils/assessment';
import styled from 'styled-components';

const DetailPageContainer = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'stretch',
        height: '100%',
        overflow: 'hidden',
    }),
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
    })),
);

const ContentContainer = withTheme(
    styled.div((props) => ({
        flex: 1,
        padding: props.theme.spacing(3),
        overflowX: 'hidden',
        overflowY: 'auto',
    })),
);

const Section = withTheme(
    styled.div((props) => ({
        marginBottom: props.theme.spacing(12),
    })),
);

const SectionTitle = withTheme(
    styled(Typography)((props) => ({
        marginTop: props.theme.spacing(2),
        marginBottom: props.theme.spacing(4),
        textTransform: 'uppercase',
        fontWeight: 600,
    })),
);

type IContent = IContentItem & { content?: React.ReactNode };

export const PatientDetailPage: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const { recordId } = useParams<{ recordId: string | undefined }>();
    const currentPatient = rootStore.patientsStore.getPatientByRecordId(recordId);
    const validAssessments = rootStore.appContentConfig.assessments;

    useEffect(() => {
        runInAction(() => {
            currentPatient?.load(
                () => rootStore.authStore.getToken(),
                () => rootStore.authStore.refreshToken(),
            );
        });
    }, [currentPatient]);

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
            label: 'Session & Review Information',
            top: true,
            content: <SessionInformation />,
        },
        {
            hash: 'sessions',
            label: 'Sessions & Reviews',
        },
    ] as IContent[];
    contentMenu.push.apply(contentMenu, sessionInfoMenu);

    const progressMenu = [
        {
            hash: 'progress',
            label: 'Progress',
            top: true,
            content: <ProgressInformation />,
        },
    ] as IContent[];

    progressMenu.push.apply(
        progressMenu,
        validAssessments
            .slice()
            .sort(sortAssessmentContent)
            .map(
                (a) =>
                    ({
                        hash: a.id,
                        label: a.name,
                    } as IContent),
            ),
    );

    progressMenu.push({
        hash: getString('patient_progress_activity_hash'),
        label: getString('patient_progress_activity_name'),
    } as IContent);

    contentMenu.push.apply(contentMenu, progressMenu);

    const baMenu = [
        {
            hash: getString('patient_detail_section_behavior_strategies_hash'),
            label: getString('patient_detail_section_behavior_strategies_title'),
            top: true,
            content: <BehavioralInformation />,
        },
        {
            hash: getString('patient_detail_subsection_checklist_hash'),
            label: getString('patient_detail_subsection_checklist_title'),
        },
        {
            hash: getString('patient_detail_subsection_values_inventory_hash'),
            label: getString('patient_detail_subsection_values_inventory_title'),
        },
        {
            hash: getString('patient_detail_subsection_safety_plan_hash'),
            label: getString('patient_detail_subsection_safety_plan_title'),
        },
    ] as IContent[];
    contentMenu.push.apply(contentMenu, baMenu);

    return (
        <PageLoader
            state={rootStore.patientsStore.state}
            name="the registry"
            hasValue={rootStore.patientsStore.patients.length > 0}>
            {currentPatient && (
                <PatientStoreProvider patient={currentPatient}>
                    <DetailPageContainer>
                        <LeftPaneContainer elevation={3} square>
                            <Grid
                                container
                                spacing={1}
                                direction="column"
                                justifyContent="flex-start"
                                alignItems="stretch">
                                <Grid item>
                                    <PatientCard
                                        loading={
                                            currentPatient.loadPatientState.pending ||
                                            currentPatient.loadProfileState.pending
                                        }
                                        error={currentPatient.loadProfileState.error}
                                    />
                                </Grid>
                                <Grid item>
                                    <Divider variant="middle" />
                                </Grid>
                                <Grid item>
                                    <PatientCardExtended />
                                </Grid>
                                <Grid item>
                                    <Divider variant="middle" />
                                </Grid>
                                <Grid item>
                                    <ContentsMenu contents={contentMenu} contentId="#scroll-content" />
                                </Grid>
                            </Grid>
                        </LeftPaneContainer>
                        <ContentContainer id="scroll-content">
                            {contentMenu
                                .filter((c) => c.top)
                                .map((c) => (
                                    <Section id={c.hash} key={c.hash}>
                                        <SectionTitle variant="h4">{c.label}</SectionTitle>
                                        {c.content ? c.content : null}
                                    </Section>
                                ))}
                        </ContentContainer>
                    </DetailPageContainer>
                </PatientStoreProvider>
            )}
        </PageLoader>
    );
});

export default PatientDetailPage;
