import React, { Fragment, FunctionComponent, ReactNode } from "react";

import AddIcon from "@mui/icons-material/Add";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import {
  Box,
  Button,
  // FormControl,
  Divider,
  Grid,
  IconButton,
  // InputLabel,
  List,
  ListItem,
  ListItemSecondaryAction,
  Menu,
  MenuItem,
  // Select,
  // SelectChangeEvent,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import withTheme from "@mui/styles/withTheme";
import { random } from "lodash";
import { action, runInAction } from "mobx";
import { observer, useLocalObservable } from "mobx-react";
import { useNavigate, useParams } from "react-router";
import { Link } from "react-router-dom";
import { LifeAreaIdOther } from "shared/enums";
import {
  IActivity,
  ILifeAreaContent,
  ILifeAreaValue,
  IValue,
} from "shared/types";
import ContentLoader from "src/components/Chrome/ContentLoader";
import { DetailPage } from "src/components/common/DetailPage";
import StatefulDialog from "src/components/common/StatefulDialog";
import FormSection, {
  HeaderText,
  HelperText,
  SubHeaderText,
} from "src/components/Forms/FormSection";
import {
  getFormLink,
  getFormPath,
  Parameters,
  ParameterValues,
} from "src/services/routes";
import { getString } from "src/services/strings";
import { useStores } from "src/stores/stores";
import styled from "styled-components";

const CompactList = withTheme(
  styled(List)((props) => ({
    marginLeft: props.theme.spacing(-2),
    marginRight: props.theme.spacing(-2),
    paddingBottom: props.theme.spacing(0),
    paddingTop: props.theme.spacing(0),
    "li>.MuiListItemIcon-root": {
      minWidth: 36,
    },
  })),
);

interface IActivitiesSection {
  activities: IActivity[];
  valueId?: string;
  handleMoreClickActivity: (
    activity: IActivity,
    event: React.MouseEvent<HTMLElement>,
  ) => void;
}

const ActivitiesSection: FunctionComponent<IActivitiesSection> = (
  props: IActivitiesSection,
) => {
  const rootStore = useStores();
  const { patientStore } = rootStore;

  const renderActivityDetail = (activity: IActivity): ReactNode => {
    return (
      <Stack spacing={1}>
        {(() => {
          const renderEnjoyment =
            activity.enjoyment != null ? activity.enjoyment : -1;
          const renderImportance =
            activity.importance != null ? activity.importance : -1;

          return (
            (renderEnjoyment >= 0 || renderImportance >= 0) && (
              <HelperText>
                {renderEnjoyment >= 0 && (
                  <Fragment>
                    {getString("values_inventory_value_activity_enjoyment")}{" "}
                    {activity.enjoyment}
                  </Fragment>
                )}
                {renderEnjoyment >= 0 && renderImportance >= 0 && " / "}
                {renderImportance >= 0 && (
                  <Fragment>
                    {getString("values_inventory_value_activity_importance")}{" "}
                    {activity.importance}
                  </Fragment>
                )}
              </HelperText>
            )
          );
        })()}
        {!!activity.activityId &&
          (() => {
            const activitySchedules =
              patientStore.getActivitySchedulesByActivityId(
                activity.activityId,
              );
            const repeatActivitySchedules = activitySchedules.filter((as) => {
              return as.hasRepetition;
            });

            return (
              <Fragment>
                {activitySchedules.length == 0 && (
                  <HelperText>No Schedule</HelperText>
                )}
                {activitySchedules.length == 1 &&
                  repeatActivitySchedules.length == 0 && (
                    <HelperText>{`1 Schedule`}</HelperText>
                  )}
                {activitySchedules.length == 1 &&
                  repeatActivitySchedules.length == 1 && (
                    <HelperText>{`1 Schedule, with Repeat`}</HelperText>
                  )}
                {activitySchedules.length > 1 &&
                  repeatActivitySchedules.length == 0 && (
                    <HelperText>{`${activitySchedules.length} Schedules`}</HelperText>
                  )}
                {activitySchedules.length > 1 &&
                  repeatActivitySchedules.length > 0 && (
                    <HelperText>{`${activitySchedules.length} Schedules; ${repeatActivitySchedules.length} Repeat`}</HelperText>
                  )}
              </Fragment>
            );
          })()}
      </Stack>
    );
  };

  const renderActivities = (activities: IActivity[]): ReactNode => {
    const sortedActivities = activities
      .slice()
      .sort((a, b) =>
        a.name.toLocaleLowerCase().localeCompare(b.name.toLocaleLowerCase()),
      );

    return (
      <CompactList>
        {sortedActivities.map((activity, idx) => (
          <Fragment key={activity.activityId as string}>
            <ListItem
              alignItems="flex-start"
              button
              component={Link}
              to={getFormLink(ParameterValues.form.editActivity, {
                [Parameters.activityId as string]:
                  activity.activityId as string,
              })}
            >
              <Grid
                container
                direction="row"
                alignItems="flex-start"
                flexWrap="nowrap"
              >
                <Grid item flexGrow={1} overflow="hidden">
                  <Stack spacing={0}>
                    <Typography variant="body1" noWrap>
                      {activity.name}
                    </Typography>
                    {renderActivityDetail(activity)}
                  </Stack>
                </Grid>
              </Grid>
              <ListItemSecondaryAction
                sx={{ alignItems: "flex-start", height: "100%" }}
              >
                <IconButton
                  edge="end"
                  aria-label="more"
                  onClick={(e) => props.handleMoreClickActivity(activity, e)}
                  size="large"
                >
                  <MoreVertIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            {idx < sortedActivities.length - 1 && <Divider variant="middle" />}
          </Fragment>
        ))}
      </CompactList>
    );
  };

  return (
    <Stack spacing={1}>
      {renderActivities(props.activities)}
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Button
          variant="contained"
          color="primary"
          size="small"
          startIcon={<AddIcon />}
          component={Link}
          to={getFormLink(
            ParameterValues.form.addActivity,
            (() => {
              if (props.valueId) {
                return {
                  [Parameters.valueId]: props.valueId as string,
                  [Parameters.addSchedule]: ParameterValues.addSchedule.false,
                };
              } else {
                return {
                  [Parameters.addSchedule]: ParameterValues.addSchedule.false,
                };
              }
            })(),
          )}
        >
          {getString("values_inventory_add_activity")}
        </Button>
      </Box>
    </Stack>
  );
};

interface IValueEditFormSection {
  error: boolean;
  loading: boolean;
  value: IValue;
  activityExamples: string[];
  handleMoreClickValue: (
    value: IValue,
    event: React.MouseEvent<HTMLElement>,
  ) => void;
  handleMoreClickActivity: (
    activity: IActivity,
    event: React.MouseEvent<HTMLElement>,
  ) => void;
}

const ValueEditFormSection = observer((props: IValueEditFormSection) => {
  const {
    // error,
    // loading,
    value,
    // activityExamples,
    handleMoreClickValue,
    handleMoreClickActivity,
  } = props;

  const rootStore = useStores();
  const { patientStore } = rootStore;

  const valueActivities = patientStore.getActivitiesByValueId(
    value.valueId as string,
  );

  return (
    <Stack spacing={0}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <SubHeaderText>{value.name}</SubHeaderText>
        <IconButton
          edge="end"
          aria-label="more"
          onClick={(e) => handleMoreClickValue(value, e)}
          size="large"
        >
          <MoreVertIcon />
        </IconButton>
      </Stack>
      <Box sx={{ marginLeft: 2, marginTop: -1 }}>
        <ActivitiesSection
          activities={valueActivities}
          valueId={value.valueId}
          handleMoreClickActivity={handleMoreClickActivity}
        />
      </Box>
    </Stack>
  );
});

export const AddEditValueDialog: FunctionComponent<{
  open: boolean;
  isEdit: boolean;
  lifeArea: string;
  value: string;
  examples: string[];
  error?: boolean;
  loading?: boolean;
  nameIsUnique: () => boolean;
  handleChange: (change: string) => void;
  handleCancel: () => void;
  handleSave: () => void;
}> = (props) => {
  const {
    open,
    isEdit,
    lifeArea,
    value,
    examples,
    error,
    loading,
    nameIsUnique,
    handleCancel,
    handleChange,
    handleSave,
  } = props;

  return (
    <StatefulDialog
      open={open}
      error={error}
      loading={loading}
      title={
        isEdit
          ? getString("Values_inventory_dialog_edit_value")
          : getString("Values_inventory_dialog_add_value")
      }
      content={
        <Stack spacing={2}>
          <SubHeaderText>{lifeArea}</SubHeaderText>
          <Examples
            title={getString("values_inventory_values_example_title")}
            examples={examples}
          />
          <TextField
            autoFocus
            margin="dense"
            variant="outlined"
            label={getString("Values_inventory_dialog_add_value_label")}
            value={value}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
              handleChange(event.target.value)
            }
            fullWidth
            error={!nameIsUnique()}
            helperText={
              !nameIsUnique() &&
              getString(
                "Values_inventory_dialog_value_name_validation_not_unique",
              )
            }
          />
        </Stack>
      }
      handleCancel={handleCancel}
      //handleDelete={handleDelete}
      handleSave={handleSave}
      disableSave={!value || !nameIsUnique()}
    />
  );
};

