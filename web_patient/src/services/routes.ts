import { useLocation } from 'react-router';

export const Routes = {
    home: 'home',
    careplan: 'careplan',
    progress: 'progress',
    profile: 'profile',
    valuesInventory: 'profile/inventory',
    resources: 'profile/resources',
    phqProgress: 'progress/phq',
    gadProgress: 'progress/gad',
    activityProgress: 'progress/activities',
};

export const Parameters = {
    form: 'form',
    activityId: 'activity-id',
    assessmentId: 'assessment-id',
    taskId: 'task-id',
};

export const ParameterValues = {
    form: {
        moodLog: 'log-mood',
        assessmentLog: 'log-assessment',
        activityLog: 'log-activity',
        addActivity: 'add-activity',
        editActivity: 'edit-activity',
    },
};

export const getRouteParameter = (paramName: string) => {
    const { search } = useLocation();
    const query = new URLSearchParams(search);
    return query.get(paramName);
};

export const getCurrentPath = () => {
    const { pathname } = useLocation();

    return pathname.replace('/', '');
};

export const getFormLink = (formId: string, query?: { [key: string]: string }) => {
    const { pathname } = window.location;
    const searchParams = new URLSearchParams();
    searchParams.set(Parameters.form, formId);
    if (!!query) {
        Object.entries(query).forEach(([key, value]) => {
            searchParams.set(key, value);
        });
    }

    return {
        pathname: pathname.replace(/\/\//g, '/'),
        search: searchParams.toString() ? `?${searchParams.toString()}` : '',
    };
};

export const getFormPath = (formId: string, query: { [key: string]: string }) => {
    const link = getFormLink(formId, query);
    return `${link.pathname}${link.search}`;
};

export const getLevel = (path: string) => {
    return path.split('/').length;
};

export const getLifeAreaLink = (lifearea: string) => {
    return {
        pathname: `${Routes.valuesInventory}/${lifearea}`,
        relative: false,
    };
};

export const getResourceLink = (filename: string) => {
    return `/resources/${filename}`;
};
