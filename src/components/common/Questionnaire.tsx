import { Grid, Radio, Table, TableBody, TableCell, TableHead, TableRow } from '@material-ui/core';
import React, { FunctionComponent } from 'react';

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
    onSelect?: (qid: string, value: number) => void;
}

export const Questionnaire: FunctionComponent<IQuestionnaireProps> = (props) => {
    const { instruction, questions, options, selectedValues, onSelect } = props;

    const handleChange = (q: IQuestion) => (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onSelect) {
            onSelect(q.id, Number(event.target.value));
        }
    };

    return (
        <Grid item container spacing={2} alignItems="stretch" xs={12}>
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
                                {`${idx + 1}. ${q.question}`}
                            </TableCell>
                            {options.map((o) => (
                                <TableCell key={o.text}>
                                    <Radio
                                        checked={selectedValues[idx] === o.value}
                                        onChange={handleChange(q)}
                                        value={o.value}
                                    />
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Grid>
    );
};

export default Questionnaire;
