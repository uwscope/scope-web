import React, { FunctionComponent } from "react";

import AssignmentIcon from "@mui/icons-material/Assignment";
import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import {
  Grid,
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
import { IActivity } from "shared/types";
import ActionPanel, { IActionButton } from "src/components/common/ActionPanel";
import { getString } from "src/services/strings";
import { usePatient, useStores } from "src/stores/stores";

export const ValuesInventory: FunctionComponent = observer(() => {
  const rootStore = useStores();
  const currentPatient = usePatient();
  // const { lifeAreas } = rootStore.appContentConfig;
  const { activities, valuesInventory } = currentPatient;
  const { assigned, assignedDateTime } = valuesInventory;

  var dateStrings: string[] = [];
  if (assigned && !!assignedDateTime) {
    dateStrings.push(
      `${getString("patient_values_inventory_assigned_date")} ${format(assignedDateTime, "MM/dd/yyyy")}`,
    );
  }
  if (activities.length > 0) {
    const mostRecentlyEditedActivityWithValue = activities
      .filter((activity) => {
        return !!activity.valueId;
      })
      .reduce((mostRecent: IActivity | undefined, current: IActivity) => {
        if (!mostRecent) {
          return current;
        }

        return compareDesc(mostRecent.editedDateTime, current.editedDateTime) <
          0
          ? mostRecent
          : current;
      }, undefined);

    if (mostRecentlyEditedActivityWithValue) {
      dateStrings.push(
        `${getString("patient_values_inventory_activity_date_header")} ${format(
          mostRecentlyEditedActivityWithValue.editedDateTime as Date,
          "MM/dd/yyyy",
        )}`,
      );
    }
  }

  const sortedActivities = ((): IActivity[] => {
    return activities.slice().sort((activityA, activityB) => {
      let compare = 0;

      const valueA = !!activityA.valueId
        ? currentPatient.getValueById(activityA.valueId)
        : undefined;
      const valueB = !!activityB.valueId
        ? currentPatient.getValueById(activityB.valueId)
        : undefined;

      if (compare == 0) {
        // Activities without a value sort after activities with a value
        if (!!valueA) {
          compare = !!valueB ? 0 : -1;
        } else {
          compare = !!valueB ? 1 : 0;
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
        compare = activityA.name.localeCompare(activityB.name, undefined, {
          sensitivity: "base",
        });
      }

      return compare;
    });
  })();

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
          icon: assigned ? <AssignmentTurnedInIcon /> : <AssignmentIcon />,
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
                {sortedActivities.map((activity, idx) => {
                  const value = currentPatient.getValueById(
                    activity.valueId as string,
                  );
                  const lifeAreaContent = rootStore.getLifeAreaContent(
                    value?.lifeAreaId as string,
                  );

                  return (
                    <TableRow key={idx}>
                      <TableCell component="th" scope="row">
                        {!!lifeAreaContent ? lifeAreaContent.name : "-"}
                      </TableCell>
                      <TableCell>{!!value ? value.name : "-"}</TableCell>
                      <TableCell>{activity.name}</TableCell>
                      <TableCell>
                        {activity.enjoyment != null ? activity.enjoyment : "-"}
                      </TableCell>
                      <TableCell>
                        {activity.importance != null
                          ? activity.importance
                          : "-"}
                      </TableCell>
                      <TableCell>
                        {format(activity.editedDateTime, "MM/dd/yyyy")}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Grid>
    </ActionPanel>
  );
});

export default ValuesInventory;
