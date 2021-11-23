// import '../node_modules/react-vis/dist/style.css';
import { FormControlLabel, InputLabel, Switch, withStyles, withTheme } from '@material-ui/core';
import { addDays, format } from 'date-fns';
import { addMonths } from 'date-fns/esm';
import throttle from 'lodash.throttle';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React from 'react';
import {
    Crosshair,
    HorizontalGridLines,
    LineMarkSeries,
    LineMarkSeriesPoint,
    MarkSeries,
    RVNearestXData,
    VerticalGridLines,
    XAxis,
    XYPlot,
    YAxis,
} from 'react-vis';
import { AssessmentData } from 'src/services/types';
import { getAssessmentScore } from 'src/utils/assessment';
import { useResize } from 'src/utils/hooks';
import { clearTime } from 'src/utils/time';
import styled, { ThemedStyledProps } from 'styled-components';

const Container = withTheme(
    styled.div({
        display: 'flex',
        flexDirection: 'row',
    })
);

const ChartContainer = withTheme(
    styled.div({
        flexGrow: 1,
    })
);

const LegendContainer = withTheme(
    styled.div((props) => ({
        width: 150,
        margin: props.theme.spacing(1, 2),
        fontSize: '0.95em',
    }))
);

const LegendTitle = styled(InputLabel)({
    fontSize: '1em',
    textTransform: 'uppercase',
});

const LegendArea = withTheme(
    styled.div((props) => ({
        margin: props.theme.spacing(1, 2),
    }))
);

const CrosshairContainer = withTheme(
    styled.div((props) => ({
        margin: props.theme.spacing(1),
        minWidth: 100,
    }))
);

const getColoredSwitch = (color: string) =>
    withStyles({
        switchBase: {
            '&$checked': {
                color: color,
            },
            '&$checked + $track': {
                backgroundColor: color,
            },
        },
        checked: {},
        track: {},
    })(Switch);

export interface IVisDataPoint {
    recordedDate: Date;
    pointValues: AssessmentData;
}

export interface IAssessmentChartProps {
    data: Array<IVisDataPoint>;
    maxValue: number;
    useTime?: boolean;
}

type Point = LineMarkSeriesPoint;

type LegendItem = {
    title: string;
    color: string;
    visible: boolean;
};
interface IAssessmentChartState {
    hoveredPoint: Point | undefined;
    hoveredIndex: number | undefined;
    expanded: boolean;
    visibility: LegendItem[];
}

const state = observable<IAssessmentChartState>({
    hoveredPoint: undefined,
    hoveredIndex: undefined,
    expanded: false,
    visibility: [],
});

const onNearestX = throttle(
    action((point: Point, { index }: RVNearestXData<Point>) => {
        state.hoveredPoint = point;
        state.hoveredIndex = index;
    }),
    500
);

export const AssessmentVis = withTheme(
    observer((props: ThemedStyledProps<IAssessmentChartProps, any>) => {
        const ref = React.useRef(null);
        const { width } = useResize(ref);
        const { data, maxValue, useTime } = props;

        const dataKeys = !!data && data.length > 0 ? Object.keys(data[0].pointValues) : [];

        const toggleExpand = action(() => {
            state.expanded = !state.expanded;

            if (state.expanded && state.visibility.length != dataKeys.length) {
                state.visibility = dataKeys.map((key, idx) => ({
                    title: key,
                    color: props.theme.customPalette.discrete10[idx],
                    visible: true,
                }));
            }
        });

        const toggleVisibility = action((key: string) => {
            const visibility = state.visibility.find((v) => v.title == key);

            if (!!visibility) {
                visibility.visible = !visibility.visible;
            }
        });

        const getDataForKey = (key: string) => {
            return data.map(
                (d) =>
                    ({
                        x: d.recordedDate.getTime(),
                        y: d.pointValues[key],
                        name: key,
                    } as Point)
            );
        };

        if (!!data && data.length > 0) {
            // TODO: Limit to 14-15 data points per view and allow horizontal scrolling

            const dataPoints = data.map(
                (d) =>
                    ({
                        x: (useTime ? d.recordedDate : clearTime(d.recordedDate)).getTime(),
                        y: getAssessmentScore(d.pointValues),
                    } as Point)
            );

            const minXTicks = Math.max(width / 200, 3);
            const minYTicks = state.expanded ? maxValue + 1 : (maxValue * dataKeys.length) / 5;
            const yDomain = [0, state.expanded ? maxValue + 1 : maxValue * dataKeys.length + 1];
            const xDomain = [
                addMonths(clearTime(new Date()), -2).getTime(),
                addDays(clearTime(new Date()), 1).getTime(),
            ];

            return (
                <Container>
                    <ChartContainer ref={ref}>
                        <XYPlot
                            height={300}
                            width={width}
                            xType="time"
                            xDomain={xDomain}
                            yDomain={yDomain}
                            animation={{ duration: 100 }}>
                            <VerticalGridLines />
                            <HorizontalGridLines />
                            <XAxis title="Submitted date" on0={true} tickTotal={minXTicks} />
                            <YAxis title="Score" tickTotal={minYTicks} />
                            {state.expanded ? (
                                state.visibility
                                    .filter(({ visible }) => visible)
                                    .map(({ title, color }) => (
                                        <LineMarkSeries
                                            key={title}
                                            data={getDataForKey(title)}
                                            color={color}
                                            opacity={0.7}
                                            onNearestX={onNearestX}
                                            curve="curveMonotoneX"
                                        />
                                    ))
                            ) : (
                                <LineMarkSeries data={dataPoints} onNearestX={onNearestX} curve="curveMonotoneX" />
                            )}

                            {!state.expanded && state.hoveredPoint && (
                                <MarkSeries data={[state.hoveredPoint]} animation={false} />
                            )}
                            {state.hoveredPoint && data[state.hoveredIndex as number] && (
                                <Crosshair values={[state.hoveredPoint]}>
                                    <CrosshairContainer>
                                        <div>
                                            Date:{' '}
                                            {format(data[state.hoveredIndex as number].recordedDate, 'MM/dd/yyyy')}
                                        </div>
                                        {dataKeys.map((key) => (
                                            <div key={key}>
                                                {key}: {data[state.hoveredIndex as number].pointValues[key]}
                                            </div>
                                        ))}
                                    </CrosshairContainer>
                                </Crosshair>
                            )}
                        </XYPlot>
                    </ChartContainer>
                    {dataKeys.length > 1 && (
                        <LegendContainer>
                            <FormControlLabel
                                control={<Switch color="primary" checked={state.expanded} onChange={toggleExpand} />}
                                label="Expand"
                            />
                            {state.expanded && (
                                <LegendArea>
                                    <LegendTitle>Legend</LegendTitle>
                                    {state.visibility.map(({ title, color, visible }) => {
                                        const ColoredSwitch = getColoredSwitch(color);
                                        return (
                                            <FormControlLabel
                                                key={title}
                                                control={
                                                    <ColoredSwitch
                                                        size="small"
                                                        checked={visible}
                                                        onChange={() => toggleVisibility(title)}
                                                    />
                                                }
                                                label={title}
                                            />
                                        );
                                    })}
                                </LegendArea>
                            )}
                        </LegendContainer>
                    )}
                </Container>
            );
        } else {
            return null;
        }
    })
);
