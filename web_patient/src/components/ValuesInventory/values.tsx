import EmojiNatureIcon from '@material-ui/icons/EmojiNature';
import HelpIcon from '@material-ui/icons/Help';
import ListAltIcon from '@material-ui/icons/ListAlt';
import SpaIcon from '@material-ui/icons/Spa';
import SupervisorAccountIcon from '@material-ui/icons/SupervisorAccount';
import WorkIcon from '@material-ui/icons/Work';
import React from 'react';
import { getString } from 'src/services/strings';

export const getLifeAreaIcon = (lifeareaId: string) => {
    switch (lifeareaId) {
        case 'relationship':
            return <SupervisorAccountIcon fontSize="large" />;
        case 'education':
            return <WorkIcon fontSize="large" />;
        case 'recreation':
            return <EmojiNatureIcon fontSize="large" />;
        case 'mindbody':
            return <SpaIcon fontSize="large" />;
        case 'responsibilities':
            return <ListAltIcon fontSize="large" />;
        default:
            return <HelpIcon fontSize="large" />;
    }
};

export const getValuesString = (valueCount: number) => {
    return `${valueCount} ${
        valueCount == 1 ? getString('Values_inventory_value_singular') : getString('Values_inventory_value_plural')
    }`;
};

export const getActivitiesString = (activityCount: number) => {
    return `${activityCount} ${
        activityCount == 1
            ? getString('Values_inventory_activity_singular')
            : getString('Values_inventory_activity_plural')
    }`;
};

export const getActivityDetailText = (enjoyment: number, importance: number) => {
    return `${getString('Values_inventory_value_item_activities_enjoyment')}: ${enjoyment} / ${getString(
        'Values_inventory_value_item_activities_importance'
    )}: ${importance}`;
};