const Examples: FunctionComponent<{ title: string; examples: string[] }> = (
  props,
) => {
  const { title, examples } = props;
  return (
    <HelperText>
      <Stack spacing={1}>
        <div>{`${title}:`}</div>
        {examples.map((ex, idx) => (
          <div key={idx}>{`${idx + 1}. ${ex}`}</div>
        ))}
      </Stack>
    </HelperText>
  );
};

const NestedExamples: FunctionComponent<{
  title: string;
  examples: ILifeAreaValue[];
}> = (props) => {
  const { title, examples } = props;
  return (
    <HelperText>
      <Stack spacing={1}>
        <div>{`${title}:`}</div>
        {examples.map((ex, valueIdx) => (
          <React.Fragment>
            <div key={`value` + valueIdx}>{`${valueIdx + 1}. ${ex.name}`}</div>
            <ol type="i">
              {ex.activities.map((activityEx, activityIdx) => (
                <li key={`activity` + activityIdx}>{activityEx.name}</li>
              ))}
            </ol>
          </React.Fragment>
        ))}
      </Stack>
    </HelperText>
  );
};

export const LifeAreaDetail: FunctionComponent = observer(() => {
  const { lifeAreaId } = useParams<{ lifeAreaId: string }>();
  if (!lifeAreaId) {
    return null;
  }
  const rootStore = useStores();
  const { patientStore } = rootStore;
  const lifeAreaContent = rootStore.getLifeAreaContent(lifeAreaId);
  if (!lifeAreaContent && lifeAreaId != LifeAreaIdOther) {
    return null;
  }

  interface IViewStateModeNone {
    mode: "none";
  }
  interface IViewStateModeAdd {
    mode: "add";
  }
  interface IViewStateModeEdit {
    mode: "edit";
    editValue: IValue;
  }
  interface IViewState {
    openAddEditValue: boolean;

    name: string;
    modeState: IViewStateModeNone | IViewStateModeAdd | IViewStateModeEdit;

    deleteValueConfirmOpen: boolean;
    moreTargetValueEl: (EventTarget & HTMLElement) | undefined;
    selectedValue: IValue | undefined;

    deleteActivityConfirmOpen: boolean;
    moreTargetActivityEl: (EventTarget & HTMLElement) | undefined;
    selectedActivity: IActivity | undefined;
  }

  const viewState = useLocalObservable<IViewState>(() => ({
    openAddEditValue: false,
    name: "",
    modeState: {
      mode: "none",
    },
    deleteValueConfirmOpen: false,
    moreTargetValueEl: undefined,
    selectedValue: undefined,
    deleteActivityConfirmOpen: false,
    moreTargetActivityEl: undefined,
    selectedActivity: undefined,
  }));

  const navigate = useNavigate();

  const handleGoBack = action(() => {
    navigate(-1);
  });

  const handleMoreClickValue = action(
    (value: IValue, event: React.MouseEvent<HTMLElement>) => {
      viewState.selectedValue = value;
      viewState.moreTargetValueEl = event.currentTarget;
    },
  );

  const handleMoreCloseValue = action(() => {
    viewState.selectedValue = undefined;
    viewState.moreTargetValueEl = undefined;
  });

  const handleAddValue = action(() => {
    // Open AddEditValueDialog to Add value.

    viewState.openAddEditValue = true;
    viewState.name = "";
    viewState.modeState = {
      mode: "add",
    };
  });

  const handleEditValue = action(() => {
    // Open AddEditValueDialog to Edit value.

    // valueId is sufficient for creating this interface callback,
    // but upon activation our viewState takes a copy of the value that is being edited.

    const value = viewState.selectedValue;
    console.assert(value, `Value to edit not found: ${value?.valueId}`);

    if (value) {
      viewState.moreTargetValueEl = undefined;
      viewState.openAddEditValue = true;
      viewState.name = value.name;
      viewState.modeState = {
        mode: "edit",
        editValue: value,
      };
    }
  });

  const handleCancelValue = action(() => {
    viewState.openAddEditValue = false;
  });

  const handleChangeValue = action((change: string) => {
    viewState.name = change;
  });

  const handleDeleteValue = action(() => {
    // Remove the popup menu
    // Do not yet clear the selected value because it's needed by dialog handlers
    viewState.moreTargetValueEl = undefined;

    // Open delete confirmation dialog
    viewState.deleteValueConfirmOpen = true;
  });

  const handleDeleteValueConfirmDelete = action(async () => {
    const value = viewState.selectedValue;

    if (!!value) {
      await patientStore.deleteValue(value);
    }
    runInAction(() => {
      viewState.deleteValueConfirmOpen = false;
      viewState.selectedValue = undefined;
    });
  });

  const handleDeleteValueConfirmCancel = action(() => {
    viewState.deleteValueConfirmOpen = false;
    viewState.selectedValue = undefined;
  });

  const handleSaveValue = action(async () => {
    const valueName = viewState.name.trim();
    if (viewState.modeState.mode == "add") {
      // TODO Activity Refactor: check that our 'add' is valid
      // Defer until this is more cleanly-organized
      // is a unique name

      await patientStore.addValue({
        name: valueName,
        lifeAreaId: lifeAreaId,
        editedDateTime: new Date(),
      });
    } else if (viewState.modeState.mode == "edit") {
      // TODO Activity Refactor: check that our 'edit' is valid
      // Defer until this is more cleanly-organized
      // is a unique name
      // the value changed?

      await patientStore.updateValue({
        ...viewState.modeState.editValue,
        name: valueName,
        editedDateTime: new Date(),
      });
    }

    runInAction(() => {
      if (!patientStore.loadValuesState.error) {
        viewState.openAddEditValue = false;
      }
    });
  });

  const handleMoreClickActivity = action(
    (activity: IActivity, event: React.MouseEvent<HTMLElement>) => {
      viewState.selectedActivity = activity;
      viewState.moreTargetActivityEl = event.currentTarget;
    },
  );

  const handleMoreCloseActivity = action(() => {
    viewState.selectedActivity = undefined;
    viewState.moreTargetActivityEl = undefined;
  });

  const handleEditActivity = action(() => {
    const activity = viewState.selectedActivity;

    // Remove the popup menu
    viewState.moreTargetActivityEl = undefined;

    navigate(
      getFormPath(ParameterValues.form.editActivity, {
        [Parameters.activityId as string]: activity?.activityId as string,
      }),
    );
  });

  const handleDeleteActivity = action(() => {
    // Remove the popup menu
    // Do not yet clear the selected activity because it's needed by dialog handlers
    viewState.moreTargetActivityEl = undefined;

    // Open delete confirmation dialog
    viewState.deleteActivityConfirmOpen = true;
  });

  const handleDeleteActivityConfirmDelete = action(async () => {
    const activity = viewState.selectedActivity;

    if (!!activity) {
      await patientStore.deleteActivity(activity);
    }
    runInAction(() => {
      viewState.deleteActivityConfirmOpen = false;
      viewState.selectedActivity = undefined;
    });
  });

  const handleDeleteActivityConfirmCancel = action(() => {
    viewState.deleteActivityConfirmOpen = false;
    viewState.selectedActivity = undefined;
  });

  const handleAddActivitySchedule = action(() => {
    const activity = viewState.selectedActivity;

    // Remove the popup menu
    viewState.moreTargetActivityEl = undefined;

    navigate(
      getFormPath(ParameterValues.form.addActivitySchedule, {
        [Parameters.activityId as string]: activity?.activityId as string,
      }),
    );
  });

  const valueValidateName = () => {
    //
    // This function effectively duplicates valueValidateName in AddEditActivityForm
    //
    // They should be consolidated for avoiding confusion in maintenance
    //

    // Value name must be unique within the life area, accounting for case-insensitive comparisons
    const nameIsUnique: boolean =
      patientStore
        .getValuesByLifeAreaId(lifeAreaId)
        .filter((value: IValue): boolean => {
          // In case of edit, do not validate against the value being edited
          if (viewState.modeState.mode == "edit") {
            return viewState.modeState.editValue?.valueId != value.valueId;
          }

          return true;
        })
        .findIndex((value: IValue): boolean => {
          // Search for a case-insensitive match, trimming any whitespace
          return (
            value.name.toLocaleLowerCase().trim() ==
            viewState.name.toLocaleLowerCase().trim()
          );
        }) < 0;

    return nameIsUnique;
  };

  const displayLifeAreaName: string = (() => {
    if (lifeAreaId == LifeAreaIdOther) {
      return getString("values_inventory_life_area_other_activities_name");
    } else {
      return (lifeAreaContent as ILifeAreaContent).name;
    }
  })();
  const displayValueExamples: string[] = (() => {
    if (lifeAreaContent) {
      return lifeAreaContent.examples.map((e) => e.name);
    } else {
      return [];
    }
  })();

  const displayValueAndActivityExamples: ILifeAreaValue[] = (() => {
    if (lifeAreaContent) {
      return lifeAreaContent.examples;
    } else {
      return [];
    }
  })();

  const displayActivityExamples: string[] = (() => {
    if (lifeAreaContent) {
      return lifeAreaContent?.examples[
        random(lifeAreaContent.examples.length - 1, false)
      ].activities.map((a) => a.name);
    } else {
      return [];
    }
  })();

  return (
    <DetailPage title={displayLifeAreaName} onBack={handleGoBack}>
      <ContentLoader
        state={patientStore.loadValuesInventoryState}
        name="values & activities inventory"
        onRetry={() => patientStore.loadValuesInventory()}
      >
        <Stack spacing={6}>
          {lifeAreaId == LifeAreaIdOther ? (
            <FormSection
              prompt={getString(
                "values_inventory_life_area_other_activities_title",
              )}
              subPrompt={getString(
                "values_inventory_life_area_other_activities_subprompt",
              )}
              content={
                <ActivitiesSection
                  activities={patientStore.getActivitiesWithoutValueId()}
                  handleMoreClickActivity={handleMoreClickActivity}
                />
              }
            />
          ) : (
            <Fragment>
              {patientStore.getValuesByLifeAreaId(lifeAreaId).length == 0 ? (
                <FormSection
                  prompt={getString("values_inventory_values_identify_title")}
                  subPrompt={getString(
                    "values_inventory_values_empty_subprompt",
                  )}
                  content={
                    <NestedExamples
                      title={getString(
                        "values_inventory_values_activity_example_title",
                      )}
                      examples={displayValueAndActivityExamples}
                    />
                  }
                />
              ) : (
                <Stack spacing={0}>
                  <HeaderText>
                    {getString(
                      "values_inventory_values_identify_existing_title",
                    )}
                  </HeaderText>
                  <Stack spacing={4}>
                    {patientStore
                      .getValuesByLifeAreaId(lifeAreaId)
                      .map((value) => {
                        return (
                          <Fragment key={value.valueId}>
                            <ValueEditFormSection
                              error={
                                patientStore.loadValuesInventoryState.error
                              }
                              loading={
                                patientStore.loadValuesInventoryState.pending
                              }
                              value={value}
                              activityExamples={displayActivityExamples}
                              handleMoreClickValue={handleMoreClickValue}
                              handleMoreClickActivity={handleMoreClickActivity}
                            />
                          </Fragment>
                        );
                      })}
                  </Stack>
                </Stack>
              )}
              <FormSection
                prompt={
                  patientStore.getValuesByLifeAreaId(lifeAreaId).length > 0
                    ? getString("values_inventory_values_identify_more_title")
                    : ""
                }
                content={
                  <React.Fragment>
                    <Button
                      sx={{ marginTop: 1, alignSelf: "flex-start" }}
                      variant="contained"
                      color="primary"
                      startIcon={<AddIcon />}
                      onClick={handleAddValue}
                    >
                      {getString("Values_inventory_add_value")}
                    </Button>
                    <Box paddingTop={4}>
                      {patientStore.getValuesByLifeAreaId(lifeAreaId).length >
                      0 ? (
                        <NestedExamples
                          title={getString(
                            "values_inventory_values_activity_example_title",
                          )}
                          examples={displayValueAndActivityExamples}
                        />
                      ) : (
                        ""
                      )}
                    </Box>
                  </React.Fragment>
                }
              />
            </Fragment>
          )}
        </Stack>
        <Menu
          id="value-menu"
          anchorEl={viewState.moreTargetValueEl}
          keepMounted
          open={Boolean(viewState.moreTargetValueEl)}
          onClose={handleMoreCloseValue}
        >
          <MenuItem onClick={handleEditValue}>
            {getString("values_inventory_value_menu_edit")}
          </MenuItem>
          <MenuItem onClick={handleDeleteValue}>
            {getString("values_inventory_value_menu_delete")}
          </MenuItem>
        </Menu>
        <Menu
          id="activity-menu"
          anchorEl={viewState.moreTargetActivityEl}
          keepMounted
          open={Boolean(viewState.moreTargetActivityEl)}
          onClose={handleMoreCloseActivity}
        >
          <MenuItem onClick={handleEditActivity}>
            {getString("menuitem_activity_edit")}
          </MenuItem>
          <MenuItem onClick={handleAddActivitySchedule}>
            {getString("menuitem_activityschedule_add")}
          </MenuItem>
          <MenuItem onClick={handleDeleteActivity}>
            {getString("menuitem_activity_delete")}
          </MenuItem>
        </Menu>
        <AddEditValueDialog
          open={viewState.openAddEditValue}
          isEdit={viewState.modeState.mode == "edit"}
          lifeArea={displayLifeAreaName}
          value={viewState.name}
          examples={displayValueExamples}
          error={patientStore.loadValuesInventoryState.error}
          loading={patientStore.loadValuesInventoryState.pending}
          nameIsUnique={valueValidateName}
          handleCancel={handleCancelValue}
          handleChange={handleChangeValue}
          handleSave={handleSaveValue}
        />
        <StatefulDialog
          open={viewState.deleteValueConfirmOpen}
          title={getString("Form_confirm_delete_value")}
          content={viewState.selectedValue?.name as string}
          handleCancel={handleDeleteValueConfirmCancel}
          handleDelete={handleDeleteValueConfirmDelete}
        />
        <StatefulDialog
          open={viewState.deleteActivityConfirmOpen}
          title={getString("Form_confirm_delete_activity")}
          content={viewState.selectedActivity?.name as string}
          handleCancel={handleDeleteActivityConfirmCancel}
          handleDelete={handleDeleteActivityConfirmDelete}
        />
      </ContentLoader>
    </DetailPage>
  );
});

export default LifeAreaDetail;
