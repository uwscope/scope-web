import AssignmentIcon from '@mui/icons-material/Assignment';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import { Grid } from '@mui/material';
import { format } from 'date-fns';
import { observer } from 'mobx-react-lite';
import React, { FunctionComponent } from 'react';
import ActionPanel, { IActionButton } from 'src/components/common/ActionPanel';
import { GridTextField } from 'src/components/common/GridField';
import { getString } from 'src/services/strings';
import { usePatient } from 'src/stores/stores';

export const SafetyPlan: FunctionComponent = observer(() => {
    const currentPatient = usePatient();
    const { safetyPlan } = currentPatient;
    const { assigned, assignedDate, lastUpdatedDate } = safetyPlan;

    var dateStrings: string[] = [];
    if (assigned && !!assignedDate) {
        dateStrings.push(`${getString('patient_safety_plan_assigned_date')} ${format(assignedDate, 'MM/dd/yyyy')}`);
    }

    if (!!lastUpdatedDate) {
        dateStrings.push(
            `${getString('patient_safety_plan_activity_date_header')} ${format(lastUpdatedDate, 'MM/dd/yyyy')}`
        );
    }

    return (
        <ActionPanel
            id={getString('patient_detail_subsection_safety_plan_hash')}
            title={getString('patient_detail_subsection_safety_plan_title')}
            inlineTitle={dateStrings.join(', ')}
            loading={currentPatient?.state == 'Pending'}
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
                    value={safetyPlan.warningSigns?.join('\n')}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Coping Strategies"
                    value={safetyPlan.copingStrategies?.join('\n')}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Social Distractions"
                    value={safetyPlan.socialDistractions?.map((value) => value.name).join('\n')}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Setting Distractions"
                    value={safetyPlan.settingDistractions?.join('\n')}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Social Support"
                    value={safetyPlan.supporters?.map((value) => value.name).join('\n')}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Professional Support"
                    value={safetyPlan.professionals?.map((value) => value.name).join('\n')}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Local Urgent Care Services"
                    value={safetyPlan.urgentServices?.map((value) => value.name).join('\n')}
                />
                <GridTextField
                    sm={6}
                    minLine={2}
                    multiline={true}
                    label="Safe Environment"
                    value={safetyPlan.safeEnvironment?.join('\n')}
                />
            </Grid>
        </ActionPanel>
    );
});

export default SafetyPlan;
