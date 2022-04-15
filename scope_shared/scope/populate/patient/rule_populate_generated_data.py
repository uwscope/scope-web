import copy
import faker as _faker
import pymongo.database
from typing import List, Optional

import scope.database.patient_unsafe_utils
import scope.database.patient
import scope.database.patients
import scope.database.providers
import scope.enums
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.testing.fake_data.fixtures_fake_activity
import scope.testing.fake_data.fixtures_fake_activity_logs
import scope.testing.fake_data.fixtures_fake_assessments
import scope.testing.fake_data.fixtures_fake_assessment_contents
import scope.testing.fake_data.fixtures_fake_assessment_logs
import scope.testing.fake_data.fixtures_fake_activities
import scope.testing.fake_data.fixtures_fake_case_review
import scope.testing.fake_data.fixtures_fake_case_reviews
import scope.testing.fake_data.fixtures_fake_clinical_history
import scope.testing.fake_data.fixtures_fake_contact
import scope.testing.fake_data.fixtures_fake_life_area_contents
import scope.testing.fake_data.fixtures_fake_mood_log
import scope.testing.fake_data.fixtures_fake_mood_logs
import scope.testing.fake_data.fixtures_fake_patient_profile
import scope.testing.fake_data.fixtures_fake_provider_identity
import scope.testing.fake_data.fixtures_fake_referral_status
import scope.testing.fake_data.fixtures_fake_safety_plan
import scope.testing.fake_data.fixtures_fake_session
import scope.testing.fake_data.fixtures_fake_sessions
import scope.testing.fake_data.fixtures_fake_scheduled_activities
import scope.testing.fake_data.fixtures_fake_scheduled_assessments
import scope.testing.fake_data.fixtures_fake_values_inventory

ACTION_NAME = "populate_generated_data"


