import copy
import faker
import pymongo.database

import scope.database.patient.activities
import scope.database.patient.case_reviews
import scope.database.patient.clinical_history
import scope.database.patient.mood_logs
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.sessions
import scope.database.patient.values_inventory
import scope.database.patients
import scope.database.providers
import scope.testing.fake_data.enums
import scope.testing.fake_data.fixtures_fake_activity
import scope.testing.fake_data.fixtures_fake_activities
import scope.testing.fake_data.fixtures_fake_case_review
import scope.testing.fake_data.fixtures_fake_case_reviews
import scope.testing.fake_data.fixtures_fake_clinical_history
import scope.testing.fake_data.fixtures_fake_contact
import scope.testing.fake_data.fixtures_fake_life_areas
import scope.testing.fake_data.fixtures_fake_mood_log
import scope.testing.fake_data.fixtures_fake_mood_logs
import scope.testing.fake_data.fixtures_fake_patient_profile
import scope.testing.fake_data.fixtures_fake_provider_identity
import scope.testing.fake_data.fixtures_fake_referral_status
import scope.testing.fake_data.fixtures_fake_safety_plan
import scope.testing.fake_data.fixtures_fake_session
import scope.testing.fake_data.fixtures_fake_sessions
import scope.testing.fake_data.fixtures_fake_values_inventory


def populate_database(
    *,
    database: pymongo.database.Database,
):
    # Faker instance
    faker_factory = faker.Faker(locale="la")

    #
    # Patient profile factory
    #
    fake_patient_profile_factory = scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
        faker_factory=faker_factory,
    )

    # TODO: Remove when patient app includes authentication
    patient_persistent_identity = scope.database.patients.get_patient_identity(
        database=database, patient_id="persistent"
    )
    if patient_persistent_identity is None:
        profile = fake_patient_profile_factory()

        patient_identity_current = scope.database.patients.create_patient(
            database=database,
            patient_id="persistent",
            name=profile["name"],
            MRN=profile["MRN"],
        )
        patient_collection = database.get_collection(patient_identity_current["collection"])

        _populate_patient(
            faker_factory=faker_factory,
            database=database,
            patient_collection=patient_collection,
            patient_id=patient_identity_current["patientId"],
            profile=profile,
        )

    for patient_count in range(10):
        profile = fake_patient_profile_factory()

        patient_identity_current = scope.database.patients.create_patient(
            database=database,
            name=profile["name"],
            MRN=profile["MRN"],
        )
        patient_collection = database.get_collection(patient_identity_current["collection"])

        _populate_patient(
            faker_factory=faker_factory,
            database=database,
            patient_collection=patient_collection,
            patient_id=patient_identity_current["patientId"],
            profile=profile,
        )

    #
    # Provider identity factory
    #

    fake_provider_identity_factory = scope.testing.fake_data.fixtures_fake_provider_identity.fake_provider_identity_factory(
        faker_factory=faker_factory,
    )

    generate_roles = [
        {"role_value": scope.testing.fake_data.enums.ProviderRole.StudyStaff.value, "number_to_generate": 5},
        {"role_value": scope.testing.fake_data.enums.ProviderRole.Oncologist.value, "number_to_generate": 2},
        {"role_value": scope.testing.fake_data.enums.ProviderRole.Psychiatrist.value, "number_to_generate": 2},
        {"role_value": scope.testing.fake_data.enums.ProviderRole.SocialWorker.value, "number_to_generate": 8},
    ]
    for generate_current in generate_roles:
        for _ in range(generate_current["number_to_generate"]):
            provider_identity_current = fake_provider_identity_factory()

            provider_identity_current = scope.database.providers.create_provider(
                database=database,
                name=provider_identity_current["name"],
                role=generate_current["role_value"],
            )


