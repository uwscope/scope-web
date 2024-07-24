import React, { FunctionComponent } from "react";

import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import AssignmentTurnedInOutlinedIcon from "@mui/icons-material/AssignmentTurnedInOutlined";
import {
  Grid,
  SxProps,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { compareDesc, format } from "date-fns";
import { observer } from "mobx-react-lite";
import { IActivity, IValue } from "shared/types";
import ActionPanel, { IActionButton } from "src/components/common/ActionPanel";
import { getString } from "src/services/strings";
import { usePatient, useStores } from "src/stores/stores";

export const ValuesInventory: FunctionComponent = observer(() => {
  const rootStore = useStores();
  const currentPatient = usePatient();
  // const { lifeAreas } = rootStore.appContentConfig;
  const { activities, values, valuesInventory } = currentPatient;
  const { assigned, assignedDateTime } = valuesInventory;

  var dateStrings: string[] = [];
  if (assigned && !!assignedDateTime) {
    dateStrings.push(
      `${getString("patient_values_inventory_assigned_date")} ${format(assignedDateTime, "MM/dd/yyyy")}`,
    );
  }

  let mostRecentlyEditedActivity: IActivity | undefined;
  let mostRecentlyEditedValue: IValue | undefined;
  if (activities.length > 0) {
    mostRecentlyEditedActivity =
      !!currentPatient.activitiesSortedByDateAndTimeDescending &&
      currentPatient.activitiesSortedByDateAndTimeDescending[0];
  }
  if (values.length > 0) {
    mostRecentlyEditedValue =
      !!currentPatient.valuesSortedByDateAndTimeDescending &&
      currentPatient.valuesSortedByDateAndTimeDescending[0];
  }

  const valuesInventoryActivityDateHeader = getString(
    "patient_values_inventory_activity_date_header",
  );
  const dateFormat = "MM/dd/yyyy";
  dateStrings.push(
    !!mostRecentlyEditedActivity && !!mostRecentlyEditedValue
      ? `${valuesInventoryActivityDateHeader} ${format(
          compareDesc(
            mostRecentlyEditedActivity.editedDateTime,
            mostRecentlyEditedValue.editedDateTime,
          ) < 0
            ? mostRecentlyEditedActivity.editedDateTime
            : mostRecentlyEditedValue.editedDateTime,
          dateFormat,
        )}`
      : !!mostRecentlyEditedActivity
        ? `${valuesInventoryActivityDateHeader} ${format(
            mostRecentlyEditedActivity.editedDateTime,
            dateFormat,
          )}`
        : !!mostRecentlyEditedValue
          ? `${valuesInventoryActivityDateHeader} ${format(
              mostRecentlyEditedValue.editedDateTime,
              dateFormat,
            )}`
          : "",
  );

  const valuesWithoutActivity = currentPatient.getValuesWithoutActivity();

  const activitiesAndValuesWithoutActivity = activities.concat(
    valuesWithoutActivity || [],
  );

  const compareActivitiesAndValuesWithoutActivity = (
    activityOrValueWithoutActivityA: IActivity | IValue,
    activityOrValueWithoutActivityB: IActivity | IValue,
  ) => {
    let compare = 0;

    const activityA =
      "activityId" in activityOrValueWithoutActivityA &&
      !!activityOrValueWithoutActivityA.activityId
        ? activityOrValueWithoutActivityA
        : undefined;

    const activityB =
      "activityId" in activityOrValueWithoutActivityB &&
      !!activityOrValueWithoutActivityB.activityId
        ? activityOrValueWithoutActivityB
        : undefined;

    const valueA = !!activityOrValueWithoutActivityA.valueId
      ? currentPatient.getValueById(activityOrValueWithoutActivityA.valueId)
      : undefined;
    const valueB = !!activityOrValueWithoutActivityB.valueId
      ? currentPatient.getValueById(activityOrValueWithoutActivityB.valueId)
      : undefined;

    console.assert(
      !((!activityA && !valueA) || (!activityB && !valueB)),
      `Document without activity or value: ${activityOrValueWithoutActivityA} ${activityOrValueWithoutActivityB}`,
    );

    if (!!valueA) {
      if (!!activityA) {
        // "Activities with a Value" sort before "Activities without a Value" and "Values without an Activity".
        if ((!!activityB && !valueB) || (!!valueB && !activityB)) {
          compare = -1;
        } else if (!!valueB && !!activityB) {
          compare = 0;
        }
      } else {
        // "Values without an Activity" sort before "Activities without a Value".
        if (!!activityB && !valueB) {
          compare = -1;
        } else if (!!valueB && !activityB) {
          compare = 0;
        }
        // "Values without an Activity" sort after "Activities with a Value".
        else {
          compare = 1;
        }
      }
    } else {
      if (!!activityA) {
        // "Activities without a Value" sort after "Values without an Activity" and "Values with an Activity".
        if (!!valueB) {
          compare = 1;
        } else if (!valueB && !!activityB) {
          compare = 0;
        }
      }
    }

    if (compare === 0) {
      // Sort by life area sort key
      if (!!valueA && !!valueB) {
        const lifeAreaContentA = rootStore.getLifeAreaContent(
          valueA.lifeAreaId,
        );
        const lifeAreaContentB = rootStore.getLifeAreaContent(
          valueB.lifeAreaId,
        );

        if (!!lifeAreaContentA && !!lifeAreaContentB) {
          compare = lifeAreaContentA.sortKey - lifeAreaContentB.sortKey;
        }
      }
    }

    if (compare === 0) {
      // Sort by value name
      if (!!valueA && !!valueB) {
        compare = valueA.name.localeCompare(valueB.name, undefined, {
          sensitivity: "base",
        });
      }
    }

    if (compare === 0) {
      // Sort by activity name, which is unique
      if (!!activityA && !!activityB) {
        compare = activityA.name.localeCompare(activityB.name, undefined, {
          sensitivity: "base",
        });
      }
    }

    return compare;
  };

  const sortedActivitiesAndValuesWithoutActivity =
    activitiesAndValuesWithoutActivity
      .slice()
      .sort(compareActivitiesAndValuesWithoutActivity);

  const getTableRowSxProps = (activityOrValue: IActivity | IValue): SxProps => {
    if ("activityId" in activityOrValue && !!activityOrValue.activityId) {
      const data = currentPatient.getRecentActivityById(
        activityOrValue.activityId,
      );
      if (!!data) {
        return { backgroundColor: "rgba(197, 202, 233, 1)" };
      }
    } else if (!!activityOrValue.valueId) {
      const data = currentPatient.getRecentValueById(activityOrValue.valueId);
      if (!!data) {
        return { backgroundColor: "rgba(197, 202, 233, 1)" };
      }
    }
    return {};
  };

  return (
    <ActionPanel
      id={getString("patient_detail_subsection_values_inventory_hash")}
      title={getString("patient_detail_subsection_values_inventory_title")}
      inlineTitle={dateStrings.join(", ")}
      loading={
        currentPatient?.loadPatientState.pending ||
        currentPatient?.loadValuesInventoryState.pending
      }
      error={currentPatient?.loadValuesInventoryState.error}
      actionButtons={[
        {
          icon: assigned ? (
            <AssignmentTurnedInOutlinedIcon />
          ) : (
            <AssignmentOutlinedIcon />
          ),
          text: assigned
            ? getString("patient_values_inventory_assigned_button")
            : getString("patient_values_inventory_assign_button"),
          onClick: () => currentPatient?.assignValuesInventory(),
        } as IActionButton,
      ]}
    >
      <Grid container spacing={2} alignItems="stretch">
        {activities.length == 0 ? (
          <Grid item xs={12}>
            <Typography>
              {getString("patient_values_inventory_empty")}
            </Typography>
          </Grid>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    {getString(
                      "patient_values_inventory_activity_lifearea_header",
                    )}
                  </TableCell>
                  <TableCell>
                    {getString(
                      "patient_values_inventory_activity_value_header",
                    )}
                  </TableCell>
                  <TableCell>
                    {getString("patient_values_inventory_activity_name_header")}
                  </TableCell>
                  <TableCell>
                    {getString(
                      "patient_values_inventory_activity_enjoyment_header",
                    )}
                  </TableCell>
                  <TableCell>
                    {getString(
                      "patient_values_inventory_activity_importance_header",
                    )}
                  </TableCell>
                  <TableCell>
                    {getString("patient_values_inventory_activity_date_header")}
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sortedActivitiesAndValuesWithoutActivity.map(
                  (activityOrValue, idx) => {
                    const value = currentPatient.getValueById(
                      activityOrValue.valueId as string,
                    );

                    const activity = currentPatient.getActivityById(
                      activityOrValue.activityId as string,
                    );

                    const lifeAreaContent = rootStore.getLifeAreaContent(
                      value?.lifeAreaId as string,
                    );

                    return (
                      <TableRow
                        key={idx}
                        sx={getTableRowSxProps(activityOrValue)}
                      >
                        <TableCell component="th" scope="row">
                          {!!lifeAreaContent ? lifeAreaContent.name : "-"}
                        </TableCell>
                        <TableCell>{!!value ? value.name : "-"}</TableCell>
                        <TableCell>
                          {!!activity ? activity.name : "--"}
                        </TableCell>
                        <TableCell>
                          {activityOrValue.enjoyment != null
                            ? activityOrValue.enjoyment
                            : "-"}
                        </TableCell>
                        <TableCell>
                          {activityOrValue.importance != null
                            ? activityOrValue.importance
                            : "-"}
                        </TableCell>
                        <TableCell>
                          {format(activityOrValue.editedDateTime, "MM/dd/yyyy")}
                        </TableCell>
                      </TableRow>
                    );
                  },
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Grid>
    </ActionPanel>
  );
});

export default ValuesInventory;
