import { useLocation } from "react-router";

export const Routes = {
  home: 'home',
  careplan: 'careplan',
  progress: 'progress',
  resources: 'resources',
  valuesInventory: 'inventory',
  worksheets: 'worksheets',
  aboutus: 'aboutus',
  crisisresources: 'crisisresources',
  notifications: 'notifications',
  phqProgress: 'phq',
  gadProgress: 'gad',
  activityProgress: 'activities',
  moodProgress: 'mood',
};

export const Parameters = {
  form: "form",
  activityId: "activity-id",
  activityScheduleId: "activity-schedule-id",
  addSchedule: "add-schedule",
  assessmentId: "assessment-id",
  taskId: "task-id",
  valueId: "value-id",
};

export const ParameterValues = {
  form: {
    moodLog: "log-mood",
    assessmentLog: "log-assessment",
    activityLog: "log-activity",
    addActivity: "add-activity",
    addActivitySchedule: "add-activity-schedule",
    editActivity: "edit-activity",
    editActivitySchedule: "edit-activity-schedule",
    safetyPlan: "safety-plan",
  },
  addSchedule: {
    true: "true",
    false: "false",
  },
};

export const getRouteParameter = (paramName: string) => {
  const { search } = useLocation();
  const query = new URLSearchParams(search);
  return query.get(paramName);
};

export const getCurrentPath = () => {
  const { pathname } = useLocation();

  return pathname.replace("/", "");
};

export const getFormLink = (
  formId: string,
  query?: { [key: string]: string },
) => {
  const { pathname } = window.location;
  const searchParams = new URLSearchParams();
  searchParams.set(Parameters.form, formId);
  if (!!query) {
    Object.entries(query).forEach(([key, value]) => {
      searchParams.set(key, value);
    });
  }

  return {
    pathname: pathname.replace(/\/\//g, "/"),
    search: searchParams.toString() ? `?${searchParams.toString()}` : "",
  };
};

export const getFormPath = (
  formId: string,
  query: { [key: string]: string } = {},
) => {
  const link = getFormLink(formId, query);
  return `${link.pathname}${link.search}`;
};

export const getLevel = (path: string) => {
  return path.split("/").length;
};

export const getResourceLink = (filename: string) => {
  return `/resources/${filename}`;
};
