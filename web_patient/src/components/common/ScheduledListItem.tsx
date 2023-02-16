import { ListItem, ListItemIcon, ListItemText, Typography } from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import React, { FunctionComponent } from 'react';
import { IScheduledActivity } from 'shared/types';
import { getTaskItemDueTimeString } from 'src/utils/schedule';
import { useStores } from 'src/stores/stores';

export interface IScheduledListItemProps {
    item: IScheduledActivity;
    onClick?: () => void;
}

export const ScheduledListItem: FunctionComponent<IScheduledListItemProps> = (props) => {
    const { item, onClick } = props;
    const rootStore = useStores();
    const { patientStore } = rootStore;

    const activity = patientStore.getActivityByActivityScheduleId(item.activityScheduleId);

    return (
        <ListItem button onClick={onClick} disabled={item.completed}>
            <ListItemIcon style={{ justifyContent: 'center' }}>
                {item.completed ? <CheckIcon /> : <RadioButtonUncheckedIcon />}
            </ListItemIcon>
            <ListItemText
                primary={<Typography noWrap>{activity?.name}</Typography>}
                secondary={getTaskItemDueTimeString(item, new Date())}
            />
        </ListItem>
    );
};

export default ScheduledListItem;
