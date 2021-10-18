import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { format } from 'date-fns';
import { action, observable } from 'mobx';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridDropdownField } from 'src/components/common/GridField';
import { ClickableTableRow } from 'src/components/common/Table';
import { AssessmentFrequency, assessmentFrequencyValues } from 'src/services/enums';
import { IAssessment } from 'src/services/types';
import { usePatient, useStores } from 'src/stores/stores';
import { last } from 'src/utils/array';
import { sortAssessment } from 'src/utils/assessment';

interface IAssessmentEditState {
    assessmentId: string | undefined;
    assessmentType: string;
    frequency: AssessmentFrequency;
    availableAssessments: string[];
}

const state = observable<{ open: boolean; isNew: boolean } & IAssessmentEditState>({
    open: false,
    isNew: false,
    assessmentId: undefined,
    assessmentType: 'PHQ-9',
    frequency: 'Every 2 weeks',
    availableAssessments: [],
});

const AssessmentEdit: FunctionComponent = observer(() => {
    const onValueChange = action((key: string, value: any) => {
        (state as any)[key] = value;
    });

    return (
        <Grid container spacing={2} alignItems="stretch">
            <GridDropdownField
                editable={state.isNew}
                label="Assessment Type"
                value={state.assessmentType}
                options={state.availableAssessments}
                onChange={(text) => onValueChange('assessmentType', text)}
                xs={12}
                sm={12}
            />
            <GridDropdownField
                editable={true}
                label="Assessment Frequency"
                value={state.frequency}
                options={assessmentFrequencyValues}
                xs={12}
                sm={12}
                onChange={(text) => onValueChange('frequency', text)}
            />
        </Grid>
    );
});

export const AssessmentInfo: FunctionComponent = observer(() => {
    const {
        appConfig: { assessments },
    } = useStores();

    const currentPatient = usePatient();

    const validAssessmentNames = assessments.map((a) => a.name);
    const patientAssessmentNames = currentPatient?.assessments?.map((a) => a.assessmentType) || [];

    const availableAssessments = validAssessmentNames.filter((t) => !patientAssessmentNames.includes(t));

    const handleClose = action(() => {
        state.open = false;
    });

    const handleAddAssessment = action(() => {
        state.open = true;
        state.assessmentId = undefined;
        state.assessmentType = availableAssessments[0];
        state.frequency = 'Every 2 weeks';
        state.availableAssessments = availableAssessments;
        state.isNew = true;
    });

    const handleEditAssessment = action((assessment: IAssessment) => {
        state.open = true;
        state.assessmentId = assessment.assessmentId;
        state.assessmentType = assessment.assessmentType;
        state.frequency = assessment.frequency;
        state.availableAssessments = [assessment.assessmentType];
        state.isNew = false;
    });

    const onSave = action(() => {
        const { assessmentId, assessmentType, frequency } = { ...state };
        currentPatient?.updateAssessment({ assessmentId, assessmentType, frequency, data: [] });
        state.open = false;
    });

    const actionButtons = [
        {
            icon: <AddIcon />,
            text: 'Add Assessment',
            onClick: availableAssessments.length > 0 ? handleAddAssessment : undefined,
        } as IActionButton,
    ];

    return (
        <ActionPanel
            id="assessments"
            title="Assessments"
            loading={currentPatient?.state == 'Pending'}
            actionButtons={actionButtons}>
            {currentPatient?.assessments && currentPatient?.assessments.length > 0 ? (
                <Grid container spacing={2} alignItems="stretch">
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Assessment</TableCell>
                                    <TableCell>Frequency</TableCell>
                                    <TableCell>Last completed</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {currentPatient?.assessments
                                    .slice()
                                    .sort(sortAssessment)
                                    .map((a) => {
                                        return (
                                            <ClickableTableRow
                                                hover
                                                key={a.assessmentType}
                                                onClick={() => handleEditAssessment(a)}>
                                                <TableCell component="th" scope="row">
                                                    {a.assessmentType}
                                                </TableCell>
                                                <TableCell>{a.frequency}</TableCell>
                                                <TableCell>
                                                    {a.data.length > 0
                                                        ? format(last(a.data)?.date as Date, 'MM/dd/yyyy')
                                                        : 'NA'}
                                                </TableCell>
                                            </ClickableTableRow>
                                        );
                                    })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Grid>
            ) : (
                <Grid item xs={12}>
                    <Typography>There are no assessments assigned for this patient</Typography>
                </Grid>
            )}

            <Dialog open={state.open} onClose={handleClose}>
                <DialogTitle>{`${state.isNew ? 'Add' : 'Edit'} Assessment${
                    state.isNew ? '' : ' Frequency'
                }`}</DialogTitle>
                <DialogContent>
                    <AssessmentEdit />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={onSave} color="primary">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </ActionPanel>
    );
});

export default AssessmentInfo;
