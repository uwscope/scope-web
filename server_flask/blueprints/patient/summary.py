import datetime
import flask
import flask_json
from typing import List

import request_context
import request_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory


patient_summary_blueprint = flask.Blueprint(
    "patient_summary_blueprint",
    __name__,
)


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


@patient_summary_blueprint.route(
    "/<string:patient_id>/summary",
    methods=["GET"],
)
@flask_json.as_json
def get_patient_summary(patient_id):
    """
    Obtain patient summary to be used by patient app.
    """

    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    activity_documents = scope.database.patient.activities.get_activities(
        collection=patient_collection,
    )
    activity_documents = activity_documents or []

    safety_plan_document = scope.database.patient.safety_plan.get_safety_plan(
        collection=patient_collection,
    )

    scheduled_assessment_documents = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=patient_collection,
        )
    )
    scheduled_assessment_documents = scheduled_assessment_documents or []

    values_inventory_document = (
        scope.database.patient.values_inventory.get_values_inventory(
            collection=patient_collection,
        )
    )

    if not all(
        [
            safety_plan_document,
            values_inventory_document,
        ]
    ):
        request_utils.abort_document_not_found()

    return compute_patient_summary(
        activity_documents=activity_documents,
        safety_plan_document=safety_plan_document,
        scheduled_assessment_documents=scheduled_assessment_documents,
        values_inventory_document=values_inventory_document,
    )
