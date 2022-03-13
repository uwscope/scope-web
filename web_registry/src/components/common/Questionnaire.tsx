import { Grid, Radio, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import React, { FunctionComponent } from 'react';
import Disable from 'src/components/common/Disable';
import { GridDateField, GridSwitchField, GridTextField } from 'src/components/common/GridField';
import { getString } from 'src/services/strings';

export interface IOption {
    text: string;
    value: number;
}

export interface IQuestion {
    id: string;
    question: string;
}

export interface IQuestionnaireProps {
    readonly?: boolean;
    instruction?: string;
    questions: IQuestion[];
    options: IOption[];
    selectedValues: (number | undefined)[];
    selectedDate: Date;
    totalOnly: boolean;
    totalScore?: string;
    maxTotal: number;
    comment?: string;
    onDateChange?: (date: Date) => void;
    onSelect?: (qid: string, value: number) => void;
    onToggleTotalOnly?: (on: boolean) => void;
    onTotalChange?: (total: string) => void;
    onCommentChange?: (comment: string) => void;
}

export const Questionnaire: FunctionComponent<IQuestionnaireProps> = (props) => {
    const {
        readonly = false,
        instruction,
        questions,
        options,
        selectedValues,
        selectedDate,
        onSelect,
        onDateChange,
        totalOnly,
        totalScore,
        maxTotal,
        onToggleTotalOnly,
        onTotalChange,
        comment,
        onCommentChange,
    } = props;

    const handleSelectChange = (q: IQuestion) => (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!onSelect && !readonly) {
            onSelect(q.id, Number(event.target.value));
        }
    };

    return (
        <Grid container spacing={2} alignItems="center">
            <GridDateField
                xs={4}
                sm={4}
                editable={!readonly}
                label={
                    readonly
                        ? getString('patient_progress_assessment_dialog_add_submitted_date_label')
                        : getString('patient_progress_assessment_dialog_add_administered_date_label')
                }
                value={selectedDate}
                required={true}
                onChange={(value) => onDateChange && onDateChange(value as Date)}
            />
            {!readonly && (
                <GridSwitchField
                    xs={4}
                    sm={4}
                    editable={!readonly}
                    label={getString('patient_progress_assessment_dialog_add_total_score_label')}
                    on={totalOnly}
                    onChange={(value) => onToggleTotalOnly && onToggleTotalOnly(value)}
                />
            )}
            {totalOnly && (
                <GridTextField
                    xs={4}
                    sm={4}
                    editable={!readonly && totalOnly}
                    label="Total score"
                    value={totalScore}
                    required={totalOnly}
                    helperText={`Must be 0-${maxTotal}`}
                    onChange={(value) => onTotalChange && onTotalChange(`${value}`)}
                />
            )}
            <Grid item xs={12}>
                <Disable disabled={totalOnly}>
                    <Table stickyHeader size="small">
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
                </Disable>
            </Grid>
            <GridTextField
                xs={12}
                sm={12}
                editable={!readonly}
                label={getString('patient_progress_assessment_dialog_comment_label')}
                value={comment}
                onChange={(value) => onCommentChange && onCommentChange(value as string)}
                multiline
                minLine={3}
            />
        </Grid>
    );
};

export default Questionnaire;
