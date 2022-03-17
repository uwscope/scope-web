import copy
import faker
from typing import List

import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.assessments
import scope.database.patient.assessment_logs
import scope.database.patient.case_reviews
import scope.database.patient.clinical_history
import scope.database.patient.mood_logs
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.sessions
import scope.database.patient.scheduled_activities
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory
import scope.database.patient_unsafe_utils
import scope.database.patients
import scope.database.providers
import scope.enums
import scope.populate.fake.populate_fake
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


def create_fake_patient_configs(
    *,
    faker_factory: faker.Faker,
    create_fake: int,
    actions: List[str],
) -> List[dict]:
    created_patient_configs = []
    for _ in range(create_fake):
        created_patient_config = create_fake_patient_config(
            faker_factory=faker_factory,
            actions=actions,
        )
        created_patient_configs.append(created_patient_config)

    return created_patient_configs


def create_fake_patient_config(
    *,
    faker_factory: faker.Faker,
    actions: List[str],
) -> dict:
    # Obtain a fake profile, from which we can take necessary fields
    fake_patient_profile_factory = scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
        faker_factory=faker_factory,
    )
    fake_patient_profile = fake_patient_profile_factory()

    # Create the config for creating this fake patient
    fake_patient_config = {
        "name": fake_patient_profile["name"],
        "MRN": fake_patient_profile["MRN"],
        "actions": copy.deepcopy(actions),
    }

    return fake_patient_config
