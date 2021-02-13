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
            hash: 'basic-info',
            label: 'Basic information',
        },
        {
            hash: 'treatment-info',
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
                {contents.map((c) => (
                    <div style={{ minHeight: '600px' }} id={c.hash} key={c.hash}>
                        {c.content ? c.content : <Typography variant={c.top ? 'h5' : 'h6'}>{c.label}</Typography>}
                    </div>
                ))}
            </ContentContainer>
        </DetailPageContainer>
    );
});

export default PatientDetailPage;
