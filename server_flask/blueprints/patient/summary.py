import datetime
import flask
import flask_json
from request_context import request_context
import scope.database.date_utils as date_utils
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory


patient_summary_blueprint = flask.Blueprint(
    "patient_summary_blueprint",
    __name__,
)


@patient_summary_blueprint.route(
    "/<string:patient_id>/summary",
    methods=["GET"],
)
@flask_json.as_json
def get_patient_summary(patient_id):
    """
    Obtain patient summary to be used by patient app.
    {
        # assignedValuesInventory <- True, if assigned is True, and not a single activity exists in values inventory singleton
        assignedValuesInventory: boolean;

        # assignedSafetyPlan <- True, if assigned is True, and lastUpdatedDate < assignedDate in safety plan singleton
        assignedSafetyPlan: boolean;

        # scheduledAssessments that are not completed and dueDate <= today.
        assignedScheduledAssessments: IScheduledAssessment[];
    }
    """

    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # assignedValuesInventory boolean flag
    assigned_values_inventory: bool = True
    # Get the values inventory document
    values_inventory = scope.database.patient.values_inventory.get_values_inventory(
        collection=patient_collection,
    )
    # flask.current_app.logger.info(values_inventory)
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

    # assignedSafetyPlan boolean flag
    assigned_safety_plan: bool = True
    # Get the safety plan document
    safety_plan = scope.database.patient.safety_plan.get_safety_plan(
        collection=patient_collection,
    )

    if safety_plan["assigned"]:
        if safety_plan.get("assignedDate", []) and safety_plan.get(
            "lastUpdatedDate", []
        ):

            assigned_date = date_utils.format_string(safety_plan.get("assignedDate"))
            last_updated_date = date_utils.format_string(
                safety_plan.get("lastUpdatedDate")
            )
            if last_updated_date >= assigned_date:
                assigned_safety_plan = False

    else:
        assigned_safety_plan = False

    # assignedScheduledAssessments list
    scheduled_assessments = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=patient_collection,
        )
    )

    assigned_scheduled_assessments = list(
        filter(
            lambda scheduled_assessment_current: (
                (scheduled_assessment_current["completed"] == False)
                and (
                    date_utils.format_string(scheduled_assessment_current["dueDate"])
                    <= datetime.datetime.today()
                )
            ),
            scheduled_assessments,
        )
    )

    result = {
        "assignedValuesInventory": assigned_values_inventory,
        "assignedSafetyPlan": assigned_safety_plan,
        "assignedScheduledAssessments": assigned_scheduled_assessments,
    }

    return result
