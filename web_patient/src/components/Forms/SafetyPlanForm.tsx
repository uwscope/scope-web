import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { Box, Button, Grid, IconButton, Stack, TextField, Typography } from '@mui/material';
import { action } from 'mobx';
import { observer, useLocalObservable } from 'mobx-react';
import React, { Fragment, FunctionComponent } from 'react';
import { ContactType } from 'shared/enums';
import { IContact, ISafetyPlan } from 'shared/types';
import FormDialog from 'src/components/Forms/FormDialog';
import FormSection from 'src/components/Forms/FormSection';
import { IFormProps } from 'src/components/Forms/GetFormDialog';
import { getString } from 'src/services/strings';
import { useStores } from 'src/stores/stores';

interface IStringListFormSectionProps {
    prompt: string;
    subPrompt: string;
    stringList: string[];
    onListItemChange: (change: string, idx: number) => void;
    onDeleteListItem: (idx: number) => void;
    onAddListItem: () => void;
}

const StringListFormSection = (props: IStringListFormSectionProps) => {
    const { prompt, subPrompt, stringList, onListItemChange, onDeleteListItem, onAddListItem } = props;

    const handleListItemChange = (idx: number) => (event: React.ChangeEvent<HTMLInputElement>) => {
        onListItemChange(event.target.value, idx);
    };

    return (
        <FormSection
            prompt={prompt}
            subPrompt={subPrompt}
            content={
                <Stack spacing={2}>
                    {stringList.map((s, idx) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography sx={{ paddingRight: 1 }}>{`${idx + 1}.`}</Typography>
                            <TextField
                                sx={{ flexGrow: 1 }}
                                key={idx}
                                fullWidth
                                rows={1}
                                value={s}
                                variant="standard"
                                onChange={handleListItemChange(idx)}
                            />
                            <IconButton
                                size="small"
                                aria-label="delete"
                                disabled={!s}
                                onClick={() => onDeleteListItem(idx)}>
                                <DeleteIcon fontSize="small" />
                            </IconButton>
                        </Box>
                    ))}
                    <Button
                        sx={{ marginTop: 1, alignSelf: 'flex-end' }}
                        disabled={!stringList[0]}
                        variant="contained"
                        color="primary"
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={onAddListItem}>
                        {getString('Safetyplan_add')}
                    </Button>
                </Stack>
            }
        />
    );
};

const getEmptyContact = (contactType: ContactType) => {
    return { name: '', phoneNumber: '', address: '', emergencyNumber: '', contactType };
};

interface IContactLabels {
    name?: string;
    address?: string;
    phoneNumber?: string;
    emergencyNumber?: string;
}

interface IContactListFormSectionProps {
    prompt: string;
    subPrompt: string;
    contactList: IContact[];
    fieldLabels: IContactLabels;
    onContactItemChange: (change: IContact, idx: number) => void;
    onDeleteContactItem: (idx: number) => void;
    onAddContactItem: () => void;
}

const ContactListFormSection = (props: IContactListFormSectionProps) => {
    const { prompt, subPrompt, contactList, fieldLabels, onContactItemChange, onDeleteContactItem, onAddContactItem } =
        props;

    const handleContactItemChange = (prop: string, idx: number) => (event: React.ChangeEvent<HTMLInputElement>) => {
        const newContact = { ...contactList[idx] };
        (newContact as any)[prop] = event.target.value;
        onContactItemChange(newContact, idx);
    };

    return (
        <FormSection
            prompt={prompt}
            subPrompt={subPrompt}
            content={
                <Stack spacing={4}>
                    {contactList.map((contact, idx) => (
                        <Grid container direction="row" alignItems="flex-start" key={idx}>
                            <Grid item>
                                <Typography sx={{ paddingRight: 1 }}>{`${idx + 1}.`}</Typography>
                            </Grid>
                            <Grid item flexGrow={1}>
                                <Stack spacing={1}>
                                    {fieldLabels.name && (
                                        <TextField
                                            label={fieldLabels.name}
                                            fullWidth
                                            rows={1}
                                            value={contact.name}
                                            variant="standard"
                                            InputLabelProps={{ shrink: true }}
                                            onChange={handleContactItemChange('name', idx)}
                                        />
                                    )}
                                    {fieldLabels.address && (
                                        <TextField
                                            label={fieldLabels.address}
                                            fullWidth
                                            rows={1}
                                            value={contact.address}
                                            variant="standard"
                                            InputLabelProps={{ shrink: true }}
                                            onChange={handleContactItemChange('address', idx)}
                                        />
                                    )}
                                    {fieldLabels.phoneNumber && (
                                        <TextField
                                            label={fieldLabels.phoneNumber}
                                            fullWidth
                                            rows={1}
                                            value={contact.phoneNumber}
                                            variant="standard"
                                            InputLabelProps={{ shrink: true }}
                                            onChange={handleContactItemChange('phoneNumber', idx)}
                                        />
                                    )}
                                    {fieldLabels.emergencyNumber && (
                                        <TextField
                                            label={fieldLabels.emergencyNumber}
                                            fullWidth
                                            rows={1}
                                            value={contact.emergencyNumber}
                                            variant="standard"
                                            InputLabelProps={{ shrink: true }}
                                            onChange={handleContactItemChange('emergencyNumber', idx)}
                                        />
                                    )}
                                </Stack>
                            </Grid>

                            <IconButton
                                size="small"
                                aria-label="delete"
                                disabled={!contact.name}
                                onClick={() => onDeleteContactItem(idx)}>
                                <DeleteIcon fontSize="small" />
                            </IconButton>
                        </Grid>
                    ))}
                    <Button
                        sx={{ marginTop: 1, alignSelf: 'flex-end' }}
                        disabled={!contactList[0]?.name}
                        variant="contained"
                        color="primary"
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={onAddContactItem}>
                        {getString('Safetyplan_add')}
                    </Button>
                </Stack>
            }
        />
    );
};

