import { Grid, Radio, Table, TableBody, TableCell, TableHead, TableRow } from '@material-ui/core';
import React, { FunctionComponent } from 'react';
import { GridDateField, GridSwitchField, GridTextField } from 'src/components/common/GridField';

export interface IOption {
    text: string;
    value: number;
}

export interface IQuestion {
    id: string;
    question: string;
}

export interface IQuestionnaireProps {
    instruction?: string;
    questions: IQuestion[];
    options: IOption[];
    selectedValues: (number | undefined)[];
    selectedDate: Date;
    totalOnly: boolean;
    totalScore?: number;
    onDateChange?: (date: Date) => void;
    onSelect?: (qid: string, value: number) => void;
    onToggleTotalOnly?: (on: boolean) => void;
    onTotalChange?: (total: number) => void;
}

export const Questionnaire: FunctionComponent<IQuestionnaireProps> = (props) => {
    const {
        instruction,
        questions,
        options,
        selectedValues,
        selectedDate,
        onSelect,
        onDateChange,
        totalOnly,
        totalScore,
        onToggleTotalOnly,
        onTotalChange,
    } = props;

    const handleSelectChange = (q: IQuestion) => (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onSelect) {
            onSelect(q.id, Number(event.target.value));
        }
    };

    return (
        <Grid container spacing={2} alignItems="center" xs={12}>
            <GridDateField
                xs={6}
                sm={4}
                editable={true}
                label="Administered Date"
                value={selectedDate}
                onChange={(value) => onDateChange && onDateChange(value as Date)}
            />
            <GridSwitchField
                xs={6}
                sm={4}
                editable={true}
                label="Submit total score only"
                on={totalOnly}
                onChange={(value) => onToggleTotalOnly && onToggleTotalOnly(value)}
            />
            {totalOnly ? (
                <GridTextField
                    xs={12}
                    sm={12}
                    editable={true}
                    label="Total score"
                    value={totalScore}
                    onChange={(value) => onTotalChange && onTotalChange(value as number)}
                />
            ) : (
                <Table stickyHeader>
                    <TableHead>
                        <TableRow>
                            <TableCell>{instruction}</TableCell>
                            {options.map((o) => (
                                <TableCell key={o.text}>{o.text}</TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {questions.map((q, idx) => (
                            <TableRow key={idx}>
                                <TableCell component="th" scope="row">
                                    <strong>{q.id}</strong>
                                    {`: ${q.question}`}
                                </TableCell>
                                {options.map((o) => (
                                    <TableCell key={o.text}>
                                        <Radio
                                            checked={selectedValues[idx] === o.value}
                                            onChange={handleSelectChange(q)}
                                            value={o.value}
                                        />
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </Grid>
    );
};

export default Questionnaire;
