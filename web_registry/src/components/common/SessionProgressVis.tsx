import { useTheme } from '@mui/styles';
import withTheme from '@mui/styles/withTheme';
import { addDays, addMonths, compareAsc } from 'date-fns';
import React, { FunctionComponent } from 'react';
import {
    DiscreteColorLegend,
    HorizontalGridLines,
    LineMarkSeries,
    LineMarkSeriesPoint,
    VerticalGridLines,
    VerticalRectSeries,
    XAxis,
    XYPlot,
    YAxis,
} from 'react-vis';
import { formatDateOnly } from 'shared/time';
import { useResize } from 'src/utils/hooks';
import styled from 'styled-components';

const Container = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'column',
    }),
);

const ChartContainer = withTheme(
    styled.div({
        flexGrow: 1,
    }),
);

export interface IAssessionDataPoint {
    date: Date;
    score: number;
}

export interface ISessionReviewDataPoint {
    id: string;
    date: Date;
}

export interface ISessionProgressVisProps {
    phqScores: Array<IAssessionDataPoint>; // Data points should be sorted in date ascending
    gadScores: Array<IAssessionDataPoint>; // Data points should be sorted in date ascending
    sessions: Array<ISessionReviewDataPoint>;
    reviews: Array<ISessionReviewDataPoint>;
    onSessionClick?: (sessionId: string) => void;
    onReviewClick?: (caseReviewId: string) => void;
}

export const SessionProgressVis: FunctionComponent<ISessionProgressVisProps> = (props) => {
    const ref = React.useRef(null);
    const { width } = useResize(ref);
    const { phqScores = [], gadScores = [], sessions = [], reviews = [], onSessionClick, onReviewClick } = props;
    const theme = useTheme();

    const phqColor = theme.customPalette.discrete10[0];
    const gadColor = theme.customPalette.discrete10[1];
    const sessionColor = theme.customPalette.discrete10[2];
    const reviewColor = theme.customPalette.discrete10[3];

    const legendItems = [
        {
            title: 'PHQ-9',
            color: phqColor,
        },
        { title: 'GAD-7', color: gadColor },
        { title: 'Session', color: sessionColor },
        { title: 'Case review', color: reviewColor },
    ];

    const yMax = 28;
    const yDomain = [0, yMax];

    const minStartDate = addMonths(new Date(), -3);
    const dateMax = addDays(new Date(), 2);
    const scoreDateMin =
        phqScores.concat(gadScores).sort((a, b) => compareAsc(a.date, b.date))[0]?.date || minStartDate;
    const sessionDateMin = sessions.concat(reviews).sort((a, b) => compareAsc(a.date, b.date))[0]?.date || minStartDate;
    const dateMin = addDays([scoreDateMin, sessionDateMin, minStartDate].sort(compareAsc)[0], -2);

    const xDomain = [dateMin.getTime(), dateMax.getTime()];

    const phqData = phqScores.map((ps) => ({ x: ps.date.getTime(), y: ps.score } as LineMarkSeriesPoint));

    const gadData = gadScores.map((ps) => ({ x: ps.date.getTime(), y: ps.score } as LineMarkSeriesPoint));

    const sessionRectData = sessions.map((s) => ({
        x0: s.date.getTime(),
        x: s.date.getTime() + 86400000,
        y0: 0,
        y: yMax,
        id: s.id,
    }));

    const reviewRectData = reviews.map((s) => ({
        x0: s.date.getTime(),
        x: s.date.getTime() + 86400000,
        y0: 0,
        y: yMax,
        id: s.id,
    }));

    return (
        <Container>
            <ChartContainer ref={ref}>
                <XYPlot
                    height={300}
                    width={width}
                    xType="time"
                    animation={{ duration: 100 }}
                    yDomain={yDomain}
                    xDomain={xDomain}>
                    <VerticalGridLines />
                    <HorizontalGridLines />
                    <XAxis
                        title="Date"
                        on0={true}
                        tickFormat={(tick: number) => formatDateOnly(tick, 'MMM d')}
                        tickLabelAngle={-45}
                    />
                    <YAxis title="Score" />
                    <LineMarkSeries key="phq9" data={phqData} color={phqColor} opacity={0.7} curve="curveMonotoneX" />
                    <LineMarkSeries key="gad7" data={gadData} color={gadColor} opacity={0.7} curve="curveMonotoneX" />
                    <VerticalRectSeries
                        data={sessionRectData}
                        style={{ fill: sessionColor, stroke: sessionColor, opacity: 0.5 }}
                        onValueClick={(point) => onSessionClick && onSessionClick(point.id)}
                    />
                    <VerticalRectSeries
                        data={reviewRectData}
                        style={{ fill: reviewColor, stroke: reviewColor, opacity: 0.5 }}
                        onValueClick={(point) => onReviewClick && onReviewClick(point.id)}
                    />
                </XYPlot>
                <DiscreteColorLegend orientation="horizontal" width={width} items={legendItems} />
            </ChartContainer>
        </Container>
    );
};