export interface ISafetyPlanFormProps extends IFormProps {}

export const SafetyPlanForm: FunctionComponent<ISafetyPlanFormProps> = observer(() => {
    const rootStore = useStores();
    const { patientStore } = rootStore;
    const safetyPlan = patientStore.safetyPlan;

    const dataState = useLocalObservable<ISafetyPlan>(() => ({ ...safetyPlan }));

    const handleNext = action((prev: number) => {
        prev;
        // TODO: save
    });

    const handleSubmit = action(async () => {
        await patientStore.updateSafetyPlan(dataState);
        return true;
    });

    const onValueChange = (key: string) =>
        action((event: React.ChangeEvent<HTMLInputElement>) => {
            (dataState as any)[key] = event.target.value;
        });

    const onListItemChange = action((listKey: string, idx: number, change: string) => {
        const list = (dataState as any)[listKey] || [];
        list[idx] = change;
        (dataState as any)[listKey] = list;
    });

    const onAddListItem = (listKey: string) =>
        action(() => {
            const list = (dataState as any)[listKey] || [];
            list.push('');
            (dataState as any)[listKey] = list;
        });

    const onDeleteListItem = action((listKey: string, idx: number) => {
        const list = (dataState as any)[listKey] || [];
        list.splice(idx, 1);
        (dataState as any)[listKey] = list;
    });

    const onContactItemChange = action((listKey: string, idx: number, change: IContact) => {
        const list = (dataState as any)[listKey] || [];
        list[idx] = change;
        (dataState as any)[listKey] = list;
    });

    const onAddContactItem = (key: string, contactType: ContactType) =>
        action(() => {
            const list = (dataState as any)[key] || [];
            list.push(getEmptyContact(contactType));
            (dataState as any)[key] = list;
        });

    const onDeleteContactItem = action((key: string, idx: number) => {
        const list = (dataState as any)[key] || [];
        list.splice(idx, 1);
        (dataState as any)[key] = list;
    });

    const pages = [
        {
            content: (
                <Stack spacing={4}>
                    <FormSection
                        prompt={getString('Safetyplan_reasons_for_living_title')}
                        subPrompt={getString('Safetyplan_reasons_for_living_description')}
                        content={
                            <TextField
                                fullWidth
                                multiline
                                rows={3}
                                value={dataState.reasonsForLiving}
                                onChange={onValueChange('reasonsForLiving')}
                                variant="outlined"
                            />
                        }
                    />
                    <StringListFormSection
                        prompt={getString('Safetyplan_warning_signs_title')}
                        subPrompt={getString('Safetyplan_warning_signs_description')}
                        stringList={
                            dataState.warningSigns && dataState.warningSigns.length > 0 ? dataState.warningSigns : ['']
                        }
                        onListItemChange={(change: string, idx: number) =>
                            onListItemChange('warningSigns', idx, change)
                        }
                        onDeleteListItem={(idx: number) => onDeleteListItem('warningSigns', idx)}
                        onAddListItem={onAddListItem('warningSigns')}
                    />
                </Stack>
            ),
            canGoNext: true,
        },
        {
            content: (
                <StringListFormSection
                    prompt={getString('Safetyplan_coping_strategies_title')}
                    subPrompt={getString('Safetyplan_coping_strategies_description')}
                    stringList={
                        dataState.copingStrategies && dataState.copingStrategies.length > 0
                            ? dataState.copingStrategies
                            : ['']
                    }
                    onListItemChange={(change: string, idx: number) =>
                        onListItemChange('copingStrategies', idx, change)
                    }
                    onDeleteListItem={(idx: number) => onDeleteListItem('copingStrategies', idx)}
                    onAddListItem={onAddListItem('copingStrategies')}
                />
            ),
            canGoNext: true,
        },
        {
            content: (
                <Stack spacing={4}>
                    <ContactListFormSection
                        prompt={getString('Safetyplan_social_distraction_person_title')}
                        subPrompt={getString('Safetyplan_social_distraction_person_description')}
                        contactList={
                            dataState.socialDistractions && dataState.socialDistractions.length > 0
                                ? dataState.socialDistractions
                                : [getEmptyContact('Person')]
                        }
                        fieldLabels={{ name: getString('Safetyplan_name'), phoneNumber: getString('Safetyplan_phone') }}
                        onContactItemChange={(change: IContact, idx: number) =>
                            onContactItemChange('socialDistractions', idx, change)
                        }
                        onDeleteContactItem={(idx: number) => onDeleteContactItem('socialDistractions', idx)}
                        onAddContactItem={onAddContactItem('socialDistractions', 'Person')}
                    />

                    <StringListFormSection
                        prompt={getString('Safetyplan_social_distraction_setting_title')}
                        subPrompt={getString('Safetyplan_social_distraction_setting_description')}
                        stringList={
                            dataState.settingDistractions && dataState.settingDistractions.length > 0
                                ? dataState.settingDistractions
                                : ['']
                        }
                        onListItemChange={(change: string, idx: number) =>
                            onListItemChange('settingDistractions', idx, change)
                        }
                        onDeleteListItem={(idx: number) => onDeleteListItem('settingDistractions', idx)}
                        onAddListItem={onAddListItem('settingDistractions')}
                    />
                </Stack>
            ),
            canGoNext: true,
        },
        {
            content: (
                <Stack spacing={4}>
                    <ContactListFormSection
                        prompt={getString('Safetyplan_people_help_title')}
                        subPrompt={getString('Safetyplan_people_help_description')}
                        contactList={
                            dataState.supporters && dataState.supporters.length > 0
                                ? dataState.supporters
                                : [getEmptyContact('Person')]
                        }
                        fieldLabels={{ name: getString('Safetyplan_name'), phoneNumber: getString('Safetyplan_phone') }}
                        onContactItemChange={(change: IContact, idx: number) =>
                            onContactItemChange('supporters', idx, change)
                        }
                        onDeleteContactItem={(idx: number) => onDeleteContactItem('supporters', idx)}
                        onAddContactItem={onAddContactItem('supporters', 'Person')}
                    />
                </Stack>
            ),
            canGoNext: true,
        },
        {
            content: (
                <Stack spacing={4}>
                    <FormSection
                        prompt={getString('Safetyplan_suicide_hotline_title')}
                        subPrompt={getString('Safetyplan_suicide_hotline_phone')}
                        content={<Fragment />}
                    />
                    <ContactListFormSection
                        prompt={getString('Safetyplan_professional_help_title')}
                        subPrompt={getString('Safetyplan_professional_help_description')}
                        contactList={
                            dataState.professionals && dataState.professionals.length > 0
                                ? dataState.professionals
                                : [getEmptyContact('Professional')]
                        }
                        fieldLabels={{
                            name: getString('Safetyplan_clinician_name'),
                            phoneNumber: getString('Safetyplan_phone'),
                            emergencyNumber: getString('Safetyplan_clinician_pager'),
                        }}
                        onContactItemChange={(change: IContact, idx: number) =>
                            onContactItemChange('professionals', idx, change)
                        }
                        onDeleteContactItem={(idx: number) => onDeleteContactItem('professionals', idx)}
                        onAddContactItem={onAddContactItem('professionals', 'Professional')}
                    />
                    <ContactListFormSection
                        prompt={getString('Safetyplan_agency_help_title')}
                        subPrompt={getString('Safetyplan_agency_help_description')}
                        contactList={
                            dataState.urgentServices && dataState.urgentServices.length > 0
                                ? dataState.urgentServices
                                : [getEmptyContact('Service')]
                        }
                        fieldLabels={{
                            name: getString('Safetyplan_local_care_name'),
                            address: getString('Safetyplan_local_care_address'),
                            phoneNumber: getString('Safetyplan_local_care_phone'),
                        }}
                        onContactItemChange={(change: IContact, idx: number) =>
                            onContactItemChange('urgentServices', idx, change)
                        }
                        onDeleteContactItem={(idx: number) => onDeleteContactItem('urgentServices', idx)}
                        onAddContactItem={onAddContactItem('urgentServices', 'Service')}
                    />
                </Stack>
            ),
            canGoNext: true,
        },
        {
            content: (
                <StringListFormSection
                    prompt={getString('Safetyplan_environment_title')}
                    subPrompt={getString('Safetyplan_environment_description')}
                    stringList={
                        dataState.safeEnvironment && dataState.safeEnvironment.length > 0
                            ? dataState.safeEnvironment
                            : ['']
                    }
                    onListItemChange={(change: string, idx: number) => onListItemChange('safeEnvironment', idx, change)}
                    onDeleteListItem={(idx: number) => onDeleteListItem('safeEnvironment', idx)}
                    onAddListItem={onAddListItem('safeEnvironment')}
                />
            ),
            canGoNext: true,
        },
    ];

    return (
        <FormDialog
            title={getString('Safetyplan_title')}
            isOpen={true}
            canClose={false}
            pages={pages}
            onNext={handleNext}
            onSubmit={handleSubmit}
            submitToast={getString('Safetyplan_submit_success')}
        />
    );
});

export default SafetyPlanForm;
