import datetime
import flask
import flask_json

import request_context
import request_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory
import scope.utils.compute_patient_summary


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

    return scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=activity_documents,
        safety_plan_document=safety_plan_document,
        scheduled_assessment_documents=scheduled_assessment_documents,
        values_inventory_document=values_inventory_document,
        date_due=datetime.date.today(),
    )
