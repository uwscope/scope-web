import { Checkbox, FormControlLabel, FormHelperText, Grid } from '@material-ui/core';
import { format } from 'date-fns';
import { observer } from 'mobx-react';
import React, { FunctionComponent } from 'react';
import ActionPanel from 'src/components/common/ActionPanel';
import { BehavioralActivationChecklistItem, behavioralActivationChecklistValues } from 'src/services/enums';
import { useStores } from 'src/stores/stores';

export const BAChecklist: FunctionComponent = observer(() => {
    const { currentPatient } = useStores();

    const baCompletion: { [key: string]: Date | undefined } = {};
    currentPatient?.sessions.forEach((s) => {
        Object.keys(s.behavioralActivationChecklist).forEach((key) => {
            if (s.behavioralActivationChecklist[key as BehavioralActivationChecklistItem]) {
                baCompletion[key] = s.date;
            }
        });
    });

    return (
        <ActionPanel id="checklist" title="Checklist" loading={currentPatient?.state == 'Pending'} actionButtons={[]}>
            <Grid container spacing={2} alignItems="stretch">
                {behavioralActivationChecklistValues.map((item) => {
                    const completed = !!baCompletion[item];
                    return (
                        <Grid item xs={12} md={6} xl={4} key={item}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={completed}
                                        name={item}
                                        color="primary"
                                        inputProps={{
                                            readOnly: true,
                                        }}
                                    />
                                }
                                label={item}
                            />
                            {completed ? (
                                <FormHelperText>{`Last performed on ${format(
                                    baCompletion[item] as Date,
                                    'MM/dd/yyyy'
                                )}`}</FormHelperText>
                            ) : null}
                        </Grid>
                    );
                })}
            </Grid>
        </ActionPanel>
    );
});

export default BAChecklist;
