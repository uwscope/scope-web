import datetime
import flask
import flask_json
from request_context import request_context
import request_utils
import scope.database.date_utils as date_utils
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory


patient_summary_blueprint = flask.Blueprint(
    "patient_summary_blueprint",
    __name__,
)


def compute_patient_summary(patient: dict) -> dict:
    """
    {
        # assignedValuesInventory <- True, if assigned is True, and not a single activity exists in values inventory singleton
        assignedValuesInventory: boolean;

        # assignedSafetyPlan <- True, if assigned is True, and lastUpdatedDate < assignedDate in safety plan singleton
        assignedSafetyPlan: boolean;

        # scheduledAssessments that are not completed and dueDate <= today.
        assignedScheduledAssessments: IScheduledAssessment[];
    }
    """
    # assignedValuesInventory
    assigned_values_inventory: bool = True
    values_inventory = patient["valuesInventory"]
    if values_inventory["assigned"]:
        if values_inventory.get("values", []):
            values = values_inventory.get("values")
            for value in values:
                # If there is even a single activity, assignedValuesInventory will become False
                if len(value.get("activities", [])) > 0:
                    assigned_values_inventory = False
                    break
    else:
        assigned_values_inventory = False

    # assignedSafetyPlan
    assigned_safety_plan: bool = True
    # Get the safety plan document
    safety_plan = patient["safetyPlan"]

    if safety_plan["assigned"]:
        if safety_plan.get("assignedDate", []) and safety_plan.get(
            "lastUpdatedDate", []
        ):
            assigned_date = date_utils.parse_date(safety_plan.get("assignedDate"))
            last_updated_date = date_utils.parse_date(
                safety_plan.get("lastUpdatedDate")
            )
            if last_updated_date >= assigned_date:
                assigned_safety_plan = False

    else:
        assigned_safety_plan = False

    # assignedScheduledAssessments
    scheduled_assessments = patient["scheduledAssessments"]
    assigned_scheduled_assessments = list(
        filter(
            lambda scheduled_assessment_current: (
                (scheduled_assessment_current["completed"] == False)
                and (
                    date_utils.parse_date(scheduled_assessment_current["dueDate"])
                    <= datetime.datetime.today()
                )
            ),
            scheduled_assessments,
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

    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    patient = {
        "valuesInventory": scope.database.patient.values_inventory.get_values_inventory(
            collection=patient_collection,
        ),
        "safetyPlan": scope.database.patient.safety_plan.get_safety_plan(
            collection=patient_collection,
        ),
        "scheduledAssessments": scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=patient_collection,
        ),
    }
    for document in patient.values():
        if document is None:
            request_utils.abort_document_not_found()

    return compute_patient_summary(patient=patient)
