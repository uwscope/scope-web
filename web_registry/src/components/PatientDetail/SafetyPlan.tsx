import AssignmentIcon from '@mui/icons-material/Assignment';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import { Grid } from '@mui/material';
import { format } from 'date-fns';
import { observer } from 'mobx-react-lite';
import React, { FunctionComponent } from 'react';
import { IContact } from 'shared/types';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';
import { getString } from 'src/services/strings';
import { usePatient } from 'src/stores/stores';

export const SafetyPlan: FunctionComponent = observer(() => {
    const currentPatient = usePatient();
    const { safetyPlan } = currentPatient;
    const { assigned, assignedDateTime, lastUpdatedDateTime } = safetyPlan;

    var dateStrings: string[] = [];
    if (assigned && !!assignedDateTime) {
        dateStrings.push(`${getString('patient_safety_plan_assigned_date')} ${format(assignedDateTime, 'MM/dd/yyyy')}`);
    }

    if (!!lastUpdatedDateTime) {
        dateStrings.push(
            `${getString('patient_safety_plan_activity_date_header')} ${format(lastUpdatedDateTime, 'MM/dd/yyyy')}`,
        );
    }

    const formatStringArray = (stringArray: string[] | undefined) => {
        return stringArray?.map((s, idx) => `${idx + 1}. ${s}`).join('\n');
    };

    const formatContactArray = (contactArray: IContact[] | undefined) => {
        return contactArray
            ?.map(
                (c, idx) =>
                    `${idx + 1}. ${c.name}${
                        c.phoneNumber || c.emergencyNumber || c.address
                            ? ` at ${c.phoneNumber || c.emergencyNumber || c.address}`
                            : ''
                    }`,
            )
            .join('\n');
    };

    return (
        <ActionPanel
            id={getString('patient_detail_subsection_safety_plan_hash')}
            title={getString('patient_detail_subsection_safety_plan_title')}
            inlineTitle={dateStrings.join(', ')}
            loading={currentPatient?.loadPatientState.pending || currentPatient?.loadSafetyPlanState.pending}
            error={currentPatient?.loadSafetyPlanState.error}
            actionButtons={[
                {
                    icon: assigned ? <AssignmentTurnedInIcon /> : <AssignmentIcon />,
                    text: assigned
                        ? getString('patient_safety_plan_assigned_button')
                        : getString('patient_safety_plan_assign_button'),
                    onClick: () => currentPatient?.assignSafetyPlan(),
                } as IActionButton,
            ]}>
            <Grid container rowSpacing={2} columnSpacing={8} alignItems="stretch">
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Reasons for Living"
                    value={safetyPlan.reasonsForLiving}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Warning Signs"
                    value={formatStringArray(safetyPlan.warningSigns)}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Coping Strategies"
                    value={formatStringArray(safetyPlan.copingStrategies)}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Social Distractions"
                    value={formatContactArray(safetyPlan.socialDistractions)}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Setting Distractions"
                    value={formatStringArray(safetyPlan.settingDistractions)}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Social Support"
                    value={formatContactArray(safetyPlan.supporters)}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Professional Support"
                    value={formatContactArray(safetyPlan.professionals)}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Local Urgent Care Services"
                    value={formatContactArray(safetyPlan.urgentServices)}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Safe Environment"
                    value={formatStringArray(safetyPlan.safeEnvironment)}
                />
            </Grid>
        </ActionPanel>
    );
});

export default SafetyPlan;