class PopulateGeneratedData(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # Search for any existing patient who has the desired action pending
        for patient_config_current in populate_config["patients"]["existing"]:
            actions = patient_config_current.get("actions", [])
            if ACTION_NAME in actions:
                return _PopulateGeneratedDataAction(
                    patient_id=patient_config_current["patientId"],
                    patient_name=patient_config_current["name"],
                )

        return None


class _PopulateGeneratedDataAction(PopulateAction):
    patient_id: str
    patient_name: str

    def __init__(
        self,
        *,
        patient_id: str,
        patient_name: str,
    ):
        self.patient_id = patient_id
        self.patient_name = patient_name

    def prompt(self) -> List[str]:
        return [
            "Populate generated data for patient '{}' ({})".format(
                self.patient_name,
                self.patient_id,
            )
        ]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Get the patient config
        patient_config = None
        for patient_config_current in populate_config["patients"]["existing"]:
            if patient_config_current["patientId"] == self.patient_id:
                patient_config = patient_config_current
                break

        # Confirm we found the patient
        if not patient_config:
            raise ValueError("populate_config was modified")

        # Remove the action from the pending list
        patient_config["actions"].remove(ACTION_NAME)

        # Perform the populate
        _populate_generated_data(
            database=populate_context.database,
            faker=populate_context.faker,
            patient_config=patient_config,
        )

        return populate_config


def _populate_generated_data(
    *,
    database: pymongo.database.Database,
    faker: _faker.Faker,
    patient_config: dict,
) -> None:
    """
    Populate the specific documents we want in a "new" patient.
    """

    # Get the patient ID
    patient_id = patient_config["patientId"]

    # Get the patient identity document
    patient_identity_document = scope.database.patients.get_patient_identity(
        database=database,
        patient_id=patient_id,
    )

    # Get the patient collection
    patient_collection = database.get_collection(
        name=patient_identity_document["collection"]
    )

    def _profile():
        ################################################################################
        # Store a full profile.
        # - It will need the current "_rev", because the profile will already exist.
        ################################################################################

        existing_profile = scope.database.patient.get_patient_profile(
            collection=patient_collection,
        )

        # Obtain a fake profile
        fake_patient_profile_factory = scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
            faker_factory=faker,
        )
        fake_patient_profile = fake_patient_profile_factory()

        fake_patient_profile.update(
            {
                "_rev": existing_profile["_rev"],
                "name": existing_profile["name"],
                "MRN": existing_profile["MRN"],
            }
        )

        scope.database.patient.put_patient_profile(
            database=database,
            collection=patient_collection,
            patient_id=patient_id,
            patient_profile=fake_patient_profile,
        )

    _profile()

    ################################################################################
    # These documents are simple and do not have any cross dependencies.
    ################################################################################

    def _clinical_history():
        existing_clinical_history = (
            scope.database.patient.clinical_history.get_clinical_history(
                collection=patient_collection
            )
        )

        fake_clinical_history_factory = scope.testing.fake_data.fixtures_fake_clinical_history.fake_clinical_history_factory(
            faker_factory=faker,
        )
        fake_clinical_history = fake_clinical_history_factory()

        clinical_history = copy.deepcopy(existing_clinical_history)
        del clinical_history["_id"]
        clinical_history.update(fake_clinical_history)
        scope.database.patient.clinical_history.put_clinical_history(
            collection=patient_collection,
            clinical_history=clinical_history,
        )

    _clinical_history()

    def _case_reviews():
        fake_case_reviews_factory = scope.testing.fake_data.fixtures_fake_case_reviews.fake_case_reviews_factory(
            fake_case_review_factory=scope.testing.fake_data.fixtures_fake_case_review.fake_case_review_factory(
                faker_factory=faker,
            ),
        )
        case_reviews = fake_case_reviews_factory()
        for case_review_current in case_reviews:
            scope.database.patient.post_case_review(
                collection=patient_collection,
                case_review=case_review_current,
            )

    _case_reviews()

    def _mood_logs():
        fake_mood_logs_factory = scope.testing.fake_data.fixtures_fake_mood_logs.fake_mood_logs_factory(
            fake_mood_log_factory=scope.testing.fake_data.fixtures_fake_mood_log.fake_mood_log_factory(
                faker_factory=faker,
            ),
        )
        mood_logs = fake_mood_logs_factory()
        for mood_log_current in mood_logs:
            scope.database.patient.post_mood_log(
                collection=patient_collection,
                mood_log=mood_log_current,
            )

    _mood_logs()

    ################################################################################
    # Contacts are used only for safety plan.
    ################################################################################
    def _safety_plan():
        fake_contact_factory = (
            scope.testing.fake_data.fixtures_fake_contact.fake_contact_factory(
                faker_factory=faker,
            )
        )
        fake_safety_plan_factory = (
            scope.testing.fake_data.fixtures_fake_safety_plan.fake_safety_plan_factory(
                faker_factory=faker,
                fake_contact_factory=fake_contact_factory,
            )
        )

        existing_safety_plan = scope.database.patient.get_safety_plan(
            collection=patient_collection
        )

        fake_safety_plan = fake_safety_plan_factory()

        safety_plan = copy.deepcopy(existing_safety_plan)
        del safety_plan["_id"]
        safety_plan.update(fake_safety_plan)
        scope.database.patient.put_safety_plan(
            collection=patient_collection,
            safety_plan=safety_plan,
        )

    _safety_plan()

    ################################################################################
    # Referral status are used only for sessions.
    ################################################################################
    def _sessions():
        fake_referral_status_factory = scope.testing.fake_data.fixtures_fake_referral_status.fake_referral_status_factory(
            faker_factory=faker,
        )
        fake_sessions_factory = scope.testing.fake_data.fixtures_fake_sessions.fake_sessions_factory(
            fake_session_factory=scope.testing.fake_data.fixtures_fake_session.fake_session_factory(
                faker_factory=faker,
                fake_referral_status_factory=fake_referral_status_factory,
            ),
        )
        for session in fake_sessions_factory():
            scope.database.patient.sessions.post_session(
                collection=patient_collection,
                session=session,
            )

    _sessions()

    ################################################################################
    # Assessments required to create scheduled assessments.
    ################################################################################
    def _assessments_and_scheduled_assessments():
        fake_assessment_contents = (
            scope.testing.fake_data.fixtures_fake_assessment_contents.fake_assessment_contents_factory()()
        )

        fake_assessments_factory = (
            scope.testing.fake_data.fixtures_fake_assessments.fake_assessments_factory(
                faker_factory=faker,
                assessment_contents=fake_assessment_contents,
            )
        )
        fake_assessments = fake_assessments_factory()

        for fake_assessment_current in fake_assessments:
            scope.database.patient_unsafe_utils.unsafe_update_assessment(
                collection=patient_collection,
                set_id=fake_assessment_current[
                    scope.database.patient.assessments.SEMANTIC_SET_ID
                ],
                assessment_complete=fake_assessment_current,
            )

            # fake_scheduled_assessments_factory = scope.testing.fake_data.fixtures_fake_scheduled_assessments.fake_scheduled_assessments_factory(
            #     faker_factory=faker_factory,
            #     assessment=fake_assessment_current,
            # )
            # fake_scheduled_assessments = fake_scheduled_assessments_factory()
            #
            # for fake_scheduled_assessment_current in fake_scheduled_assessments:
            #     scope.database.patient.scheduled_assessments.post_scheduled_assessment(
            #         collection=patient_collection,
            #         scheduled_assessment=fake_scheduled_assessment_current,
            #     )

    _assessments_and_scheduled_assessments()

    ################################################################################
    # Life area contents is required to create a values inventory.
    # Values inventory is required to create activities.
    # - If a value inventory does not include include at least one value,
    #   then we cannot generate any associated activities.
    ################################################################################
    def _values_inventory_and_activities():
        # Create life areas
        fake_life_area_contents_factory = (
            scope.testing.fake_data.fixtures_fake_life_area_contents.fake_life_area_contents_factory()
        )
        life_area_contents = fake_life_area_contents_factory()

        # Create and store values inventory
        existing_values_inventory = scope.database.patient.get_values_inventory(
            collection=patient_collection
        )

        fake_values_inventory_factory = scope.testing.fake_data.fixtures_fake_values_inventory.fake_values_inventory_factory(
            faker_factory=faker,
            life_areas=life_area_contents,
        )
        fake_values_inventory = fake_values_inventory_factory()

        values_inventory = copy.deepcopy(existing_values_inventory)
        del values_inventory["_id"]
        values_inventory.update(fake_values_inventory)
        scope.database.patient.put_values_inventory(
            collection=patient_collection,
            values_inventory=values_inventory,
        )

        # Create and store activities
        if len(values_inventory.get("values", [])) > 1:
            fake_activities_factory = scope.testing.fake_data.fixtures_fake_activities.fake_activities_factory(
                fake_activity_factory=scope.testing.fake_data.fixtures_fake_activity.fake_activity_factory(
                    faker_factory=faker,
                    values_inventory=values_inventory,
                )
            )
            activities = fake_activities_factory()
            for activity_current in activities:
                scope.database.patient.post_activity(
                    collection=patient_collection,
                    activity=activity_current,
                )

    _values_inventory_and_activities()
