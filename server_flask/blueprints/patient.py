from database import DocumentDB
from flask import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_json import as_json
from models.patient import Patient

patient_blueprint = Blueprint("patient_blueprint", __name__)


@patient_blueprint.route("/add_patient", methods=["POST"])
@as_json
def add_patient_account():
    """
    Create dummy patient account.
    """
    new_patient = Patient(name="Ted Lasso")
    new_patient.insert()
    # DocumentDB.insert("patient", {"name": "anant"}) - #Another way to add the patient if we want to use model files.
    return "Patient successfully created", 200
