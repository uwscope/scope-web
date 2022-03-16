import { ButtonBase, IconButton } from '@mui/material';
import withTheme from '@mui/styles/withTheme';
import { teal } from '@mui/material/colors';
import { alpha } from '@mui/material/styles';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { addDays, addMonths, format, getDate, isSameDay, isSameMonth, lastDayOfMonth } from 'date-fns';
import { eachWeekOfInterval } from 'date-fns/esm';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import * as React from 'react';
import { FunctionComponent } from 'react';
import styled from 'styled-components';

const Container = styled.div({
    position: 'relative',
});

const NavContainer = styled.div({
    alignItems: 'center',
    display: 'flex',
    justifyContent: 'center',
});

const MonthText = styled.div({
    textAlign: 'center',
    fontWeight: 600,
});

const DoWHeaderContainer = styled.div({
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    height: 36,
    alignItems: 'center',
});

const DowHeader = styled.div({
    flex: '1 0',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    textAlign: 'center',
    verticalAlign: 'middle',
    fontWeight: 600,
});

const MonthRowContainer = styled.div({
    display: 'flex',
    position: 'relative',
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    height: 36,
});

const MonthRowDateContainer = styled.div({
    flex: '1 0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
});

const MonthRowDate = withTheme(
    styled(ButtonBase)<{ $selected: boolean; $offRange: boolean }>((props) => ({
        textAlign: 'center',
        fontWeight: 300,
        minWidth: 36,
        height: 36,
        border: '1px solid transparent',
        borderRadius: '50%',
        backgroundColor: props.$selected ? alpha(teal[500], 0.3) : 'transparent',
        color: props.$offRange ? alpha(props.theme.palette.text.primary, 0.5) : props.theme.palette.text.primary,
    }))
);

interface ICalendarProps {
    selectedDate: Date;
    onDayClick?: (date: Date) => void;
}

export const Calendar: FunctionComponent<ICalendarProps> = observer((props) => {
    const { onDayClick, selectedDate } = props;

    const viewState = useLocalObservable<{ currentMonth: Date }>(() => ({
        currentMonth: new Date(),
    }));

    const handlePreviousClick = action(() => {
        viewState.currentMonth = addMonths(viewState.currentMonth, -1);
    });

    const handleNextClick = action(() => {
        viewState.currentMonth = addMonths(viewState.currentMonth, 1);
    });

    const getWeekRow = (start: Date) => {
        return (
            <MonthRowContainer key={start.getTime()}>
                {Array.from(Array(7).keys()).map((dayId, idx) => {
                    const date = addDays(start, dayId);
                    const day = getDate(date);
                    const offRange = !isSameMonth(date, viewState.currentMonth);
                    const selected = isSameDay(date, selectedDate);

                    return (
                        <MonthRowDateContainer key={`${dayId}-${idx}`}>
                            <MonthRowDate
                                onClick={() => onDayClick && onDayClick(date)}
                                key={dayId}
                                $selected={selected}
                                $offRange={offRange}>
                                {day}
                            </MonthRowDate>
                        </MonthRowDateContainer>
                    );
                })}
            </MonthRowContainer>
        );
    };

    const year = viewState.currentMonth.getFullYear();
    const month = viewState.currentMonth.getMonth();
    const weeksInCurrentMonth = eachWeekOfInterval(
        {
            start: new Date(year, month, 1),
            end: lastDayOfMonth(viewState.currentMonth),
        },
        { weekStartsOn: 0 }
    );

    return (
        <Container>
            <NavContainer>
                <IconButton onClick={handlePreviousClick} size="large">
                    <ChevronLeftIcon />
                </IconButton>
                <MonthText>{format(viewState.currentMonth, 'MMMM yyyy')}</MonthText>
                <IconButton onClick={handleNextClick} size="large">
                    <ChevronRightIcon />
                </IconButton>
            </NavContainer>
            <DoWHeaderContainer>
                <DowHeader>Su</DowHeader>
                <DowHeader>M</DowHeader>
                <DowHeader>Tu</DowHeader>
                <DowHeader>W</DowHeader>
                <DowHeader>Th</DowHeader>
                <DowHeader>F</DowHeader>
                <DowHeader>Sa</DowHeader>
            </DoWHeaderContainer>
            {weeksInCurrentMonth.map((mondayOfWeek) => {
                return getWeekRow(mondayOfWeek);
            })}
        </Container>
    );
});

export default Calendar;
