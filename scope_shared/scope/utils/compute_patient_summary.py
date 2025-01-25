"""
Used in server_flask/blueprints/patient/summary.py

Placed in utils so that reminder calculations can also use.
"""

import datetime
from typing import List

import scope.database.date_utils as date_utils


def compute_patient_summary(
    activity_documents: List[dict],
    safety_plan_document: dict,
    scheduled_assessment_documents: List[dict],
    values_inventory_document: dict,
) -> dict:
    """
    {
        # assignedValuesInventory <- True, if assigned is True, and
        editedDateTime of an activity with value < assignedDateTime
        assignedValuesInventory: boolean;

        # assignedSafetyPlan <- True, if assigned is True, and lastUpdatedDateTime < assignedDateTime in safety plan singleton
        assignedSafetyPlan: boolean;

        # scheduledAssessments that are not completed and dueDate <= today.
        assignedScheduledAssessments: IScheduledAssessment[];
    }
    """
    # assignedValuesInventory
    assigned_values_inventory: bool = values_inventory_document["assigned"]
    if assigned_values_inventory:
        assigned_values_inventory_datetime = date_utils.parse_datetime(
            values_inventory_document["assignedDateTime"]
        )

        for activity_current in activity_documents:
            # If an activity with value was created after the assignment, the assignment is resolved
            if (
                "valueId" in activity_current
                and date_utils.parse_datetime(activity_current["editedDateTime"])
                > assigned_values_inventory_datetime
            ):
                assigned_values_inventory = False
                break

    # assignedSafetyPlan
    assigned_safety_plan: bool = safety_plan_document["assigned"]
    if assigned_safety_plan:
        if "lastUpdatedDateTime" in safety_plan_document:
            assigned_safety_plan = date_utils.parse_datetime(
                safety_plan_document["lastUpdatedDateTime"]
            ) < date_utils.parse_datetime(safety_plan_document["assignedDateTime"])

    # assignedScheduledAssessments
    assigned_scheduled_assessments = list(
        filter(
            lambda scheduled_assessment_current: (
                (not scheduled_assessment_current["completed"])
                and (
                    date_utils.parse_date(scheduled_assessment_current["dueDate"])
                    <= datetime.date.today()
                )
            ),
            scheduled_assessment_documents,
        )
    )

    return {
        "assignedValuesInventory": assigned_values_inventory,
        "assignedSafetyPlan": assigned_safety_plan,
        "assignedScheduledAssessments": assigned_scheduled_assessments,
    }
