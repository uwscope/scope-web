"""
Used in server_flask/blueprints/patient/summary.py

Placed in utils so that reminder calculations can also use.
"""
import copy
import datetime
from typing import List

import scope.database.date_utils as date_utils


def compute_patient_summary(
    *,
    activity_documents: List[dict],
    assessment_log_documents: List[dict],
    safety_plan_document: dict,
    scheduled_assessment_documents: List[dict],
    values_inventory_document: dict,
    date_due: datetime.date,
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
    assigned_scheduled_assessments = []

    # identify unique values of assessmentId
    assessment_id_values = set(
        scheduled_assessment_current["assessmentId"]
        for scheduled_assessment_current in scheduled_assessment_documents
    )
    for assessment_id_current in assessment_id_values:
        scheduled_assessment_documents_current = copy.deepcopy(
            scheduled_assessment_documents
        )

        # keep only scheduled assessments of this id
        scheduled_assessment_documents_current = [
            scheduled_assessment_current
            for scheduled_assessment_current in scheduled_assessment_documents_current
            if scheduled_assessment_current["assessmentId"] == assessment_id_current
        ]

        # keep only scheduled assessments that are due
        scheduled_assessment_documents_current = [
            scheduled_assessment_current
            for scheduled_assessment_current in scheduled_assessment_documents_current
            if date_utils.parse_date(scheduled_assessment_current["dueDate"])
            <= date_due
        ]

        # sort by how recently they became due
        scheduled_assessment_documents_current = sorted(
            scheduled_assessment_documents_current,
            key=lambda doc: date_utils.parse_date(doc["dueDate"]),
        )

        # Determine if we possibly have an assessment that is due
        scheduled_assessment_currently_due = None
        if scheduled_assessment_documents_current:
            scheduled_assessment_currently_due = scheduled_assessment_documents_current[
                -1
            ]

        # Check it is not already marked as completed
        if scheduled_assessment_currently_due:
            if scheduled_assessment_currently_due["completed"]:
                scheduled_assessment_currently_due = None

        # We have had low confidence in the code which marks completed.
        # Check the possibility that a patient has submitted an assessment log since this was due.
        if scheduled_assessment_currently_due:
            # gather patient-submitted assessment logs for this assessment
            assessment_log_documents_current = [
                assessment_log_current
                for assessment_log_current in assessment_log_documents
                if assessment_log_current["assessmentId"] == assessment_id_current
                and assessment_log_current["patientSubmitted"]
            ]

            if assessment_log_documents_current:
                # determine which was most recent
                assessment_log_most_recent = sorted(
                    assessment_log_documents_current,
                    key=lambda doc: date_utils.parse_datetime(doc["recordedDateTime"]),
                )[-1]

                # if it came after we were due, then we were already submitted
                if date_utils.parse_datetime(
                    assessment_log_most_recent["recordedDateTime"]
                ).date() >= date_utils.parse_date(
                    scheduled_assessment_currently_due["dueDate"]
                ):
                    scheduled_assessment_currently_due = None

        # This assessment appears due
        if scheduled_assessment_currently_due:
            assigned_scheduled_assessments.append(scheduled_assessment_currently_due)

    return {
        "assignedValuesInventory": assigned_values_inventory,
        "assignedSafetyPlan": assigned_safety_plan,
        "assignedScheduledAssessments": assigned_scheduled_assessments,
    }