def _populate_patient(
    *,
    faker_factory: faker.Faker,
    database: pymongo.database.Database,
    patient_id: str,
    patient_collection: pymongo.collection.Collection,
    profile: dict,
):
    # Store the profile used to create this patient.
    # It will need the current "_rev".
    profile = copy.deepcopy(profile)
    profile["_rev"] = scope.database.patient.patient_profile.get_patient_profile(
        collection=patient_collection,
    )["_rev"]
    scope.database.patient.patient_profile.put_patient_profile(
        database=database,
        collection=patient_collection,
        patient_id=patient_id,
        patient_profile=profile,
    )

    # Obtain factories used by other factories
    fake_contact_factory = (
        scope.testing.fake_data.fixtures_fake_contact.fake_contact_factory(
            faker_factory=faker_factory,
        )
    )
    fake_life_areas_factory = (
        scope.testing.fake_data.fixtures_fake_life_areas.fake_life_areas_factory()
    )

    # Obtain fixed documents
    fake_life_areas = fake_life_areas_factory()

    # Obtain necessary document factories
    fake_clinical_history_factory = scope.testing.fake_data.fixtures_fake_clinical_history.fake_clinical_history_factory(
        faker_factory=faker_factory,
    )
    fake_values_inventory_factory = scope.testing.fake_data.fixtures_fake_values_inventory.fake_values_inventory_factory(
        faker_factory=faker_factory,
        fake_life_areas=fake_life_areas,
    )
    # Obtain fake values inventory document to pass it in fake_activities_factory
    fake_values_inventory = fake_values_inventory_factory()

    fake_safety_plan_factory = (
        scope.testing.fake_data.fixtures_fake_safety_plan.fake_safety_plan_factory(
            faker_factory=faker_factory,
            fake_contact_factory=fake_contact_factory,
        )
    )
    fake_sessions_factory = scope.testing.fake_data.fixtures_fake_sessions.fake_sessions_factory(
        fake_session_factory=scope.testing.fake_data.fixtures_fake_session.fake_session_factory(
            faker_factory=faker_factory,
            fake_referral_status_factory=scope.testing.fake_data.fixtures_fake_referral_status.fake_referral_status_factory(
                faker_factory=faker_factory,
            ),
        ),
    )
    fake_case_reviews_factory = scope.testing.fake_data.fixtures_fake_case_reviews.fake_case_reviews_factory(
        fake_case_review_factory=scope.testing.fake_data.fixtures_fake_case_review.fake_case_review_factory(
            faker_factory=faker_factory,
        ),
    )

    fake_mood_logs_factory = scope.testing.fake_data.fixtures_fake_mood_logs.fake_mood_logs_factory(
        fake_mood_log_factory=scope.testing.fake_data.fixtures_fake_mood_log.fake_mood_log_factory(
            faker_factory=faker_factory,
        ),
    )

    fake_activities_factory = scope.testing.fake_data.fixtures_fake_activities.fake_activities_factory(
        fake_activity_factory=scope.testing.fake_data.fixtures_fake_activity.fake_activity_factory(
            faker_factory=faker_factory,
            fake_life_areas=fake_life_areas,
            fake_values_inventory=fake_values_inventory,
        )
    )

    # Put appropriate documents
    scope.database.patient.clinical_history.put_clinical_history(
        collection=patient_collection,
        clinical_history=fake_clinical_history_factory(),
    )
    scope.database.patient.values_inventory.put_values_inventory(
        collection=patient_collection,
        values_inventory=fake_values_inventory_factory(),
    )
    scope.database.patient.safety_plan.put_safety_plan(
        collection=patient_collection,
        safety_plan=fake_safety_plan_factory(),
    )
    for session in fake_sessions_factory():
        scope.database.patient.sessions.post_session(
            collection=patient_collection,
            session=session,
        )
    for case_review in fake_case_reviews_factory():
        scope.database.patient.case_reviews.post_case_review(
            collection=patient_collection,
            case_review=case_review,
        )

    for mood_log in fake_mood_logs_factory():
        scope.database.patient.mood_logs.post_mood_log(
            collection=patient_collection,
            mood_log=mood_log,
        )

    if fake_values_inventory.get("values") is not None:
        for activity in fake_activities_factory():
            scope.database.patient.activities.post_activity(
                collection=patient_collection,
                activity=activity,
            )
