import EmojiNatureIcon from '@mui/icons-material/EmojiNature';
import HelpIcon from '@mui/icons-material/Help';
import ListAltIcon from '@mui/icons-material/ListAlt';
import SpaIcon from '@mui/icons-material/Spa';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import WorkIcon from '@mui/icons-material/Work';
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

export const getActivityDetailText = (enjoyment: number | undefined, importance: number | undefined) => {
    return `${getString('Values_inventory_value_item_activities_enjoyment')}: ${
        enjoyment != undefined ? enjoyment : -1
    } / ${getString('Values_inventory_value_item_activities_importance')}: ${
        importance != undefined ? importance : -1
    }`;
};
